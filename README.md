# Headroom

[![CI](https://github.com/GreatStreetsFighter-401/headroom/actions/workflows/ci.yml/badge.svg)](https://github.com/GreatStreetsFighter-401/headroom/actions/workflows/ci.yml) [![reproduce](https://github.com/GreatStreetsFighter-401/headroom/actions/workflows/reproduce.yml/badge.svg)](https://github.com/GreatStreetsFighter-401/headroom/actions/workflows/reproduce.yml)

Public repository: https://github.com/GreatStreetsFighter-401/headroom · **Live page: https://greatstreetsfighter-401.github.io/headroom/** (published from `site/` by `pages.yml` on every push to `main`)

**How much housing a state-level reform makes room for.** A transparent, replicable capacity-and-uptake model that estimates how many more homes a state is likely to permit over five years under each of the five benchmark reforms, as a range rather than a point, with every number traceable to a public dataset, a statute section or a named assumption. Built for the [Housing Data and Technology Innovation Challenge](https://housingchallenge.turnout.rocks/), with Rhode Island as the showcase state and a Census-only mode that runs for any state.

## What this tool does

For a policymaker, one question: *if the state enacts this reform, how many more homes are likely to be permitted over the next five years, and how sure can we be?* Headroom answers per municipality and statewide, for 2027–2031, as P10 / P50 / P90, and shows which assumption each answer turns on.

**Scenarios:** the baseline plus **all five** benchmark scenarios — accessory dwelling units, missing middle / gentle density, transit-oriented density, parking requirement reduction, development fee reduction (run both at the handbook's $50,000 per unit and at Rhode Island's actual fees) — and the five together as a capped upper bound. Each reform is an increment over current law, which in Rhode Island already includes by-right ADUs on larger lots (§ 45-24-73) and a one-space parking cap near transit (§ 45-24-33(a)(28)).

**States:** Rhode Island at three data tiers (ordinance-derived, State zoning layer, Census only), and any other state at the Census-only tier with no state-specific code (`--state MA`, `--state CT` are run in the generated chapters).

```
permits(scenario, town, year) = baseline(town, year)
                              + Σ  eligible_capacity(channel, town)    ← Stage 1: data, no judgment
                                   × uptake(channel, year)             ← Stage 2: a ledger parameter
                                   × feasibility(channel, town)        ← Stage 2: a ledger parameter
```

Stage 1 is computed from public data by a spatial join with no judgment. Stage 2 is where every behavioural assumption lives: each is a record in [`assumptions.yaml`](assumptions.yaml) with a default, a range, a distribution, a status (statutory / verified / prior / placeholder / design), a source and a justification; the Monte Carlo samples that file, and a test fails if a behavioural constant appears in the model code instead.

## Command contract

These are the exact commands a reviewer runs from a clean checkout. They need **Python 3.11+** and [**uv**](https://docs.astral.sh/uv/) (`pip install uv`); nothing else. No environment variable is required (`.env.example` lists the optional ones).

| Step | Command | Notes |
| --- | --- | --- |
| Setup | `sh scripts/setup.sh` | `uv sync --extra dev --frozen`: creates `.venv` from the pinned `uv.lock` |
| Run | `sh scripts/run.sh` | Acquires every input from its source (≈ 100 MB, 3–4 minutes the first time, cached after), builds Stage 1 at all tiers, runs the Monte Carlo, the calibration and the report, publishes the results into `site/` and serves the page at http://localhost:8765/ |
| Test | `sh scripts/test.sh` | `pytest` (55 tests over the core logic) plus `ruff check` and `ruff format --check`; exits non-zero on any failure |

Without uv: `python -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"`, then the same `headroom …` commands below with the environment active.

The individual commands, for anyone who wants one step at a time:

```bash
headroom acquire                                 # fetch every input from its source (cached)
headroom build --tier all                        # Stage 1 at tiers A, B, C
headroom run --tier all                          # Stage 2 Monte Carlo (2,000 draws, seeded)
headroom calibrate                               # implied vs observed 2024 ADU permits
headroom hindcast                                # fit the baseline through 2023, score 2024–2025
headroom explain adu_uptake_detached_annual      # any ledger entry
headroom report                                  # generate docs/generated/*.md
headroom site                                    # publish results into site/ (open site/index.html)
headroom check                                   # compare with the committed reference results
headroom build --state MA && headroom run --state MA   # any other state, tier C, Census data only
```

## The page

The page is live at https://greatstreetsfighter-401.github.io/headroom/, and `scripts/run.sh` serves the same `site/` at http://localhost:8765/ (any static host works; there is no server-side code). The page shows the committed results and, under **Try an assumption**, offers every sampled ledger parameter as a slider. Moving one pins that assumption at your value and **re-runs the model in your browser**: `site/worker.js` loads Pyodide (CPython compiled to WebAssembly) and the model's own source files from `site/model/` — published by `headroom site` and checked against `src/` by the test suite — and calls `headroom.model.web.run`. Nothing is re-implemented in JavaScript; 500 draws take about a second. If the runtime cannot be fetched the page says so and the sliders fall back to rescaling the committed medians. `?pyodide=<dir>/` points the worker at a self-hosted copy of the runtime.

## Data

No dataset is committed. `headroom acquire` (the first step of `scripts/run.sh`) retrieves every input from its authoritative source — the Rhode Island zoning layer, E-911 structure points and sewered areas (RIGIS), the Census Building Permits Survey and ACS summary files, the State's 2025 Integrated Housing Report, RIPTA's GTFS feed — and records each file's URL, retrieval time, size and SHA-256 in `cache/manifest.json`. See [data/README.md](data/README.md) for the two small team-created inputs that are committed, and [docs/DATA_PROVENANCE.md](docs/DATA_PROVENANCE.md) for every dataset's source, vintage, licence, cleaning steps and limitations.

Optional: `CENSUS_API_KEY` reads ACS tables from the Census API instead of the summary files; `HEADROOM_EOH_PDF` points at a saved copy of the State report for networks its host refuses.

## Documentation

- [Model & Assumptions Overview](docs/MODEL_AND_ASSUMPTIONS.md) — how the tool works, what it assumes, what it cannot say
- [Policy Scenario Comparison](docs/POLICY_SCENARIO_COMPARISON.md) — the ranking, its drivers, the assumptions that matter most
- [Data Provenance](docs/DATA_PROVENANCE.md) — sources, licences, cleaning steps, limitations
- [Disclosures](docs/DISCLOSURES.md) — AI assistance, external services, dependency licences
- [Generated chapters](docs/generated/) — every assumption, every data file, every result, written by `headroom report`
- [Presentation Guide](docs/PRESENTATION_GUIDE.md) and [Challenge Specification](docs/CHALLENGE_SPEC.md) — from the challenge's starter template
- [Submission checklist](SUBMISSION_CHECKLIST.md)

## What is where

```
assumptions.yaml        the ledger — every Stage 2 parameter, with source and status
scripts/                the command contract: setup.sh, run.sh, test.sh
src/headroom/
  acquire/              one module per source; every download goes through base.fetch()
  build/                Stage 1: spatial join, district reading, transit buffers, town table
  model/core.py         Stage 2: baseline, scenario increments, Monte Carlo, sensitivity
  model/hindcast.py     out-of-sample test of the baseline
  ledger.py             load / validate / sample / explain the ledger
  report.py             the generated chapters
  cli.py                the commands above
site/                   static page (no build step, no server) over site/data/*.json
docs/                   the four required documents; docs/generated/ is written by `headroom report`
data/                   two small team-created inputs; everything else is acquired
schema/                 district_params.md — what a state fills in for tier A
tests/                  55 tests, including the "no behavioural literals in the model" guard
out/reference/          committed results the reproducibility check compares against
```

## Replicability

`headroom check` compares a run's statewide results with the committed reference; `.github/workflows/reproduce.yml` re-acquires every source weekly and on every push to `main` and fails on drift, so a republished source or a changed answer is visible. `ci.yml` runs the command contract on every push.

## License

Apache License 2.0 — see [LICENSE](LICENSE) and [NOTICE](NOTICE). The challenge's recommended default; its express patent grant is the safest choice for a tool that may be adopted or integrated downstream. Data carry their own terms (see Data Provenance).

## Team

Gregory Guertin (Team Leader) — Smithfield, Rhode Island. MuniAnchor, a municipal ordinance platform the author builds, is disclosed as the publisher of one optional dataset (the ordinance-derived district table); none of its code is part of this submission.
