# Results — tier B

Metric: permitted housing units (new privately owned residential units authorised by building permit). 2,000 draws, seed 20261216. Horizon 2027–2031. Values are permitted units over the five years, as P10 / P50 / P90.

| Scenario | 5-year increment over baseline (P10 / P50 / P90) | Mean |
|---|---|---|
| Baseline (level, not increment) | 16,189 / 18,601 / 21,387 | 18,694 |
| Accessory dwelling units | +432 / +1,162 / +3,174 | +1,474 |
| Missing middle (2–6 units on single-family lots) | +97 / +357 / +1,260 | +548 |
| Parking requirement reduction | +69 / +201 / +499 | +250 |
| Fee reduction (handbook $50,000 baseline) | +427 / +820 / +1,492 | +895 |
| Fee reduction (Rhode Island actual fees) | +70 / +142 / +280 | +162 |
| Transit-oriented density | +112 / +337 / +950 | +446 |

## By year (P50, statewide)

| Scenario | 2027 | 2028 | 2029 | 2030 | 2031 |
|---|---|---|---|---|---|
| Baseline | 3,524 | 3,625 | 3,691 | 3,769 | 3,884 |
| Accessory dwelling units | +104 | +203 | +271 | +293 | +297 |
| Missing middle (2–6 units on single-family lots) | +32 | +61 | +82 | +91 | +92 |
| Parking requirement reduction | +37 | +38 | +40 | +41 | +43 |
| Fee reduction (handbook $50,000 baseline) | +158 | +161 | +163 | +166 | +173 |
| Fee reduction (Rhode Island actual fees) | +27 | +28 | +28 | +29 | +30 |
| Transit-oriented density | +30 | +58 | +77 | +85 | +85 |

## Sensitivity

Spearman rank correlation between each sampled parameter and the scenario's five-year statewide increment across draws, with the median increment in the parameter's bottom and top quintiles.

### Accessory dwelling units

| Parameter | ρ | P50 at low quintile | P50 at high quintile | Status |
|---|---|---|---|---|
| `adu_uptake_detached_annual` | +0.99 | +432 | +3,175 | prior |
| `adu_ramp_years` | -0.16 | +1,348 | +898 | prior |
| `tierc_sewered_share` | -0.05 | +1,168 | +1,106 | prior |
| `baseline_trend_weight` | -0.04 | +1,184 | +1,142 | design |
| `adu_uptake_conversion_annual` | +0.03 | +1,120 | +1,249 | prior |
| `baseline_noise_cv` | -0.02 | +1,139 | +1,150 | verified |
| `permit_undercount_adjustment` | +0.01 | +1,208 | +1,158 | verified |
| `adu_septic_multiplier` | -0.01 | +1,242 | +1,202 | prior |
| `tierc_lot20k_share` | +0.01 | +1,170 | +1,181 | prior |
| `statewide_permit_capacity` | -0.01 | +1,157 | +1,140 | prior |

### Missing middle (2–6 units on single-family lots)

| Parameter | ρ | P50 at low quintile | P50 at high quintile | Status |
|---|---|---|---|---|
| `mm_conversion_rate_annual` | +0.90 | +104 | +1,194 | prior |
| `mm_units_per_conversion` | +0.35 | +222 | +574 | statutory |
| `mm_feasibility_share` | +0.25 | +239 | +520 | placeholder |
| `mm_ramp_years` | -0.11 | +434 | +279 | prior |
| `mm_septic_multiplier` | +0.06 | +311 | +360 | prior |
| `baseline_trend_weight` | -0.04 | +366 | +346 | design |
| `tierc_sf_only_share` | +0.03 | +331 | +418 | prior |
| `tierc_sewered_share` | -0.01 | +363 | +357 | prior |
| `baseline_noise_cv` | +0.01 | +348 | +389 | verified |
| `permit_undercount_adjustment` | -0.00 | +365 | +357 | verified |
| `statewide_permit_capacity` | -0.00 | +340 | +378 | prior |

