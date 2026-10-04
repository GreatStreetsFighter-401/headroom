"""The model's arithmetic on a small synthetic state."""

import numpy as np

from headroom.ledger import load
from headroom.model.core import Model, calibrate_adu


def _towns(tier="B"):
    def town(name, r1, lot20, sf_only, permits, mf_share, sew=0.5):
        return {
            "municipality": name,
            "tier": tier,
            "permits_bps": {str(y): v for y, v in zip(range(2018, 2026), permits, strict=True)},
            "permits_eoh_2025": None,
            "mf_share_2018_2025": mf_share,
            "stock": {"units_1": r1, "units_total": r1 * 2},
            "n_R1": r1,
            "n_R1_sewered": r1 * sew,
            "n_R1_lot20k_plus": lot20,
            "n_R1_lot20k_plus_sewered": lot20 * sew,
            "n_R1_sf_only": sf_only,
            "n_R1_sf_only_sewered": sf_only * sew,
            "n_R1_unknown": 0,
            "n_R1_unknown_sewered": 0,
            "tod_districts": [[100.0, 4.0]],  # 100 acres at 4 units/acre today
        }

    return {
        "tier": tier,
        "permit_undercount": {"eoh_to_bps_ratio_2025": 1.0},
        "towns": {
            "Alpha": town("Alpha", 10000, 4000, 6000, [100] * 8, 0.5),
            "Beta": town("Beta", 2000, 2000, 0, [10] * 8, 0.0),
        },
    }


def test_run_shapes_and_monotone_percentiles():
    ledger = load()
    res = Model(ledger, _towns(), draws=300, seed=1).run()
    sw = res["statewide"]
    assert sw["baseline"]["years"] == list(range(2027, 2032))
    for s in ("baseline", "adu", "missing_middle", "parking", "fees_handbook", "fees_ri", "tod"):
        f = sw[s]["five_year"]
        assert f["p10"] <= f["p50"] <= f["p90"], s
        assert all(a <= b for a, b in zip(sw[s]["p10"], sw[s]["p90"], strict=True))
    assert set(res["towns"]) == {"Alpha", "Beta"}


def test_adu_increment_is_zero_where_every_lot_is_already_eligible():
    ledger = load()
    res = Model(ledger, _towns(), draws=200, seed=2).run()
    assert res["towns"]["Beta"]["adu"]["five_year"]["p90"] == 0.0
    assert res["towns"]["Alpha"]["adu"]["five_year"]["p50"] > 0


def test_missing_middle_needs_single_family_only_lots():
    ledger = load()
    res = Model(ledger, _towns(), draws=200, seed=3).run()
    assert res["towns"]["Beta"]["missing_middle"]["five_year"]["p90"] == 0.0


def test_fee_scenario_scales_with_fee_level():
    ledger = load()
    res = Model(ledger, _towns(), draws=400, seed=4).run()
    hb = res["statewide"]["fees_handbook"]["five_year"]["p50"]
    ri = res["statewide"]["fees_ri"]["five_year"]["p50"]
    assert hb > ri > 0


def test_increments_are_linear_in_uptake_rate():
    """What the page's sliders rely on: doubling the rate doubles the median."""
    ledger = load()
    base = Model(ledger, _towns(), draws=200, seed=5).run()
    p = ledger.parameters["adu_uptake_detached_annual"]
    p.default, p.low, p.high = p.default * 2, p.low * 2, p.high * 2
    doubled = Model(ledger, _towns(), draws=200, seed=5).run()
    a = base["statewide"]["adu"]["five_year"]["p50"]
    b = doubled["statewide"]["adu"]["five_year"]["p50"]
    assert np.isclose(b, 2 * a, rtol=0.02)


def test_same_seed_same_answer():
    ledger = load()
    a = Model(ledger, _towns(), draws=100, seed=9).run()
    b = Model(ledger, _towns(), draws=100, seed=9).run()
    assert a["statewide"] == b["statewide"]


def test_calibration_reports_bracket():
    ledger = load()
    out = calibrate_adu(ledger, _towns())
    assert out["observed_2024_adu_permits"] == 163
    assert out["implied_2024_if_ramp_year_2"] >= out["implied_2024_if_ramp_year_1"] > 0


def test_tier_c_uses_stock_and_ledger_shares():
    ledger = load()
    res = Model(ledger, _towns(tier="C"), draws=100, seed=6).run()
    assert res["statewide"]["adu"]["five_year"]["p50"] > 0
    assert res["statewide"]["tod"]["five_year"]["p90"] > 0  # tod_districts given even at C here
