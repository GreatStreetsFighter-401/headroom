"""The model as the page runs it — in the browser, through Pyodide.

``site/worker.js`` loads this package into a Python interpreter compiled to
WebAssembly and calls :func:`run`. Nothing is re-implemented in JavaScript:
the page runs ``Model.run`` on the same ledger and the same town table the
CLI uses, so a number on screen after a slider moves was produced by the
same arithmetic as the number in the committed results. The only difference
is the *overrides* — a reader may pin any sampled parameter at a chosen
value, which replaces its distribution with a fixed one for that run; every
other parameter keeps its range, so the band shown is the remaining
uncertainty given that choice.

The functions here are plain Python and are unit-tested natively; the
worker is a thin transport around them.
"""

from __future__ import annotations

import copy
import json

from headroom import ledger as ledger_mod
from headroom.model.core import Model

# What the page needs from a run; ``samples`` is left out, it is large and
# the page never shows it.
_KEEP = ("meta", "statewide", "towns", "sensitivity")


def apply_overrides(ledger: ledger_mod.Ledger, overrides: dict[str, float]) -> tuple[ledger_mod.Ledger, dict]:
    """A copy of the ledger with each overridden parameter pinned.

    Returns the copy and a record of what was pinned, in the ledger's own
    terms, so the page can say exactly what differs from the committed run.
    An unknown parameter id, or a fixed (statutory) one, is refused: the
    page may not change the law or the handbook's benchmark.
    """
    led = copy.deepcopy(ledger)
    pinned: dict[str, dict] = {}
    for pid, value in (overrides or {}).items():
        if pid not in led.parameters:
            raise KeyError(f"unknown parameter {pid!r}")
        par = led.parameters[pid]
        if par.distribution == "fixed":
            raise ValueError(f"{pid} is fixed by statute or the handbook and cannot be overridden")
        v = float(value)
        lo, hi = float(par.low), float(par.high)
        v = min(max(v, lo), hi)
        pinned[pid] = {"was_default": par.default, "range": [lo, hi], "pinned_at": v}
        par.default = v
        par.distribution = "fixed"
        par.sensitivity = False  # a pinned value has no rank correlation to report
    return led, pinned


def run(
    towns: dict,
    overrides: dict[str, float] | None = None,
    *,
    draws: int | None = None,
    seed: int | None = None,
) -> dict:
    """Run the model on ``towns`` with ``overrides`` pinned; the page's entry point."""
    base = ledger_mod.load()
    led, pinned = apply_overrides(base, overrides or {})
    res = Model(led, towns, draws=draws, seed=seed).run()
    out = {k: res[k] for k in _KEEP}
    out["meta"]["pinned"] = pinned
    out["meta"]["engine"] = "pyodide" if _in_pyodide() else "cpython"
    return out


def run_json(towns_json: str, overrides_json: str, draws: int | None = None, seed: int | None = None) -> str:
    """String-in, string-out wrapper for the worker (no proxy objects cross the boundary)."""
    towns = json.loads(towns_json)
    overrides = json.loads(overrides_json or "{}")
    return json.dumps(run(towns, overrides, draws=draws, seed=seed))


def _in_pyodide() -> bool:
    try:
        import sys

        return sys.platform == "emscripten"
    except Exception:  # pragma: no cover
        return False
