# 0007 — YoY compares like-for-like periods, cut at the last date with data

- **Project:** `projects/bi-task-1/`
- **Date:** 2026-09-01
- **Status:** decided

## The fork in the road

The data ends **29 February 2016**, so 2016 is two months of a year. A plain
`SAMEPERIODLASTYEAR` comparison reads:

| | Sales | Plain YoY |
|---|---|---|
| 2015 (full year) | £55,817,887.45 | |
| 2016 (Jan–Feb only) | £8,711,620.80 | **−84.4%** |

That number is arithmetically right and completely wrong as a business
statement — it says nothing except "we have less than a year of 2016". Options
were a like-for-like comparison, or plain YoY with a visible caveat on the
page.

## What was decided

**Like-for-like.** `[Sales LY (Like-for-Like)]` trims the prior year to the
same month-and-day the current period's data stops at — but only when that
trimming is actually needed:

```
VAR LastSalesDate = [Last Sales Date]                      -- 2016-02-29
VAR CutoffMonthDay = MONTH ( LastSalesDate ) * 100 + DAY ( LastSalesDate )
VAR PeriodEnd = MAX ( 'Dim Date'[Date] )
VAR SelectedPeriodRunsPastData = PeriodEnd > LastSalesDate
RETURN
    IF (
        SelectedPeriodRunsPastData,
        CALCULATE ( [Total Sales], SAMEPERIODLASTYEAR ( 'Dim Date'[Date] ),
                    'Dim Date'[Month Day Number] <= CutoffMonthDay ),
        CALCULATE ( [Total Sales], SAMEPERIODLASTYEAR ( 'Dim Date'[Date] ) )
    )
```

Two details worth keeping:

- The guard is `PeriodEnd > LastSalesDate`, so **complete years are still
  compared in full**. Selecting 2015 compares all of 2015 against all of 2014;
  only 2016 (and any selection running past 29 Feb 2016) gets trimmed. A
  blanket "always cut at February" would have thrown away ten months of every
  complete year.
- The cut-off compares **month-and-day** (`MONTH * 100 + DAY`), not day-of-year.
  2016 is a leap year, so day-of-year 60 is 29 February in 2016 but 1 March in
  2015 — the month/day form lands on 28 February 2015 correctly.

`Dim Date[Month Day Number]` exists solely to support this.

## Why

User's answer on issue #1: "use period comparisons here — if you're looking at
yoy then the previous year should be cut at the same point as 2016."

## Consequences

- `[Sales YoY %]` is the only YoY measure in the model. There is no plain
  full-period variant, deliberately: two measures both called YoY showing
  −1.7% and −84.4% would be worse than one correct one.
- The resulting series, which is a genuine like-for-like read:

  | Year | Sales in comparison window | YoY |
  |---|---|---|
  | 2014 vs 2013 | £51,492,003.40 vs £46,928,592.80 | +9.7% |
  | 2015 vs 2014 | £55,817,887.45 vs £51,492,003.40 | +8.4% |
  | 2016 vs 2015 | £8,711,620.80 vs £8,863,884.50 (Jan 1 – Feb 28) | **−1.7%** |

  2013 has no prior year and correctly returns blank.
- `[Sales YoY %]` at an "all years" grand total is not meaningful (there is no
  single prior period to compare against). Use it at year or month grain.
- The report should still carry a visible "data through 29 February 2016"
  caption — `[Last Sales Date]` exists for exactly that.
