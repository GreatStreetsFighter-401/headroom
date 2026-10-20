# Policy Scenario Comparison

*Headroom — draft v0.2, 2026-10-20, from the tier-B run for Rhode Island (seed 20261216, 2,000 draws). Numbers are permitted homes over 2027–2031, statewide, shown as a middle estimate (P50) with a likely range (P10–P90). Page budget: 4.*

# Scenarios Addressed

The baseline and all five benchmark scenarios, each modelled as an increment over current Rhode Island law; the development-fee scenario is run twice, at the handbook's $50,000 per unit and at Rhode Island's actual fee level; and a sixth line adds all five together as a capped upper bound. No additional scenarios yet (candidates with mentors: the State's 800 sq ft ADU cap, and the comprehensive-permit channel under chapter 45-53).

**The baseline.** With no new reform, Rhode Island is on course to permit roughly **18,600 homes** over the five years (likely range 16,200–21,400). That already clears the State's Housing 2030 goal of 15,000, because 2025 was the strongest permit year since the 1980s and the model carries part of that momentum forward. Whether 2025 was a new level or a peak is the biggest single uncertainty in every number below.

# Ranking of Results

| Scenario | Modelled effect vs. baseline (five years) | Confidence | Notes |
| --- | --- | --- | --- |
| 1. Accessory dwelling units | **+1,160** (+430 to +3,170) | medium | Calibrated to Rhode Island's own 2024 ADU count; range is wide because two years of data cannot pin the rate |
| 2. Development fees −50 % at the handbook's $50,000 | **+820** (+430 to +1,490) | medium | The comparable-across-states number; see the next row for Rhode Island |
| 3. Transit-oriented density | **+370** (+130 to +1,050) | low | Statutory buffers; realisation rate borrowed from other cities' station areas |
| 4. Missing middle (2–6 units) | **+360** (+100 to +1,260) | medium-low | Conversion rates from Portland and Minneapolis; feasibility share is a placeholder |
| 5. Parking minimums reduced | **+200** (+70 to +500) | low-medium | Cost channel; the mandated-spaces baseline is a placeholder |
| — Development fees −50 % at Rhode Island's actual fees | **+140** (+70 to +280) | low-medium | The Rhode Island answer; the fee level is a placeholder, the direction is not |
| All five together (fees at the RI level) | **+2,700** (+1,550 to +4,640) | upper bound | Increments added, no interactions, capped by construction capacity; ≈ 15 % on top of the baseline |

# What Drives the Differences

**ADUs lead because the eligible stock is large and the behaviour is measured.** Rhode Island already allows an ADU by right on lots of 20,000 sq ft or more and within an existing building, so the reform's effect falls on the ~60 % of single-family lots below that size, discounted where the lot is on septic. The number is almost entirely the uptake rate — how many newly eligible owners build one each year — which the model sets so that it reproduces the 163 ADUs the State permitted in 2024. Even a few tenths of a percent a year across ~150,000 newly eligible lots is the largest channel.

**Fees matter at the handbook's level and not at Rhode Island's.** Both fee lines are the same cost channel: the saving divided by all-in cost per unit, times a supply elasticity near 0.8. The gap between them *is* the finding: Rhode Island's fees are a fraction of the $50,000 benchmark (building fees of $10–15 per $1,000 of value, few impact fees), so halving them buys little here while it would buy a lot in a high-fee state.

**Transit-oriented density is slow by construction.** Residential land within ⅛ mile of a frequent stop or ¼ mile of one of the eight regional mobility hubs — the distances Rhode Island wrote into law in 2026 — times the gap between a 20-home-per-acre allowance and today's minimum-lot density, gives a large capacity; the realisation rate turns it into a small five-year number, because upzoned land near transit builds out over decades.

**Missing middle is rare in practice.** The stock of houses in single-family-only districts is large, but small conversions are rare where they are legal: Portland's first year was about 0.13 % of lots, Minneapolis an order of magnitude lower for 2–3-unit buildings, and most of Minneapolis's new homes came in 4+-unit buildings that this scenario excludes by definition.

**Parking is a small cost channel in a surface-parking state.** A mandated space developers would not otherwise build costs roughly $8,000–45,000; the saving is a few percent of a $400,000 unit; and near transit the State already caps the mandate at one space, so the reform's increment there is small.

# Which Assumptions Matter Most

* **The uptake, conversion or realisation rate** in every scenario (rank correlation +0.9 to +0.99 with the result). Change the ADU uptake rate from 0.2 % to 0.6 % a year and the ADU line moves from +1,160 to the top of its range; that one input flips the ranking between ADUs and the handbook fee line.
* **The ramp length** (second in every scenario, and negative): a five-year ramp roughly halves a five-year total.
* **The supply elasticity** for the two cost channels; the low end of its range (0.3) puts parking and Rhode Island-level fees under +100 each.
* **The three placeholders:** the missing-middle feasibility share (ρ ≈ +0.25, the only placeholder with real weight), the mandated-parking baseline, and the Rhode Island fee level. Each is flagged on the page; replacing them with the assessor ratios, the 39 parking schedules and the 39 fee schedules is the remaining data work.
* **The baseline itself:** the trend-versus-mean weight moves the baseline by about ±2,000 over five years but moves the *increments* little, because they are added on top. The ranking does not depend on it.

Evidence that the ranges are reasonable: the ADU rate brackets the State's observed 2024 count; the conversion rate brackets Portland and Minneapolis; the elasticity brackets the cross-metro literature; the baseline's out-of-sample hindcast covers 60 % of 2024–25 town-years in its P10–P90 band and the overview says so rather than claiming better.

# What the Tool Cannot Say

* Where within a town the homes land, or which lots convert first — the model has no parcel precision by design.
* Prices, rents, or who occupies the new homes; the affordability tier of what is built; whether existing residents move.
* Whether 2025's record permit year persists. The baseline band assumes no further regime change.
* How the saving from a cost reform is split between rents, land prices and more units — the elasticity bundles those.
* What towns' 800 sq ft ADU caps do, or site assembly, infrastructure limits and design review near transit — these are folded into the rates.
* Anything about interactions between reforms; "all five together" is a sum, not a joint forecast, and over-reading it as a plan's total would be a mistake.
* For another state run at tier C: the permit level is the Census series as published (which undercounts Rhode Island by half and may undercount theirs), and the eligibility shares are Rhode Island's until replaced.

Read the five together: every reform helps and none is transformative on its own over five years; the largest, ADUs, adds about six percent to the baseline. The handbook's fee scenario is the clearest case of a reform that matters elsewhere and not here, and running it at local fee levels is the honest answer. The ranges are wide because the behavioural rates are the uncertainty, not the land: the land is counted; the owners' decisions are estimated.
