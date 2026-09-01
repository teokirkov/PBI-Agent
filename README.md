# Power BI Build Agent

A GitHub-resident Claude agent (via `@claude` comments, powered by
[claude-code-action](https://github.com/anthropics/claude-code-action) —
not GitHub Copilot) that turns a written BI assignment plus source data
into a **Power BI Project (PBIP/TMDL)**: data model, Power Query
transformations, DAX measures, and (best-effort) visuals and analysis.

## How it works

1. You (or the app) trigger a run with an `@claude <request>` comment on an
   issue or PR.
2. Claude reads `CLAUDE.md` (its job description) and the relevant
   `.claude/skills/*/SKILL.md` files (domain conventions), plus this repo's
   accumulated decision log (`docs/decisions/`) — since every run is
   stateless, the repo *is* its memory.
3. It profiles the source data, proposes a model, writes Power Query and
   DAX, and commits the result under `projects/<project-name>/` — usually
   via a PR so it's reviewable.
4. Wherever a modeling or measure decision is genuinely ambiguous (a
   many-to-many relationship, an underspecified metric, etc.), it stops and
   asks in a comment instead of guessing. Answer it with another `@claude`
   comment; the decision gets logged to `docs/decisions/` so future runs
   remember it.
5. Open the resulting `.pbip` in Power BI Desktop to compile it and finish
   any visuals by hand.

## First-time setup

Not set up yet? Follow
[`docs/setup/github-integration-setup.md`](docs/setup/github-integration-setup.md)
top to bottom — it covers creating the repo, wiring up the GitHub App and
Actions workflow, and adding your `ANTHROPIC_API_KEY` secret.

## Repo map

| Path | Purpose |
|---|---|
| `CLAUDE.md` | The agent's job description — read this first |
| `.claude/skills/` | Domain conventions (TMDL, Power Query, DAX, modeling, SharePoint ingestion, best practices) |
| `docs/assignment/` | Assignment briefs per project |
| `docs/sample-data/` | Source data files (interim manual drop location — see the SharePoint ingestion skill) |
| `docs/best-practices/` | Team best-practices reference (placeholder, to be filled in later) |
| `docs/decisions/` | Permanent log of every cross-roads decision, with rationale |
| `projects/<name>/` | Each PBIP deliverable, plus its `NOTES.md`/`ANALYSIS.md` |
| `.github/workflows/claude.yml` | The GitHub Action that runs Claude on `@claude` comments |

## Known open items

- **SharePoint access is currently manual.** The Action can't authenticate
  to `marlabseur.sharepoint.com` — files need to be downloaded and committed
  to `docs/sample-data/`, or attached to the triggering issue, until
  automated ingestion is built (see
  `.claude/skills/sharepoint-data-ingestion/SKILL.md`).
- **Visuals are best-effort.** TMDL/PBIP doesn't lend itself to reliably
  hand-authoring report visuals; expect the semantic model (tables, Power
  Query, measures) to be solid, and the report layer to need a human pass in
  Power BI Desktop.
- **Best-practices doc not yet added.** Placeholder exists at
  `docs/best-practices/` for the team's internal best-practices spreadsheet,
  to be converted to markdown in a later pass.
- **`allowedTools` may need widening** for the Action to reliably read
  `.xlsx` sources (e.g. Python + pandas via `Bash`) — currently scoped
  narrowly (`WebSearch,WebFetch,Read,Write,Edit,Bash(git:*)`) as a
  deliberate, conservative starting point. See the note in
  `docs/setup/github-integration-setup.md` Step 8.
