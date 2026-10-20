# Data

No raw or large data is committed to this repository. Every input is retrieved from its authoritative source by the tool itself:

```
uv run headroom acquire        # or: scripts/run.sh, which runs it first
```

Downloads land in `cache/` (git-ignored), and `cache/manifest.json` records each file's URL, retrieval time, size and SHA-256. The first run fetches about 100 MB — the largest file is the State's E-911 structure layer, one point per building — and takes three to four minutes; later runs reuse the cache.

## What is in this directory

| File | What it is | Size |
|---|---|---|
| `ri_mobility_hubs.csv` | The eight regional mobility hubs named in *Transit Forward RI 2040* (the 2020 Transit Master Plan, which § 45-24-33(a)(28) defers to), located at their RIPTA stops. Team-created from the plan's text and the GTFS stop list. | 8 rows |
| `district_params_ri.csv` | *Optional, tier A.* Allowed residential uses and dimensional envelopes by zoning district, read from adopted ordinance text and published by MuniAnchor. Absent in this checkout; the tool runs at tier B without it. Schema in `../schema/district_params.md`. | — |

Both are small, team-created inputs, not source datasets, and are the only data files under version control.

## Optional environment

`CENSUS_API_KEY` reads ACS tables from the Census API instead of the summary files; `HEADROOM_EOH_PDF` points at a saved copy of the State's 2025 Integrated Housing Report for networks its host refuses. See `.env.example`.

## Provenance

Source, version, access date, licence and cleaning steps for every dataset: [docs/DATA_PROVENANCE.md](../docs/DATA_PROVENANCE.md). The challenge's own list of state data portals is reproduced in [DATA_SOURCES.md](DATA_SOURCES.md).
