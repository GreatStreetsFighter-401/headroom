# Other states — tier C from federal data alone

`headroom build --state XX && headroom run --state XX`: county subdivisions from the Census geography index, permits from the Building Permits Survey place file, structure counts from the ACS summary files. No state-specific code. Two caveats travel with every number: the permit level is the Census series as published (Rhode Island's undercounts by about half, and this state's may too), and the eligibility shares (`tierc_*`) are Rhode Island's tier-B values until replaced with the state's own.

| Scenario | CT (P10 / P50 / P90) | MA (P10 / P50 / P90) |
|---|---|---|
| Baseline | 31,474 / 36,412 / 41,951 | 61,412 / 69,513 / 77,902 |
| Accessory dwelling units | +1,433 / +3,881 / +10,135 | +2,469 / +6,687 / +17,526 |
| Missing middle (2–6 units on single-family lots) | +369 / +1,379 / +4,904 | +636 / +2,376 / +8,456 |
| Parking requirement reduction | +176 / +516 / +1,266 | +308 / +911 / +2,189 |
| Fee reduction (Rhode Island actual fees) | +141 / +285 / +554 | +270 / +539 / +1,046 |
| Transit-oriented density | +0 / +0 / +0 | +0 / +0 / +0 |
| All five together (fees at RI level; upper bound, capped) | +3,684 / +7,056 / +13,593 | +6,431 / +12,160 / +23,578 |

Towns with a permit series / county subdivisions: CT 169; MA 351.

---
_Generated 2026-10-20T13:28+00:00 by `headroom report`._
