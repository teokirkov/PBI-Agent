---
name: data-modeling-decisions
description: Use when designing the table/relationship structure of a semantic model — star-schema heuristics and the specific modeling situations that must be escalated to the user (per CLAUDE.md §1) rather than resolved silently.
---

# Data modeling decisions

See also `../best-practices/SKILL.md` — this file implements the team's
modeling conventions from `docs/best-practices/power-bi-best-practices.md`;
if the two ever disagree, the best-practices doc wins.

## Default to a star schema

- One or more `Fact` tables at a transactional or aggregated grain, each row
  representing one clearly-statable thing ("one order line", "one daily
  snapshot").
- Surrounding `Dim` tables, each with a single-column primary key, joined
  many (fact) to one (dimension).
- Avoid snowflaking (dimension → dimension chains) unless a dimension is
  genuinely large/shared and reuse across facts justifies it. For a single
  small assignment dataset, flatten dimension hierarchies into one dimension
  table rather than normalizing further — it's simpler to reason about and
  query.

## Grain discipline

Before modeling a fact table, state its grain explicitly in `NOTES.md`
("one row per order line") and verify every source row actually matches
that grain (no duplicate rows for the same conceptual event, no rows that
mix two grains). A fact table with an unstated or inconsistent grain is the
single most common cause of double-counted totals.

## Situations that must be escalated (CLAUDE.md §1), not resolved silently

- **Many-to-many relationships.** If two tables only relate through a
  multi-valued join (e.g. a customer with multiple concurrent accounts, a
  product in multiple categories), do not silently set a many-to-many
  relationship or fabricate a bridge table's grain. Present the fork: which
  side should be the "many," does a bridge table need to be built from the
  data, and what does that do to measure totals (double-counting risk).
- **Bidirectional filtering.** Team convention is to avoid it by default —
  never reach for it as a quick fix when "the filter isn't reaching the
  table I expected" (that's usually a sign the model shape is wrong).  Only
  propose it with a stated reason tied to a specific cross-filtering
  requirement in the brief, and if used, explicitly note in `NOTES.md` that
  it needs to be tested for correct results (a bidirectional relationship
  can silently produce wrong totals via filter loops).
- **Conflicting candidate keys.** If a dimension could be keyed on more than
  one plausible column (e.g. both `Email` and `CustomerID` look unique),
  ask which one to treat as authoritative rather than picking one.
- **Role-playing dimensions.** If a fact table has multiple date columns
  that could each relate to `Dim Date` (e.g. `OrderDate` and `ShipDate`),
  ask which is the primary analytical date (single active relationship)
  before deciding whether the others need inactive relationships +
  `USERELATIONSHIP` measures — this is real added complexity, not a default.
- **Slowly changing dimensions.** If source data implies an attribute
  changes over time (e.g. a customer's region), ask whether the assignment
  needs historical accuracy (SCD Type 2) or a current-state snapshot is
  fine — don't assume the more complex option is wanted by default.

## Situations that are fine to resolve without asking

- Which column is the key when only one column is plausibly unique.
- Straightforward fact/dimension split when the source data is already
  close to that shape (e.g. one wide "orders" file plus a separate
  "customers" file).
- Standard single-direction fact→dimension relationships.
