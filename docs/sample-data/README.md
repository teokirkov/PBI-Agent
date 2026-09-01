# Sample / source data

Interim manual drop location for source files (CSV/XLSX) a project's model
is built from, until automated SharePoint ingestion exists — see
`.claude/skills/sharepoint-data-ingestion/SKILL.md`.

Organize by project:

```
docs/sample-data/
  bi-task-1/
    orders.csv
    customers.xlsx
```

Keep raw source files as originally provided (don't hand-edit them) — any
cleanup happens in Power Query per
`.claude/skills/power-query-conventions/SKILL.md`, so the transformation is
visible and reviewable rather than baked silently into the source file.
