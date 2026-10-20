# Data Provenance

Every dataset the tool uses is listed here. The code licence (Apache-2.0) does **not** relicense data — each dataset carries its own terms below. No raw or large data is committed: `headroom acquire` retrieves every input from its authoritative source and records each file's URL, retrieval time, size and SHA-256 in `cache/manifest.json`; the generated chapter [`generated/data.md`](generated/data.md) prints that manifest for the current build. The only data files under version control are two small team-created inputs (`data/`).

# Dataset Inventory

| Dataset | Source | Version / vintage | Access date | License / terms | Category |
| --- | --- | --- | --- | --- | --- |
| Rhode Island Zoning and Overlay Zones — municipal zoning classifications (layer 1) and overlay areas (layer 0) | RI Division of Statewide Planning, Land Use 2050 Data Services (HR&A Advisors + Go Consulting), via RIGIS — https://www.rigis.org/maps/c8d4094c9141466eb6d3e9d82c349dd8 | 2025 compilation; feature service read live | 2026-10-04 | RIGIS: provided as-is; acknowledge RIGIS and the primary producer in derived products | public (state) |
| E-911 Address Points | RI E 9-1-1 Uniform Emergency Telephone System, via RIGIS — https://www.arcgis.com/home/item.html?id=26c8df834cbb4aa49ed571ad35c5647f | 2026 | 2026-10-04 | RIGIS (as above) | public (state) |
| Sewered Areas | RIGIS — https://www.arcgis.com/home/item.html?id=d1f22828f48946be88e8c30c422ec61b | current service layer | 2026-10-04 | RIGIS (as above) | public (state) |
| Building Permits Survey, annual place files (Northeast region) | U.S. Census Bureau — https://www2.census.gov/econ/bps/Place/Northeast%20Region/ | 2018–2025 annual files (`ne{yyyy}a.txt`) | 2026-10-04 | Public domain (U.S. government work) | public |
| American Community Survey 5-year, table-based summary files (B25024, B25002, B25003) and geography index | U.S. Census Bureau — https://www2.census.gov/programs-surveys/acs/summary_file/ | 2024 5-year release | 2026-10-04 | Public domain | public |
| American Community Survey 5-year via API (optional, with `CENSUS_API_KEY`) | U.S. Census Bureau — https://api.census.gov/data/ | 2023 5-year | 2026-10-04 | Public domain; free key required | public |
| 2025 Integrated Housing Report | RI Executive Office of Housing — https://housing.ri.gov/sites/g/files/xkgbur401/files/2026-04/2025%20Integrated%20Housing%20Report.pdf | published 2026-04-15 | 2026-10-04 | State of Rhode Island public record | public (state) |
| RIPTA GTFS schedule feed | Rhode Island Public Transit Authority — https://ripta.com/RIPTA-GTFS.zip | feed effective 2026-09-16 | 2026-10-04 | Published for public developer use | public (state) |
| Transit Forward RI 2040 (2020 Transit Master Plan) — the eight regional mobility hubs | RI Division of Statewide Planning / RIPTA — https://www.ripta.com/wp-content/uploads/2021/07/SPC-9-10-20.pdf | 2020 | 2026-10-04 | State of Rhode Island public record | public (state); encoded as team-created `data/ri_mobility_hubs.csv` |
| Ordinance-derived district parameters, Rhode Island (optional, tier A) | MuniAnchor — https://munianchor.com/ (publication URL to be announced) | not yet published | — | Apache-2.0 for the derived table; the underlying ordinances are public law; each row cites the section it was read from | third-party (team-affiliated) |
| HousingWorks RI 2025 Housing Fact Book (ADU permit counts 2021–2024) | HousingWorks RI at Roger Williams University | 2025 | 2026-10-04 | Published report; two figures cited in the ledger, not ingested | third-party (citation only) |

Categories follow the template: **public** — nationally available or state-published public datasets; **third-party** — other organisations' publications; **team-created** — built by the team.

