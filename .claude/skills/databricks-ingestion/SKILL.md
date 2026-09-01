---
name: databricks-ingestion
description: Use when a project's source data lives in the org's Databricks/Unity Catalog warehouse rather than local files. Covers how the agent profiles tables at build time via the REST API, and how the final model's Power Query connects at open-time via the Databricks connector.
---

# Databricks ingestion

This is now the **primary** data source for this agent's projects — confirmed
reachable from the GitHub Actions runner (see
`docs/decisions/0009-databricks-as-primary-data-source.md`). Local file drops
(`../sharepoint-data-ingestion/SKILL.md`) remain valid for the "small,
file-sourced report" exception the best-practices doc carves out, but default
to Databricks when the data is there.

## Credentials available to a run

Set as GitHub Actions secrets/variables and injected into the job
environment via `.github/workflows/claude.yml`:

- `DATABRICKS_TOKEN` (secret) — a personal access token scoped to `sql` +
  `unity-catalog` only (see `docs/decisions/0009...` for why not broader).
  Never print this value, never write it into a committed file — it's only
  ever read from the environment.
- `DATABRICKS_HOST` (variable, not secret) — workspace hostname, e.g.
  `adb-1234567890123456.7.azuredatabricks.net`. No `https://` prefix, no
  trailing slash.
- `DATABRICKS_HTTP_PATH` (variable, not secret) — the SQL warehouse's HTTP
  path, e.g. `/sql/1.0/warehouses/abc123def4567890`. Found in Databricks:
  the SQL warehouse → **Connection details** tab → **HTTP path**. The
  trailing segment (`abc123def4567890`) is also the warehouse's
  `warehouse_id`, used directly by the REST API below.

If any of these three are empty/unset when a run needs them, stop and post a
comment asking for them rather than guessing or falling back to files
silently — this is a hard capability boundary like the SharePoint one, not a
judgment call.

## Table naming convention

`<catalog>.<schema>.<table>`, e.g. `dss_demos.bi_tasks.customer`. Get the
exact catalog/schema from the assignment or the triggering comment — don't
assume `dss_demos.bi_tasks` is fixed across projects, it's this project's
location.

## How the agent profiles data during a build (Discover/Profile)

Use `python3` (already an allowed `Bash` tool) with the standard library
(`urllib.request`) or `requests` (pip install if needed) to call the
**SQL Statement Execution API** — this is REST, not the M/Power Query
engine, which only runs inside Power BI Desktop and isn't usable from a
Linux Actions runner.

```python
import os, json, time, urllib.request

host = os.environ["DATABRICKS_HOST"]
token = os.environ["DATABRICKS_TOKEN"]
http_path = os.environ["DATABRICKS_HTTP_PATH"]
warehouse_id = http_path.rstrip("/").split("/")[-1]

def run_sql(statement, wait_timeout="30s"):
    req = urllib.request.Request(
        f"https://{host}/api/2.0/sql/statements",
        data=json.dumps({
            "warehouse_id": warehouse_id,
            "statement": statement,
            "wait_timeout": wait_timeout,
        }).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)

# Schema/grain profiling
print(run_sql("DESCRIBE TABLE dss_demos.bi_tasks.customer"))

# Sampling — always LIMIT, never pull a full large fact table into the
# profiling step
print(run_sql("SELECT * FROM dss_demos.bi_tasks.sales LIMIT 200"))

# Row counts, distinct-key checks, etc. - same run_sql() pattern
print(run_sql("SELECT COUNT(*) FROM dss_demos.bi_tasks.sales"))
```

If the exact table names in a schema aren't already known (e.g. from the
assignment comment), list them via the Unity Catalog metadata API instead of
guessing:

```python
req = urllib.request.Request(
    f"https://{host}/api/2.0/unity-catalog/tables?catalog_name=dss_demos&schema_name=bi_tasks",
    headers={"Authorization": f"Bearer {token}"},
)
```

A statement that takes longer than `wait_timeout` returns a `PENDING`/
`RUNNING` state with a `statement_id` — poll
`GET /api/2.0/sql/statements/{statement_id}` rather than raising
`wait_timeout` indefinitely. This shouldn't come up for profiling-scale
queries (`LIMIT`ed samples, `DESCRIBE`, `COUNT`), only if a run is tempted to
pull a full large fact table — don't do that at profiling time regardless.

## How the final model connects (Power Query M, at Desktop open-time)

The M partition source uses the `Databricks.Catalogs` connector, **not**
hardcoded credentials — Desktop prompts the person opening the file to sign
in (their own Entra ID/SSO login, or a token, depending on how the workspace
is configured), the same way `SourceFolderPath` was a parameter rather than
a baked-in path.

```tmdl
expression DatabricksHost = "adb-1234567890123456.7.azuredatabricks.net" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]

expression DatabricksHttpPath = "/sql/1.0/warehouses/abc123def4567890" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
```

Then in each table's partition:

```tmdl
partition 'Customer' = m
	mode: import
	source =
		let
			Source = Databricks.Catalogs(DatabricksHost, DatabricksHttpPath, [Catalog=null, Database=null, EnableAutomaticProxyDiscovery=null, Implementation="2.0"]),
			dss_demos = Source{[Name="dss_demos",Kind="Database"]}[Data],
			bi_tasks = dss_demos{[Name="bi_tasks",Kind="Schema"]}[Data],
			customer = bi_tasks{[Name="customer",Kind="Table"]}[Data],
			// normal typing/renaming/filtering steps from here, per
			// ../power-query-conventions/SKILL.md
			Result = customer
		in
			Result
```

**`Kind="Database"` at the first level is not a typo for `Kind="Catalog"`.**
Confirmed against Microsoft's own Azure Databricks connector docs
(`learn.microsoft.com/en-us/power-query/connectors/databricks-azure`) and a
second independent example — both show this exact shape. The connector uses
"Database" as its internal name for what Unity Catalog and the Databricks UI
call a catalog. A first attempt at this got it wrong (`Kind="Catalog"`,
which doesn't exist) and every table failed to refresh with
`Expression.Error: The key didn't match any rows in the table.` — see
`docs/decisions/0009-databricks-as-primary-data-source.md` for the full
story. This is now a confirmed-correct pattern, not a guess — use it as
written rather than re-deriving it.

Also include the full options record shown above
(`Catalog=null, Database=null, ..., Implementation="2.0"`) — that's the
exact record Microsoft's documented example uses, not just the one option a
partial reading of it originally kept.

## What NOT to do

- Never write `DATABRICKS_TOKEN`'s value into a `.tmdl` file, a decision
  doc, `NOTES.md`, or a comment. It's an environment variable at profiling
  time and a Desktop-prompted credential at open time — it never belongs in
  a file.
- Don't pull full fact-table contents during profiling. `LIMIT` samples and
  `DESCRIBE`/`COUNT` are enough to understand grain and shape; full-table
  reads happen when Desktop actually refreshes the model, not during a
  profiling run.
