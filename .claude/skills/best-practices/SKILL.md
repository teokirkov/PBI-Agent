---
name: best-practices
description: Points to the team's internal Power BI best-practices reference. Currently a placeholder — the source spreadsheet has not yet been converted into this repo. Load anyway to check status before assuming conventions from other skills are the full picture.
---

# Team best practices — status: not yet populated

The user has an internal "Power BI best practices" spreadsheet that will be
converted into markdown and dropped into `docs/best-practices/` in a later
pass. Until that happens, `docs/best-practices/` is empty and this skill has
nothing team-specific to add beyond the general conventions already covered
in:

- `../pbip-tmdl-structure/SKILL.md`
- `../power-query-conventions/SKILL.md`
- `../dax-measures/SKILL.md`
- `../data-modeling-decisions/SKILL.md`

**When the spreadsheet is converted:** it should land as one or more `.md`
files under `docs/best-practices/`, and this file should be updated to
summarize and link to them, so this skill remains the entry point domain
work checks first. If team conventions in that spreadsheet conflict with
anything in the other skill files above, the team's best-practices document
wins — update the other skill files to match rather than leaving two
contradictory conventions in the repo.

If you are a Claude run and this file still says "not yet populated" but you
can see content under `docs/best-practices/`, treat that as a sign this
SKILL.md is stale — read the best-practices docs directly and flag in your
run's `NOTES.md` that this skill file needs a follow-up update.
