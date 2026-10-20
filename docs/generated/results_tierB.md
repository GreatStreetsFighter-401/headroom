# Results — tier B

Metric: permitted housing units (new privately owned residential units authorised by building permit). 2,000 draws, seed 20261216. Horizon 2027–2031. Values are permitted units over the five years, as P10 / P50 / P90.

| Scenario | 5-year increment over baseline (P10 / P50 / P90) | Mean |
|---|---|---|
| Baseline (level, not increment) | 16,189 / 18,607 / 21,434 | 18,719 |
| Accessory dwelling units | +432 / +1,162 / +3,173 | +1,473 |
| Missing middle (2–6 units on single-family lots) | +97 / +357 / +1,260 | +548 |
| Parking requirement reduction | +69 / +201 / +499 | +250 |
| Fee reduction (handbook $50,000 baseline) | +426 / +820 / +1,493 | +895 |
| Fee reduction (Rhode Island actual fees) | +70 / +142 / +280 | +162 |
| Transit-oriented density | +127 / +372 / +1,047 | +493 |
| All five together (fees at RI level; upper bound, capped) | +1,549 / +2,708 / +4,644 | +2,921 |

## By year (P50, statewide)

| Scenario | 2027 | 2028 | 2029 | 2030 | 2031 |
|---|---|---|---|---|---|
| Baseline | 3,524 | 3,625 | 3,691 | 3,769 | 3,884 |
| Accessory dwelling units | +104 | +203 | +271 | +293 | +297 |
| Missing middle (2–6 units on single-family lots) | +32 | +61 | +82 | +91 | +92 |
| Parking requirement reduction | +37 | +38 | +40 | +41 | +43 |
| Fee reduction (handbook $50,000 baseline) | +158 | +161 | +163 | +166 | +173 |
| Fee reduction (Rhode Island actual fees) | +27 | +28 | +28 | +29 | +30 |
| Transit-oriented density | +33 | +64 | +86 | +94 | +95 |
| All five together (fees at RI level; upper bound, capped) | +281 | +477 | +609 | +660 | +669 |

## Sensitivity

Spearman rank correlation between each sampled parameter and the scenario's five-year statewide increment across draws, with the median increment in the parameter's bottom and top quintiles.

### Accessory dwelling units

| Parameter | ρ | P50 at low quintile | P50 at high quintile | Status |
|---|---|---|---|---|
| `adu_uptake_detached_annual` | +0.99 | +432 | +3,173 | prior |
| `adu_ramp_years` | -0.16 | +1,348 | +892 | prior |
| `tierc_sewered_share` | -0.05 | +1,168 | +1,106 | prior |
| `baseline_trend_weight` | -0.04 | +1,184 | +1,142 | design |
| `adu_uptake_conversion_annual` | +0.03 | +1,120 | +1,249 | prior |
| `baseline_noise_cv` | -0.02 | +1,139 | +1,150 | verified |
| `permit_undercount_adjustment` | +0.01 | +1,208 | +1,158 | verified |
| `adu_septic_multiplier` | -0.01 | +1,242 | +1,202 | prior |
| `tierc_lot20k_share` | +0.01 | +1,170 | +1,181 | prior |
| `statewide_capacity_multiple` | -0.00 | +1,157 | +1,140 | prior |

### Missing middle (2–6 units on single-family lots)

| Parameter | ρ | P50 at low quintile | P50 at high quintile | Status |
|---|---|---|---|---|
| `mm_conversion_rate_annual` | +0.90 | +104 | +1,194 | prior |
| `mm_units_per_conversion` | +0.35 | +222 | +574 | statutory |
| `mm_feasibility_share` | +0.25 | +239 | +520 | placeholder |
| `mm_ramp_years` | -0.11 | +434 | +278 | prior |
| `mm_septic_multiplier` | +0.06 | +311 | +360 | prior |
| `baseline_trend_weight` | -0.04 | +366 | +346 | design |
| `tierc_sf_only_share` | +0.03 | +331 | +418 | prior |
| `tierc_sewered_share` | -0.01 | +363 | +357 | prior |
| `baseline_noise_cv` | +0.01 | +348 | +389 | verified |
| `permit_undercount_adjustment` | -0.00 | +365 | +357 | verified |
| `statewide_capacity_multiple` | -0.00 | +340 | +378 | prior |

### Parking requirement reduction

| Parameter | ρ | P50 at low quintile | P50 at high quintile | Status |
|---|---|---|---|---|
| `supply_cost_elasticity` | +0.59 | +112 | +393 | prior |
| `parking_provided_unmandated` | -0.44 | +283 | +108 | prior |
| `parking_cost_per_space` | +0.41 | +127 | +311 | prior |
| `parking_required_mf_baseline` | +0.36 | +128 | +283 | placeholder |
| `dev_cost_per_unit_mf` | -0.18 | +242 | +173 | prior |
| `baseline_trend_weight` | +0.16 | +170 | +250 | design |
| `mf_permit_share_in_tod_buffers` | -0.10 | +227 | +183 | placeholder |
| `permit_undercount_adjustment` | +0.10 | +181 | +225 | verified |
| `baseline_noise_cv` | -0.02 | +217 | +201 | verified |
| `statewide_capacity_multiple` | -0.01 | +204 | +204 | prior |

