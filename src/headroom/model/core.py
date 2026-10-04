"""Stage 2 — uptake, feasibility and the cost channel, as a Monte Carlo.

Every behavioural constant comes from the ledger (``assumptions.yaml``);
this module contains arithmetic only. For each draw the ledger is sampled
once, the baseline is drawn, and each scenario's *increment over current
law* is computed per municipality and year. Results are percentiles over
draws. ``tests/test_ledger.py`` fails if a numeric literal that looks like
a behavioural assumption appears here.
"""

from __future__ import annotations

import numpy as np

from headroom.ledger import Ledger

SCENARIOS = ("adu", "missing_middle", "parking", "fees_handbook", "fees_ri", "tod")
# The five enacted together (fees at the state's actual level), reported as an
# upper bound: increments are added and only the statewide capacity ceiling
# limits the sum; no interaction between reforms is modelled.
COMBINED = ("adu", "missing_middle", "parking", "fees_ri", "tod")
PCTS = (10, 50, 90)


def _ramp(years: np.ndarray, ramp: np.ndarray) -> np.ndarray:
    """Uptake scaling by year: year 1 at 1/ramp … reaching 1 at year = ramp."""
    # years: (Y,), ramp: (N,) -> (N, Y)
    return np.minimum(1.0, years[None, :] / np.maximum(ramp[:, None], 1e-9))


