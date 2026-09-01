---
name: pbip-tmdl-structure
description: Use when creating or editing a Power BI Project (PBIP) — the folder layout, file naming, and TMDL syntax for tables, relationships, and the model file. Load before writing any .tmdl file.
---

# PBIP / TMDL structure

See also `../best-practices/SKILL.md` — this file implements the team's
model-structure conventions from
`docs/best-practices/power-bi-best-practices.md`; if the two ever disagree,
the best-practices doc wins.

## Folder layout for one project

Everything for one deliverable lives under `projects/<project-name>/`:

```
projects/<project-name>/
  <ProjectName>.pbip                          # pointer file, opens in PBI Desktop
  <ProjectName>.Report/
    definition/                               # report pages/visuals (best-effort, see CLAUDE.md §2)
    .platform
  <ProjectName>.SemanticModel/
    definition/
      database.tmdl
      model.tmdl
      relationships.tmdl
      tables/
        <TableName>.tmdl                      # one file per table
      cultures/
        en-US.tmdl
    definition.pbism
    .platform
  NOTES.md                                    # run-to-run memory (required, see CLAUDE.md §0)
  ANALYSIS.md                                 # written findings, if requested
```

Use `PascalCase` for `<ProjectName>` and table names, matching the source
entity they represent (e.g. `Sales`, `Customer`, `Product`).

## Naming convention

**Plain business names, no `Fact`/`Dim` prefix** — e.g. `Sales`, `Customer`,
`Date`, not `Fact Sales` / `Dim Customer` / `Dim Date`. See
`docs/decisions/0008-drop-fact-dim-table-prefixes.md`: this was a live naming
tension between this file and `docs/best-practices/power-bi-best-practices.md`
("clear business names — you don't need DIM/FACT prefix"), resolved in favor
of the best-practices doc, which is authoritative per
`../best-practices/SKILL.md`.

The rest of this repo's skill files still use the words "fact table" and
"dimension table" freely — that's describing a table's **role** in the star
schema (one row per transaction/event vs. one row per business entity), not
prescribing a literal name prefix. Don't read "Dim Customer" in an example
elsewhere as an instruction to prefix the actual table name; it may be a
holdover from before decision 0008 — treat the plain-name convention as
current and fix any example you find that still shows a prefix.

- Always include an explicit date dimension table (named `Date`, not
  `Dim Date`) marked as a date table in `model.tmdl` (`dataCategory: Time`
  and `variation` set to its Date column) rather than relying on auto
  date/time.
- Measures live in a dedicated `_Measures` table (no data columns, just
  measures) so they're easy to find in the model tree — see
  `../dax-measures/SKILL.md`. This is the one exception to "no prefix",
  since `_Measures` isn't a business entity — the leading underscore is
  there to sort it to the top of the model tree.

## TMDL basics

TMDL is indentation-sensitive (like YAML), not brace-delimited. A minimal
table file:

```tmdl
table 'Sales'

	column OrderDate
		dataType: dateTime
		formatString: Long Date
		sourceColumn: OrderDate

	column Quantity
		dataType: int64
		sourceColumn: Quantity
		summarizeBy: sum

	partition 'Sales' = m
		mode: import
		source =
			let
				Source = ...
			in
				Source
```

Key rules:
- Table/column names with spaces are single-quoted: `'Sales'`.
- Indentation is one tab per nesting level — be consistent, don't mix tabs
  and spaces.
- Every table's data is loaded via a `partition ... = m` block whose `source`
  is the Power Query M expression (see `../power-query-conventions/SKILL.md`
  for how to write that expression).
- Set `summarizeBy: none` on any numeric column that is a key or shouldn't
  auto-aggregate (e.g. an ID stored as a number) — leaving Power BI's default
  aggregation on ID-like numeric columns is a common, easy-to-miss mistake.
