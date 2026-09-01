# 0002 — "Sales" means Quantity × Unit Price, ex-tax, at order-line grain

- **Project:** `projects/bi-task-1/`
- **Date:** 2026-09-01
- **Status:** decided

## The fork in the road

`Sales.xlsx` is a pre-joined flattening of four grains (order header → order
line → invoice → customer transaction). Its row grain is one order line
(`OrderLineID` unique across all 212,774 rows), but three of its money columns
— `AmountExcludingTax`, `TaxAmount`, `TransactionAmount` — are at **invoice
grain, repeated on every line of that invoice**. Verified: across all 64,819
invoices, none carries more than one distinct `AmountExcludingTax`, and only
5,135 invoices are single-line.

So `SUM(AmountExcludingTax)` over the fact table returns **£583,888,532**
against a true ex-tax total of **£158,081,488** — a 3.69× overstatement that
looks entirely plausible on a report.

The assignment says "average order amount in £" and "YOY sales" without ever
defining what counts as sales. The realistic options were:

1. `Quantity × UnitPrice` per line, ex-tax — safe at the fact's own grain.
2. The invoice-header `AmountExcludingTax`, which would need the fact
   deduplicated to invoice grain first.
3. Tax-inclusive (`TransactionAmount` equivalent), roughly 10–15% higher.

`Quantity × UnitPrice` was verified to reconcile **to the penny on all 64,819
invoices** against the invoice header amount, so option 1 loses nothing.

## What was decided

**Total Sales = SUM of a Power Query column `Line Amount = Quantity × Unit
Price`, ex-tax, at order-line grain.**

The `UnitPrice` used is the numeric one — `Sales.xlsx` has three columns
literally headed `UnitPrice` (currency-formatted text, always-empty, numeric);
the numeric one is identical to the text one on every row.

`AmountExcludingTax`, `TaxAmount` and `TransactionAmount` are **not loaded into
the model at all**, so the trap cannot be walked into later.

## Why

User's answer on issue #1: "sales should be the quantity * the price as you've
suggested." No further reasoning was given beyond agreeing with the
recommendation, which was based on the grain analysis above.

## Consequences

- All nine KPIs are built on `[Total Sales]`; nothing else aggregates
  `Line Amount` directly.
- Headline figures the model must reproduce: **£162,950,104.45** total sales,
  **67,628** orders, **£2,409.51** average order amount.
- All sales figures in this project are **ex-tax**. If a tax-inclusive view is
  ever wanted, `Tax Rate` is on the fact table, so it is a new measure
  (`Line Amount × (1 + Tax Rate)`) rather than a remodel.
- Because tax is excluded, these figures will not tie to the invoice
  `TransactionAmount` totals if anyone reconciles against the source workbook.