def level_noise(expected: np.ndarray, cv: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Multiplicative year-to-year noise with mean one.

    Two components: a level uncertainty (the ledger's coefficient of
    variation) and count noise — a town permitting ten units a year varies
    by ±30 % from chance alone, so the Poisson variance 1/expected is added
    to the CV squared. Lognormal so the draw is never negative.
    """
    cv_tot2 = cv[:, None] ** 2 + 1.0 / np.maximum(expected, 1.0)
    sigma = np.sqrt(np.log1p(cv_tot2))
    return rng.lognormal(-(sigma**2) / 2, sigma, size=expected.shape)


def _trend_forecast(ys: list[float], years_hist: list[int], years_out: list[int], recent_n: int):
    """Linear trend and recent mean for one town. Returns (trend[Y], recent mean)."""
    x = np.array(years_hist, dtype=float)
    y = np.array(ys, dtype=float)
    if len(x) >= 2 and np.ptp(x) > 0:
        b, a = np.polyfit(x, y, 1)
    else:
        b, a = 0.0, float(y.mean()) if len(y) else 0.0
    trend = np.maximum(0.0, a + b * np.array(years_out, dtype=float))
    recent = y[-recent_n:] if len(y) >= recent_n else y
    recent_mean = float(recent.mean()) if len(recent) else 0.0
    return trend, recent_mean


class Model:
    def __init__(self, ledger: Ledger, towns: dict, *, draws: int | None = None, seed: int | None = None):
        self.ledger = ledger
        self.towns_meta = towns
        self.towns = towns["towns"]
        self.names = list(self.towns.keys())
        self.tier = towns["tier"]
        self.draws = draws or int(ledger.meta["monte_carlo_draws"])
        self.seed = seed if seed is not None else int(ledger.meta["seed"])
        self.recent_n = int(ledger.meta["baseline_recent_years"])
        h0, h1 = ledger.meta["horizon"]
        self.years = list(range(int(h0), int(h1) + 1))
        self.year_idx = np.arange(1, len(self.years) + 1, dtype=float)

    # ------------------------------------------------------------ inputs
    def _stage1(self, name: str, p: dict) -> dict:
        """Stage 1 quantities for one town, at this tier, as (N,) arrays."""
        t = self.towns[name]
        N = self.draws
        ones = np.ones(N)
        if self.tier in ("A", "B") and t.get("n_R1") is not None:
            r1 = t["n_R1"] * ones
            r1_sew = t["n_R1_sewered"] * ones
            lot20 = t["n_R1_lot20k_plus"] * ones
            lot20_sew = t["n_R1_lot20k_plus_sewered"] * ones
            sf_only = t["n_R1_sf_only"] + t["n_R1_unknown"] * p["tierc_sf_only_share"]
            sf_only_sew = t["n_R1_sf_only_sewered"] + t["n_R1_unknown_sewered"] * p["tierc_sf_only_share"]
        else:
            u1 = float(t["stock"].get("units_1") or 0)
            r1 = u1 * ones
            r1_sew = r1 * p["tierc_sewered_share"]
            lot20 = r1 * p["tierc_lot20k_share"]
            lot20_sew = lot20 * p["tierc_sewered_share"]
            sf_only = r1 * p["tierc_sf_only_share"]
            sf_only_sew = sf_only * p["tierc_sewered_share"]
        return {
            "r1": r1,
            "r1_sew": r1_sew,
            "lot20": lot20,
            "lot20_sew": lot20_sew,
            "sf_only": sf_only,
            "sf_only_sew": sf_only_sew,
        }

    # ------------------------------------------------------------ baseline
    def baseline(self, p: dict, rng: np.random.Generator) -> np.ndarray:
        """Baseline permits, shape (N, T, Y)."""
        N, T, Y = self.draws, len(self.names), len(self.years)
        out = np.zeros((N, T, Y))
        # Census BPS → State-survey level (data), times its uncertainty (ledger).
        ratio = float((self.towns_meta.get("permit_undercount") or {}).get("eoh_to_bps_ratio_2025", 1.0))
        scale = ratio * p["permit_undercount_adjustment"]
        recent_total = np.zeros(N)
        for j, name in enumerate(self.names):
            t = self.towns[name]
            hist = {int(k): v for k, v in t["permits_bps"].items()}
            yrs = sorted(hist)
            trend, recent = _trend_forecast([hist[y] for y in yrs], yrs, self.years, self.recent_n)
            w = p["baseline_trend_weight"][:, None]
            expected = (w * trend[None, :] + (1 - w) * recent) * scale[:, None]
            out[:, j, :] = expected * level_noise(expected, p["baseline_noise_cv"], rng)
            recent_total += recent * scale
        # Statewide construction-capacity ceiling: a multiple of the state's own
        # recent annual level, so the same ledger entry scales to any state.
        self.ceiling = p["statewide_capacity_multiple"] * recent_total  # (N,)
        return self.cap_total(out)

    def cap_total(self, arr: np.ndarray) -> np.ndarray:
        """Scale every town down proportionally in any draw-year above the ceiling."""
        total = arr.sum(axis=1)  # (N, Y)
        ceiling = self.ceiling[:, None]
        scale = np.where(total > ceiling, ceiling / np.maximum(total, 1e-9), 1.0)
        return arr * scale[:, None, :]

    # ------------------------------------------------------------ scenarios
    def increments(self, p: dict, base: np.ndarray) -> dict[str, np.ndarray]:
        N, T, Y = base.shape
        yi = self.year_idx
        inc = {s: np.zeros((N, T, Y)) for s in SCENARIOS}
        adu_ramp = _ramp(yi, p["adu_ramp_years"])
        mm_ramp = _ramp(yi, p["mm_ramp_years"])
        tod_ramp = _ramp(yi, p["tod_ramp_years"])
        for j, name in enumerate(self.names):
            s1 = self._stage1(name, p)
            t = self.towns[name]

            # ADU: lots below the by-right threshold become eligible for a
            # detached ADU; sewered and septic lots weighted separately.
            newly = np.maximum(0.0, s1["r1"] - s1["lot20"])
            newly_sew = np.maximum(0.0, s1["r1_sew"] - s1["lot20_sew"])
            newly_sep = np.maximum(0.0, newly - newly_sew)
            eff = newly_sew + newly_sep * p["adu_septic_multiplier"]
            inc["adu"][:, j, :] = (eff * p["adu_uptake_detached_annual"])[:, None] * adu_ramp

            # Missing middle: single-family-only lots convert to 2–6 units.
            sf, sf_sew = s1["sf_only"], s1["sf_only_sew"]
            sf_sep = np.maximum(0.0, sf - sf_sew)
            eff_mm = (sf_sew + sf_sep * p["mm_septic_multiplier"]) * p["mm_feasibility_share"]
            net_units = np.maximum(0.0, p["mm_units_per_conversion"] - 1.0)
            inc["missing_middle"][:, j, :] = (eff_mm * p["mm_conversion_rate_annual"] * net_units)[:, None] * mm_ramp

            # Cost channel: parking.
            mf = base[:, j, :] * t["mf_share_2018_2025"]
            sf_units = base[:, j, :] - mf
            req, prov = p["parking_required_mf_baseline"], p["parking_provided_unmandated"]
            excess_out = np.maximum(0.0, req - prov)
            excess_in = np.maximum(0.0, np.minimum(req, 1.0) - prov)  # current-law cap near transit
            share_in = p["mf_permit_share_in_tod_buffers"]
            saving = (excess_out * (1 - share_in) + excess_in * share_in) * p["parking_cost_per_space"]
            pct = saving / p["dev_cost_per_unit_mf"]
            inc["parking"][:, j, :] = mf * (p["supply_cost_elasticity"] * pct)[:, None]

            # Cost channel: fees, at the handbook benchmark and at RI actual.
            for key, fee in (
                ("fees_handbook", p["fee_per_unit_handbook"]),
                ("fees_ri", p["fee_per_unit_ri"]),
            ):
                sav = fee * p["fee_reduction_share"]
                pct_mf = sav / p["dev_cost_per_unit_mf"]
                pct_sf = sav / p["dev_cost_per_unit_sf"]
                inc[key][:, j, :] = (
                    mf * (p["supply_cost_elasticity"] * pct_mf)[:, None]
                    + sf_units * (p["supply_cost_elasticity"] * pct_sf)[:, None]
                )

            # TOD: net capacity inside buffers at the scenario density.
            rows = t.get("tod_districts") or []
            if rows:
                area = np.array([r[0] for r in rows])
                cur = np.array([r[1] for r in rows])
                dens = p["tod_scenario_density_upa"][:, None]
                net = np.maximum(0.0, dens - cur[None, :]) * area[None, :]
                cap = net.sum(axis=1)
                inc["tod"][:, j, :] = (cap * p["tod_realization_rate_annual"])[:, None] * tod_ramp

        # The ceiling applies to every scenario total, and to all five together.
        combined = sum(inc[s] for s in COMBINED)
        for s in SCENARIOS:
            inc[s] = np.maximum(0.0, self.cap_total(base + inc[s]) - base)
        inc["combined"] = np.maximum(0.0, self.cap_total(base + combined) - base)
        return inc

    # ------------------------------------------------------------ run
    def run(self) -> dict:
        rng = np.random.default_rng(self.seed)
        p = self.ledger.sample(rng, self.draws)
        base = self.baseline(p, rng)
        inc = self.increments(p, base)
        res = {
            "meta": {
                "tier": self.tier,
                "draws": self.draws,
                "seed": self.seed,
                "years": self.years,
                "metric": self.ledger.meta.get("metric"),
                "towns": self.names,
            },
            "statewide": {},
            "towns": {},
            "sensitivity": {},
            "samples": {},
        }
        res["statewide"]["baseline"] = self._summ(base.sum(axis=1))
        for s, arr in inc.items():
            res["statewide"][s] = self._summ(arr.sum(axis=1))
            res["statewide"][f"{s}_total"] = self._summ((base + arr).sum(axis=1))
        for j, name in enumerate(self.names):
            res["towns"][name] = {"baseline": self._summ(base[:, j, :])}
            for s, arr in inc.items():
                res["towns"][name][s] = self._summ(arr[:, j, :])
        # Sensitivity: rank correlation of each parameter with the 5-year
        # statewide increment of each scenario it belongs to.
        for s, arr in inc.items():
            five = arr.sum(axis=(1, 2))
            scen_key = "fees" if s.startswith("fees") else s
            rows = []
            for pid, par in self.ledger.parameters.items():
                if par.distribution == "fixed" or not par.sensitivity:
                    continue
                if not (scen_key in par.scenarios or "all" in par.scenarios):
                    continue
                x = p[pid]
                if np.ptp(x) == 0 or np.ptp(five) == 0:
                    rho = 0.0
                else:
                    rho = float(np.corrcoef(_rank(x), _rank(five))[0, 1])
                lo = float(np.percentile(five[x <= np.percentile(x, 20)], 50)) if np.ptp(x) else 0.0
                hi = float(np.percentile(five[x >= np.percentile(x, 80)], 50)) if np.ptp(x) else 0.0
                rows.append(
                    {
                        "parameter": pid,
                        "label": par.label,
                        "spearman": round(rho, 3),
                        "p50_at_low_quintile": round(lo, 1),
                        "p50_at_high_quintile": round(hi, 1),
                        "status": par.status,
                    }
                )
            rows.sort(key=lambda r: -abs(r["spearman"]))
            res["sensitivity"][s] = rows
        res["samples"] = {pid: _quantiles(p[pid]) for pid in p}
        return res

    def _summ(self, arr: np.ndarray) -> dict:
        """Percentiles per year and for the five-year sum; arr is (N, Y)."""
        per_year = np.percentile(arr, PCTS, axis=0)
        total = arr.sum(axis=1)
        return {
            "years": self.years,
            "p10": [round(float(v), 1) for v in per_year[0]],
            "p50": [round(float(v), 1) for v in per_year[1]],
            "p90": [round(float(v), 1) for v in per_year[2]],
            "five_year": {f"p{q}": round(float(np.percentile(total, q)), 1) for q in PCTS},
            "five_year_mean": round(float(total.mean()), 1),
        }


def _rank(x: np.ndarray) -> np.ndarray:
    return np.argsort(np.argsort(x)).astype(float)


def _quantiles(x: np.ndarray) -> dict:
    return {f"p{q}": float(np.percentile(x, q)) for q in (5, 25, 50, 75, 95)}


def calibrate_adu(ledger: Ledger, towns: dict, p: dict | None = None) -> dict:
    """Implied 2024 ADU permits under current law versus the observed 163.

    Current law (2024): detached by right on lots ≥ 20,000 sq ft, conversions
    by right on any lot. 2024 was the first year after the expansion, so the
    ramp is at year one.
    """
    p = p or ledger.defaults()
    m = Model(ledger, towns, draws=1)
    pp = {k: np.array([v]) for k, v in p.items()}
    ramp = max(1.0, p["adu_ramp_years"])
    steady = 0.0
    eligible_detached = eligible_conversion = 0.0
    for name in m.names:
        s1 = m._stage1(name, pp)
        lot20_sep = max(0.0, float(s1["lot20"][0] - s1["lot20_sew"][0]))
        eff_det = float(s1["lot20_sew"][0]) + lot20_sep * p["adu_septic_multiplier"]
        r1_sep = max(0.0, float(s1["r1"][0] - s1["r1_sew"][0]))
        eff_conv = float(s1["r1_sew"][0]) + r1_sep * p["adu_septic_multiplier"]
        eligible_detached += eff_det
        eligible_conversion += eff_conv
        steady += eff_det * p["adu_uptake_detached_annual"] + eff_conv * p["adu_uptake_conversion_annual"]
    year1 = steady * min(1.0, 1.0 / ramp)
    year2 = steady * min(1.0, 2.0 / ramp)
    return {
        "eligible_lots_detached_by_right_today_sewer_adjusted": round(eligible_detached),
        "eligible_lots_conversion_sewer_adjusted": round(eligible_conversion),
        "implied_annual_adu_permits_at_steady_state": round(steady, 1),
        "implied_2024_if_ramp_year_1": round(year1, 1),
        "implied_2024_if_ramp_year_2": round(year2, 1),
        "observed_2024_adu_permits": 163,
        "observed_source": "HousingWorks RI 2025 Housing Fact Book (11 in 2021, 163 in 2024)",
        "observed_within_bracket": bool(min(year1, year2) <= 163 <= max(year1, year2)),
    }