- **TMDL has exactly one comment form at the document level: `///`, and it
  must attach with zero blank lines to the object it documents.** Confirmed
  against real Power BI Desktop (June 2026 release), across two separate
  errors:
  1. A `///` block with a blank line before the object it documents (or
     before a second `///` block) fails with
     `InvalidLineType: Unexpected line type: Empty!` — `///` opens a
     "pending documentation" state that cannot contain a blank line before
     it attaches to a declaration.
  2. **`//` (double-slash) is not valid TMDL syntax at all** — Desktop's
     parser doesn't recognize it as any known line type and fails with
     `InvalidLineType: Unexpected line type: Other!`. Don't reach for `//`
     as a workaround for problem 1; it produces a different failure, not a
     fix. (`//` *is* valid — but only inside an M expression, i.e. within a
     `partition ... = m` / `source =` block. That's a different, nested
     language with its own comment syntax, not the TMDL document itself.)

  The only correct pattern for a comment that logically covers more than
  just the next single declaration (e.g. general context before the first
  of several related objects) is one continuous `///` block with **no
  blank text lines**, using a bare `///` (three slashes, nothing after) as
  a paragraph break where you'd otherwise want a blank line:

  ```tmdl
  /// General context that applies to everything below.
  ///
  /// Then the specific note for the object immediately following.
  relationship Sales_OrderDate_to_Date
  	fromColumn: 'Sales'.'Order Date'
  	toColumn: 'Date'.Date
  ```

  If a comment doesn't belong to any specific following object at all,
  don't force it into a `///` block — put that context in the project's
  `NOTES.md`/`ANALYSIS.md` instead, or drop it.

  **Watch specifically for decorative section-header dividers** (e.g.
  `/// ---------------------------- Sales` before a group of measures that
  share a `displayFolder`) — this is the shape that breaks in practice,
  because it's naturally followed by a blank line for visual spacing before
  the next `///` block or object. It's also **repetitive**: a `_Measures`
  table grouped into several `displayFolder`s will have one of these before
  *every* group, so a single miss compounds into several parse failures
  found one Desktop-open at a time instead of caught all at once. When
  checking your own output for this, grep for a divider-style pattern (e.g.
  `/// -{3,}`) specifically, in addition to the generic
  blank-line-after-`///` check — and make sure that check strips leading
  whitespace before matching `///`, since these dividers are typically
  indented inside a table body, not at column 0.

