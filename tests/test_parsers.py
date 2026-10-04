"""Parsers for the two tabular sources, against a fixture and (when present) the real PDF."""

import os
from pathlib import Path

import pytest

from headroom.acquire import bps, eoh

BPS_SAMPLE = """Survey,State,6-Digit,County,Census Place,FIPS Place,FIPS MCD,Pop,CSA,CBSA,Footnote,Central,Zip,Region,Division,Number of,Place,,1-unit,,,2-units,,,3-4 units,,,5+ units,,,1-unit rep,,,2-units rep,,,3-4 units rep,,,5+ units rep
Date,Code,ID,Code,Code,Code,Code,  ,Code,Code,Code,City,Code,Code,Code,Months Rep,Name,Bldgs,Units,Value,Bldgs,Units,Value,Bldgs,Units,Value,Bldgs,Units,Value,Bldgs,Units,Value,Bldgs,Units,Value,Bldgs,Units,Value,Bldgs,Units,Value
2025,44,001000,001,    ,00000 ,05140 ,16015 ,148,39300, , ,02806      ,1,1,12,Barrington town,7,7,3334300,1,2,330000,0,0,0,0,0,0,7,7,3334300,1,2,330000,0,0,0,0,0,0
2025,44,013000,007,0150,14140 ,14140 ,19468 ,148,39300, , ,02863      ,1,1,12,Central Falls,2,2,120000,0,0,0,0,0,0,1,25,3900000,2,2,120000,0,0,0,0,0,0,1,25,3900000
2025,25,001000,001,    ,00000 ,00135 ,1,148,39300, , ,02000      ,1,1,12,Abington town,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0
"""


def test_bps_parser_keys_rows_by_mcd_and_sums_units(tmp_path, monkeypatch):
    f = tmp_path / "bps_place_ne_2025a.txt"
    f.write_text(BPS_SAMPLE, encoding="latin-1")
    monkeypatch.setattr(bps, "fetch", lambda *a, **k: f)
    rows = bps.fetch_year(2025)
    assert [r["municipality"] for r in rows] == ["Barrington", "Central Falls"]
    b = rows[0]
    assert (b["units_1"], b["units_2"], b["units_3_4"], b["units_5plus"], b["units_total"]) == (7, 2, 0, 0, 9)
    assert b["months_reported"] == 12
    cf = rows[1]
    assert cf["units_5plus"] == 25 and cf["bldgs_5plus"] == 1 and cf["units_total"] == 27


def test_repair_one_short_places_the_blank_where_arithmetic_says():
    names = [
        "bldgs_1",
        "units_1",
        "bldgs_2",
        "units_2",
        "bldgs_3_4",
        "units_3_4",
        "bldgs_5plus",
        "units_5plus",
        "units_total",
    ]
    # North Smithfield, 2025 certificates of occupancy: the 5+ buildings cell is blank.
    assert eoh._repair_one_short([5, 5, 0, 0, 0, 0, 3, 8], names) == [5, 5, 0, 0, 0, 0, None, 3, 8]
    # Ambiguous or inconsistent rows are refused, never guessed.
    assert eoh._repair_one_short([5, 5, 0, 0, 0, 0, 3, 9], names) is None


_PDF = os.environ.get("HEADROOM_EOH_PDF")


@pytest.mark.skipif(not (_PDF and Path(_PDF).exists()), reason="EOH PDF not available offline")
def test_eoh_report_tables_reconcile_to_printed_totals():
    r = eoh.read_report(Path(_PDF))
    for key in ("permits_2025", "co_2025", "stock", "by_type"):
        assert r["checks"][key]["agrees"], key
    assert r["statewide"]["permits_2025"]["units_total"] == 3778
    assert r["statewide"]["co_2025"]["units_total"] == 2162
    assert len(r["permits_2025"]) == 39
    assert r["permits_2025"]["Providence"]["units_total"] == 778
    assert r["co_2025"]["North Smithfield"]["units_5plus"] == 3
    assert r["lmih_2024"]["Barrington"]["lmih_share"] == pytest.approx(0.0372)
