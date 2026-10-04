"""Census geography: the county subdivisions (towns) of a state.

New England's municipalities are Census *county subdivisions* (summary
level 060). The ACS summary-file geography index lists every one with its
GEO_ID, which is the join key for both the ACS summary tables and — through
the 5-digit MCD code it ends in — the Building Permits Survey place file.
Reading the list from the Census means another state needs no hand-typed
town table to run tier C.
"""

from __future__ import annotations

from headroom.acquire.base import fetch_filtered

GEOS_URL = (
    "https://www2.census.gov/programs-surveys/acs/summary_file/{year}/table-based-SF/documentation/Geos{year}5YR.txt"
)
COUSUB_SUMLEVEL = "060"


def _clean_name(name: str) -> str:
    """'Barrington town, Bristol County, Rhode Island' → 'Barrington'."""
    first = name.split(",")[0].strip()
    for suffix in (" town", " city", " Town", " City", " plantation", " borough"):
        if first.endswith(suffix):
            first = first[: -len(suffix)]
    return first


def county_subdivisions(state_fips: str, *, year: int = 2024, refresh: bool = False) -> dict[str, dict]:
    """GEO_ID → {name, county, mcd, full_name} for one state's county subdivisions."""
    state_fips = str(state_fips).zfill(2)
    path = fetch_filtered(
        GEOS_URL.format(year=year),
        name=f"acs_geos_{year}_cousub_{state_fips}.txt",
        source_id="census_acs_sf",
        keep=lambda line: f"|{COUSUB_SUMLEVEL}|" in line and f"|{state_fips}|" in line,
        refresh=refresh,
    )
    out: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        parts = line.split("|")
        if len(parts) < 42 or parts[2] != COUSUB_SUMLEVEL or parts[7] != state_fips:
            continue
        geo_id, full = parts[40], parts[41]
        # "County subdivisions not defined" are water; skip them.
        if "not defined" in full:
            continue
        out[geo_id] = {
            "geo_id": geo_id,
            "name": _clean_name(full),
            "full_name": full,
            "county": parts[8],
            "mcd": parts[9],
        }
    return out
