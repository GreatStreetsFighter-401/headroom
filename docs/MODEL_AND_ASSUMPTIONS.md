# Model & Assumptions Overview

*Headroom — draft v0.2, 2026-10-20. Written for a policymaker with no technical background. The tables in `docs/generated/` (every assumption, every data file, every result) are produced by `headroom report` from the ledger and the run outputs and are authoritative for numbers; this document is the explanation around them. Page budget: 25.*

# Purpose and Scope

**The question.** If a state enacts one of the five benchmark reforms, how many more homes are likely to be permitted over the next five years — and how sure can anyone be?

**The answer the tool gives.** A range, never a point: the 10th, 50th and 90th percentiles of permitted housing units per scenario, per municipality and statewide, for 2027–2031, with every number traceable to a public dataset, a statute section, or a named assumption with its source and range.

**For whom.** Policy staff, planners and legislators who have to put a number beside a bill and defend where it came from.

**Geography.** The showcase state is Rhode Island (39 municipalities, every one a permit-issuing place). The same code runs for any state from federal data alone (see *Data tiers* below); Massachusetts and Connecticut are run in the generated chapters as the demonstration.

**Scenarios addressed.** The baseline and all five benchmarks — accessory dwelling units, missing middle, transit-oriented density, parking requirement reduction, development fee reduction — plus the five together as a capped upper bound. Each reform is modelled as an **increment over current law**, which matters in Rhode Island because parts of three benchmarks are already enacted (§ 45-24-73 ADUs by right on lots of 20,000 sq ft or more and within existing footprints; § 45-24-33(a)(28) capping parking at one space per multifamily unit near transit; chapter 45-53 comprehensive permits).

**In scope:** statewide and municipal permit counts by year; what drives each scenario; which assumptions carry the uncertainty; what richer data would change.

**Out of scope:** where within a town the units land; prices, rents and who occupies the homes; funding, interest rates and construction labour beyond a statewide capacity ceiling; interactions between reforms beyond a shared cost channel.

# Core Assumptions and Their Rationale

Every behavioural, cost and feasibility assumption is a record in [`assumptions.yaml`](../assumptions.yaml) — a default, a range, a sampling distribution, a status, a source and a justification — and the Monte Carlo samples that file. `headroom explain <id>` prints any entry; [`docs/generated/assumptions.md`](generated/assumptions.md) lists all 32. A unit test fails if a number that could be a behavioural assumption appears in the model code instead of the ledger. The ones that move the results most:

