# 0008 — Drop `Fact`/`Dim` table name prefixes; use plain business names

- **Project:** repo-wide (naming convention, applies to every project)
- **Date:** 2026-09-01
- **Status:** decided — supersedes the naming convention in
  `.claude/skills/pbip-tmdl-structure/SKILL.md` as it stood for the BI Task 1
  build

## The fork in the road

`docs/best-practices/power-bi-best-practices.md` (authoritative team
convention) says: *"Tables and fields must have clear business names — you
don't need DIM/FACT prefix."* `.claude/skills/pbip-tmdl-structure/SKILL.md`,
as originally written, said the opposite: `Fact <Subject>` / `Dim <Subject>`
naming. The BI Task 1 model was built under the skill file's (wrong) reading,
using `Fact Sales`, `Dim Customer`, `Dim Date`, etc. — approved at the time on
issue #1, before the conflict was noticed. The agent itself flagged the
contradiction in `projects/bi-task-1/NOTES.md` §7.2 and asked for one document
to be corrected.

## What was decided

Plain business names, no prefix: `Sales`, `Customer`, `Date`, `Product`,
`Supplier`, `Package Type`, `Category`. The one exception is the measures
table, `_Measures` — kept as-is, since it isn't a business entity and the
leading underscore exists to sort it to the top of the model tree, not to
mark it as a "fact" or "dimension."

`.claude/skills/pbip-tmdl-structure/SKILL.md` has been corrected to match.

## Why

The best-practices doc is the authoritative source per
`.claude/skills/best-practices/SKILL.md` — where the two disagree, it wins.
No reasoning beyond that was given; this is a straightforward correction of
which document was wrong, not a judgment call.

## Consequences

- The already-built BI Task 1 model (`Fact Sales`, `Dim Customer`, `Dim Date`,
  `Dim Product`, `Dim Supplier`, `Dim Package Type`, `Dim Category`,
  `Bridge Product Category`) needs to be renamed to plain business names
  before report visuals are built — renaming after visuals exist would mean
  re-binding every visual's field references. This is tracked as follow-up
  work on issue #1, not done as part of this decision entry.
- Renaming touches: the table's `table 'X'` declaration in its own `.tmdl`
  file (and the filename itself), every `fromColumn`/`toColumn` reference in
  `relationships.tmdl`, every DAX table reference in `_Measures.tmdl`
  (`SUM('Fact Sales'[...])` → `SUM('Sales'[...])`, etc.), and any
  `USERELATIONSHIP`/`RELATED` calls. Re-run the "Validating your own output"
  checklist in `pbip-tmdl-structure/SKILL.md` after renaming — it's exactly
  the kind of mechanical, wide-reaching change that checklist exists to catch
  a missed reference in.
- "Fact table" / "dimension table" remain fine as role terminology in prose
  across the skill files — only the literal name prefix is dropped.

## Status of the rename

**Done** on 2026-09-01 (issue #1, branch `claude/issue-1-20260901-1203`),
before any report visuals existed, so nothing had to be re-bound. Verified with
`projects/bi-task-1/validate_tmdl.py`, added in the same commit to mechanise
the "Validating your own output" checklist this entry points at.

Decisions `0002`–`0007` were **deliberately left unedited**: they are a
permanent log of what was decided at the time, and rewriting them to match a
later naming convention would falsify that record. The consequence is that
their examples still read `Dim Product[Category Group]` and similar. A future
run should take current table names from `projects/bi-task-1/NOTES.md` §2, not
from an ADR — this is flagged at the top of that file.
