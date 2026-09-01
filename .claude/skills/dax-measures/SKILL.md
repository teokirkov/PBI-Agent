---
name: dax-measures
description: Use when writing DAX measures for a semantic model. Naming, formatting, and patterns for common measure types (totals, YoY, ratios, distinct counts). Also defines which measure situations must be escalated to the user rather than guessed.
---

# DAX measure conventions

See also `../best-practices/SKILL.md` — this file implements the team's
DAX/measure conventions from `docs/best-practices/power-bi-best-practices.md`;
if the two ever disagree, the best-practices doc wins.

## Where measures live

All measures go in a dedicated, columnless `_Measures` table (see
`../pbip-tmdl-structure/SKILL.md`), never scattered as columns bolted onto
fact tables. Group related measures with a `displayFolder`; once there are
many measures, use sub-folders (`displayFolder: Sales\Time Intelligence`) to
keep the table browsable.

## Explicit measures only — non-negotiable

Never rely on an implicit measure (a visual auto-aggregating a raw numeric
column). Every value a visual displays that involves aggregation must come
from an explicit measure in `_Measures`, even for something as simple as
`SUM('Fact Sales'[Amount])`. This is a hard team rule, not a style
preference — implicit measures are a common source of inconsistent
aggregation behavior across visuals.

## Naming

- `PascalCase with spaces`, business-readable: `Total Revenue`, not
  `TotRev` or `total_revenue`.
- A measure that's a variant of another should say so:
  `Total Revenue YoY %`, `Total Revenue LY`.
- Every measure gets a `formatString` (currency, percent, whole number as
  appropriate) — don't leave format to the report author.

## Style

```tmdl
measure 'Total Revenue' = SUM('Fact Sales'[Amount])
	formatString: "$#,##0.00"
	displayFolder: Sales

measure 'Total Revenue LY' =
		CALCULATE(
			[Total Revenue],
			SAMEPERIODLASTYEAR('Dim Date'[Date])
		)
	formatString: "$#,##0.00"
	displayFolder: Sales\Time Intelligence
```

- Multi-line DAX: `CALCULATE`/`VAR` bodies indented one level under the `=`,
  matching the block above — keeps diffs readable.
- Prefer `VAR ... RETURN` over deeply nested `CALCULATE`/`IF` when a measure
  has more than one intermediate value, for readability and to avoid
  recomputing the same sub-expression twice.
- Reference other measures (`[Total Revenue]`), not raw
  `SUM(...)` repeated — keeps a single source of truth per business
  definition.
- Time intelligence measures require a proper marked date table
  (`Dim Date`) — see the TMDL skill. If one doesn't exist yet, that's a
  prerequisite step, not something to skip around with `DATEADD` tricks on a
  non-contiguous date column.

## When a measure definition is a cross-roads, not a guess

Per `CLAUDE.md` §1, stop and ask (don't silently pick) whenever:

- The assignment names a metric without defining it precisely, and more than
  one definition is defensible (gross vs. net, inclusive/exclusive of tax or
  returns, calendar vs. fiscal year, unique customers vs. unique orders).
- A ratio/rate measure's denominator could reasonably be filtered or
  unfiltered (e.g. "conversion rate" — of what universe?).
- A requested measure implies a many-to-many relationship or a bridge table
  that doesn't exist yet in the model.
- The brief asks for a comparison ("vs. target", "vs. budget") but no
  target/budget data exists in the sources provided.

Measures that are mechanical and standard — `SUM`, `COUNT`, `DISTINCTCOUNT`,
`AVERAGE` of a clearly-named column, straightforward YoY/MoM using a proper
date table — do not need escalation. Reserve asking for genuine ambiguity,
not every measure.
