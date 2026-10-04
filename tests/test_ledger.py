"""The ledger is the only place a behavioural number may live."""

import re
from pathlib import Path

import numpy as np
import pytest

from headroom import ROOT
from headroom.ledger import Parameter, load

MODEL_SRC = ROOT / "src" / "headroom" / "model" / "core.py"


def test_ledger_loads_and_validates():
    ledger = load()
    assert len(ledger.parameters) >= 25
    assert set(ledger.scenarios) >= {"baseline", "adu", "missing_middle", "parking", "fees", "tod"}
    for p in ledger.parameters.values():
        assert p.source.strip() and p.justification.strip()


def test_every_parameter_belongs_to_a_known_scenario():
    ledger = load()
    for p in ledger.parameters.values():
        for s in p.scenarios:
            assert s == "all" or s in ledger.scenarios, p.id


def test_sampling_respects_ranges_and_is_reproducible():
    ledger = load()
    a = ledger.sample(np.random.default_rng(1), 500)
    b = ledger.sample(np.random.default_rng(1), 500)
    for pid, p in ledger.parameters.items():
        x = a[pid]
        assert np.array_equal(x, b[pid]), pid
        if p.distribution == "fixed":
            assert np.all(x == p.default)
        else:
            assert x.min() >= p.low - 1e-9 and x.max() <= p.high + 1e-9, pid


def test_lognormal_median_is_default():
    p = Parameter("x", "x", ["adu"], 2, "", 0.001, 0.0002, 0.005, "lognormal", "prior", "s", "j")
    x = p.sample(np.random.default_rng(0), 20000)
    assert abs(np.median(x) / 0.001 - 1) < 0.05


def test_invalid_default_outside_range_is_rejected():
    p = Parameter("x", "x", ["adu"], 2, "", 9.0, 0.0, 1.0, "triangular", "prior", "s", "j")
    assert p.validate()


def test_model_core_carries_no_behavioural_literals():
    """Numeric literals in the model must be structural (0, 1, 2, percentiles),
    never a rate, a cost or a share. Anything else belongs in the ledger."""
    src = MODEL_SRC.read_text()
    # strip docstrings, string literals and comments: only code numbers count
    src = re.sub(r'"""[\s\S]*?"""', "", src)
    src = re.sub(r'"[^"\n]*"', '""', src)
    src = re.sub(r"'[^'\n]*'", "''", src)
    src = "\n".join(line.split("#")[0] for line in src.splitlines())
    # Structural constants: zero/one/two, rounding digits (3, 4), the percentile
    # grid, the ramp years in the calibration bracket, and the observed 2024
    # ADU count (a datum, cited in the calibration output).
    allowed = {
        "0",
        "1",
        "2",
        "3",
        "4",
        "0.0",
        "1.0",
        "2.0",
        "1e-9",
        "163",
        "163.0",
        "10",
        "50",
        "90",
        "5",
        "25",
        "75",
        "95",
        "20",
        "80",
    }
    found = set(re.findall(r"(?<![\w.])(\d+\.?\d*(?:e-?\d+)?)(?![\w.])", src))
    stray = sorted(found - allowed, key=lambda s: float(s))
    assert not stray, f"behavioural-looking literals in model/core.py: {stray}"


@pytest.mark.parametrize(
    "pid",
    [
        "adu_uptake_detached_annual",
        "mm_conversion_rate_annual",
        "supply_cost_elasticity",
        "tod_realization_rate_annual",
    ],
)
def test_key_parameters_have_calibration_or_source_text(pid):
    ledger = load()
    p = ledger.parameters[pid]
    assert len(p.source) > 40 and len(p.justification) > 40


def test_explain_prints_source_and_status():
    ledger = load()
    text = ledger.explain("adu_uptake_detached_annual")
    assert "Source." in text and "status: **prior**" in text


def test_ledger_file_is_tracked_next_to_package():
    assert Path(ROOT / "assumptions.yaml").exists()