**Not used, and why.** The National Zoning Atlas was examined and refused: its terms prohibit commercial use, and the rules say such a dataset is inappropriate where downstream users may be commercial. No parcel layer is used — Rhode Island publishes none statewide, which is why structures stand in for lots.

# Cleaning and Preparation

* **Zoning polygons.** Read from the ArcGIS feature service in pages of 2,000 in the State plane coordinate system (EPSG:3438). Fields kept: district code, description, generalised class, density class, minimum lot size. Rows for the Quonset Development Corporation are kept but are not a municipality.
* **Structure points.** 420,441 E-911 points, filtered to residential types (R1 single-family, R2 multi-family, R3–R6, A1 accessory, DV development site); 388,830 loaded; each joined to the zoning polygon containing it (Shapely STRtree). 3,046 points (0.8 %) fall in no polygon, mostly on water or roads, and are dropped.
* **Allowed-use reading.** Each residential district's description text is read by a rule-based classifier into *single-family only* / *allows 2+ units* / *unknown*, with the matched evidence stored per district. The State layer's `DENSITY` field is a lot-size band, not an allowed-use field, and is not used for this.
* **Sewer.** Points inside any wastewater service polygon are *sewered*; all others *septic*.
* **Transit.** Weekday 7–9 am departures per stop from GTFS `stop_times`; stops with at least four an hour are *frequent*; the eight hubs are matched to their GTFS stops by name and coordinates. Buffers of ⅛ mile (frequent) and ¼ mile (hub) are intersected with residential-district land.
* **Permits.** BPS place files parsed by fixed columns; the 39 Rhode Island places identified by county and county-subdivision FIPS codes taken from the files themselves; imputed values used as published; months reported carried.
* **Municipal names.** Every source spells towns differently (`Barrington town`, `PORTSMOUTH`, `East` / `Greenwich` split across PDF lines); all are mapped to one canonical spelling so joins cannot silently drop a town, and a build fails if a town is missing from any required source.
* **State report tables.** Five municipal tables parsed from the PDF; a one-cell repair rule fills a blank only where the row's own arithmetic identity determines it (recorded per row); each table's sum of municipalities is checked against the report's printed statewide total (four of five agree exactly; LMIH differs by one unit in the report's own arithmetic).
* **ACS.** Summary files streamed and filtered to the state's county subdivisions (duplicate town names across counties are disambiguated by county, never merged); the State report's ACS tables are compared with the Census file at build and agree town for town.
* **Scaling.** Baseline levels are the BPS series scaled by the 2025 State-survey-to-BPS ratio (≈ 2.17), the one year both exist; the ratio's uncertainty is a ledger parameter.

# Known Limitations

* The Census permit survey carries about half of Rhode Island's permits (1,738 vs 3,778 in 2025) because many towns do not return the form; only 2025 can be compared, so the undercount's stability is unknown.
* The State zoning layer carries no allowed-use, height, parking or FAR fields; 59 % of single-family structures in residential districts sit in districts whose description text says nothing about allowed uses.
* Structures are not parcels: a lot with two buildings or none is miscounted, and lot size is known only as the district minimum.
* RIPTA's feed carries no `calendar.txt` (service is defined in `calendar_dates.txt`); frequency is measured on one representative weekday.
* The State report is a PDF; the parser is checked against the printed totals but a future layout change would break it.
* Some networks receive HTTP 403 from the State's report host; `HEADROOM_EOH_PDF` points at a saved copy.
* The MuniAnchor table is not yet published, so tier A currently equals tier B.

# Restricted, Sensitive, or Personal Data

No sensitive, confidential, restricted-use or personally identifiable data is used. The E-911 layer is a public GIS dataset of structure locations and types, not of people; it is used only to count structures by zoning district and municipality, is never redistributed, and no address appears in any output. All outputs are aggregated to municipality or state. Small-cell note: a municipality–district cell may hold a handful of structures, but the cells describe buildings, not households, and carry no attribute beyond type and location that is not already public in the source layer. ACS figures are the Census Bureau's own published estimates for county subdivisions.
