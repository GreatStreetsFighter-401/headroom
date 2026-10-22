"""The browser entry point: overrides pin a parameter and the run stays the model's own."""

import json

import numpy as np
import pytest

from headroom import ledger as ledger_mod
from headroom.model import core, web


def _towns(n=3):
    towns = {}
    for i in range(n):
        name = f"Town {i}"
        towns[name] = {
            "municipality": name,
            "n_R1": 1000.0 * (i + 1),
            "n_R1_sewered": 600.0 * (i + 1),
            "n_R1_lot20k_plus": 400.0 * (i + 1),
            "n_R1_lot20k_plus_sewered": 200.0 * (i + 1),
            "n_R1_sf_only": 500.0 * (i + 1),
            "n_R1_sf_only_sewered": 300.0 * (i + 1),
            "n_R1_unknown": 100.0 * (i + 1),
            "n_R1_unknown_sewered": 50.0 * (i + 1),
            "permits_bps": {str(y): 20 + 2 * i + (y - 2018) for y in range(2018, 2026)},
            "mf_share_2018_2025": 0.3,
            "stock": {"units_1": 1000.0 * (i + 1)},
            "tod_districts": [[40.0, 4.0]] if i == 0 else [],
        }
    return {"tier": "B", "towns": towns, "permit_undercount": {"eoh_to_bps_ratio_2025": 1.0}}


def test_apply_overrides_pins_a_parameter_and_records_it():
    led, pinned = web.apply_overrides(ledger_mod.load(), {"adu_uptake_detached_annual": 0.004})
    p = led.parameters["adu_uptake_detached_annual"]
    assert p.distribution == "fixed" and p.default == 0.004 and p.sensitivity is False
    assert pinned["adu_uptake_detached_annual"]["pinned_at"] == 0.004
    assert pinned["adu_uptake_detached_annual"]["was_default"] == 0.002
    # The draw is now constant.
    assert np.ptp(p.sample(np.random.default_rng(1), 50)) == 0


def test_an_override_is_clamped_to_the_ledgers_range():
    led, pinned = web.apply_overrides(ledger_mod.load(), {"adu_ramp_years": 99})
    assert led.parameters["adu_ramp_years"].default == 5 and pinned["adu_ramp_years"]["pinned_at"] == 5


def test_the_law_and_the_handbook_cannot_be_overridden():
    with pytest.raises(ValueError):
        web.apply_overrides(ledger_mod.load(), {"fee_per_unit_handbook": 1})
    with pytest.raises(KeyError):
        web.apply_overrides(ledger_mod.load(), {"not_a_parameter": 1})


def test_the_original_ledger_is_untouched():
    base = ledger_mod.load()
    web.apply_overrides(base, {"adu_uptake_detached_annual": 0.006})
    assert base.parameters["adu_uptake_detached_annual"].distribution == "lognormal"


def test_run_without_overrides_matches_the_cli_model():
    towns = _towns()
    expected = core.Model(ledger_mod.load(), towns, draws=200, seed=7).run()
    got = web.run(towns, {}, draws=200, seed=7)
    assert got["statewide"]["adu"] == expected["statewide"]["adu"]
    assert got["towns"]["Town 1"]["baseline"] == expected["towns"]["Town 1"]["baseline"]
    assert got["meta"]["pinned"] == {} and got["meta"]["engine"] == "cpython"
    assert "samples" not in got


def test_a_higher_uptake_moves_the_adu_increment_up_and_only_that():
    towns = _towns()
    low = web.run(towns, {"adu_uptake_detached_annual": 0.0005}, draws=300, seed=3)
    high = web.run(towns, {"adu_uptake_detached_annual": 0.006}, draws=300, seed=3)
    assert high["statewide"]["adu"]["five_year"]["p50"] > low["statewide"]["adu"]["five_year"]["p50"]
    # The pinned parameter drops out of the sensitivity table; the band of the
    # other scenarios is unchanged because the draw stream is the same.
    assert all(r["parameter"] != "adu_uptake_detached_annual" for r in high["sensitivity"]["adu"])
    assert high["statewide"]["missing_middle"] == low["statewide"]["missing_middle"]


def test_run_json_round_trips_strings():
    out = json.loads(web.run_json(json.dumps(_towns()), json.dumps({"mm_ramp_years": 2}), draws=50, seed=1))
    assert out["meta"]["pinned"]["mm_ramp_years"]["pinned_at"] == 2
    assert set(out) == {"meta", "statewide", "towns", "sensitivity"}
