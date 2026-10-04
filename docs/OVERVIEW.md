# Headroom — Model and Assumptions Overview

*Draft v0.1, 2026-10-04. The generated chapters in `docs/generated/` (assumptions, data,
results, tiers) are produced by `headroom report` from the ledger and the run outputs and
are the authoritative tables; this document is the prose around them. Page budget: 25.*

## 1. Purpose and the question answered

Headroom estimates, for a state, how many more homes are likely to be **permitted over the
next five years** if a state-level pro-housing reform is enacted, as a **range** rather than
a point, with every number traceable to a public dataset, a statute section or a named
assumption. It is built for policy staff who have to put a number beside a bill and defend
where it came from.

The showcase state is Rhode Island: 39 municipalities, every one a permit-issuing place; a
statewide digital zoning layer published for the first time in 2025; and a legislature that
has already enacted parts of three of the five benchmark scenarios, which makes them
measurable rather than hypothetical.

## 2. Metric

**Permitted housing units** — new privately owned residential units authorised by building
permit — over 2027–2031. Why: it is the metric Rhode Island's statutory Integrated Housing
Report and the Housing 2030 goal (15,000 permits, 2026–2030) use; it is the only production
metric the State publishes by municipality for every year since 2018; and the Census Building
Permits Survey publishes it for every permit-issuing place in the country, which is what lets
the same code run in another state. Completions (certificates of occupancy) are shown where
the State has them (2025 only) and are not forecast.

One finding about the metric itself matters for anyone modelling Rhode Island: the Census
survey carries roughly **half** of the State's own count (1,738 versus 3,778 units in 2025),
because many towns do not return the Census form and the imputation does not recover them.
The State says its survey "is more accurate than the Census survey". Headroom uses the Census
series for its shape (2018–2025, every town) and scales its level to the State survey, with
the scaling's uncertainty as a ledger parameter (`permit_undercount_adjustment`). In a state
whose Census series is complete the ratio is 1.0 and the parameter does nothing.

## 3. Method

Two stages, kept apart so a reader can see which numbers are *law and land* and which are
*behaviour*:

```
permits(scenario, town, year) = baseline(town, year)
                              + Σ  eligible_capacity(channel, town)    ← Stage 1: data, no judgment
                                   × uptake(channel, year)             ← Stage 2: ledger parameter
                                   × feasibility(channel, town)        ← Stage 2: ledger parameter
```

**Stage 1 — regulatory capacity.** Computed from public data by a spatial join with no
judgment: the State's 15,733 zoning polygons (district code, generalised class, minimum lot
size), the State's E-911 structure layer (one typed point per building: 264,799 single-family
homes, 87,412 multi-family), sewer service areas, and RIPTA's schedule. Where an ordinance has
been parsed (tier A) the allowed residential uses by district are read from the adopted
zoning text; otherwise from the district's description in the State layer (tier B); otherwise
from Census structure counts and a statewide share (tier C).

**Stage 2 — uptake and feasibility.** Every behavioural, cost and feasibility parameter is a
record in `assumptions.yaml` with a default, a range, a sampling distribution, a status
(statutory / verified / prior / placeholder / design), a source and a justification. The
Monte Carlo (2,000 draws, fixed seed) samples the ledger once per draw. A unit test fails if a
numeric literal that could be a behavioural assumption appears in the model code.

**Output.** P10 / P50 / P90 of permitted units per scenario, per municipality and statewide,
per year and over five years, plus a sensitivity table — the rank correlation of every
parameter with the five-year statewide increment — for each scenario.

## 4. Scenarios

Baseline plus the five handbook benchmarks. Each is modelled as an **increment over current
law**, which in Rhode Island already includes by-right ADUs on lots of 20,000 sq ft or more
and within existing footprints (R.I.G.L. § 45-24-73, 2024) and a one-space parking cap for
multifamily within ¼ mile of a regional mobility hub or ⅛ mile of a frequent transit stop
(§ 45-24-33(a)(28), 2026-H 8005A, effective June 2026). The handbook definitions, how each is
modelled, the Rhode Island law in force, and what each cannot tell a policymaker are in
`docs/generated/assumptions.md`, generated from the ledger.

## 5. Baseline and its validation

Per municipality: a blend of the 2018–2025 linear trend and the 2023–2025 mean (the blend
weight is sampled uniformly, because 2025 was the highest permit year since the late 1980s
and whether it is a level or a peak is not knowable), times level noise plus Poisson count
noise. A statewide construction-capacity ceiling — a multiple of the state's own recent
annual permits, default 2×, because Rhode Island's record year (≈ 7,300 in 1986–87) was
about 2.4× today's level — applies to the baseline and to every scenario total, so a stacked
reform cannot exceed what the industry has ever delivered. Being a multiple, the same
ceiling scales to any state.

**Hindcast.** The baseline is the only component with a time series to test against, so it
is tested out of sample: fit on 2018–2023, predict 2024–2025, score against what happened.
Result (Census level, 78 town-years):

| Statistic | Value |
|---|---|
| Mean absolute error of the P50, per town-year | 26.9 units |
| Statewide error of the P50 | −30.9 % |
| Observed values inside the P10–P90 band | 60 % |

Read plainly: a trend fitted through 2023 **misses the 2024–2025 surge**, and the bands
cover six town-years in ten rather than eight. The forecast uses the series through 2025 and
so carries the surge, but the hindcast is the reason the overview says the baseline band is
conditional on no further regime change, and why the trend weight is a sampled parameter
rather than a choice.

## 6. Calibration — the ADU scenario against Rhode Island's own record