### Parking requirement reduction

| Parameter | ρ | P50 at low quintile | P50 at high quintile | Status |
|---|---|---|---|---|
| `supply_cost_elasticity` | +0.59 | +112 | +393 | prior |
| `parking_provided_unmandated` | -0.44 | +283 | +108 | prior |
| `parking_cost_per_space` | +0.41 | +127 | +311 | prior |
| `parking_required_mf_baseline` | +0.36 | +128 | +283 | placeholder |
| `dev_cost_per_unit_mf` | -0.18 | +242 | +173 | prior |
| `baseline_trend_weight` | +0.16 | +171 | +249 | design |
| `mf_permit_share_in_tod_buffers` | -0.10 | +227 | +183 | placeholder |
| `permit_undercount_adjustment` | +0.10 | +181 | +225 | verified |
| `tod_hub_min_routes` | +0.03 | +186 | +200 | placeholder |
| `baseline_noise_cv` | -0.02 | +213 | +201 | verified |
| `tod_frequent_peak_departures_per_hour` | +0.02 | +202 | +197 | prior |
| `statewide_permit_capacity` | -0.01 | +200 | +204 | prior |

### Fee reduction (handbook $50,000 baseline)

| Parameter | ρ | P50 at low quintile | P50 at high quintile | Status |
|---|---|---|---|---|
| `supply_cost_elasticity` | +0.95 | +428 | +1,484 | prior |
| `dev_cost_per_unit_mf` | -0.17 | +931 | +724 | prior |
| `permit_undercount_adjustment` | +0.17 | +735 | +929 | verified |
| `baseline_trend_weight` | +0.12 | +780 | +915 | design |
| `dev_cost_per_unit_sf` | -0.12 | +885 | +768 | prior |
| `baseline_noise_cv` | -0.03 | +826 | +780 | verified |
| `fee_per_unit_ri` | +0.00 | +847 | +865 | placeholder |
| `statewide_permit_capacity` | +0.00 | +839 | +820 | prior |

### Fee reduction (Rhode Island actual fees)

| Parameter | ρ | P50 at low quintile | P50 at high quintile | Status |
|---|---|---|---|---|
| `supply_cost_elasticity` | +0.82 | +76 | +255 | prior |
| `fee_per_unit_ri` | +0.47 | +101 | +214 | placeholder |
| `dev_cost_per_unit_mf` | -0.16 | +162 | +126 | prior |
| `permit_undercount_adjustment` | +0.15 | +124 | +160 | verified |
| `dev_cost_per_unit_sf` | -0.12 | +158 | +133 | prior |
| `baseline_trend_weight` | +0.10 | +135 | +153 | design |
| `baseline_noise_cv` | -0.04 | +146 | +135 | verified |
| `statewide_permit_capacity` | +0.01 | +144 | +147 | prior |

### Transit-oriented density

| Parameter | ρ | P50 at low quintile | P50 at high quintile | Status |
|---|---|---|---|---|
| `tod_realization_rate_annual` | +0.86 | +125 | +889 | prior |
| `tod_scenario_density_upa` | +0.47 | +183 | +590 | design |
| `tod_ramp_years` | -0.12 | +401 | +283 | prior |
| `statewide_permit_capacity` | +0.04 | +325 | +324 | prior |
| `baseline_trend_weight` | -0.03 | +370 | +312 | design |
| `dev_cost_per_unit_mf` | -0.03 | +361 | +316 | prior |
| `tod_frequent_peak_departures_per_hour` | +0.02 | +303 | +328 | prior |
| `tod_hub_min_routes` | +0.02 | +325 | +362 | placeholder |
| `parking_cost_per_space` | +0.01 | +336 | +340 | prior |
| `baseline_noise_cv` | +0.01 | +316 | +354 | verified |
| `parking_provided_unmandated` | -0.01 | +348 | +322 | prior |
| `permit_undercount_adjustment` | -0.00 | +319 | +327 | verified |

