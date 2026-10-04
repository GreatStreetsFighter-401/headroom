# Assumptions

Generated from `assumptions.yaml`. Status: **statutory** fixed by law or by the challenge handbook; **verified** read from a primary Rhode Island source; **prior** evidence from elsewhere adapted to Rhode Island; **placeholder** not yet collected, and said so; **design** a modelling choice.

## Baseline (current law, no new reform)

**Handbook definition.** Housing production under the current regulatory and economic environment, with no policy changes.

**Modelled as.** Per municipality, a blend of the 2018–2025 linear trend and the 2023–2025 mean of permitted units (Census BPS, with the State's 2025 municipal survey as a cross-check), with multiplicative noise, capped statewide by a construction-capacity ceiling. Current Rhode Island law is part of the baseline: § 45-24-73 ADUs by right on lots of 20,000 sq ft or more and within existing footprints (2024), and the one-space parking cap near transit in § 45-24-33(a)(28) (2026).

**Rhode Island law today.** R.I.G.L. § 45-24-73 (ADUs, as amended 2024); § 45-24-33(a)(28) (parking near transit, 2026-H 8005A); chapter 45-53 (comprehensive permits / 10 % low-moderate income housing).

**What it cannot tell policymakers.** Whether 2025's record permit year (3,778 units, the highest since the 1980s) is a new level or a peak; the band is wide for that reason and the trend weight is a parameter.

| Parameter | Default | Range | Status | Source |
|---|---|---|---|---|
| `baseline_trend_weight` — Weight on the linear trend versus the recent mean | 0.5 share (0 = recent three-year mean, 1 = 2018–2025 linear trend) | 0.0 – 1.0 (uniform) | design | Modelling choice; Census Building Permits Survey 2018–2025 by place. |
| `permit_undercount_adjustment` — Uncertainty on the Census-to-State permit scaling ratio | 1.0 multiplier on the computed 2025 ratio (State survey ÷ Census BPS) | 0.8 – 1.2 (triangular) | verified | EOH 2025 Integrated Housing Report, Fig. 2.1 (3,778 units permitted in 2025, municipal survey) and Fig. 2.2 note ("this data is used as it is more accurate than the Census survey"); Census BPS place file ne2025a.txt (1,738 units for the same 39 places). |
| `baseline_noise_cv` — Year-to-year noise in municipal permits (coefficient of variation) | 0.35 share of the expected value, on top of count (Poisson) noise | 0.15 – 0.6 (triangular) | verified | Residuals of each municipality's 2018–2025 Census BPS series around its linear trend; the median coefficient of variation across the 39 towns is 0.40 (computed at the 2026-10-04 build by `pipeline.noise_cv_from_history`). |
| `statewide_capacity_multiple` — Statewide ceiling on annual permits, as a multiple of the recent level (construction capacity) | 2.0 multiple of the state's mean annual permits over the last three years (at the scaled level) | 1.5 – 3.0 (triangular) | prior | Units permitted 1980–2025 (EOH 2025 Integrated Housing Report, Fig. 2.2: the record, ≈ 7,300 in 1986–87, is about 2.4 × the 2023–2025 mean at the State-survey level); BLS construction employment, Rhode Island. |

### `baseline_trend_weight`

**Why this value.** Rhode Island's 2025 permits (3,778) are the highest since the late 1980s after a decade near 1,000–1,500. A pure trend extrapolates the surge; a pure mean assumes it holds. Neither is knowable, so the blend is sampled uniformly and the band carries it.

**What it cannot say.** Whether the 2025 level persists.

### `permit_undercount_adjustment`

**Why this value.** The Census survey carries roughly half of Rhode Island's permits because many towns do not return its monthly form and the imputation does not recover them. Baseline levels are therefore the BPS series scaled by the 2025 ratio computed at build time (≈ 2.17); this parameter carries the uncertainty of applying one year's ratio to eight. In a state whose BPS is complete the ratio is 1.0 and this parameter does nothing.

**What it cannot say.** Whether the undercount is stable across years and towns; only 2025 can be compared.

### `baseline_noise_cv`

**Why this value.** Small towns permit 5–50 units a year and a single project moves a year by half. The model adds Poisson count noise to this level noise, so the parameter is set a little below the raw residual CV, which already contains the count component. The hindcast (`headroom hindcast`) reports how often observed 2024–2025 values fell inside the band.

### `statewide_capacity_multiple`

**Why this value.** Zoning creates room; builders fill it. A state's building industry can roughly double its recent output in a boom and no more within five years, which is what Rhode Island's own record shows. Expressed as a multiple so the same ceiling scales to any state; it is applied to the baseline and to every scenario total, so a stacked reform cannot exceed what the industry has ever delivered.

## Accessory dwelling units

**Handbook definition.** Allow one ADU on parcels with existing single-family buildings. Assume detached and semi-detached ADUs of at least 600 square feet are allowed, and no additional parking is required.

**Modelled as.** Stage 1 counts existing single-family structures (E-911 R1 points) in residential districts by municipality, split by whether the district's minimum lot size is 20,000 sq ft or more (by-right detached ADU under current law) and by sewer service. The scenario extends detached by-right eligibility to every single-family lot. Stage 2 applies an annual uptake rate to newly eligible lots, ramping over a few years, with a septic multiplier. Reported as the increment over current law.

**Rhode Island law today.** § 45-24-73 already allows one ADU by right on lots ≥ 20,000 sq ft, within an existing footprint on any lot, and for a family member with a disability; towns may cap size at 800 sq ft (from 2025-07-01); at most one parking space per bedroom; no short-term rental. Rhode Island therefore already has part of this scenario in force, and the State publishes ADU permits by municipality for 2024–2025.

**What it cannot tell policymakers.** How many ADUs are rented versus occupied by family; whether towns' 800 sq ft caps bind; effects on rents.

| Parameter | Default | Range | Status | Source |
|---|---|---|---|---|
| `adu_by_right_lot_sf` — Lot size at which a detached ADU is by right under current law | 20000.0 square feet | fixed | statutory | R.I.G.L. § 45-24-73 (as amended by 2024 acts, effective 2024-06-25). |
| `adu_uptake_detached_annual` — Annual uptake of a detached or semi-detached ADU on newly eligible lots | 0.002 share of eligible single-family lots per year, at steady state | 0.0005 – 0.006 (lognormal) | prior | HousingWorks RI 2025 Housing Fact Book (Rhode Island ADU permits 11 in 2021, 163 in 2024); California HCD Annual Progress Report dashboard (statewide ADU permits 1,269 in 2016, 14,702 in 2019, ~23,000 in 2023 against roughly 7–8 million single-family homes, i.e. ≈ 0.3 %/yr of all single-family homes by 2023 after six years of ramp). |
| `adu_uptake_conversion_annual` — Annual uptake of a within-footprint ADU (already by right on any lot) | 0.0008 share of single-family lots per year | 0.0002 – 0.0025 (lognormal) | prior | Same as adu_uptake_detached_annual; conversions are a minority of California ADUs. |
| `adu_ramp_years` — Years for ADU uptake to reach its steady-state rate | 3.0 years | 1.0 – 5.0 (triangular) | prior | California statewide series 2016–2023 (HCD); Rhode Island 2021–2024. |
| `adu_septic_multiplier` — Uptake multiplier for lots without sewer service | 0.5 multiplier on uptake | 0.2 – 0.8 (triangular) | prior | RIGIS Sewered Areas; RIDEM OWTS rules (a second unit needs septic capacity). |
| `tierc_lot20k_share` — Share of single-family lots of 20,000 sq ft or more (used only without a zoning layer) | 0.35 share | 0.2 – 0.5 (triangular) | prior | Rhode Island State zoning layer (computed at tier B; 2026-10-04 build). |
| `tierc_sewered_share` — Share of single-family structures with sewer service (used only without GIS) | 0.55 share | 0.35 – 0.75 (triangular) | prior | Rhode Island State layers (computed at tier B; 2026-10-04 build). |

### `adu_by_right_lot_sf`

**Why this value.** Fixed by statute; used to split current-law from scenario eligibility.

### `adu_uptake_detached_annual`

**Why this value.** Set so that the model's own current-law eligibility (detached by right on the ~40 % of single-family structures in districts with 20,000 sq ft minimum lots, conversions by right everywhere, septic lots discounted) reproduces Rhode Island's observed 163 ADU permits in 2024 between ramp year one and ramp year two — 2024 was the first full year of the expanded statute but the second since the 2022 one. At steady state 0.2 %/yr of eligible lots is below California's 2023 rate.

**Rhode Island calibration.** `headroom calibrate` prints the 2024 permits the defaults imply at ramp year one and two against the observed 163. The EOH annual ADU report (2024–2025 by municipality) is the next anchor and will let the rate vary by town.

**What it cannot say.** Who builds them; the split between rental and family occupancy.

### `adu_uptake_conversion_annual`

**Why this value.** Conversions are by right everywhere in Rhode Island today, so they are part of the baseline and this parameter only matters for the calibration check, not the increment.

### `adu_ramp_years`

**Why this value.** Both series roughly doubled annually for the first three years after by-right rules arrived, then grew more slowly. Uptake is scaled linearly from 1/ramp in year one.

### `adu_septic_multiplier`

**Why this value.** An unsewered lot needs an onsite system sized for the added bedrooms, which is often the binding cost in Rhode Island's rural towns. The multiplier is applied to the share of eligible lots outside sewered areas, computed from the State layer.

### `tierc_lot20k_share`

**Why this value.** At tier C there is no lot-size information. The default is the tier-B value for Rhode Island, which another state can replace with its own.

### `tierc_sewered_share`

**Why this value.** At tier C the default is Rhode Island's tier-B value; another state substitutes its own.

## Missing middle / gentle density

**Handbook definition.** Allow 2–6 dwelling units on parcels currently restricted to single-family use, with building heights up to three stories; assume setback and lot coverage requirements do not constrain development.

**Modelled as.** Stage 1 counts single-family structures in districts that permit only single-family use — read from the ordinance (tier A) or the State layer's district text (tier B), or from a statewide share (tier C). Stage 2 applies an annual conversion rate, a units-per- conversion count (net of the unit replaced), a market-feasibility share and a septic multiplier.

**Rhode Island law today.** No state preemption of single-family zoning; two-family use is a local decision in all 39 municipalities.

**What it cannot tell policymakers.** Which lots convert first, or whether conversions displace existing residents; the Minneapolis and Portland evidence shows 2–3-unit conversions are rare and 4+-unit buildings on upzoned land do most of the work.

| Parameter | Default | Range | Status | Source |
|---|---|---|---|---|
| `mm_conversion_rate_annual` — Annual conversion of single-family-only lots to 2–6 unit buildings | 0.0005 share of eligible single-family lots per year, at steady state | 0.0001 – 0.002 (lognormal) | prior | Portland Residential Infill Project monitoring (514 middle-housing units in RIP year one, Aug 2022–Jul 2023, across ~150,000 single-dwelling lots); Minneapolis 2040 outcomes (a few dozen 2–3-unit buildings 2020–2023; ~1,000 units in 4+-unit buildings on formerly restrictive land). |
| `mm_units_per_conversion` — Units in a converted or replaced building | 3.0 dwelling units (one is netted off for the house replaced) | 2.0 – 6.0 (triangular) | statutory | Challenge handbook scenario definition (2–6 units). |
| `mm_feasibility_share` — Share of eligible lots where redevelopment is economically plausible within five years | 0.5 share | 0.25 – 0.8 (triangular) | placeholder | To be set from assessor land-to-improvement value ratios (municipal GIS) and FHFA HPI. |
| `mm_septic_multiplier` — Conversion multiplier for lots without sewer service | 0.3 multiplier on conversion rate | 0.1 – 0.6 (triangular) | prior | RIGIS Sewered Areas; RIDEM OWTS rules. |
| `mm_ramp_years` — Years for conversion activity to reach its steady-state rate | 3.0 years | 1.0 – 5.0 (triangular) | prior | Portland RIP and Minneapolis 2040 monitoring reports. |
| `tierc_sf_only_share` — Share of single-family structures in districts that permit only single-family use | 0.85 share | 0.6 – 0.95 (triangular) | prior | Rhode Island Zoning Atlas (HousingWorks RI, 2023): 87 % of the state's land is zoned single-family by right, 8 % allows four or more units by right. |
| `tierc_sewered_share` — Share of single-family structures with sewer service (used only without GIS) | 0.55 share | 0.35 – 0.75 (triangular) | prior | Rhode Island State layers (computed at tier B; 2026-10-04 build). |

### `mm_conversion_rate_annual`

**Why this value.** Portland's first year is ≈ 0.13 % of lots if a project averages 2.5 units; Minneapolis is an order of magnitude lower for small buildings. The default is between them and the range covers both.

**What it cannot say.** Whether Rhode Island towns would also see the 4+-unit response Minneapolis did; that is outside the 2–6 unit definition.

### `mm_units_per_conversion`

**Why this value.** Most middle-housing projects in Portland and Minneapolis are 2–4 units; 6 is the handbook ceiling.

### `mm_feasibility_share`

**Why this value.** A conversion needs land worth more than the house on it. Until assessor data is joined this is an explicit guess with a wide range, and the sensitivity chart shows its weight.

### `mm_septic_multiplier`

**Why this value.** Three to six units on septic is rarely approvable in Rhode Island; the multiplier reflects that.

### `mm_ramp_years`

**Why this value.** Builders, lenders and designers take a few years to adopt a new product type.

### `tierc_sf_only_share`

**Why this value.** Used at tier C (no zoning layer) and, at tier B, for districts whose description text says nothing about allowed uses. Replaced by the ordinance reading at tier A.

### `tierc_sewered_share`

**Why this value.** At tier C the default is Rhode Island's tier-B value; another state substitutes its own.

## Parking requirement reduction

**Handbook definition.** Reduce or eliminate minimum parking requirements for new residential development, specifying assumptions about developer-provided parking absent mandates.

**Modelled as.** A cost channel: the per-unit cost of mandated spaces developers would not otherwise build, divided by all-in cost per unit, times a supply-cost elasticity, applied to the baseline's multifamily (2+ unit) permits. Inside transit buffers current law already caps the mandate at one space, so the increment there is smaller.

**Rhode Island law today.** § 45-24-33(a)(28) (2026): no more than one space per multifamily unit within ¼ mile of a regional mobility hub or ⅛ mile of a frequent transit stop. Elsewhere, local minimums apply.

**What it cannot tell policymakers.** Where the saved parking goes (rent, land, more units) — the elasticity bundles those.

| Parameter | Default | Range | Status | Source |
|---|---|---|---|---|
| `parking_required_mf_baseline` — Mandated off-street spaces per multifamily unit under local ordinances | 1.5 spaces per unit | 1.0 – 2.0 (triangular) | placeholder | To be read from the 39 zoning ordinances (parking schedules); MuniAnchor table classifier already locates them. |
| `parking_provided_unmandated` — Spaces per multifamily unit developers provide without a mandate | 0.8 spaces per unit | 0.4 – 1.2 (triangular) | prior | Seattle (after reform, new housing near transit included 40 % less parking than previously required); Buffalo (68 % of post-reform units in buildings that would not have met the old requirement); Minneapolis/St Paul reporting. |
| `mf_permit_share_in_tod_buffers` — Share of baseline multifamily permits located inside the transit buffers | 0.3 share | 0.1 – 0.6 (triangular) | placeholder | To be computed by geocoding 2025 permit addresses against the transit buffers. |
| `parking_cost_per_space` — Construction cost of one off-street parking space | 20000.0 USD per space | 8000.0 – 45000.0 (triangular) | prior | Surface spaces $5,000–15,000; structured $25,000–50,000 (industry cost surveys and the Seattle estimate of $537 million saved on 40 % less parking). |
| `dev_cost_per_unit_mf` — All-in development cost per multifamily unit | 400000.0 USD per unit | 300000.0 – 550000.0 (triangular) | prior | RIHousing-financed developments 2023–2025 (public awards); market multifamily pro formas. |
| `supply_cost_elasticity` — Elasticity of new units with respect to per-unit development cost | 0.8 percent change in permits per one percent fall in cost | 0.3 – 1.5 (lognormal) | prior | Baum-Snow & Duranton (2025): tract-level unit-supply elasticity to price ≈ 0.5 across 306 metros; Saiz (2010) metro elasticities; cost-side responses are typically of the same order over a five-year horizon. |
| `tod_frequent_peak_departures_per_hour` — Peak-hour departures that make a stop a "frequent transit stop" | 4.0 scheduled departures per hour, 7–9 am weekday | 2.0 – 6.0 (triangular) | prior | 2020 Rhode Island Transit Master Plan (frequent service network at 15-minute headways), referenced by § 45-24-33(a)(28); RIPTA GTFS feed. |
| `tod_hub_min_routes` — Distinct routes serving a stop for it to count as a regional mobility hub (fallback only) | 6.0 routes | 4.0 – 10.0 (triangular) | design | Used only where no named hub list exists. For Rhode Island the eight regional mobility hubs named by Transit Forward RI 2040 (the 2020 Transit Master Plan § 45-24-33(a)(28) refers to) are encoded in data/ri_mobility_hubs.csv — Kennedy Plaza, Providence Station, Jewelry District, Pawtucket Downtown, Woonsocket Downtown, Warwick/CCRI, Newport Gateway Center, Wickford Junction — with coordinates from RIPTA's GTFS stops. |

### `parking_required_mf_baseline`

**Why this value.** Rhode Island suburbs typically require 2 per unit, cities 1–1.5; the hand-coded table replaces this.

### `parking_provided_unmandated`

**Why this value.** Developers still build parking where buyers want it; the mandate's cost is only the excess.

### `mf_permit_share_in_tod_buffers`

**Why this value.** Inside the buffers current law already caps the mandate at one space, so the parking scenario's increment there is smaller; this share splits the baseline accordingly.

### `parking_cost_per_space`

**Why this value.** Rhode Island multifamily is mostly surface or podium parking; the triangular mode sits low.

### `dev_cost_per_unit_mf`

**Why this value.** Sets the denominator that turns a dollar saving into a percentage cost change.

### `supply_cost_elasticity`

**Why this value.** A cost reduction works like a price increase on the developer's margin. The default is near the middle of the cross-metro range; New England is on the inelastic side, which the low end covers.

**What it cannot say.** How the saving is split between rents, land prices and more units.

### `tod_frequent_peak_departures_per_hour`

**Why this value.** Four an hour is a 15-minute headway; the range covers 10- to 30-minute service.

### `tod_hub_min_routes`

**Why this value.** A route-count proxy finds downtown Providence and Pawtucket and little else; the named list is what the statute points at. Another state without a hub list gets the proxy and this range.

## Development fee reduction

**Handbook definition.** Reduce total development fees (planning, environmental review, building, impact) by 50 %, assuming baseline fees of $50,000 per unit across all major fee categories.

**Modelled as.** The same cost channel as parking: the fee reduction divided by all-in cost per unit, times the supply-cost elasticity, applied to all baseline permits. Run twice — at the handbook's $50,000 benchmark, and at Rhode Island's actual per-unit fees, which are far lower.

**Rhode Island law today.** Impact fees are enabled by chapter 45-22.4 but adopted by few municipalities; building permit fees are typically set per $1,000 of construction value.

**What it cannot tell policymakers.** Anything about fee *levels* in other states; the Rhode Island actual is a placeholder until the 39 fee schedules are collected.

| Parameter | Default | Range | Status | Source |
|---|---|---|---|---|
| `dev_cost_per_unit_mf` — All-in development cost per multifamily unit | 400000.0 USD per unit | 300000.0 – 550000.0 (triangular) | prior | RIHousing-financed developments 2023–2025 (public awards); market multifamily pro formas. |
| `dev_cost_per_unit_sf` — All-in development cost per single-family unit | 450000.0 USD per unit | 350000.0 – 650000.0 (triangular) | prior | Census BPS average permit valuation for Rhode Island 1-unit buildings (2024–2025) plus land. |
| `supply_cost_elasticity` — Elasticity of new units with respect to per-unit development cost | 0.8 percent change in permits per one percent fall in cost | 0.3 – 1.5 (lognormal) | prior | Baum-Snow & Duranton (2025): tract-level unit-supply elasticity to price ≈ 0.5 across 306 metros; Saiz (2010) metro elasticities; cost-side responses are typically of the same order over a five-year horizon. |
| `fee_per_unit_handbook` — Baseline total development fee per unit (challenge benchmark) | 50000.0 USD per unit | fixed | statutory | Challenge handbook scenario 5. |
| `fee_reduction_share` — Fee reduction under the scenario | 0.5 share of fees removed | fixed | statutory | Challenge handbook scenario 5. |
| `fee_per_unit_ri` — Rhode Island actual total development fee per unit | 8000.0 USD per unit | 4000.0 – 15000.0 (triangular) | placeholder | To be collected from the 39 municipal fee schedules (building permit fees per $1,000 of value; impact fees under chapter 45-22.4 where adopted). |

### `dev_cost_per_unit_mf`

**Why this value.** Sets the denominator that turns a dollar saving into a percentage cost change.

### `dev_cost_per_unit_sf`

**Why this value.** Same role as dev_cost_per_unit_mf for the single-family share of baseline permits.

### `supply_cost_elasticity`

**Why this value.** A cost reduction works like a price increase on the developer's margin. The default is near the middle of the cross-metro range; New England is on the inelastic side, which the low end covers.

**What it cannot say.** How the saving is split between rents, land prices and more units.

### `fee_per_unit_handbook`

**Why this value.** Fixed by the handbook so entries are comparable across states.

### `fee_reduction_share`

**Why this value.** Fixed by the handbook.

### `fee_per_unit_ri`

**Why this value.** Rhode Island towns charge building fees of roughly $10–15 per $1,000 of construction value and few levy impact fees, so the per-unit total is a fraction of the handbook's $50,000. The scenario is run at both numbers so the difference is visible.

## Transit-oriented density

**Handbook definition.** Increase allowable residential density near major transit stops through higher heights and/or floor area ratios, with reduced or eliminated parking requirements; teams define and justify the proximity threshold.

**Modelled as.** Stage 1 buffers RIPTA stops: ⅛ mile around frequent stops and ¼ mile around hub stops, the two statutory distances. Net capacity is residential land inside the buffers times (scenario density − current density implied by minimum lot size). Stage 2 applies an annual realisation rate with a ramp. The parking channel is already in current law inside these buffers.

**Rhode Island law today.** Distances fixed by § 45-24-33(a)(28); "frequent transit stop" and "regional mobility hub" are defined by the 2020 Rhode Island Transit Master Plan, applied here through two parameters.

**What it cannot tell policymakers.** Site assembly, infrastructure limits and design review inside the buffers; these are bundled into the realisation rate.

| Parameter | Default | Range | Status | Source |
|---|---|---|---|---|
| `parking_provided_unmandated` — Spaces per multifamily unit developers provide without a mandate | 0.8 spaces per unit | 0.4 – 1.2 (triangular) | prior | Seattle (after reform, new housing near transit included 40 % less parking than previously required); Buffalo (68 % of post-reform units in buildings that would not have met the old requirement); Minneapolis/St Paul reporting. |
| `parking_cost_per_space` — Construction cost of one off-street parking space | 20000.0 USD per space | 8000.0 – 45000.0 (triangular) | prior | Surface spaces $5,000–15,000; structured $25,000–50,000 (industry cost surveys and the Seattle estimate of $537 million saved on 40 % less parking). |
| `dev_cost_per_unit_mf` — All-in development cost per multifamily unit | 400000.0 USD per unit | 300000.0 – 550000.0 (triangular) | prior | RIHousing-financed developments 2023–2025 (public awards); market multifamily pro formas. |
| `tod_frequent_peak_departures_per_hour` — Peak-hour departures that make a stop a "frequent transit stop" | 4.0 scheduled departures per hour, 7–9 am weekday | 2.0 – 6.0 (triangular) | prior | 2020 Rhode Island Transit Master Plan (frequent service network at 15-minute headways), referenced by § 45-24-33(a)(28); RIPTA GTFS feed. |
| `tod_hub_min_routes` — Distinct routes serving a stop for it to count as a regional mobility hub (fallback only) | 6.0 routes | 4.0 – 10.0 (triangular) | design | Used only where no named hub list exists. For Rhode Island the eight regional mobility hubs named by Transit Forward RI 2040 (the 2020 Transit Master Plan § 45-24-33(a)(28) refers to) are encoded in data/ri_mobility_hubs.csv — Kennedy Plaza, Providence Station, Jewelry District, Pawtucket Downtown, Woonsocket Downtown, Warwick/CCRI, Newport Gateway Center, Wickford Junction — with coordinates from RIPTA's GTFS stops. |
| `tod_scenario_density_upa` — Residential density allowed inside the buffers under the scenario | 20.0 dwelling units per acre | 12.0 – 40.0 (triangular) | design | Challenge handbook scenario 3 (teams define); comparable TOD overlays (MBTA Communities 15 units/acre minimum). |
| `tod_realization_rate_annual` — Share of net new capacity inside the buffers built per year | 0.004 share of net capacity per year, at steady state | 0.001 – 0.012 (lognormal) | prior | Build-out rates of TOD overlays and upzonings (Seattle station areas, MBTA Communities early filings, Minneapolis 2040). |
| `tod_ramp_years` — Years for TOD development to reach its steady-state rate | 3.0 years | 1.0 – 5.0 (triangular) | prior | Same as tod_realization_rate_annual. |

### `parking_provided_unmandated`

**Why this value.** Developers still build parking where buyers want it; the mandate's cost is only the excess.

### `parking_cost_per_space`

**Why this value.** Rhode Island multifamily is mostly surface or podium parking; the triangular mode sits low.

### `dev_cost_per_unit_mf`

**Why this value.** Sets the denominator that turns a dollar saving into a percentage cost change.

### `tod_frequent_peak_departures_per_hour`

**Why this value.** Four an hour is a 15-minute headway; the range covers 10- to 30-minute service.

### `tod_hub_min_routes`

**Why this value.** A route-count proxy finds downtown Providence and Pawtucket and little else; the named list is what the statute points at. Another state without a hub list gets the proxy and this range.

### `tod_scenario_density_upa`

**Why this value.** Twenty units an acre is three-story walk-up density; forty is mid-rise.

### `tod_realization_rate_annual`

**Why this value.** Upzoned land near transit builds out over decades; a few tenths of a percent a year is the observed order.

### `tod_ramp_years`

**Why this value.** Entitlement and design take two to three years before permits follow.


---
_Generated 2026-10-04T20:44+00:00 by `headroom report`._
