"""American Community Survey 5-year estimates for the 39 county subdivisions.

The Census API requires a free key (``CENSUS_API_KEY``); without one the
request is redirected to a "Missing Key" page. When no key is set, the
build falls back to the same ACS tables as transcribed in the State's 2025
Integrated Housing Report (``acquire.eoh``), which cites the table ids it
reads (B25002, B25004, B25024, B25035). The two agree by construction; the
API path is kept so another state can run without a State report.

Tables:
  B25024  units in structure (001 total, 002 1-detached, 003 1-attached,
          004 2, 005 3-4, 006 5-9, 007 10-19, 008 20-49, 009 50+,
          010 mobile home, 011 boat/RV/van)
  B25002  occupancy (001 total, 002 occupied, 003 vacant)
  B25003  tenure (001 total, 002 owner, 003 renter)
"""

from __future__ import annotations

import csv
import json
import os

from headroom.acquire.base import fetch
from headroom.municipalities import COUNTY_MCD_FIPS

API = "https://api.census.gov/data/{year}/acs/acs5"

VARS = {
    "B25024_001E": "units_total",
    "B25024_002E": "units_1_detached",
    "B25024_003E": "units_1_attached",
    "B25024_004E": "units_2",
    "B25024_005E": "units_3_4",
    "B25024_006E": "units_5_9",
    "B25024_007E": "units_10_19",
    "B25024_008E": "units_20_49",
    "B25024_009E": "units_50plus",
    "B25024_010E": "units_mobile",
    "B25002_002E": "occupied",
    "B25002_003E": "vacant",
    "B25003_002E": "owner_occupied",
    "B25003_003E": "renter_occupied",
}


def api_key() -> str | None:
    return os.environ.get("CENSUS_API_KEY") or None


def fetch_acs(year: int = 2023, *, refresh: bool = False) -> list[dict] | None:
    """Return one row per municipality, or ``None`` when no API key is set."""
    key = api_key()
    if not key:
        return None
    path = fetch(
        API.format(year=year),
        name=f"acs5_{year}_ri_cousub.json",
        source_id="census_acs",
        params={
            "get": "NAME," + ",".join(VARS),
            "for": "county subdivision:*",
            "in": "state:44",
            "key": key,
        },
        refresh=refresh,
    )
    data = json.loads(path.read_text())
    header, *rows = data
    idx = {h: i for i, h in enumerate(header)}
    by_mcd = {mcd: name for name, (_c, mcd) in COUNTY_MCD_FIPS.items()}
    out = []
    for r in rows:
        mcd = r[idx["county subdivision"]]
        muni = by_mcd.get(mcd)
        if muni is None:
            continue  # "County subdivisions not defined" water rows
        rec = {"municipality": muni, "acs_year": year, "source": "census_acs"}
        for var, name in VARS.items():
            v = r[idx[var]]
            rec[name] = int(v) if v not in (None, "", "-") else None
        rec["units_1"] = (rec["units_1_detached"] or 0) + (rec["units_1_attached"] or 0)
        rec["units_5plus"] = sum(rec[k] or 0 for k in ("units_5_9", "units_10_19", "units_20_49", "units_50plus"))
        out.append(rec)
    return out


def write_csv(rows: list[dict], path) -> None:
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
