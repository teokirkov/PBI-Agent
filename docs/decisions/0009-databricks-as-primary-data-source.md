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

---

## Status of the Power Query rewrite

**Done** on 2026-09-01 (issue #1, branch `claude/issue-1-20260901-1512`),
closing the "Not yet done as of this entry" consequence above. The seven
partitions and the staging expressions now read from `dss_demos.bi_tasks.*`;
`SourceFolderPath` is retired and `Excel.Workbook` / `File.Contents` /
`SourceFolderPath` are now hard failures in
`projects/bi-task-1/validate_tmdl.py`, so a half-applied migration cannot pass
review.

The consequence text above is deliberately left as written — it recorded what
was true when the decision was taken, and this section records what changed
since. Same convention as `0008`.

**One thing this rewrite found that the decision could not have anticipated.**
The warehouse copy is not a faithful transcription of the `.xlsx` files:

- `sales` has 33 columns, not 35. The two redundant `UnitPrice` duplicates are
  gone, which is an improvement — the old query had to keep Excel's
  `Column1..Column35` names and pick columns *by position* to dodge the
  duplicate header, and that workaround is now deleted.
- But the copy that survived is the **currency-formatted text** one, not the
  numeric one the model was reading. And the currency symbol is corrupted:
  `£13.00` is stored as `?13.00`, confirmed with `HEX()` inside Databricks
  (leading byte `3F`, a real ASCII question mark), so the `£` was lost to a
  non-UTF8 encoding during the load into the warehouse. `TaxRate` and
  `AccountOpenedDate` likewise arrive as text where the extract had a number
  and a date.

So "only the source step changes" turned out to be *nearly* true but not
exactly: parsing that the file-based model got for free now has to be explicit.
It is isolated in one `fnParseMoney` expression plus two inline parses, and
every headline figure was recomputed in the warehouse and reconciles to the
penny with the pre-migration numbers, so no reported number moved. The encoding
itself should still be fixed at source — logged as `ANALYSIS.md` §5.6.

**Update, same day:** the navigation shape *was* wrong on first open, exactly
as flagged — `Kind = "Catalog"` isn't a real value; the connector uses
`Kind = "Database"` for that level. Confirmed against Microsoft's own
Azure Databricks connector docs and fixed in the single shared
`DatabricksBiTasks` expression (see `projects/bi-task-1/NOTES.md`, "Human,
eighth Desktop attempt"). **Data refresh from Databricks is now confirmed
working end to end in real Power BI Desktop** — this is no longer an open
risk, it's a verified, working connection.
