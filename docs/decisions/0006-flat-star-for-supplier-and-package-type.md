# 0006 — Supplier and Package Type join the fact directly, not via Dim Product

- **Project:** `projects/bi-task-1/`
- **Date:** 2026-09-01
- **Status:** decided

## The fork in the road

`Sales.xlsx` carries `SupplierID` and `PackageTypeID` on every order line, but
both are fully derivable from `StockItemID`:

- `Sales.SupplierID` == `StockItem.SupplierID` on all 212,774 rows.
- `Sales.PackageTypeID` == `StockItem.UnitPackageID` on all 212,774 rows (it
  matches `OuterPackageID` on only 174,853, so it is specifically the *unit*
  package).

So either shape gives the same answers:

1. **Flat** — `Fact Sales → Dim Supplier` and `Fact Sales → Dim Package Type`
   as direct many-to-one relationships. Simpler DAX, matches how the brief
   phrases its KPIs ("Quantity and Sales by Supplier Name", "by Package
   Types"), but keeps two redundant integer columns on a 212,774-row fact.
2. **Snowflaked** — both attributes reached through `Dim Product`. Smaller
   fact, one obvious source of truth per attribute, but a deeper chain.

## What was decided

**Option 1, the flat star.** Both keys stay on the fact table (hidden), with
direct many-to-one, single-direction relationships to `Dim Supplier` and
`Dim Package Type`.

## Why

User's answer on issue #1: "use the flatter format." No further reasoning was
given. It also matches the team's general star-schema preference and the
modeling skill's guidance to avoid snowflaking for small assignment datasets.

## Consequences

- The model is a clean five-point star around one fact, plus the category
  bridge from `docs/decisions/0004`.
- `Dim Product` does **not** carry `SupplierID` or `UnitPackageID` — they would
  be unused duplicate columns.
- Two redundant int64 columns remain on the fact. At 212,774 rows with 7 and 4
  distinct values respectively they compress to almost nothing, so the size
  cost of this choice is negligible.
- Only 7 of 13 suppliers and 4 of 14 package types appear in Sales, so both
  dimensions will show zero-value members in a visual unless it filters to
  non-blank. That is a source-data fact, not a consequence of this decision.
