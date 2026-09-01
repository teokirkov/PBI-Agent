# Power BI Best Practices & Checklists

Converted from `PowerBI Best Practices + Checklists.xlsx` (internal reference).
This is the **authoritative** source for team conventions — where anything in
`.claude/skills/*/SKILL.md` conflicts with what's written here, this document
wins; the skill files should be (and have been) updated to match rather than
left contradictory. See `.claude/skills/best-practices/SKILL.md` for the
short version and pointers to which skill covers what.

---

## Data Model

- Always aim for a **one-to-many relationship** between a Dimension table and
  a Fact table.
- A many-to-many relationship can occasionally be necessary for a good
  model, but should **never be the default** — it can silently produce
  incorrect results.
- If multiple relationships are needed between two tables, create a
  **composite key** for the inactive ones and activate the primary one; use
  `USERELATIONSHIP` in specific measures to invoke an inactive relationship.

## Data

- Don't store timestamps — they consume too much RAM. Use `Date` type for
  date columns, not `Date/Time`, unless time-of-day is genuinely needed.
- Remove fields not used in the report, and remove duplicate fields.
- Tables and fields need clear **business names** — no `DIM`/`FACT` prefix
  needed on the field/table names themselves (that distinction belongs in
  the model organization, not the naming).

## Power Query, ETL, DWH

- Prefer sourcing from an underlying **data warehouse** and avoid heavy
  transformation in Power Query — **exception: small reports sourced
  directly from files**, where Power Query transformation is expected and
  fine. *(This exception is the normal case for this agent's projects —
  source data usually arrives as files, not a DWH connection.)*
- Group related queries into **folders** in Power Query for a cleaner
  overview.
- Load **only required columns**.
- Keep join operations at load time / in the DWH rather than doing them
  live in DAX.

## Data Model Viewer (layout)

- Create multiple views/tabs in the model viewer:
  - One tab containing **all Fact tables at the bottom and all Dim tables at
    the top**.
  - One tab **per Fact table**, showing the full star schema around that
    fact.

## Filters and Slicers

- Prefer the **filter pane** over on-canvas slickers where possible — frees
  up screen space for visuals.
- Exception can be made for managerial/executive reports, but challenge that
  choice with the business first rather than defaulting to it.
- **Avoid bi-directional filters** — only use when there's a specific,
  understood need, and test that it produces correct results.

## Measures and Fields

- Give fields good business names. If a field's source name isn't good,
  fix it in the ETL/Power Query — don't just rename it cosmetically on the
  front end and leave the underlying name wrong.
- Document the original/technical field name (e.g. as a field description or
  comment) when the display name diverges from it.
- **Never use implicit measures in visuals** — always create an explicit
  measure.
- Hide fields that aren't used in the report.
- Prefer creating calculated columns in **Power Query** over the DAX/front
  end — front-end calculated columns can hurt performance on large tables.
  (Nuance: this is a default, not an absolute — see the SQLBI article on
  when a DAX calculated column is actually the right call, referenced in
  the Checklists sheet below.)

## DAX

- **Always format your DAX code.**

## PBIX File / Dataset Size

- Flag it if the file is larger than 200MB on disk.
- Consider whether the file can be optimized to reduce what's read into RAM
  (tools like "Power BI Helper" can analyze this).
- Consider whether the file is likely to grow past 1GB, and whether growth
  is being bounded (e.g. always keeping only the last N years of data).

---

## Pre-Development Checklist

Power BI Desktop / model-level settings to configure before building:

- Disable **"Update or delete relationships when refreshing data"** and
  **"Autodetect new relationships after data is loaded."**
- Disable **"Auto date/time"** — avoids performance issues and excess
  storage from the hidden auto-generated date tables.
- Disable **Q&A** if it isn't needed.
- Disable **"Enable parallel loading of tables"** if the model is large /
  has many queries, to avoid refresh failures in Desktop.
- Disable **"Allow data preview to download in the background"** for large
  models — avoids long refreshes and CPU/RAM spikes.
