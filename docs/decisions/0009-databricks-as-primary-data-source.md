# 0009 — Databricks becomes the default data source; assignment/feedback move to comments

- **Project:** repo-wide (infrastructure + workflow convention)
- **Date:** 2026-09-01
- **Status:** decided

## The fork in the road

BI Task 1 was originally built from seven `.xlsx` files committed to
`docs/sample-data/bi-task-1/`, because the GitHub Action can't authenticate
to SharePoint (see `sharepoint-data-ingestion/SKILL.md`) and file drop was
the only available path at the time. Separately, the assignment brief was
committed as a PDF to `docs/assignment/`.

Two things changed: (1) the same tables are available in the org's
Databricks warehouse (`dss_demos.bi_tasks.*`), and a connectivity test
confirmed the GitHub Actions runner can reach the workspace over the network
(`.github/workflows/test-databricks-connectivity.yml`); (2) for this to work
for a real client engagement, not just this test project, the assignment and
ongoing feedback need to arrive the way a client would actually give them —
as comments on the issue — not as files someone commits to the repo on the
client's behalf.

## What was decided

1. **Databricks is now the default data source**, via a new
   `databricks-ingestion` skill. `docs/sample-data/` /
   `sharepoint-data-ingestion` remain valid for the explicit "small report
   sourced from files" exception the best-practices doc carves out, but
   aren't the default anymore.
2. **The assignment and ongoing feedback default to arriving as comments**
   on the triggering issue, not as committed files. `docs/assignment/`
   remains a valid optional archive location, but `CLAUDE.md`'s Discover
   step now reads the comment thread first.
3. BI Task 1's original `docs/sample-data/bi-task-1/*.xlsx` files were
   removed from the working tree (still recoverable from git history if
   ever needed) since the project now sources from Databricks instead.

## Why

Realism for how this agent will actually be used with a client: a client
won't `git commit` a brief or a data export, they'll comment. And sourcing
from the actual warehouse instead of one-off file exports matches the
best-practices doc's own stated default (DWH-sourced, files as the
exception) rather than fighting it.

## Consequences

- `CLAUDE.md` §0 and §3, and the skills list in §4, updated to reflect
  comment-first discovery and Databricks-first ingestion.
- `.github/workflows/claude.yml` now injects `DATABRICKS_TOKEN` (secret),
  `DATABRICKS_HOST`, and `DATABRICKS_HTTP_PATH` (variables) into the job
  environment.
- **Not yet done as of this entry**: BI Task 1's actual `.tmdl` partitions
  still use the old `Excel.Workbook(File.Contents(SourceFolderPath & ...))`
  M source, not the new Databricks connector. Rewriting those seven
  partitions (plus the three staging expressions) to source from
  `dss_demos.bi_tasks.*` per `databricks-ingestion/SKILL.md` is follow-up
  work for the next run, not done as part of this decision.
- Existing `docs/assignment/bi-task-1.pdf` was left in place as historical
  record — this decision changes the convention going forward, not
  retroactively.