| Assumption | Value / range | Rationale | Source |
| --- | --- | --- | --- |
| ADU uptake on newly eligible lots, per year at steady state | 0.2 % (0.05–0.6 %), lognormal | Set so current-law eligibility reproduces Rhode Island's 163 ADU permits in 2024 between ramp year one and two; below California's 2023 rate (≈ 0.3 %) | HousingWorks RI 2025 Fact Book; California HCD APR dashboard |
| Ramp to steady state (ADU, missing middle, TOD) | 3 years (1–5) | Rhode Island's and California's ADU series roughly doubled annually for three years after by-right rules | HCD 2016–2023; RI 2021–2024 |
| Uptake multiplier on septic lots | 0.5 (0.2–0.8) for ADUs; 0.3 (0.1–0.6) for 3–6 units | A second unit needs onsite wastewater capacity, often the binding cost in rural towns | RIGIS Sewered Areas; RIDEM OWTS rules |
| Missing-middle conversion of single-family-only lots, per year | 0.05 % (0.01–0.2 %), lognormal | Portland's first year ≈ 0.13 % of lots; Minneapolis an order of magnitude lower for 2–3-unit buildings | Portland RIP monitoring; Minneapolis 2040 outcomes |
| Share of eligible lots where redevelopment is plausible | 0.5 (0.25–0.8) — **placeholder** | Needs land worth more than the house on it; to be set from assessor land-to-improvement ratios | Municipal assessor data (not yet joined) |
| Supply elasticity to per-unit cost | 0.8 (0.3–1.5), lognormal | Tract-level supply elasticities ≈ 0.5 across 306 metros; New England on the inelastic side | Baum-Snow & Duranton (2025); Saiz (2010) |
| Cost of a mandated parking space | $20,000 ($8,000–45,000) | Surface $5–15k, structured $25–50k; Rhode Island multifamily is mostly surface or podium | Industry cost surveys; Seattle reform estimate |
| Spaces developers provide without a mandate | 0.8 per unit (0.4–1.2) | Seattle, Buffalo and Minneapolis post-reform buildings still include parking buyers want | City monitoring reports |
| Mandated spaces per multifamily unit today | 1.5 (1.0–2.0) — **placeholder** | Suburbs typically 2, cities 1–1.5; to be read from the 39 parking schedules | Municipal ordinances |
| Development fee per unit, Rhode Island actual | $8,000 ($4,000–15,000) — **placeholder** | Building fees ≈ $10–15 per $1,000 of value, few impact fees; run beside the handbook's $50,000 | Municipal fee schedules (to be collected) |
| TOD realisation of net capacity near transit, per year | 0.4 % (0.1–1.2 %), lognormal | Upzoned station areas build out over decades | Seattle station areas; MBTA Communities filings |
| Scenario density near transit | 20 units/acre (12–40) | Three-story walk-up density; MBTA Communities sets 15 as a minimum | Handbook (teams define); MBTA Communities |
| Weight on linear trend vs recent mean in the baseline | 0.5 (0–1), uniform | 2025 was the highest permit year since the 1980s; whether it is a level or a peak is not knowable, so the blend is sampled | Census BPS 2018–2025 |
| Year-to-year noise in municipal permits | CV 0.35 (0.15–0.60) on top of Poisson count noise | Median residual CV around each town's trend is 0.40, computed at build | Census BPS residuals (`pipeline.noise_cv_from_history`) |
| Statewide construction-capacity ceiling | 2.0 × recent annual permits (1.5–3.0) | Rhode Island's record year (≈ 7,300, 1986–87) was 2.4 × today's level; a multiple scales to any state | EOH 2025 report Fig. 2.2 |
| Census-to-State permit scaling | ratio computed at build (≈ 2.17) × 1.0 (0.8–1.2) | The Census survey carries about half of Rhode Island's permits; the State says its own survey is more accurate | EOH 2025 report Figs 2.1–2.2; Census BPS |

Statutory values — the 20,000 sq ft by-right ADU lot, the handbook's $50,000 fee and 50 % cut, the 2–6 unit range — are fixed, not sampled, and carry their citation in the ledger. Each entry's status (statutory / verified / prior / placeholder / design) is shown on the page beside the number it feeds, so a reader can see at once which numbers are law, which are measured, and which are informed guesses with a wide range.

# Data Sources and Cleaning Steps

Every dataset is retrieved from its authoritative source by `headroom acquire` and recorded in `cache/manifest.json` with URL, retrieval time, size and SHA-256; nothing is bundled. Full provenance, licences, cleaning and limitations are in [DATA_PROVENANCE.md](DATA_PROVENANCE.md); in summary:

| Dataset | Used for |
| --- | --- |
| Rhode Island zoning layer (RIGIS, 2025; 15,733 polygons) | District class, minimum lot size, district description text |
| E-911 address points (RIGIS, 2026; 388,830 residential structures) | One typed point per building: the count of existing single-family homes by district |
| Sewered areas (RIGIS) | Sewer vs septic feasibility filter |
| Census Building Permits Survey, place files 2018–2025 | The permit series for every town (shape of the baseline) |
| Census ACS 5-year table-based summary files (B25024, B25002, B25003) | Housing stock by structure type, streamed without an API key; the tier-C input |
| Rhode Island 2025 Integrated Housing Report (Executive Office of Housing) | The State's own 2025 permits and certificates of occupancy by town; the permit scaling ratio |
| RIPTA GTFS schedule | Frequent transit stops (four peak departures an hour) |
| Transit Forward RI 2040 | The eight named regional mobility hubs |
| MuniAnchor district table (optional, tier A) | Allowed residential uses and envelopes read from adopted ordinance text |

The main preparation steps: a spatial join of every structure point into a zoning polygon in the State plane coordinate system (99.6 % land in a district); a rule-based reading of each district's description text for "single-family only" versus "allows two or more units" with the evidence recorded per district; ¼-mile and ⅛-mile buffers around hub and frequent stops; municipal name reconciliation across sources that spell towns differently; and parsing of the State report's PDF tables, each checked against the report's own printed statewide totals (four of five agree exactly; the fifth differs by one unit in the report's arithmetic). The State report's ACS tables are also compared with the Census summary file at build time and agree town for town.

