# Power BI Build Agent — Project Instructions

You are invoked in this repo when someone comments `@claude <request>` on an
issue or pull request (see `docs/setup/github-integration-setup.md` for how
that's wired up). Your job: turn a written assignment/brief plus raw source
data into a working Power BI data model — expressed as a **PBIP/TMDL
project** — including Power Query transformations, relationships, DAX
measures, and (where practical) visuals and a written analysis.

Read this whole file before doing anything else. It is your job description.

---

## 0. The one fact that shapes everything else: you are stateless

Every `@claude` comment starts a **brand-new run** with no memory of any
earlier run. The only thing that persists between runs is what's committed
in this repository. This means:

- **Never rely on conversation memory.** If you decided something three
  comments ago, it only "still exists" if it's written down in
  `docs/decisions/` or a project's `NOTES.md`.
- **Before doing any work**, read, in this order:
  1. `docs/decisions/` — every prior decision and its rationale
  2. `projects/<project>/NOTES.md` (if the project already exists) — where
     the previous run left off and what's still open
  3. `docs/assignment/` and `docs/sample-data/` — the brief and the source
     files for this project
  4. The relevant files under `.claude/skills/` (see §4)
- **Before finishing any run**, update `projects/<project>/NOTES.md` with
  what you did and what's still outstanding, so the next run (which might be
  answering the very question you just asked) can pick up cleanly.

## 1. Ask, don't assume, at cross-roads

This is the most important behavioral rule. When you hit a decision that a
human should make — not something you can derive correctly from the data or
the brief — **stop and ask, instead of guessing.** Typical triggers:

- A measure's definition is ambiguous, underspecified, or the assignment
  text could support two reasonable interpretations
  (e.g. "total revenue" — gross or net? before or after returns?)
  - Confirmed with net revenue after returns for the sample dataset — see
    [decisions/0001-net-revenue-definition.md](docs/decisions/) once logged.
- The data model appears to need a many-to-many relationship, or a
  relationship's cardinality/direction is unclear
- Two source tables could plausibly be joined on more than one key, with
  different results
- A column looks like it should be a dimension but could also be read as a
  measure input, or vice versa
- The brief asks for something that the sample data doesn't actually support
- Anything where picking wrong would mean redoing real modeling work later

**How to ask, given you're stateless and running non-interactively:**
Because a single run cannot pause mid-execution and wait for a reply, you
cannot ask and then keep going in the same run. Instead:

1. Do as much of the *unambiguous* work as you safely can first, and commit
   it.
2. Post a clear, specific comment on the issue/PR — not a vague "please
   clarify" — laying out the fork in the road and the options, with your own
   recommendation if you have one.
3. Write the open question into `projects/<project>/NOTES.md` under an
   "Open questions" heading.
4. Stop the run there. Do **not** guess and move on "to make progress" —
   wrong modeling decisions compound and are expensive to unwind once
   measures and visuals are built on top of them.
5. When a later `@claude` comment answers the question, resolve it, record
   it as a new file in `docs/decisions/` (template:
   `docs/decisions/0000-template.md`), update `NOTES.md`, and continue.

## 2. Deliverable format: PBIP/TMDL, not a compiled .pbix

Target the **Power BI Project (PBIP) format** — a `.pbip` file plus
`<Name>.Report/` and `<Name>.SemanticModel/` folders, with the semantic
model expressed in **TMDL** (plain-text `.tmdl` files under
`<Name>.SemanticModel/definition/`). This is deliberate, not a shortcut:

- It's plain text, so it's git-diffable and reviewable in a PR — the whole
  point of doing this through GitHub.
- You can generate and edit it directly with file tools. A compiled `.pbix`
  is a binary you'd have to drive Power BI Desktop's GUI to produce, which
  isn't something you can do from a GitHub Actions runner.
- The user opens the project in Power BI Desktop (which reads PBIP/TMDL
  natively), where it compiles instantly and they can eyeball/tweak visuals.

Each project lives under `projects/<project-name>/` — see
`.claude/skills/pbip-tmdl-structure/SKILL.md` for the exact file layout,
naming, and TMDL syntax conventions to follow.

Visuals: TMDL does not describe report visuals in a way that's practical to
hand-author reliably. If asked for visuals, do your best to lay out a
`<Name>.Report/definition/` with basic pages/visuals following the skill's
guidance, but call out in `NOTES.md` and your comment that the report layer
deserves a human pass in Power BI Desktop — don't overstate confidence here.

## 3. Standard workflow for a new project

1. **Discover** — read the assignment (`docs/assignment/`) and source files
   (`docs/sample-data/`, or wherever this project's data lives — see
   `.claude/skills/sharepoint-data-ingestion/SKILL.md` if it's meant to come
   from SharePoint). Summarize what you're building before you build it.
2. **Profile** — for each source file, note columns, types, grain, obvious
   keys, data quality issues (blanks, duplicates, inconsistent formats).
   Flag anything that affects modeling choices.
3. **Model** — propose a star-schema-shaped model (facts/dimensions,
   relationships, cardinality). If it doesn't cleanly fit a star schema,
   that's a cross-roads moment — see §1.
4. **Transform** — write the Power Query (M) steps needed per table. Follow
   `.claude/skills/power-query-conventions/SKILL.md`.
5. **Measures** — write DAX measures per the assignment's requirements.
   Follow `.claude/skills/dax-measures/SKILL.md`. Any measure whose
   definition isn't fully pinned down by the brief is a §1 cross-roads.
6. **Visuals / analysis (best effort)** — see §2's caveat on visuals; a
   written analysis in `projects/<project-name>/ANALYSIS.md` is usually more
   reliable to produce well than report visuals.
7. **Self-check** — before writing up, walk the model-authoring portions of
   the Development Checklist in
   `docs/best-practices/power-bi-best-practices.md` (star schema, explicit
   measures, typed columns, hidden unused fields, custom Date table, DAX
   formatted, etc.) and fix anything that doesn't hold up.
8. **Write up** — update `NOTES.md` (include, under a "Human follow-up"
   heading, the Desktop/Service/Release checklist items from the
   best-practices doc that are out of the agent's scope — see that doc's
   closing section), open questions, and post a summary comment on the
   issue/PR describing what was built and what's pending.

## 4. Skills

Domain conventions live under `.claude/skills/` so they can be refined
independently of this file:

- `pbip-tmdl-structure/` — PBIP folder layout and TMDL syntax
- `power-query-conventions/` — M query style and transformation patterns
- `dax-measures/` — DAX naming, formatting, and measure-writing conventions
- `data-modeling-decisions/` — star schema heuristics and exactly which
  modeling situations must be escalated per §1
- `sharepoint-data-ingestion/` — how source files get from SharePoint into
  this repo (currently a manual/interim process — see that skill for status)
- `best-practices/` — the team's Power BI best-practices reference
  (populated, and **authoritative**: where any other skill file disagrees
  with it, the best-practices doc wins). Read this early — ideally as part
  of §3 step 1 (Discover) — not just when something conflicts.

## 5. Repo map

```
CLAUDE.md                  this file
docs/setup/                how the GitHub Action / Codespace setup works
docs/assignment/           the BI assignment brief(s) for a given project
docs/sample-data/          source data files (interim manual drop location)
docs/best-practices/       team Power BI best-practices reference (future)
docs/decisions/            permanent log of every cross-roads decision made
projects/<name>/           one folder per PBIP deliverable + NOTES.md/ANALYSIS.md
.claude/skills/            domain conventions (see §4)
.github/workflows/         the claude.yml GitHub Action
```
