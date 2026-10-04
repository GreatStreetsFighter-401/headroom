"""Census geography index and summary-file parsing, on fixture lines."""

from headroom.acquire import acs, geos

GEOS_LINES = """﻿FILEID|STUSAB|SUMLEVEL|COMPONENT|US|REGION|DIVISION|STATE|COUNTY|COUSUB|PLACE|TRACT|BLKGRP|CONCIT|AIANHH|AIANHHFP|AIHHTLI|AITS|AITSFP|ANRC|CBSA|CSA|METDIV|MACC|MEMI|NECTA|CNECTA|NECTADIV|UA|CDCURR|SLDU|SLDL|ZCTA5|SUBMCD|SDELM|SDSEC|SDUNI|UR|PCI|PUMA5|GEO_ID|NAME|BTTR|BTBG|TL_GEO_ID
ACSSF|RI|060|00||||44|001|05140|||||||||||||||||.|.|||||||||||||0600000US4400105140|Barrington town, Bristol County, Rhode Island|||4400105140
ACSSF|RI|060|00||||44|007|14140|||||||||||||||||.|.|||||||||||||0600000US4400714140|Central Falls city, Providence County, Rhode Island|||4400714140
ACSSF|RI|060|00||||44|009|00000|||||||||||||||||.|.|||||||||||||0600000US4400900000|County subdivisions not defined, Washington County, Rhode Island|||4400900000
ACSSF|MA|060|00||||25|017|41690|||||||||||||||||.|.|||||||||||||0600000US2501741690|Melrose city, Middlesex County, Massachusetts|||2501741690
"""

SF_LINES = """GEO_ID|B25024_E001|B25024_M001|B25024_E002|B25024_M002|B25024_E003|B25024_M003|B25024_E004|B25024_M004|B25024_E005|B25024_M005|B25024_E006|B25024_M006|B25024_E007|B25024_M007|B25024_E008|B25024_M008|B25024_E009|B25024_M009|B25024_E010|B25024_M010|B25024_E011|B25024_M011
0600000US4400105140|6341|278|5906|261|36|30|194|79|16|20|11|18|0|23|0|23|178|80|0|23|0|23
0600000US2501741690|12000|300|6000|200|500|50|2000|100|1500|90|1000|80|500|40|300|30|200|20|0|10|0|10
"""


def test_county_subdivisions_reads_names_and_skips_undefined(tmp_path, monkeypatch):
    f = tmp_path / "geos.txt"
    f.write_text(GEOS_LINES, encoding="utf-8")
    monkeypatch.setattr(geos, "fetch_filtered", lambda *a, **k: f)
    ri = geos.county_subdivisions("44")
    assert set(ri) == {"0600000US4400105140", "0600000US4400714140"}
    assert ri["0600000US4400105140"]["name"] == "Barrington"
    assert ri["0600000US4400714140"]["name"] == "Central Falls"
    assert ri["0600000US4400714140"]["mcd"] == "14140"


def test_summary_file_rows_parse_estimates_only(tmp_path):
    f = tmp_path / "b25024.dat"
    f.write_text(SF_LINES, encoding="utf-8")
    rows = acs._sf_rows(f, "0600000US44")
    assert set(rows) == {"0600000US4400105140"}
    r = rows["0600000US4400105140"]
    assert r["units_total"] == 6341
    assert r["units_1_detached"] == 5906 and r["units_1_attached"] == 36
    assert r["units_2"] == 194 and r["units_3_4"] == 16
    assert "B25024_M001" not in r


def test_summary_stock_merges_tables_and_derives_totals(tmp_path, monkeypatch):
    f = tmp_path / "b25024.dat"
    f.write_text(SF_LINES, encoding="utf-8")
    g = tmp_path / "other.dat"
    g.write_text("GEO_ID|B25002_E001|B25002_E002|B25002_E003\n0600000US4400105140|6341|6100|241\n", encoding="utf-8")
    calls = iter([f, g, g])
    monkeypatch.setattr("headroom.acquire.base.fetch_filtered", lambda *a, **k: next(calls))
    stock = acs.fetch_summary_stock("44")
    rec = stock["0600000US4400105140"]
    assert rec["units_1"] == 5906 + 36
    assert rec["units_5plus"] == 11 + 0 + 0 + 178
    assert rec["occupied"] == 6100 and rec["vacant"] == 241