## By municipality (5-year P50 increment)

| Municipality | Baseline | Accessory dwelling units | Missing middle (2–6 units on single-family lots) | Parking requirement reduction | Fee reduction (handbook $50,000 baseline) | Fee reduction (Rhode Island actual fees) | Transit-oriented density |
|---|---|---|---|---|---|---|---|
| Barrington | 40 | +23 | +11 | +0 | +2 | +0 | +0 |
| Bristol | 125 | +42 | +9 | +0 | +5 | +1 | +0 |
| Burrillville | 310 | +5 | +5 | +0 | +13 | +2 | +0 |
| Central Falls | 486 | +5 | +0 | +9 | +22 | +4 | +14 |
| Charlestown | 102 | +0 | +3 | +0 | +4 | +1 | +0 |
| Coventry | 568 | +2 | +7 | +2 | +24 | +4 | +0 |
| Cranston | 483 | +139 | +36 | +2 | +20 | +4 | +10 |
| Cumberland | 344 | +13 | +13 | +2 | +15 | +3 | +0 |
| East Greenwich | 284 | +25 | +4 | +2 | +12 | +2 | +0 |
| East Providence | 2,206 | +93 | +15 | +38 | +100 | +17 | +9 |
| Exeter | 30 | +1 | +1 | +0 | +1 | +0 | +0 |
| Foster | 43 | +0 | +1 | +0 | +2 | +0 | +0 |
| Glocester | 254 | +0 | +3 | +1 | +11 | +2 | +0 |
| Hopkinton | 167 | +0 | +2 | +0 | +7 | +1 | +0 |
| Jamestown | 113 | +4 | +2 | +0 | +4 | +1 | +0 |
| Johnston | 186 | +35 | +13 | +0 | +8 | +1 | +5 |
| Lincoln | 1,065 | +33 | +10 | +11 | +48 | +8 | +17 |
| Little Compton | 115 | +9 | +2 | +0 | +5 | +1 | +0 |
| Middletown | 335 | +18 | +4 | +2 | +14 | +2 | +0 |
| Narragansett | 64 | +37 | +12 | +0 | +2 | +0 | +0 |
| New Shoreham | 136 | +0 | +1 | +0 | +6 | +1 | +0 |
| Newport | 117 | +36 | +10 | +0 | +5 | +1 | +11 |
| North Kingstown | 791 | +9 | +6 | +5 | +34 | +6 | +2 |
| North Providence | 21 | +60 | +14 | +0 | +1 | +0 | +14 |
| North Smithfield | 100 | +0 | +4 | +0 | +4 | +1 | +0 |
| Pawtucket | 13 | +82 | +16 | +0 | +0 | +0 | +45 |
| Portsmouth | 868 | +6 | +4 | +6 | +37 | +6 | +0 |
| Providence | 2,980 | +132 | +32 | +59 | +138 | +24 | +191 |
| Richmond | 78 | +0 | +2 | +0 | +3 | +0 | +0 |
| Scituate | 115 | +0 | +3 | +0 | +5 | +1 | +0 |
| Smithfield | 258 | +26 | +9 | +0 | +11 | +2 | +0 |
| South Kingstown | 785 | +14 | +10 | +2 | +33 | +6 | +1 |
| Tiverton | 32 | +1 | +4 | +0 | +1 | +0 | +0 |
| Warren | 125 | +18 | +4 | +2 | +5 | +1 | +0 |
| Warwick | 2,334 | +187 | +61 | +26 | +102 | +18 | +16 |
| West Greenwich | 27 | +1 | +1 | +0 | +1 | +0 | +0 |
| West Warwick | 684 | +48 | +4 | +12 | +31 | +6 | +0 |
| Westerly | 505 | +25 | +10 | +2 | +21 | +4 | +0 |
| Woonsocket | 1,007 | +40 | +8 | +12 | +44 | +8 | +2 |

---
_Generated 2026-10-04T20:29+00:00 by `headroom report`._
