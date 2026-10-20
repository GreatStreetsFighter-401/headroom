# Disclosures

This document exists so reviewers can confirm that the tool's code, models, services and dependencies are compatible with the challenge's open-source and downstream-use requirements.

# AI-Assisted Code Generation

**Material use.** The code and documentation in this repository were drafted with **Claude (Anthropic)**, used as a coding assistant through Claude Code under the author's direction, during the challenge's Registration and Coding Periods. That includes substantive logic: the acquisition modules, the spatial join, the district-text classifier, the Monte Carlo model, the ledger loader, the tests, the report generator and the static page. The author directed the design, reviewed every module, verified every data value, statute reading and modelling choice against the primary source named beside it, and is responsible for the result.

**How it was verified.** Fifty-five automated tests cover the core logic (`scripts/test.sh`), including a guard that fails if a behavioural constant appears in the model code instead of the assumption ledger; the ADU scenario is calibrated against Rhode Island's observed 2024 permits; the baseline is hindcast out of sample; parsed State tables are checked against their printed totals; and `headroom check` compares every run with committed reference results.

**Terms.** Anthropic's consumer and commercial terms assign the output to the user and permit its release under an open-source licence. No AI tool is used at run time.

# Pretrained Models, Weights, and Embeddings

None. The tool is arithmetic over public data: a rule-based text classifier (regular expressions over district descriptions), a spatial join, and a Monte Carlo over an explicit parameter ledger. No model weights, embeddings or inference services are incorporated or required.

| Model / asset | Source | License / terms | Restrictions |
| --- | --- | --- | --- |
| none | — | — | — |

# External APIs and Hosted Services

The tool calls public data services at acquisition time only; after the first run everything works from the local cache.

| Service | Needed for | Free tier / access | Could it lapse? | Terms |
| --- | --- | --- | --- | --- |
| RIGIS / ArcGIS Online feature services (`services2.arcgis.com`) | Zoning polygons, E-911 points, sewered areas | Free, no key | Layers are versioned by the State; a republished layer changes the manifest hash and the reproducibility check reports it | RIGIS licence, acknowledgment required |
| Census Bureau file servers (`www2.census.gov`) | Building Permits Survey place files; ACS summary files and geography index | Free, no key | Stable public archive | Public domain |
| Census API (`api.census.gov`) — optional | ACS tables, if `CENSUS_API_KEY` is set | Free key | Not needed; the summary files are the default path | Public domain |
| RI Executive Office of Housing (`housing.ri.gov`) | 2025 Integrated Housing Report PDF | Free | Some hosts refuse automated clients (HTTP 403); a saved copy can be supplied | Public record |
| RIPTA (`ripta.com`) | GTFS feed | Free | Feed URL has moved before (a 301 is followed) | Public developer use |
| MuniAnchor (`munianchor.com`) — optional, tier A | Ordinance-derived district table | Free download, to be published under Apache-2.0 | The table is optional; the tool runs at tier B without it | Apache-2.0 (derived table) |

No service limits commercial, government or downstream use of the outputs. MuniAnchor is a product of the Team Leader; it is disclosed as the publisher of one optional dataset and nothing from its code is part of this submission.

# Dependency Licenses

Runtime dependencies are permissively licensed and compatible with closed-source downstream integration, with one flagged exception explained below. Versions are pinned in `uv.lock`; the SBOM exported from GitHub's dependency graph is the source of truth. Development-only tools (test runner, linter, SBOM generator) are not shipped with the tool.

| Dependency | License | Runtime or dev-only | Notes |
| --- | --- | --- | --- |
| numpy | BSD-3-Clause (vendored components under 0BSD, MIT, Zlib, CC0-1.0) | runtime | ok — the CC0 portion is an upstream vendored file, not first-party code |
| shapely | BSD-3-Clause | runtime | ok |
| PyYAML | MIT | runtime | ok |
| requests | Apache-2.0 | runtime | ok |
| └ certifi | **MPL-2.0** | runtime | **flagged** — see below |
| └ charset-normalizer | MIT | runtime | ok |
| └ idna | BSD-3-Clause | runtime | ok |
| └ urllib3 | MIT | runtime | ok |
| pdfplumber | MIT | runtime | ok |
| └ pdfminer.six | MIT | runtime | ok |
| └ pypdfium2 | Apache-2.0 OR BSD-3-Clause (PDFium: BSD-3-Clause) | runtime | ok — its package metadata records no licence string; the dual licence is stated in the project's LICENSE files |
| └ Pillow | MIT-CMU (HPND) | runtime | ok |
| └ cryptography | Apache-2.0 OR BSD-3-Clause | runtime | ok |
| └ cffi, pycparser | MIT; BSD-3-Clause | runtime | ok |
| pytest, ruff | MIT | dev | ok |
| cyclonedx-bom and its tree (incl. fqdn, MPL-2.0) | Apache-2.0; various permissive; fqdn MPL-2.0 | dev | fqdn is pulled in only by the SBOM generator and never ships |

**Exception: certifi (MPL-2.0).** `certifi` is the Mozilla CA certificate bundle that `requests` uses to verify HTTPS connections; it is a transitive dependency of every Python HTTP client and is used unmodified. The Mozilla Public License 2.0 is a file-level copyleft: it applies only to the licensed files themselves and expressly permits combining them into a larger work under any licence (MPL 2.0 §3.3), so it does not affect the licensing of this tool or of anything that integrates it. The rules list MPL among copyleft licences and ask that such a dependency be flagged and resolved; it is flagged here, and resolved by this note rather than by replacement because the certificate bundle carries no code of ours and every alternative HTTP stack depends on the same bundle or on the operating system's.

# Generated or Copied Code

* `docs/CHALLENGE_SPEC.md`, `docs/PRESENTATION_GUIDE.md`, `data/DATA_SOURCES.md`, `.github/workflows/codeql.yml` and `.github/PULL_REQUEST_TEMPLATE.md` are copied from the challenge's starter template (The Turnout, Apache-2.0) and attributed in `NOTICE`; the four document templates in `docs/` follow its section structure.
* The transverse Mercator projection used to place GTFS stop coordinates in the State plane system (`build/transit.py`) is implemented from the published NAD83 / Rhode Island zone parameters; it is original code with an accuracy of about 3.4 ft, documented in the module.
* No other code is copied or adapted from external sources. The municipality list, the FIPS crosswalk and the mobility-hub table were built from the primary sources named in `DATA_PROVENANCE.md`.
