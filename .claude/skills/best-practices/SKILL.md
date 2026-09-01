---
name: best-practices
description: Points to the team's internal Power BI best-practices reference (now populated). Load this to check the authoritative team conventions before modeling, writing Power Query, or writing DAX — it can override the general guidance in the other skill files.
---

# Team best practices — status: populated

The full reference lives at
[`docs/best-practices/power-bi-best-practices.md`](../../../docs/best-practices/power-bi-best-practices.md),
converted from the team's internal `PowerBI Best Practices + Checklists.xlsx`.
It is **authoritative** — where anything in another skill file conflicts with
it, this wins. The other skill files have already been updated to align, but
if you notice a mismatch, trust the best-practices doc and fix the skill
file, don't silently follow the stale skill guidance.

## The non-negotiables (read the full doc for everything else)

- One-to-many Dim→Fact relationships by default. Many-to-many is never the
  default — see `../data-modeling-decisions/SKILL.md`.
- Avoid bi-directional filters by default.
- Star schema by default.
- A dedicated Measures table, with subfolders once there are many measures.
- **Never implicit measures** in visuals — always explicit.
- Always format DAX code.
- Custom `Dim Date` table; `Date` type for date columns, not `Date/Time`;
  never store timestamps.
- Type every column explicitly in Power Query — never leave a column as the
  generic `ABC123` (Any) type.
- Business names on tables/fields — no `DIM`/`FACT` prefix needed on the
  name itself.
- Load only required columns; filter early in Power Query; take advantage
  of query folding where the source supports it.

## What's NOT the agent's job

The best-practices doc also covers Power BI Desktop application settings
(e.g. disabling Auto Date/Time, parallel loading options), Power BI Service
configuration (gateways, refresh schedules, RLS in the Service), and release
process steps (workspace promotion, go-live communication). Those happen
after a human opens the generated `.pbip` in Desktop — don't attempt to
configure them, but do flag the relevant ones in a project's `NOTES.md` as
follow-up steps for the human, per the doc's closing section.
