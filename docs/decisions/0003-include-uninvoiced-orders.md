# 0003 — Uninvoiced orders are included in sales, and surfaced explicitly

- **Project:** `projects/bi-task-1/`
- **Date:** 2026-09-01
- **Status:** decided

## The fork in the road

2,857 of the 212,774 order lines have no `InvoiceID`. They belong to 2,809
orders, and those orders are **wholly** uninvoiced — there is no order with a
mix of invoiced and uninvoiced lines, which makes this a clean order-level
distinction rather than a messy line-level one.

Including or excluding them moves two of the nine KPIs:

| | Orders | Sales |
|---|---|---|
| Include | 67,628 | £162,950,104.45 |
| Exclude | 64,819 | £158,081,488.45 |
| Difference | 2,809 | £4,868,616.00 (3.0%) |

## What was decided

**Include them in `[Total Sales]` and `[Order Count]`**, and additionally
expose them so the report can show what that choice is worth:

- `Fact Sales[Is Invoiced]` — a boolean column on the fact.
- `[Invoiced Sales]`, `[Uninvoiced Sales]`, `[Uninvoiced Orders]`,
  `[Uninvoiced Sales %]` in the `Sales\Order Fulfilment` folder.
- A "Data Quality & Caveats" report page to carry the visual.
- A section in `projects/bi-task-1/ANALYSIS.md`.

## Why

User's answer on issue #1: "should be included but mentioned, as a visual later
on and as an analysis." The supporting argument was that the brief asks for
*order* count, not invoice count, so an order that exists but has not been
invoiced is still an order.

## Consequences

- Every sales figure in this model is 3.0% higher than an invoice-based figure
  would be. Anyone reconciling against an invoicing or finance system will see
  that gap; it is expected, not an error.
- `[Order Count]` = 67,628, not 64,819.
- The uninvoiced measures are the report's own audit trail for this decision —
  they should not be removed if the report is tidied up.