# Methodological Approach

Two stages, kept apart so a reader can see which numbers are *law and land* and which are *behaviour*:

```
permits(scenario, town, year) = baseline(town, year)
                              + Σ  eligible_capacity(channel, town)    ← Stage 1: data, no judgment
                                   × uptake(channel, year)             ← Stage 2: ledger parameter
                                   × feasibility(channel, town)        ← Stage 2: ledger parameter
```

**Stage 1 — regulatory capacity.** Computed from public data by the spatial join above with no judgment. Where an ordinance has been parsed (tier A) the allowed residential uses by district are read from the adopted zoning text; otherwise from the district's description in the State layer (tier B); otherwise from Census structure counts and a statewide share (tier C).

**Stage 2 — uptake and feasibility.** The Monte Carlo (2,000 draws, seed 20261216) samples the ledger once per draw and runs every scenario on the same draw, so scenario differences are not noise.

**Baseline.** Per municipality: a blend of the 2018–2025 linear trend and the 2023–2025 mean of the Census permit series, scaled to the State survey's level by the 2025 ratio, times level noise plus Poisson count noise, with the statewide capacity ceiling applied to the total.

**Scenario mechanics.**

| Scenario | Capacity (Stage 1) | Uptake (Stage 2) |
| --- | --- | --- |
| ADU | Single-family structures in districts below the 20,000 sq ft by-right threshold, split by sewer | uptake rate × ramp × septic multiplier |
| Missing middle | Single-family structures in single-family-only districts | conversion rate × (units − 1) × feasibility share × septic multiplier × ramp |
| Parking | Baseline multifamily permits, split inside/outside transit buffers | (mandated − provided spaces) × cost per space ÷ cost per unit × elasticity |
| Fees | All baseline permits | fee cut ÷ cost per unit × elasticity, at $50,000 and at the Rhode Island actual |
| Transit-oriented | Residential land inside the statutory buffers × (scenario density − current density) | realisation rate × ramp |
| All five | the sum of the increments, fees at the Rhode Island actual | capped by the statewide ceiling; no interactions modelled |

Each scenario's total is capped by the same construction-capacity ceiling as the baseline, so a stacked reform cannot exceed what the industry has ever delivered.

**Calibration.** Rhode Island permitted 11 ADUs in 2021 and 163 in 2024. With the default uptake rates and the model's own current-law eligibility (≈ 64,000 lots for a detached ADU by right, ≈ 215,000 for a within-footprint conversion), the model implies 100 ADU permits in 2024 if 2024 is ramp year one and 200 if it is year two; the observed 163 lies between. `headroom calibrate` prints this check.

**Validation.** The baseline is the only component with a time series to test against, so it is tested out of sample: fit on 2018–2023, predict 2024–2025, score against what happened (`headroom hindcast`).

| Statistic | Value |
| --- | --- |
| Mean absolute error of the P50, per town-year | 26.9 units |
| Statewide error of the P50 | −30.9 % |
| Observed values inside the P10–P90 band | 60 % |

Read plainly: a trend fitted through 2023 misses the 2024–2025 surge, and the bands cover six town-years in ten rather than eight. The forecast uses the series through 2025 and so carries the surge, but this is why the baseline band is stated as conditional on no further regime change and why the trend weight is a sampled parameter rather than a choice.

**Results (tier B, Rhode Island, 2027–2031, permitted units, P10 / P50 / P90).** Baseline 16,189 / 18,607 / 21,434. ADU +432 / +1,162 / +3,173. Missing middle +97 / +357 / +1,260. Parking +69 / +201 / +499. Fees at $50,000: +426 / +820 / +1,493; at the Rhode Island actual: +70 / +142 / +280. Transit-oriented +127 / +372 / +1,047. All five together +1,549 / +2,708 / +4,644. Full tables by year and municipality: [`generated/results_tierB.md`](generated/results_tierB.md); the three tiers side by side: [`generated/tiers.md`](generated/tiers.md).

