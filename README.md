# coast-fire-formula

**Live calculator → https://coastfirelab.com**

A reference implementation of Coast/Fat FIRE math that **subtracts Social Security** and
prices the **pre-Medicare health insurance gap** as a separate discounted bridge — the two
items most FIRE calculators leave out.

Zero dependencies, standard library only. Every number is a pure function of its
arguments, so any figure published on the live calculator can be reproduced and checked
line by line.

## The five functions

| Function | What it computes | Formula |
| --- | --- | --- |
| `target(annual_spend, swr, ss_annual)` | Portfolio target after the Social Security offset | `(annual_spend − ss_annual) / swr` |
| `annuity_factor(r, n)` | Present value of 1 per year for n years | `(1 − (1+r)^−n) / r` |
| `health_bridge(monthly_health, retire_age, medicare_age)` | Discounted cost of insurance from retirement to Medicare | `monthly_health × 12 × annuity_factor(r, medicare_age − retire_age)` |
| `capital_today(target, age, target_age)` | Lump sum needed today to compound into the target | `target / (1 + real)^(target_age − age)` |
| `years_to_target(assets, monthly_saving, target)` | Years to reach the target while saving monthly | `ln((T·r + 12s) / (A·r + 12s)) / ln(1 + r)` |

## Worked example

$10,000 a month of spending, 4% withdrawal rate, 2026 average retired-worker benefit of
$2,084 a month ($25,008 a year):

```python
from coast_fire import target, health_bridge, years_to_target

target(120_000)                        # 2_374_800  portfolio needed, SS already subtracted
target(100_000)                        # 1_874_800
health_bridge(750, 40)                 #   126_846  pre-65 insurance, discounted at 5%
years_to_target(100_000, 3_000, 2_374_800)   # 27.2 years
```

Without the Social Security offset the first number would be $3,000,000 — **$625,200 of
portfolio the reader does not need**.

## Why subtract Social Security

Most FIRE calculators apply the withdrawal rate to the full spend and assume benefits are
zero. For anyone retiring in their 40s or 50s that overshoots, because the portfolio only
ever has to fund the slice of spending that benefits do not cover.

The catch is timing, and it is why the two offsets are modelled differently. Benefits do
not start before 62, so the portfolio carries the whole bill for more than a decade — and
health insurance is a **bridge with a hard end date at 65**, not a perpetual expense. That
is why `health_bridge` is discounted as an annuity over a fixed number of years and never
multiplied by 25.

Benefit figure: **$2,084/month, $25,008/year** — SSA monthly statistical snapshot, June
2026 (average benefit for all retired workers).

## Test

```bash
pip install pytest
pytest -q
```

The suite asserts the published figures, so a failing test means the code and the live
calculator have diverged.

MIT licensed.