### Fee reduction (handbook $50,000 baseline)

| Parameter | ρ | P50 at low quintile | P50 at high quintile | Status |
|---|---|---|---|---|
| `supply_cost_elasticity` | +0.95 | +428 | +1,488 | prior |
| `dev_cost_per_unit_mf` | -0.17 | +931 | +724 | prior |
| `permit_undercount_adjustment` | +0.17 | +735 | +927 | verified |
| `baseline_trend_weight` | +0.12 | +780 | +905 | design |
| `dev_cost_per_unit_sf` | -0.12 | +885 | +768 | prior |
| `baseline_noise_cv` | -0.03 | +826 | +777 | verified |
| `fee_per_unit_ri` | +0.00 | +847 | +864 | placeholder |
| `statewide_capacity_multiple` | +0.00 | +834 | +820 | prior |

### Fee reduction (Rhode Island actual fees)

| Parameter | ρ | P50 at low quintile | P50 at high quintile | Status |
|---|---|---|---|---|
| `supply_cost_elasticity` | +0.82 | +76 | +255 | prior |
| `fee_per_unit_ri` | +0.47 | +101 | +213 | placeholder |
| `dev_cost_per_unit_mf` | -0.16 | +162 | +126 | prior |
| `permit_undercount_adjustment` | +0.15 | +124 | +160 | verified |
| `dev_cost_per_unit_sf` | -0.12 | +158 | +133 | prior |
| `baseline_trend_weight` | +0.10 | +135 | +153 | design |
| `baseline_noise_cv` | -0.04 | +147 | +136 | verified |
| `statewide_capacity_multiple` | +0.01 | +146 | +147 | prior |

### Transit-oriented density

| Parameter | ρ | P50 at low quintile | P50 at high quintile | Status |
|---|---|---|---|---|
| `tod_realization_rate_annual` | +0.87 | +139 | +979 | prior |
| `tod_scenario_density_upa` | +0.46 | +209 | +646 | design |
| `tod_ramp_years` | -0.12 | +444 | +311 | prior |
| `statewide_capacity_multiple` | +0.04 | +364 | +361 | prior |
| `baseline_trend_weight` | -0.03 | +407 | +347 | design |
| `dev_cost_per_unit_mf` | -0.03 | +402 | +349 | prior |
| `parking_cost_per_space` | +0.01 | +374 | +386 | prior |
| `baseline_noise_cv` | +0.01 | +352 | +393 | verified |
| `parking_provided_unmandated` | -0.01 | +387 | +358 | prior |
| `permit_undercount_adjustment` | -0.00 | +356 | +365 | verified |

### All five together (fees at RI level; upper bound, capped)

| Parameter | ρ | P50 at low quintile | P50 at high quintile | Status |
|---|---|---|---|---|
| `adu_uptake_detached_annual` | +0.78 | +1,765 | +4,554 | prior |
| `mm_conversion_rate_annual` | +0.32 | +2,304 | +3,504 | prior |
| `tod_realization_rate_annual` | +0.30 | +2,197 | +3,391 | prior |
| `supply_cost_elasticity` | +0.16 | +2,388 | +2,979 | prior |
| `tod_scenario_density_upa` | +0.15 | +2,478 | +3,147 | design |
| `mm_units_per_conversion` | +0.15 | +2,516 | +3,082 | statutory |
| `adu_ramp_years` | -0.14 | +2,964 | +2,447 | prior |
| `mm_feasibility_share` | +0.10 | +2,424 | +2,892 | placeholder |
| `parking_cost_per_space` | +0.09 | +2,544 | +2,771 | prior |
| `parking_provided_unmandated` | -0.05 | +2,798 | +2,547 | prior |
| `dev_cost_per_unit_mf` | -0.05 | +2,787 | +2,517 | prior |
| `tierc_sewered_share` | -0.05 | +2,776 | +2,628 | prior |
| `fee_per_unit_ri` | +0.04 | +2,667 | +2,841 | placeholder |
| `mm_septic_multiplier` | +0.04 | +2,510 | +2,698 | prior |
| `baseline_trend_weight` | -0.03 | +2,763 | +2,645 | design |
| `permit_undercount_adjustment` | +0.03 | +2,724 | +2,651 | verified |
| `tierc_sf_only_share` | -0.02 | +2,725 | +2,739 | prior |
| `mm_ramp_years` | -0.02 | +2,689 | +2,615 | prior |
| `parking_required_mf_baseline` | +0.02 | +2,734 | +2,779 | placeholder |
| `tod_ramp_years` | -0.02 | +2,689 | +2,644 | prior |
| `adu_septic_multiplier` | -0.02 | +2,775 | +2,784 | prior |
| `mf_permit_share_in_tod_buffers` | +0.01 | +2,745 | +2,759 | placeholder |
| `statewide_capacity_multiple` | +0.01 | +2,636 | +2,670 | prior |
| `adu_uptake_conversion_annual` | +0.01 | +2,648 | +2,718 | prior |
| `dev_cost_per_unit_sf` | -0.01 | +2,665 | +2,682 | prior |
| `baseline_noise_cv` | -0.01 | +2,658 | +2,655 | verified |
| `tierc_lot20k_share` | -0.00 | +2,747 | +2,718 | prior |