Rhode Island permitted 11 ADUs in 2021 and 163 in 2024 (HousingWorks RI 2025 Housing Fact
Book). Under current law the model's own eligibility is ~64,000 single-family lots for a
detached ADU by right (sewer-adjusted) and ~215,000 for a within-footprint conversion. With
the default uptake rates the model implies 100 ADU permits in 2024 if 2024 is ramp year one
and 200 if it is year two; the observed 163 lies between. `headroom calibrate` prints this
check. The State's annual ADU report (2024–2025 by municipality) is the next anchor and will
let the rate vary by town.

## 7. Results (tier B, Rhode Island, 2027–2031)

| Scenario | Five-year increment over baseline, P10 / P50 / P90 |
|---|---|
| Baseline (level) | 16,189 / 18,607 / 21,434 |
| Accessory dwelling units | +432 / +1,162 / +3,173 |
| Missing middle (2–6 units) | +97 / +357 / +1,260 |
| Parking minimums reduced | +69 / +201 / +499 |
| Fees −50 % at the handbook's $50,000 | +426 / +820 / +1,493 |
| Fees −50 % at Rhode Island's actual fees | +70 / +142 / +280 |
| Transit-oriented density | +127 / +372 / +1,047 |
| All five together (fees at RI level; upper bound) | +1,549 / +2,708 / +4,644 |

Against the Housing 2030 goal of 15,000 permits over 2026–2030, the baseline median already
clears it; the reforms add between a few hundred and a few thousand units each over five
years, with ADUs the largest single channel, and all five together about 15 % on top of the
baseline (an upper bound: increments are added and only the capacity ceiling limits the sum).
Full tables, by year and by municipality, are in `docs/generated/results_tierB.md`; the three
tiers side by side in `docs/generated/tiers.md`.

## 8. Sensitivity

For each scenario the generated results chapter lists every sampled parameter's Spearman
correlation with the five-year increment and the median increment in the parameter's bottom
and top quintiles. The pattern is the same in every scenario: the **uptake or conversion
rate** dominates (ρ ≈ +0.9 to +0.99); the ramp length is the next largest and negative; the
structural shares (sewer, single-family-only) matter little because they scale eligibility,
not behaviour. For the cost channels the elasticity and the cost denominators trade off. The
one **placeholder** with weight is `mm_feasibility_share` (ρ ≈ +0.25), which is why the plan
collects assessor land-value ratios before the deadline.

## 9. What the tool cannot tell policymakers

* Where within a town the units land, or which lots convert first.
* Prices, rents, or who occupies the new units; the affordability tier of what is built.
* Whether 2025's record year persists; the baseline band is conditional on no further regime
  change (section 5).
* Anything about towns whose ordinance did not parse beyond what the State layer says — at
  tier B, 59 % of single-family structures in residential districts sit in districts whose
  description text says nothing about allowed uses, and the statewide share applies there.
* Effects of state funding (the housing bond), interest rates or construction labour beyond
  the statewide capacity ceiling.
* Interactions between scenarios beyond the shared cost channel; the "all five together"
  line adds the increments and caps the total, nothing more.
* Which transit stops are "frequent" beyond the schedule: four peak departures an hour is
  the Transit Master Plan's 15-minute standard applied to RIPTA's published timetable, not
  a ridership measure. The eight regional mobility hubs are the plan's own list
  (`data/ri_mobility_hubs.csv`), located at their RIPTA stops.

## 10. Replicability

* **Tiers.** The same model runs at three input tiers; tier C needs only the Census permit
  survey and ACS structure counts, which every state has, and both are read from Census
  files that need no API key (the Building Permits Survey place files and the ACS table-based
  summary files, streamed and filtered to the state). The tier comparison chapter shows what
  the State layer and the ordinance reading buy — for Rhode Island, tier C's ADU and
  missing-middle ranges are within a few percent of tier B's (because the tier-C shares were
  set from tier B), and tier C cannot run the transit scenario at all.
* **Two more states, run.** `headroom build --state MA && headroom run --state MA` (and CT)
  produce tier-C results from federal data alone, in under a minute each, with no state-
  specific code: Massachusetts (351 county subdivisions, 347 with a permit series) baseline
  61,412 / 69,513 / 77,902 permits over 2027–2031, ADU +2,469 / +6,687 / +17,526; Connecticut
  (169) baseline 31,474 / 36,412 / 41,951, ADU +1,433 / +3,881 / +10,135. Two caveats are
  printed with them: the permit level is the Census series as published (Rhode Island's
  undercounts by half and theirs may too), and the eligibility shares are Rhode Island's
  tier-B values until replaced with the state's own.
* **A cross-check that costs nothing.** The State report's ACS tables (units by structure
  type, all 39 towns) are compared with the Census summary file at build time; they agree
  town for town, which is recorded in `out/build/towns_tierB.json` and the data chapter.
* **Reproducibility check.** `headroom check` compares a run's statewide results with the
  committed reference in `out/reference/`; the workflow in `.github/workflows/reproduce.yml`
  re-acquires every source weekly and fails on drift, so a republished source or a changed
  answer is visible.
* **Another state.** Fill `data/district_params_<state>.csv` (schema in `schema/`) for tier
  A, point `acquire/arcgis.py` at the state's zoning service for tier B, or run tier C as is.

## 11. Reproduce this document's numbers

```
headroom acquire && headroom build --tier all && headroom run --tier all
headroom hindcast && headroom calibrate && headroom report && headroom check
```

Seed 20261216, 2,000 draws; the manifest in `cache/manifest.json` records each file's URL,
retrieval time and SHA-256.

## 12. Disclosures

Code and documentation were drafted with Claude (Anthropic) under the author's direction;
every data value, statute reading and modelling choice was verified against the primary
source named beside it. No pretrained model or hosted inference is used at run time. The
software bill of materials is `sbom.json` (CycloneDX 1.6). Licence: Apache-2.0.
