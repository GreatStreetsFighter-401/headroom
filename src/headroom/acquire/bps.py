"""Census Building Permits Survey, annual, by permit-issuing place.

Files: ``https://www2.census.gov/econ/bps/Place/Northeast%20Region/ne{YYYY}a.txt``
— one row per permit-issuing place with buildings, units and valuation by
size class (1, 2, 3–4, 5+ units), plus a "months reported" column; the
Census imputes non-reporting months, and a second block of columns carries
reported-months-only values. We keep the published (imputed) totals and
carry ``months_reported`` so a reader can discount a town that reported
three months of twelve.

Rhode Island's 39 municipalities are all permit-issuing places, keyed by
FIPS MCD code, which is how the join avoids the ``Barrington town`` vs
``Barrington`` spelling problem.
"""

from __future__ import annotations

import csv
import io

from headroom.acquire.base import fetch
from headroom.municipalities import MCD_TO_MUNICIPALITY

BASE = "https://www2.census.gov/econ/bps/Place/Northeast%20Region/ne{year}a.txt"
STATE_FIPS_RI = "44"

# Column positions in the place file (two header rows, then data). Verified
# against ne2024a.txt on 2026-10-04.
COLS = {
    "year": 0,
    "state": 1,
    "county": 3,
    "mcd": 6,
    "months_reported": 15,
    "name": 16,
    "u1_bldgs": 17,
    "u1_units": 18,
    "u2_bldgs": 20,
    "u2_units": 21,
    "u34_bldgs": 23,
    "u34_units": 24,
    "u5_bldgs": 26,
    "u5_units": 27,
}


def _int(s: str) -> int:
    s = s.strip()
    return int(s) if s else 0


def fetch_year(
    year: int,
    *,
    refresh: bool = False,
    state_fips: str = STATE_FIPS_RI,
    mcd_to_name: dict[str, str] | None = None,
) -> list[dict]:
    """One state's rows for one year, keyed to municipality names by MCD code.

    Rhode Island's 39 towns are the default mapping; another state passes the
    MCD → name mapping read from the Census geography index (``acquire.geos``).
    """
    path = fetch(
        BASE.format(year=year),
        name=f"bps_place_ne_{year}a.txt",
        source_id="census_bps",
        refresh=refresh,
    )
    mapping = mcd_to_name if mcd_to_name is not None else MCD_TO_MUNICIPALITY
    text = path.read_text(encoding="latin-1")
    rows: list[dict] = []
    reader = csv.reader(io.StringIO(text))
    for i, rec in enumerate(reader):
        if i < 2 or len(rec) < 28:
            continue
        if rec[COLS["state"]].strip() != str(state_fips).zfill(2):
            continue
        mcd = rec[COLS["mcd"]].strip()
        muni = mapping.get(mcd)
        if muni is None:
            # A permit-issuing place that is not a county subdivision we track.
            continue
        u1, u2, u34, u5 = (
            _int(rec[COLS["u1_units"]]),
            _int(rec[COLS["u2_units"]]),
            _int(rec[COLS["u34_units"]]),
            _int(rec[COLS["u5_units"]]),
        )
        rows.append(
            {
                "year": int(rec[COLS["year"]]),
                "municipality": muni,
                "months_reported": _int(rec[COLS["months_reported"]]),
                "units_1": u1,
                "units_2": u2,
                "units_3_4": u34,
                "units_5plus": u5,
                "units_total": u1 + u2 + u34 + u5,
                "bldgs_1": _int(rec[COLS["u1_bldgs"]]),
                "bldgs_2": _int(rec[COLS["u2_bldgs"]]),
                "bldgs_3_4": _int(rec[COLS["u34_bldgs"]]),
                "bldgs_5plus": _int(rec[COLS["u5_bldgs"]]),
                "source": "census_bps",
            }
        )
    return rows


def fetch_years(
    years: range | list[int],
    *,
    refresh: bool = False,
    state_fips: str = STATE_FIPS_RI,
    mcd_to_name: dict[str, str] | None = None,
) -> list[dict]:
    out: list[dict] = []
    for y in years:
        out.extend(fetch_year(int(y), refresh=refresh, state_fips=state_fips, mcd_to_name=mcd_to_name))
    return out