## By municipality (5-year P50 increment)

| Municipality | Baseline | Accessory dwelling units | Missing middle (2–6 units on single-family lots) | Parking requirement reduction | Fee reduction (handbook $50,000 baseline) | Fee reduction (Rhode Island actual fees) | Transit-oriented density | All five together (fees at RI level; upper bound, capped) |
|---|---|---|---|---|---|---|---|---|
| Barrington | 40 | +23 | +11 | +0 | +2 | +0 | +0 | +42 |
| Bristol | 125 | +42 | +9 | +0 | +5 | +1 | +0 | +58 |
| Burrillville | 310 | +5 | +5 | +0 | +13 | +2 | +0 | +16 |
| Central Falls | 486 | +5 | +0 | +9 | +22 | +4 | +14 | +37 |
| Charlestown | 102 | +0 | +3 | +0 | +4 | +1 | +0 | +4 |
| Coventry | 569 | +2 | +7 | +2 | +24 | +4 | +0 | +18 |
| Cranston | 483 | +139 | +36 | +2 | +20 | +4 | +10 | +222 |
| Cumberland | 344 | +13 | +13 | +2 | +15 | +3 | +0 | +37 |
| East Greenwich | 284 | +25 | +4 | +2 | +12 | +2 | +0 | +37 |
| East Providence | 2,207 | +93 | +15 | +38 | +100 | +17 | +9 | +201 |
| Exeter | 30 | +1 | +1 | +0 | +1 | +0 | +0 | +4 |
| Foster | 43 | +0 | +1 | +0 | +2 | +0 | +0 | +2 |
| Glocester | 254 | +0 | +3 | +1 | +11 | +2 | +0 | +7 |
| Hopkinton | 167 | +0 | +2 | +0 | +7 | +1 | +0 | +4 |
| Jamestown | 113 | +4 | +2 | +0 | +4 | +1 | +0 | +8 |
| Johnston | 186 | +35 | +13 | +0 | +8 | +1 | +5 | +64 |
| Lincoln | 1,067 | +33 | +10 | +11 | +48 | +8 | +17 | +96 |
| Little Compton | 116 | +9 | +2 | +0 | +5 | +1 | +0 | +12 |
| Middletown | 336 | +18 | +4 | +2 | +14 | +2 | +0 | +30 |
| Narragansett | 64 | +37 | +12 | +0 | +2 | +0 | +0 | +58 |
| New Shoreham | 136 | +0 | +1 | +0 | +6 | +1 | +0 | +3 |
| Newport | 118 | +36 | +10 | +0 | +5 | +1 | +18 | +78 |
| North Kingstown | 792 | +9 | +6 | +5 | +34 | +6 | +18 | +52 |
| North Providence | 21 | +60 | +14 | +0 | +1 | +0 | +14 | +102 |
| North Smithfield | 100 | +0 | +4 | +0 | +4 | +1 | +0 | +7 |
| Pawtucket | 13 | +82 | +16 | +0 | +0 | +0 | +43 | +168 |
| Portsmouth | 869 | +6 | +4 | +6 | +37 | +6 | +0 | +27 |
| Providence | 2,981 | +132 | +32 | +59 | +138 | +24 | +173 | +508 |
| Richmond | 78 | +0 | +2 | +0 | +3 | +0 | +0 | +3 |
| Scituate | 115 | +0 | +3 | +0 | +5 | +1 | +0 | +4 |
| Smithfield | 258 | +26 | +9 | +0 | +11 | +2 | +0 | +44 |
| South Kingstown | 785 | +14 | +10 | +2 | +33 | +6 | +1 | +39 |
| Tiverton | 32 | +1 | +4 | +0 | +1 | +0 | +0 | +5 |
| Warren | 125 | +18 | +4 | +2 | +5 | +1 | +0 | +29 |
| Warwick | 2,334 | +187 | +61 | +26 | +102 | +18 | +46 | +407 |
| West Greenwich | 27 | +1 | +1 | +0 | +1 | +0 | +0 | +2 |
| West Warwick | 684 | +48 | +4 | +12 | +31 | +6 | +0 | +76 |
| Westerly | 506 | +25 | +10 | +2 | +21 | +4 | +0 | +48 |
| Woonsocket | 1,008 | +40 | +8 | +12 | +44 | +8 | +8 | +90 |

---
_Generated 2026-10-20T13:28+00:00 by `headroom report`._