**Data tiers — the replicability design.** The same model runs on three input sets, so what richer data buys is measured rather than asserted: tier A adds ordinance-derived allowed uses and envelopes; tier B is the State zoning layer, structure points, sewer and GTFS; tier C is Census structure counts and ledger shares, which every state has and which are read from Census files that need no API key. `headroom build --state MA && headroom run --state MA` produces tier-C results for another state in under a minute with no state-specific code ([`generated/other_states.md`](generated/other_states.md)), with two caveats printed beside them: the permit level is the Census series as published, and the eligibility shares are Rhode Island's until replaced with the state's own.

# Limitations and Known Edge Cases

* **The 2025 surge.** Rhode Island's 2025 permits (3,778) were the highest since the 1980s. The baseline band is conditional on no further regime change; the hindcast shows what a trend fitted before a surge does.
* **Half the permits are invisible to the Census.** The Census survey carries ≈ 1,738 of the State's 3,778 units for 2025 because many towns do not return the form. The level is scaled by the one year in which both series exist; whether the undercount is stable is unknown and is carried as a parameter. In a state whose Census series is complete the ratio is 1.0.
* **Unread districts.** At tier B, 59 % of single-family structures in residential districts sit in districts whose description text says nothing about allowed uses, and the statewide share applies there. Tier A exists to close this; it is empty until the ordinance table is published.
* **Structures, not parcels.** The E-911 layer gives one point per building, not a parcel. "Eligible lots" are counted as single-family structures in a district; a lot with two buildings or none is miscounted.
* **Three placeholders.** The missing-middle feasibility share, the mandated-parking baseline and the Rhode Island fee level are explicit guesses with wide ranges, flagged on the page; the sensitivity notes show how much each matters.
* **Small towns and small cells.** A town permitting five units a year has a noisy history; Poisson noise is included, but a single project can move a year by half.
* **Transit definitions.** "Frequent" is four peak departures an hour on RIPTA's published timetable, the Transit Master Plan's 15-minute standard — a schedule measure, not ridership. The eight hubs are the plan's own list.
* **No interactions.** "All five together" adds the increments and caps the total; it is an upper bound, not a joint forecast.
* **Other states at tier C.** Eligibility shares are borrowed from Rhode Island's tier-B values until a state supplies its own, and the transit scenario cannot run without a zoning layer.

# Sensitivity Notes

For each scenario the generated results chapter lists every sampled parameter's Spearman rank correlation with the five-year statewide increment, and the median increment in the parameter's bottom and top quintiles. The pattern is the same in every scenario: the **uptake, conversion or realisation rate dominates** (ρ ≈ +0.9 to +0.99); the ramp length is the next largest and negative; the structural shares (sewer, single-family-only) matter little because they scale eligibility rather than behaviour. For the cost channels the elasticity and the cost denominators trade off. The one placeholder with real weight is the missing-middle feasibility share (ρ ≈ +0.25). The page's *Try an assumption* panel offers every sampled parameter as a slider; moving one **pins** it at the chosen value in place of its range and re-runs the whole model in the browser (Pyodide runs the same Python as the CLI, on the same town table, with the same seed), so the band that comes back is the remaining uncertainty given that choice, and a pinned parameter drops out of the sensitivity table because it no longer varies. Statutory values and the handbook's benchmarks are not sliders. The validation panel shows the calibration and hindcast beside the results.

# Intended Users and Appropriate Use Cases

**Use it to** put a defensible range beside a proposed reform; to see which assumption a disagreement actually turns on (the sensitivity table names it); to compare reforms on one footing; and, in another state, to get a first Census-only estimate in a minute and see what a zoning layer or parsed ordinances would add.

**Do not use it to** site projects or rank neighbourhoods (it has no parcel precision by design); to forecast prices, rents or affordability; to claim a point estimate (every output is a range and the page refuses to show one without its band); or to assert the 2025 permit level will persist.

**How to read a number.** Every figure on the page carries a "why" link to the ledger entry or data file behind it, with its status. A number marked *placeholder* is a guess the authors are still replacing; a number marked *statutory* is law; *verified* means checked against observed data; *prior* means a justified range from the literature or another state's experience.

# Reproduce this document's numbers

```
scripts/setup.sh && scripts/run.sh        # or, step by step:
headroom acquire && headroom build --tier all && headroom run --tier all
headroom hindcast && headroom calibrate && headroom report && headroom check
```

Seed 20261216, 2,000 draws; `cache/manifest.json` records each file's URL, retrieval time and SHA-256; `headroom check` compares a run with the committed reference in `out/reference/`.
