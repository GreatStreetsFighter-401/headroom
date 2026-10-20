# Data

Every dataset is retrieved by `headroom acquire` from the source below; the manifest records what was fetched, when, and its SHA-256.

| Source | Publisher | Licence | Notes |
|---|---|---|---|
| [Rhode Island Zoning and Overlay Zones — Municipal Zoning Classifications (layer 1)](https://www.rigis.org/maps/c8d4094c9141466eb6d3e9d82c349dd8) | Rhode Island Division of Statewide Planning (Land Use 2050 Data Services; HR&A Advisors + Go Consulting), distributed by RIGIS | RIGIS licence: provided as-is; acknowledge RIGIS and the primary producer in derived products. Statewide Planning: publicly supported research, may be reprinted or used with credit. | Zoning district polygons for all 39 municipalities compiled from municipal planning offices in 2025. Carries generalized class, a lot-size density class and MIN_LOT_SF; does NOT carry allowed unit types, height, parking or FAR. |
| [Rhode Island Zoning and Overlay Zones — Zoning Overlay Areas (layer 0)](https://www.rigis.org/maps/c8d4094c9141466eb6d3e9d82c349dd8) | Rhode Island Division of Statewide Planning, distributed by RIGIS | RIGIS licence (as above). | Overlay districts with SOURCE_ORD (ordinance URL) and SOURCE_DATE. |
| [E-911 Address Points (2026)](https://www.arcgis.com/home/item.html?id=26c8df834cbb4aa49ed571ad35c5647f) | Rhode Island E 9-1-1 Uniform Emergency Telephone System, distributed by RIGIS | RIGIS licence (as above). | One point per addressed structure, typed (R1 single-family, R2 multi-family, A1 accessory building, DV development site, ...). Used as the statewide count of existing single-family structures; it is not a parcel layer. |
| [Sewered Areas](https://www.arcgis.com/home/item.html?id=d1f22828f48946be88e8c30c422ec61b) | RIGIS | RIGIS licence (as above). | Service areas of wastewater treatment facilities; used to separate sewered from septic lots as a feasibility filter for a second unit. |
| [Building Permits Survey — annual permits by permit-issuing place](https://www2.census.gov/econ/bps/Place/Northeast%20Region/) | U.S. Census Bureau | Public domain (U.S. federal government work). | Units in new privately-owned residential buildings by size class. Months reported is carried; imputed values are used for non-reporting months as published. Rhode Island's Executive Office of Housing states its own municipal survey is more accurate for 2018 onward; both series are kept. |
| [American Community Survey 5-year estimates (county subdivisions)](https://api.census.gov/data/) | U.S. Census Bureau | Public domain (U.S. federal government work). An API key is free and required. | B25024 units in structure, B25002 occupancy, B25003 tenure. |
| [American Community Survey 5-year estimates — table-based summary files](https://www2.census.gov/programs-surveys/acs/summary_file/) | U.S. Census Bureau | Public domain (U.S. federal government work). No API key needed. | One pipe-delimited file per table for every geography in the country (≈48 MB each); the acquisition streams the file and keeps only the state's county subdivisions. Geography names and codes from the Geos{year}5YR.txt index. |
| [Transit Forward RI 2040 — regional mobility hubs](https://www.ripta.com/wp-content/uploads/2021/07/SPC-9-10-20.pdf) | Rhode Island Division of Statewide Planning / RIPTA (2020 Transit Master Plan) | State of Rhode Island public record. | The eight regional mobility hubs the plan names, encoded in data/ri_mobility_hubs.csv with coordinates taken from RIPTA's GTFS stops; the statute (§ 45-24-33(a)(28)) defers to this plan for the definition. |
| [2025 Integrated Housing Report](https://housing.ri.gov/sites/g/files/xkgbur401/files/2026-04/2025%20Integrated%20Housing%20Report.pdf) | Rhode Island Executive Office of Housing (published 2026-04-15; attested by the Office of Revenue Analysis) | State of Rhode Island public record. | Municipal 2025 permits and certificates of occupancy by building size (EOH municipal survey, Feb–Mar 2026); ACS-derived stock tables; 2024 LMIH chart; household projections 2025–2035. Some hosts refuse automated clients (HTTP 403); the parser also accepts a locally supplied copy. |
| [RIPTA GTFS schedule feed](https://ripta.com/RIPTA-GTFS.zip) | Rhode Island Public Transit Authority | Published for public developer use. | Stops, trips and stop_times used to identify frequent-transit stops for the transit-oriented scenario per R.I.G.L. § 45-24-33(a)(28). |
| [MuniAnchor ordinance-derived district parameters (allowed residential uses by district, dimensional envelopes), Rhode Island](https://munianchor.com/) | MuniAnchor (Gregory Guertin), derived from adopted municipal zoning ordinances | Apache-2.0 for this derived table; the underlying ordinances are public law. Each row cites the ordinance section it was read from. | Optional tier-A input. When the file is absent the model runs at tier B from the State layer alone, which is the data-sparse demonstration. |

## Files retrieved

| File | Source | Retrieved | Bytes | SHA-256 |
|---|---|---|---|---|
| `acs_geos_2024_cousub_09.txt` | census_acs_sf | 2026-10-04T20:36:51+00:00 | 27,979 | `6a90c636295b4986…` |
| `acs_geos_2024_cousub_25.txt` | census_acs_sf | 2026-10-04T20:36:39+00:00 | 50,889 | `6994f87a3b74c3ec…` |
| `acs_geos_2024_cousub_44.txt` | census_acs_sf | 2026-10-04T20:36:27+00:00 | 6,002 | `14cb0ad79730693f…` |
| `acs_sf_2024_b25002_cousub_09.dat` | census_acs_sf | 2026-10-04T20:36:55+00:00 | 8,029 | `09daef2788da7a1b…` |
| `acs_sf_2024_b25002_cousub_25.dat` | census_acs_sf | 2026-10-04T20:36:43+00:00 | 16,192 | `75f0e3fc5050261f…` |
| `acs_sf_2024_b25002_cousub_44.dat` | census_acs_sf | 2026-10-04T20:36:31+00:00 | 1,950 | `f71fffdde3a15ad7…` |
| `acs_sf_2024_b25003_cousub_09.dat` | census_acs_sf | 2026-10-04T20:36:57+00:00 | 8,087 | `ebc858991d8740e3…` |
| `acs_sf_2024_b25003_cousub_25.dat` | census_acs_sf | 2026-10-04T20:36:45+00:00 | 16,284 | `2e55f7944fc9ef1c…` |
| `acs_sf_2024_b25003_cousub_44.dat` | census_acs_sf | 2026-10-04T20:36:33+00:00 | 1,954 | `49bf20960372bffc…` |
| `acs_sf_2024_b25024_cousub_09.dat` | census_acs_sf | 2026-10-04T20:36:53+00:00 | 17,079 | `91034b491c0969d6…` |
| `acs_sf_2024_b25024_cousub_25.dat` | census_acs_sf | 2026-10-04T20:36:42+00:00 | 34,508 | `10bbdfe924a54c32…` |
| `acs_sf_2024_b25024_cousub_44.dat` | census_acs_sf | 2026-10-04T20:36:29+00:00 | 4,334 | `0e8f01004c8bf4c6…` |
| `bps_place_ne_2018a.txt` | census_bps | 2026-10-04T20:10:06+00:00 | 844,138 | `4a21d06fc13c6797…` |
| `bps_place_ne_2019a.txt` | census_bps | 2026-10-04T20:10:07+00:00 | 845,081 | `474392792fc9f1ac…` |
| `bps_place_ne_2020a.txt` | census_bps | 2026-10-04T20:10:08+00:00 | 844,772 | `4f53ac229eb89542…` |
| `bps_place_ne_2021a.txt` | census_bps | 2026-10-04T20:10:09+00:00 | 848,063 | `16d75cc7fc49b17a…` |
| `bps_place_ne_2022a.txt` | census_bps | 2026-10-04T20:10:10+00:00 | 850,359 | `fd363296c7b756e8…` |
| `bps_place_ne_2023a.txt` | census_bps | 2026-10-04T20:10:11+00:00 | 846,858 | `e5f34b2197ed420a…` |
| `bps_place_ne_2024a.txt` | census_bps | 2026-10-04T20:10:11+00:00 | 847,210 | `51d71f93324975bc…` |
| `bps_place_ne_2025a.txt` | census_bps | 2026-10-04T20:10:12+00:00 | 847,668 | `69d27190a5529423…` |
| `eoh_integrated_2025.pdf` | eoh_integrated_2025 | 2026-10-04T20:37:12+00:00 | 1,164,914 | `03d6335b60508f23…` |
| `rigis_e911_points__098ef28be1.geojson` | rigis_e911_points | 2026-10-04T20:03:07+00:00 | 81,174,752 | `5bab44d332ac2a77…` |
| `rigis_overlays__1ce94c5a79.geojson` | rigis_overlays | 2026-10-04T20:03:09+00:00 | 1,415,993 | `91428747a7e54d5b…` |
| `rigis_sewered__e61e577393.geojson` | rigis_sewered | 2026-10-04T19:59:50+00:00 | 517,684 | `091cfee2f9250322…` |
| `rigis_zoning__9469dc9203.geojson` | rigis_zoning | 2026-10-04T19:59:49+00:00 | 19,552,540 | `764fe4f7a8e82583…` |
| `ripta_gtfs.zip` | ripta_gtfs | 2026-10-04T20:10:15+00:00 | 2,233,393 | `f7be22f92caf332a…` |

## Stage 1 join (this build)

- Zoning polygons: 15,733; structure points loaded: 388,830; unmatched points: 3,046.
- Allowed-use reading of residential districts from the State layer's text: {'single_family_only': 2675, 'allows_2plus': 1535, 'unknown': 11163}.
- Rows carrying an ordinance reading (tier A): 0.

## Derived statewide shares

- `n_R1_total`: 263687.0
- `n_R1_in_residential_districts`: 248804.0
- `share_R1_lot20k_plus`: 0.396
- `share_R1_sewered`: 0.6298
- `share_R1_sf_only_of_read`: 0.7875
- `share_R1_unread`: 0.5903

## State report tables: sum of municipalities vs printed statewide total

| Table | Sum | Printed | Agrees |
|---|---|---|---|
| permits_2025 | 3,778 | 3778 | True |
| co_2025 | 2,162 | 2162 | True |
| stock | 485,932 | 485932 | True |
| by_type | 485,932 | 485932 | True |
| lmih | 44,479 | 44478 | False |

Stock source: census_acs_sf (ACS 2024 5-yr B25024/B25002, summary files). EOH report: available.

---
_Generated 2026-10-20T13:28+00:00 by `headroom report`._
