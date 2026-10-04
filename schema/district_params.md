# `district_params` — the tier-A input schema

One row per zoning district per municipality, read from the adopted zoning ordinance.
Rhode Island's rows are exported from MuniAnchor by `scripts/export_district_params.py`
(each row cites the ordinance section it was read from). Another state fills the same
columns from whatever it has; blank cells fall back to the tier-B reading.

File: `data/district_params_<state>.csv`, UTF-8, header row required.

| Column | Type | Meaning |
|---|---|---|
| `municipality` | text | Municipality name (any common spelling; canonicalised on load) |
| `zone_code` | text | District code exactly as the State zoning layer spells it (`ZONE_CODE`), e.g. `R-20`, `A-6` |
| `allowed_1f` | `by_right` / `special` / `no` / blank | One-family dwelling |
| `allowed_2f` | same | Two-family dwelling |
| `allowed_3f` | same | Three-or-more-family / multifamily dwelling |
| `min_lot_sf` | number | Minimum lot area, square feet (ordinance value; the State layer's is used if blank) |
| `max_height_ft` | number | Maximum building height, feet |
| `max_stories` | integer | Maximum stories |
| `max_lot_coverage` | 0–1 | Maximum lot coverage as a fraction |
| `max_far` | number | Maximum floor area ratio |
| `parking_per_unit_sf` | number | Required off-street spaces per single-family unit |
| `parking_per_unit_mf` | number | Required off-street spaces per multifamily unit |
| `source_section` | text | Ordinance section the row was read from (e.g. `§ 5.4 Table of Uses`) |
| `source_url` | URL | Where that section can be read (MuniAnchor public page or the municipality's code) |

Reading rules applied by `build/capacity.py`:

* A district is **single-family-only** when `allowed_2f` is `special` or `no` and
  `allowed_3f` is `special`, `no` or blank. A special-use permit is not by-right; the missing-
  middle scenario is about by-right rights.
* A district **allows more than one unit** when `allowed_2f` or `allowed_3f` is `by_right`.
* Any other combination leaves the tier-B reading in place and is reported as such.
