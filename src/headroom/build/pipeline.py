"""Assemble the per-municipality input table the model reads.

``headroom build`` runs this. It joins Stage 1 capacity (districts.json),
the permit series (Census BPS 2018–2025), the State's 2025 municipal survey
and ACS stock into ``out/build/towns.json`` at the requested data tier:

  tier A — State zoning layer + MuniAnchor ordinance-derived allowed uses
  tier B — State zoning layer only (allowed uses read from district text)
  tier C — no GIS at all: Census structure counts + ledger shares

Tier C is what any state can run from federal data alone; tiers A and B
are what a state with a zoning layer (and, for A, parsed ordinances) gets.
The model reads the same file shape at every tier, which is what makes the
tier comparison a like-for-like run.
"""

from __future__ import annotations

import json
import os
import statistics
from pathlib import Path

from headroom import DATA_DIR, OUT_DIR
from headroom.acquire import acs, arcgis, bps, eoh, geos, gtfs
from headroom.build import capacity, transit, zone_text
from headroom.municipalities import COUNTY_MCD_FIPS, RI_MUNICIPALITIES

BASELINE_YEARS = list(range(2018, 2026))


def acquire_all(*, refresh: bool = False, with_transit: bool = True) -> dict:
    """Retrieve every input from its authoritative source (cached)."""
    paths = {
        "zoning": arcgis.query_all(
            "rigis_zoning",
            out_fields="MUNI_NAME,ZONE_CODE,CZONE_CODE,ZONE_DESC,DENSITY,MIN_LOT_SF,MIN_LOT_CAT",
            max_allowable_offset=5,
            refresh=refresh,
        ),
        "sewer": arcgis.query_all(
            "rigis_sewered", out_fields="WWTF", max_allowable_offset=5, refresh=refresh
        ),
        "points": arcgis.query_all(
            "rigis_e911_points",
            where="pointtype IN ('R1','R2','R3','R4','R5','R6','A1','DV')",
            out_fields="pointtype,municipality,status,unittype",
            refresh=refresh,
        ),
    }
    bps_rows = bps.fetch_years(BASELINE_YEARS, refresh=refresh)
    report = None
    eoh_error = ""
    try:
        report = eoh.read_report(eoh.get_pdf(refresh=refresh))
    except Exception as e:  # the host refuses some clients; the build says so
        eoh_error = f"{type(e).__name__}: {e}"
    acs_rows = acs.fetch_acs(refresh=refresh)
    acs_sf = None
    acs_sf_error = ""
    try:
        acs_sf = acs.fetch_summary_stock("44", refresh=refresh)
    except Exception as e:  # the summary files are large; a failure is reported, not fatal
        acs_sf_error = f"{type(e).__name__}: {e}"
    freq = gtfs.stop_frequencies(refresh=refresh) if with_transit else None
    hubs = transit.load_named_hubs(DATA_DIR / "ri_mobility_hubs.csv")
    return {
        "paths": paths,
        "bps": bps_rows,
        "eoh": report,
        "eoh_error": eoh_error,
        "acs": acs_rows,
        "acs_sf": acs_sf,
        "acs_sf_error": acs_sf_error,
        "gtfs": freq,
        "hubs": hubs,
    }


def _series(bps_rows: list[dict]) -> dict[str, dict[int, dict]]:
    out: dict[str, dict[int, dict]] = {m: {} for m in RI_MUNICIPALITIES}
    for r in bps_rows:
        out[r["municipality"]][r["year"]] = r
    return out


_STOCK_FIELDS = ("units_total", "units_1", "units_2", "units_3_4", "units_5plus", "units_mobile", "occupied", "vacant")


def _acs_stock(inputs: dict) -> tuple[dict[str, dict], str]:
    """Units by structure type per town.

    Preference: Census API (keyed) → Census summary files (no key) → the
    State report's transcription of the same ACS tables. All three carry the
    same estimates; the order is about replicability, not accuracy.
    """
    if inputs.get("acs"):
        rows = {r["municipality"]: r for r in inputs["acs"]}
        return {m: {k: rows[m].get(k) for k in _STOCK_FIELDS} for m in RI_MUNICIPALITIES if m in rows}, "census_acs"
    if inputs.get("acs_sf"):
        by_geo = inputs["acs_sf"]
        out = {}
        for m, (county, mcd) in COUNTY_MCD_FIPS.items():
            rec = by_geo.get(f"0600000US44{county}{mcd}")
            if rec:
                out[m] = {k: rec.get(k) for k in _STOCK_FIELDS}
        if len(out) == len(RI_MUNICIPALITIES):
            return out, "census_acs_sf (ACS 2024 5-yr B25024/B25002, summary files)"
    rep = inputs.get("eoh")
    if rep:
        bt, st = rep["units_by_type_acs2024"], rep["stock_acs2024"]
        return {
            m: {
                "units_total": bt[m]["units_total"],
                "units_1": bt[m]["units_1"],
                "units_2": bt[m]["units_2"],
                "units_3_4": bt[m]["units_3_4"],
                "units_5plus": bt[m]["units_5plus"],
                "units_mobile": bt[m]["units_mobile"],
                "occupied": st[m]["occupied"],
                "vacant": st[m]["vacant"],
            }
            for m in RI_MUNICIPALITIES
        }, "eoh_integrated_2025 (ACS 2024 5-yr tables B25024/B25002)"
    return {}, "none"


