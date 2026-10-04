"""Headroom: how much housing a state-level reform makes room for.

A two-stage model. Stage 1 computes *regulatory capacity* deterministically
from public zoning and structure data. Stage 2 applies *uptake* and
*feasibility* parameters, every one of which is a named entry in
``assumptions.yaml`` with a default, a range and a source. Results are
distributions (P10 / P50 / P90), never points.

See README.md for the design and docs/ for the model and assumptions
overview generated from the ledger.
"""

from pathlib import Path

__version__ = "0.1.0"

# The subproject root (the directory holding assumptions.yaml), resolved from
# the installed package so the CLI works from any working directory.
ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = ROOT / "assumptions.yaml"
DATA_DIR = ROOT / "data"
CACHE_DIR = ROOT / "cache"
OUT_DIR = ROOT / "out"