- **Not every object type supports `///` at all — check before you attach
  one.** `///` compiles to the TOM `Description` property, and not every
  TOM class has one. This is a semantic-deserialization error, not a
  parse error, so it fails late — after every file has parsed
  syntactically clean — with **no file or line number**, just
  `Property 'description' is unknown and is not expected in the situation
  it appears.` Confirmed against real Power BI Desktop (June 2026
  release):
  - `Relationship` has **no** `Description` property (confirmed via the
    .NET API reference — its full property list is Annotations,
    ChangedProperties, CrossFilteringBehavior, ExtendedProperties,
    FromTable, IsActive, IsRemoved, JoinOnDateBehavior, ModifiedTime, Name,
    ObjectType, Parent, RefreshedTime, RelyOnReferentialIntegrity,
    SecurityFilteringBehavior, State, ToTable, Type — no description).
    **Never put a `///` comment directly above a `relationship`
    declaration.** If you want to explain a relationship's rationale
    (e.g. why it's bidirectional, why a snowflake was flattened), put that
    in the project's `NOTES.md`/`ANALYSIS.md`, or fold it into the
    `Description` of one of the two tables it connects — not on the
    relationship itself.
  - `Annotation` also has **no** `Description` property (Name and Value
    only). **Never put a `///` comment directly above an `annotation`
    line.** If the annotation needs explaining (e.g. why
    `__PBI_TimeIntelligenceEnabled` is set to `0`), put the `///` comment
    on the enclosing `table`/`model` object instead.
  - Confirmed to work: `table`, `column`, `measure`, `expression`
    (NamedExpression), and `model` all support `Description` via `///`.
  - When in doubt about a type not listed here (`partition`, `culture`,
    `perspective`, `role`, `hierarchy`, `level`), check the corresponding
    class on `learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.<classname>`
    for a `Description` property before attaching a `///` comment to it —
    don't assume.

## Relationships

Defined in `relationships.tmdl`, one block per relationship:

```tmdl
relationship <GUID-or-stable-id>
	fromColumn: 'Sales'.CustomerKey
	toColumn: 'Customer'.CustomerKey
	crossFilteringBehavior: oneDirection
```

- The TOM enum value is `oneDirection`, not `singleDirection` — a bug in an
  earlier version of this file. It's usually safest to omit
  `crossFilteringBehavior` entirely when you want the default (one
  direction, dimension filters fact) and only state it explicitly for
  `bothDirections`.
- Default to one direction (dimension filters fact). Only use
  `bothDirections` when there's a specific, understood reason — bidirectional
  filtering can silently produce wrong totals, and is exactly the kind of
  choice that belongs in `docs/decisions/` when it comes up, not a silent
  default (see `../data-modeling-decisions/SKILL.md`).
- Every relationship should be `many` (fact) to `one` (dimension). If the
  natural relationship isn't many-to-one, that's a modeling cross-roads —
  don't just set `crossFilteringBehavior: bothDirections` or a
  many-to-many relationship as a workaround without flagging it per
  CLAUDE.md §1.

## Model viewer layout (team convention)

Organize the model diagram/perspective layout so it's reviewable at a
glance:

- One view/tab showing **all fact-role tables at the bottom and all
  dimension tables at the top** (role, not name prefix — see the naming
  convention above).
- One view/tab **per fact-role table**, showing that fact and its full
  surrounding star schema only.

In TMDL this maps to `perspective` blocks (or, if the tooling in use doesn't
support authoring diagram layout directly in TMDL, note it in `NOTES.md` as
a manual step for the human to arrange in Desktop's model view).

## Date columns and Auto Date/Time

- Date columns use the `date` data type, not `dateTime`, unless
  time-of-day is genuinely part of the grain.
- Disable Power BI's automatic date/time tables — they're redundant with an
  explicit `Dim Date` and waste RAM. In `model.tmdl` this is expressed as:
  ```tmdl
  model Model
  	...
  	annotation __PBI_TimeIntelligenceEnabled = 0
  ```
  Verify this annotation against a real Desktop-exported PBIP if it doesn't
  match what you see — TMDL's exact annotation keys can shift across Power
  BI Desktop versions.

## Dataset size

Once a project's data is in place, note the resulting `.SemanticModel`
folder's on-disk size in `NOTES.md`. Flag it (don't silently ignore it) if
it looks likely to exceed 200MB, or if the assignment implies growth that
could push it past 1GB over time — per team convention, that's worth a
comment recommending optimization (unused columns, split fact grain, etc.)
rather than building forward as if size were a non-issue.

## The root `.pbip` file's schema

Confirmed against real Power BI Desktop (June 2026 release) after it
rejected a wrong value here: the root `<ProjectName>.pbip` file's `$schema`
must be exactly
`https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json`
— **not** `fabric/item/pbip/definitionProperties/...` (that `item/`-prefixed
pattern is for report/dataset definition files, e.g. `definition.pbir` uses
`fabric/item/report/definitionProperties/...`; the root pbip pointer file
is a different, non-`item` schema family). Desktop fails to open the
project at all if this is wrong, before it even gets to validate anything
else — so it's worth getting this one exactly right rather than leaving it
to the Desktop-rejection fallback table below.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
  "version": "1.0",
  "artifacts": [{ "report": { "path": "<ProjectName>.Report" } }],
  "settings": { "enableAutoRecovery": true }
}
```

## Validating your own output

Before finishing a run that touched TMDL, sanity-check:
- Every table referenced in `relationships.tmdl` actually exists as a `.tmdl`
  file with a matching name.
- Every column referenced in a relationship exists in that table with a
  matching name and compatible data type.
- `model.tmdl` lists all tables and sets the date table / culture.
- No two tables claim the same column name for a relationship key unless
  that's intentional and consistent.