def build_towns(
    inputs: dict,
    *,
    tier: str = "B",
    params_path: Path | None = None,
    frequent_per_hour: float | None = None,
    hub_min_routes: int | None = None,
    out_path: Path | None = None,
) -> dict:
    tier = tier.upper()
    assert tier in ("A", "B", "C")
    series = _series(inputs["bps"])
    stock, stock_source = _acs_stock(inputs)
    towns: dict[str, dict] = {}

    districts_out = None
    tod = None
    if tier in ("A", "B"):
        buffers = None
        if inputs.get("gtfs") and frequent_per_hour is not None and hub_min_routes is not None:
            tod = transit.buffers(
                inputs["gtfs"],
                frequent_peak_departures_per_hour=frequent_per_hour,
                hub_min_routes=hub_min_routes,
                named_hubs=inputs.get("hubs"),
            )
            buffers = {"tod_any": tod["geoms"]["tod_any"]}
        pp = params_path if tier == "A" else Path(os.devnull)
        districts_out = capacity.build_districts(
            zoning_path=inputs["paths"]["zoning"],
            points_path=inputs["paths"]["points"],
            sewer_path=inputs["paths"]["sewer"],
            params_path=pp,
            transit_buffers=buffers,
        )
        totals = capacity.town_totals(districts_out["districts"])
        # Per-district TOD inputs the density parameter is applied to at run time.
        tod_rows: dict[str, list] = {m: [] for m in RI_MUNICIPALITIES}
        if buffers is not None:
            for d in districts_out["districts"]:
                a = d.get("area_acres_tod_any", 0.0)
                if d["czone"] in capacity.RES_CLASSES and a > 0 and d.get("min_lot_sf"):
                    tod_rows[d["municipality"]].append(
                        [round(a, 3), round(capacity.SQFT_PER_ACRE / float(d["min_lot_sf"]), 3)]
                    )
    else:
        totals = {}
        tod_rows = {m: [] for m in RI_MUNICIPALITIES}

    for m in RI_MUNICIPALITIES:
        t = totals.get(m)
        if t is not None:
            # A town with districts but no row of a given kind has zero of it,
            # not "unknown"; only tier C leaves Stage 1 fields as None.
            t = {k: t.get(k, 0.0) for k in (
                "n_R1", "n_R1_sewered", "n_R1_lot20k_plus", "n_R1_lot20k_plus_sewered",
                "n_R1_sf_only", "n_R1_sf_only_sewered", "n_R1_unknown", "n_R1_unknown_sewered",
                "n_R2", "n_A1", "n_DV", "res_area_acres", "n_R1_tod_any", "n_R2_tod_any",
                "tier_A_rows", "rows",
            )} | {k: t.get(k) for k in ("mean_min_lot_sf",)}
        else:
            t = {}
        s = series[m]
        yrs = [y for y in BASELINE_YEARS if y in s]
        permits = {y: s[y]["units_total"] for y in yrs}
        mf = {y: s[y]["units_2"] + s[y]["units_3_4"] + s[y]["units_5plus"] for y in yrs}
        hist_total = sum(permits.values())
        mf_share = (sum(mf.values()) / hist_total) if hist_total else 0.0
        eoh25 = inputs["eoh"]["permits_2025"][m]["units_total"] if inputs.get("eoh") else None
        co25 = inputs["eoh"]["co_2025"][m]["units_total"] if inputs.get("eoh") else None
        lmih = inputs["eoh"]["lmih_2024"][m] if inputs.get("eoh") else None
        row = {
            "municipality": m,
            "tier": tier if tier != "A" else ("A" if t.get("tier_A_rows", 0) else "B"),
            "permits_bps": permits,
            "months_reported": {y: s[y]["months_reported"] for y in yrs},
            "permits_eoh_2025": eoh25,
            "co_eoh_2025": co25,
            "mf_share_2018_2025": round(mf_share, 4),
            "stock": stock.get(m, {}),
            "lmih_2024": lmih,
            # Stage 1 capacity (None at tier C → model uses ledger shares + ACS)
            "n_R1": t.get("n_R1"),
            "n_R1_sewered": t.get("n_R1_sewered"),
            "n_R1_lot20k_plus": t.get("n_R1_lot20k_plus"),
            "n_R1_lot20k_plus_sewered": t.get("n_R1_lot20k_plus_sewered"),
            "n_R1_sf_only": t.get("n_R1_sf_only"),
            "n_R1_sf_only_sewered": t.get("n_R1_sf_only_sewered"),
            "n_R1_unknown": t.get("n_R1_unknown"),
            "n_R1_unknown_sewered": t.get("n_R1_unknown_sewered"),
            "n_R2": t.get("n_R2"),
            "n_A1": t.get("n_A1"),
            "n_DV": t.get("n_DV"),
            "res_area_acres": t.get("res_area_acres"),
            "mean_min_lot_sf": t.get("mean_min_lot_sf"),
            "tod_districts": tod_rows.get(m, []),
            "n_R1_tod_any": t.get("n_R1_tod_any"),
            "n_R2_tod_any": t.get("n_R2_tod_any"),
            "tier_A_rows": t.get("tier_A_rows", 0),
            "district_rows": t.get("rows", 0),
        }
        towns[m] = row

    # The Census survey undercounts Rhode Island permits: the State's own 2025
    # municipal survey found 3,778 units where the BPS file carries about half.
    # The ratio is data; its uncertainty is a ledger parameter.
    bps_2025 = sum(towns[m]["permits_bps"].get(2025, 0) for m in RI_MUNICIPALITIES)
    eoh_2025 = sum((towns[m]["permits_eoh_2025"] or 0) for m in RI_MUNICIPALITIES)
    undercount = {
        "bps_2025_statewide": bps_2025,
        "eoh_2025_statewide": eoh_2025 or None,
        "eoh_to_bps_ratio_2025": round(eoh_2025 / bps_2025, 4) if (eoh_2025 and bps_2025) else 1.0,
        "note": (
            "Baseline permit levels are the BPS series scaled by this ratio. The State's report "
            "says its survey 'is more accurate than the Census survey'; the ratio is 1.0 when the "
            "State report is unavailable, and the overview says so."
        ),
    }

    # Statewide shares the ledger's tier-C parameters default to.
    derived = {}
    if totals:
        r1 = max(1, sum(v.get("n_R1", 0) for v in totals.values()))
        r1_res = sum(v.get("n_R1_res", 0) for v in totals.values())
        r1_unknown = sum(v.get("n_R1_unknown", 0) for v in totals.values())
        r1_sf_only = sum(v.get("n_R1_sf_only", 0) for v in totals.values())
        derived = {
            "n_R1_total": r1,
            "n_R1_in_residential_districts": r1_res,
            "share_R1_lot20k_plus": round(
                sum(v.get("n_R1_lot20k_plus", 0) for v in totals.values()) / r1, 4
            ),
            "share_R1_sewered": round(sum(v.get("n_R1_sewered", 0) for v in totals.values()) / r1, 4),
            # Among residential-district structures whose district text could be
            # read, the share in single-family-only districts.
            "share_R1_sf_only_of_read": round(r1_sf_only / max(1, r1_res - r1_unknown), 4),
            "share_R1_unread": round(r1_unknown / max(1, r1_res), 4),
        }
    out = {
        "tier": tier,
        "baseline_years": BASELINE_YEARS,
        "stock_source": stock_source,
        "eoh_available": bool(inputs.get("eoh")),
        "eoh_error": inputs.get("eoh_error", ""),
        "eoh_checks": inputs["eoh"]["checks"] if inputs.get("eoh") else None,
        "districts_summary": districts_out["summary"] if districts_out else None,
        "transit": (
            {
                "service_day": tod["service_day"],
                "n_frequent_stops": len(tod["frequent_stops"]),
                "n_hub_stops": len(tod["hub_stops"]),
                "hub_definition": tod["hub_definition"],
                "hub_stops": [s["stop_name"] for s in tod["hub_stops"]][:40],
            }
            if tod
            else None
        ),
        "stock_cross_check": _stock_cross_check(inputs),
        "derived_shares": derived,
        "permit_undercount": undercount,
        "towns": towns,
    }
    out_path = out_path or (OUT_DIR / "build" / f"towns_tier{tier}.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=1))
    return out


def _stock_cross_check(inputs: dict) -> dict | None:
    """The State report's ACS tables against the Census summary file, town by town."""
    rep, sf = inputs.get("eoh"), inputs.get("acs_sf")
    if not (rep and sf):
        return None
    mismatches = []
    for m, (county, mcd) in COUNTY_MCD_FIPS.items():
        rec = sf.get(f"0600000US44{county}{mcd}")
        a = rep["units_by_type_acs2024"][m]["units_total"]
        b = rec.get("units_total") if rec else None
        if b is None or a != b:
            mismatches.append({"municipality": m, "state_report": a, "census_summary_file": b})
    return {"towns_compared": len(COUNTY_MCD_FIPS), "mismatches": mismatches, "agree": not mismatches}


def build_state_tier_c(
    state_fips: str,
    state_abbr: str,
    *,
    acs_year: int = 2024,
    refresh: bool = False,
    out_path: Path | None = None,
) -> dict:
    """Tier C for any state from federal data alone: Census geography index,
    Building Permits Survey by place, ACS summary-file structure counts.

    No zoning layer, no State survey: the permit level is the Census series as
    published (undercount ratio 1.0, which the overview flags), and Stage 1
    eligibility comes from ACS single-family counts times the ledger's shares.
    """
    state_fips = str(state_fips).zfill(2)
    subs = geos.county_subdivisions(state_fips, year=acs_year, refresh=refresh)
    mcd_to_name = {v["mcd"]: v["name"] for v in subs.values()}
    # Disambiguate towns that share a name across counties (e.g. two "Lincoln"s).
    seen: dict[str, int] = {}
    for v in subs.values():
        seen[v["name"]] = seen.get(v["name"], 0) + 1
    for v in subs.values():
        if seen[v["name"]] > 1:
            mcd_to_name[v["mcd"]] = f"{v['name']} ({v['county']})"
            v["name"] = mcd_to_name[v["mcd"]]
    bps_rows = bps.fetch_years(BASELINE_YEARS, refresh=refresh, state_fips=state_fips, mcd_to_name=mcd_to_name)
    stock = acs.fetch_summary_stock(state_fips, year=acs_year, refresh=refresh)
    series: dict[str, dict[int, dict]] = {}
    for r in bps_rows:
        series.setdefault(r["municipality"], {})[r["year"]] = r
    towns: dict[str, dict] = {}
    for geo, v in subs.items():
        name = v["name"]
        s = series.get(name, {})
        yrs = [y for y in BASELINE_YEARS if y in s]
        permits = {y: s[y]["units_total"] for y in yrs}
        mf = {y: s[y]["units_2"] + s[y]["units_3_4"] + s[y]["units_5plus"] for y in yrs}
        hist_total = sum(permits.values())
        rec = stock.get(geo, {})
        towns[name] = {
            "municipality": name,
            "geo_id": geo,
            "tier": "C",
            "permits_bps": permits,
            "months_reported": {y: s[y]["months_reported"] for y in yrs},
            "permits_eoh_2025": None,
            "co_eoh_2025": None,
            "mf_share_2018_2025": round(sum(mf.values()) / hist_total, 4) if hist_total else 0.0,
            "stock": {k: rec.get(k) for k in _STOCK_FIELDS},
            "lmih_2024": None,
            "n_R1": None,
            "tod_districts": [],
            "tier_A_rows": 0,
            "district_rows": 0,
        }
    out = {
        "tier": "C",
        "state": state_abbr,
        "state_fips": state_fips,
        "baseline_years": BASELINE_YEARS,
        "stock_source": f"census_acs_sf (ACS {acs_year} 5-yr, summary files)",
        "eoh_available": False,
        "eoh_error": "not applicable outside Rhode Island",
        "n_county_subdivisions": len(subs),
        "n_with_permit_series": sum(1 for t in towns.values() if t["permits_bps"]),
        "permit_undercount": {
            "eoh_to_bps_ratio_2025": 1.0,
            "note": "No state survey to scale to; the Census series is used as published. "
            "Rhode Island's series undercounts by about half, and this state's may too.",
        },
        "towns": towns,
    }
    out_path = out_path or (OUT_DIR / "build" / f"towns_tierC_{state_abbr}.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=1))
    return out


def noise_cv_from_history(towns: dict) -> float:
    """Observed coefficient of variation of residuals around each town's trend."""
    cvs = []
    for t in towns.values():
        ys = [t["permits_bps"][y] for y in sorted(t["permits_bps"])]
        if len(ys) < 4 or sum(ys) == 0:
            continue
        n = len(ys)
        xs = list(range(n))
        xbar, ybar = statistics.mean(xs), statistics.mean(ys)
        sxx = sum((x - xbar) ** 2 for x in xs)
        b = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys, strict=True)) / sxx
        a = ybar - b * xbar
        resid = [y - (a + b * x) for x, y in zip(xs, ys, strict=True)]
        if ybar > 0:
            cvs.append(statistics.pstdev(resid) / ybar)
    return round(statistics.median(cvs), 3) if cvs else 0.25
