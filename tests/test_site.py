"""The static page's copy of the model is the model.

`headroom site` publishes the ledger and the model's source files into
site/model/ for the in-browser engine. These tests fail if those copies drift
from src/, or if the worker and the publisher disagree about which files the
engine needs — a page that runs a stale model would be worse than a page that
runs none.
"""

import json
import re

from headroom import ROOT
from headroom.cli import SITE_MODEL_FILES


def test_every_published_model_file_is_identical_to_its_source():
    published = json.loads((ROOT / "site" / "model" / "files.json").read_text())
    assert published == list(SITE_MODEL_FILES)
    for rel in SITE_MODEL_FILES:
        assert (ROOT / "site" / "model" / rel).read_text() == (ROOT / rel).read_text(), rel


def test_the_engine_needs_only_what_is_published():
    """Every headroom module the browser entry point imports must be in the published set."""
    web = (ROOT / "src" / "headroom" / "model" / "web.py").read_text()
    core = (ROOT / "src" / "headroom" / "model" / "core.py").read_text()
    ledger = (ROOT / "src" / "headroom" / "ledger.py").read_text()
    imported = set(re.findall(r"from headroom(?:\.[\w.]+)? import|import headroom[\w.]*", web + core + ledger))
    # Only the ledger, the model and the package root are imported; acquire/ and build/ never are.
    for module in ("headroom.acquire", "headroom.build", "headroom.report", "headroom.cli"):
        assert module not in web + core + ledger
    assert imported


def test_the_worker_installs_from_the_published_manifest():
    worker = (ROOT / "site" / "worker.js").read_text()
    assert 'fetch("model/files.json")' in worker
    assert (
        "/model/src" in worker
    )  # sys.path entry that makes `from headroom import LEDGER_PATH` resolve /model/assumptions.yaml
    assert "web.run_json" in worker or "run_json" in worker
    # The page must not load any script from a third party itself; only the worker fetches Pyodide.
    index = (ROOT / "site" / "index.html").read_text()
    assert "cdn." not in index and 'src="app.js"' in index
