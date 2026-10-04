# Headroom

**How much housing a state-level reform makes room for.** A transparent, replicable,
capacity-and-uptake model built for the [Housing Data and Technology Innovation
Challenge](https://housingchallenge.turnout.rocks/) (The Turnout / Arnold Ventures), with
Rhode Island as the showcase state and a Census-only mode that runs anywhere.

Headroom answers one question for a policymaker: *if the state enacts this reform, how many
more homes are likely to be permitted over the next five years, and how sure can we be?* It
answers with a range, never a point, and every number on screen can be traced to a public
dataset, a statute section or a named assumption with its source.

## How it works

```
permits(scenario, town, year) = baseline(town, year)
                              + Σ  eligible_capacity(channel, town)    ← Stage 1: data, no judgment
                                   × uptake(channel, year)             ← Stage 2: a ledger parameter
                                   × feasibility(channel, town)        ← Stage 2: a ledger parameter
```

* **Stage 1 — regulatory capacity** is computed from public data with no judgment: the
  State's zoning polygons, a typed statewide structure layer (one point per building), sewer
  service areas, transit schedules, and — where an ordinance has been parsed — the allowed
  residential uses by district read from the adopted zoning text.
* **Stage 2 — uptake and feasibility** is where every behavioural assumption lives. Each one
  is a record in [`assumptions.yaml`](assumptions.yaml): a default, a range, a sampling
  distribution, a status (statutory / verified / prior / placeholder / design), a source and
  a justification. The Monte Carlo samples that file. `headroom explain <id>` prints an
  entry. The assumptions chapter of the overview is generated from it. A test fails if a
  behavioural constant appears in the model code instead.
* **Output** is the distribution of permitted units per scenario, per municipality and
  statewide, for 2027–2031, as P10 / P50 / P90, with a sensitivity table (rank correlation of
  every parameter with the result) for each scenario.

### Scenarios

Baseline plus the five handbook benchmarks, each modelled as an *increment over current
law* — which matters in Rhode Island, where ADUs are already by right on larger lots
(§ 45-24-73) and parking near transit is already capped at one space (§ 45-24-33(a)(28)):

| Scenario | Stage 1 capacity | Stage 2 |
|---|---|---|
| ADU | Single-family structures in districts below the 20,000 sq ft by-right threshold, split by sewer | uptake rate (calibrated to Rhode Island's 163 ADU permits in 2024), ramp, septic multiplier |
| Missing middle | Single-family structures in single-family-only districts (ordinance → district text → statewide share) | conversion rate, units per conversion, feasibility share, septic multiplier |
| Parking | Baseline multifamily permits | mandated minus provided spaces × cost per space ÷ cost per unit × supply-cost elasticity |
| Fees | All baseline permits | fee cut ÷ cost per unit × elasticity, at the handbook's $50,000 and at Rhode Island's actual fees |
| Transit-oriented | Residential land within ⅛ mile of frequent stops and ¼ mile of hubs (the statutory distances), at scenario minus current density | realisation rate, ramp |

### Data tiers — the replicability story

The same model runs on three input sets, so what richer data buys is measured, not asserted:

| Tier | Inputs | Who can run it |
|---|---|---|
| **A** | State zoning layer + ordinance-derived allowed uses and envelopes (MuniAnchor) | a state with parsed ordinances |
| **B** | State zoning layer + structure points + sewer + GTFS | a state with a zoning layer (Rhode Island's is from 2025) |
| **C** | Census structure counts + ledger shares | **any state**, from federal data alone |

## Run it

```bash
cd headroom
uv venv && uv pip install -e ".[dev]"          # or: pip install -e ".[dev]"
headroom acquire                                 # fetch every input from its source (cached)
headroom build --tier all                        # Stage 1 at tiers A, B, C
headroom run --tier all                          # Stage 2 Monte Carlo (2,000 draws, seeded)
headroom calibrate                               # implied vs observed 2024 ADU permits
headroom explain adu_uptake_detached_annual      # any ledger entry
headroom report                                  # generate docs/generated/*.md
headroom site                                    # publish results into site/ (open site/index.html)
```

The acquisition step downloads about 100 MB (the statewide structure layer is 420,000 points)
and takes three to four minutes on the first run; everything after that runs in seconds.
Set `CENSUS_API_KEY` to read ACS tables from the Census API; without it the same ACS tables
are read from the State's 2025 Integrated Housing Report. Some hosts refuse automated
clients for that PDF; `HEADROOM_EOH_PDF=/path/to/copy.pdf` points at a saved copy.

## What is where

```
assumptions.yaml        the ledger — every Stage 2 parameter, with source and status
src/headroom/
  acquire/              one module per source; every download goes through base.fetch()
                        and lands in cache/manifest.json with URL, SHA-256 and time
  build/                Stage 1: spatial join, district reading, transit buffers, town table
  model/core.py         Stage 2: baseline, scenario increments, Monte Carlo, sensitivity
  ledger.py             load / validate / sample / explain the ledger
  report.py             overview chapters generated from the ledger + results
  cli.py                the commands above
site/                   static page (no build step, no server) over out/*.json
docs/                   the hand-written overview and scenario comparison; docs/generated/ is written by `headroom report`
schema/                 district_params.md — what another state fills in for tier A
tests/                  unit tests, including the "no behavioural literals in the model" guard
out/reference/          committed results the reproducibility check compares against
```

## Provenance and licences

Every dataset is listed in `src/headroom/acquire/base.py::SOURCES` with its publisher and
licence, and `cache/manifest.json` records each file actually fetched. Sources: Rhode Island
Division of Statewide Planning / RIGIS (zoning, land use, E-911 points, sewered areas),
U.S. Census Bureau (Building Permits Survey, ACS), Rhode Island Executive Office of Housing
(2025 Integrated Housing Report), RIPTA (GTFS), and — optional, tier A — MuniAnchor's
ordinance-derived district table, released under this repository's licence.

Headroom is released under the [Apache License 2.0](LICENSE).

## AI disclosure

Parts of this code and documentation were drafted with Claude (Anthropic) under the
author's direction; every data value, statute reading and modelling choice was verified
against the primary source named beside it. No pretrained model, embedding or hosted
inference service is used at run time; the tool is arithmetic over public data.
