# 0005 — "Categories" in the YTD/MTD KPI means the sales channel

- **Project:** `projects/bi-task-1/`
- **Date:** 2026-09-01
- **Status:** decided

## The fork in the road

KPI 3 in the brief reads: "YTD, MTD sales – all and separated by categories
(**Online Sales Conditional**)". Three columns could be what "categories"
means:

1. `Customer.OnlineSalesConditional` — Online Sale / Retail Sale. Named in the
   brief's own parenthetical.
2. `Customer.CustomerCategoryName` — 5 values (Novelty Shop, Supermarket,
   Computer Store, Gift Store, Corporate). The only column with "Category" in
   its name on the customer table.
3. The product categories from `docs/decisions/0004`.

## What was decided

**`OnlineSalesConditional`**, surfaced as `Dim Customer[Sales Channel]`.

Mechanically this needs no channel-specific YTD/MTD measures: `[Sales YTD]` and
`[Sales MTD]` are plain time-intelligence measures, and "separated by
categories" is achieved by putting `Dim Customer[Sales Channel]` on the visual.
Hardcoding the two channel values into four extra measures would have been the
wrong shape.

`CustomerCategoryName` is still loaded (as `Dim Customer[Customer Category]`),
so option 2 is one drag-and-drop away if the reading turns out to be wrong.
Nothing has to be remodelled.

## Why

The brief names the column in parentheses immediately after the word
"categories", which is about as explicit as the assignment gets. The user's
answer on issue #1 was "decide yourself here as well", delegating the call
without stating a preference.

## Consequences

- The column is renamed to **Sales Channel** in Power Query, because "Online
  Sales Conditional" is not a business name and the team convention is to fix
  bad source names in the ETL rather than cosmetically on the front end. The
  original name is recorded in the column's description in TMDL.
- **`OnlineSalesConditional` is a customer attribute, not a per-order flag.**
  It is perfectly determined by `BuyingGroupName`: all 402 customers with a
  buying group are "Online Sale", all 261 without are "Retail Sale". So the
  "online sales %" KPI really measures *sales to online-type customers*, not
  orders placed through an online channel. There is no order-level channel flag
  anywhere in the seven source files. This is called out in `ANALYSIS.md`
  because the KPI wording implies something the data cannot deliver.
- Online share computes to **63.34%** (£103.2m of £163.0m).