- Set the **Data Cache Management** option to its max value.
- Apply the client's colors/template.

## Development Checklist

- Name Power Query applied steps properly (describe what the step does; add
  comments where the logic needs explaining).
- Reduce step count by combining similar actions (e.g. rename all columns
  in one step rather than one step per column).
- Organize queries into folders in Power Query.
- Assign the correct data type to every column — avoid leaving columns as
  the generic `ABC123` (Any) type.
- Use **parameters** where practical — lets you load a data sample in
  Desktop and swap the parameter in the Service, and keeps M code from
  being hardcoded.
- Apply filtering in Power Query as early as possible.
- Take advantage of **query folding** where the source supports it.
- Disable load for any table you don't need to load directly.
- Aim for one-to-many Dim→Fact relationships wherever possible; aim for a
  star schema.
- Avoid bi-directional filters.
- Avoid many-to-many relationships; if unavoidable, always test that it
  produces correct results.
- Be aware of report **locale** (comma vs. period conventions differ by
  region/number format).
- Create a **custom Date table**.
- Load only required columns.
- Hide fields not used in the report.
- Think deliberately about when to use a calculated column vs. not (see the
  SQLBI article on the pros/cons of calculated columns).
- Set correct **auto-summarization** for non-additive fields (e.g. `None`
  for IDs and other non-additive numerics).
- Assign business names to fields/tables.
- Don't store timestamps.
- Use `Date` type for date columns, not `Date/Time`.
- Create a **Measures table**; use subfolders if there are many measures.
- Set report page size to **1920x1080** if more space is needed.
- Always format DAX code.
- Don't use implicit measures — create explicit measures.
- Test interactions across pages before publishing.
- Hide/lock visual, page, and report-level filters that users shouldn't
  adjust.
- Sync slicers where needed, and be aware that syncing means a change to one
  affects every synced slicer.
- When changing bookmarks/hidden pages reached via buttons, remember to
  update every page that references them.
- Check with the client whether custom visuals are allowed.
- Configure and test Row-Level Security.
- Clear the data cache if disk space is limited and causing issues.
- Configure the default page and default selections in the PBIX.
- Check whether transformations that are currently in DAX could be done in
  Power Query instead.

## Power BI Service Checklist

- Configure and test refresh in the Service (manual and scheduled).
- Configure and test gateway connections.
- Test that visuals work correctly.
- Check the data / validate it.
- Configure user access (sharing the report / adding users to the
  workspace).
- Include the report in an app, if applicable.
- Configure RLS in the Service's Security option.
- When republishing, keep the same report name — avoid double-publishing
  under a new name.
- Restrict edit rights to trusted, capable users.

## Release Checklist

- Gateway connections created and tested.
- Report moved to the correct workspace.
- Gateway connection mapped.
- Manual refresh tested; refresh schedule enabled.
- Report visuals and report data checked.
- User access configured.
- DEV/STG workspace contains the latest version; all test reports removed
  from it.
- Published version's name does not contain a version number.
- Project manager informed at go-live (e.g. by email).
- Documentation up to date.

## Documentation

- Keep report documentation and the report data catalogue up to date.

---

## What this means for this agent specifically

This agent authors the **semantic model layer** (TMDL: tables, relationships,
Power Query, measures) — it does not operate Power BI Desktop or the Power BI
Service. So:

- **Directly applicable, and enforced via the skill files:** the Data Model,
  Data, Power Query/ETL/DWH, Measures and Fields, DAX, and Data Model Viewer
  sections above, plus the model-authoring parts of the Development
  Checklist (naming, typing, relationships, star schema, measures table,
  DAX formatting, custom Date table).
- **Reference for the human, not something the agent does:** Pre-Development
  Desktop application settings, the Power BI Service checklist, and the
  Release checklist — these are Power BI Desktop UI toggles, Service
  configuration, and deployment process steps that happen after a project's
  `.pbip` is opened locally. `NOTES.md` for a project should flag these as
  the human's follow-up steps rather than the agent attempting them.
