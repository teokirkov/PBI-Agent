# BI Task 1 — NOTES

Run-to-run memory for this project (see `CLAUDE.md` §0). Every `@claude` run
starts here.

- **Project:** `projects/bi-task-1/`
- **Deliverable:** `ToyCompanySales.pbip` (+ `.SemanticModel/`, `.Report/`)
- **Brief:** `docs/assignment/bi-task-1.pdf`
- **Source data:** `docs/sample-data/bi-task-1/` (7 `.xlsx` files)
- **Status:** **Semantic model complete; report visuals are a first-pass
  draft.** Power Query, star schema, relationships and all 22 measures are
  written and cross-reference-clean. 61 visuals across the 6 pages are
  hand-authored PBIR JSON that has **never been opened in Power BI Desktop** —
  treat the report layer as a starting point for a Desktop pass, not as
  finished work (§6.1). Nothing is blocked; see §7 for what is open.

### Read these first

1. `docs/decisions/0002` … `0008` — the answered cross-roads and the naming
   convention. They are the reason the model looks the way it does.
   **Note:** `0002`–`0007` predate `0008` and therefore still spell table
   names with the old `Fact `/`Dim ` prefixes (`Dim Product[Category Group]`
   and so on). Those ADRs are a permanent log of what was decided at the time
   and were deliberately left unedited — read the *reasoning* from them, but
   take current table names from §2 below, never from an ADR.
2. `GRAIN.md` — grain of every source file and every model table
   (assignment task 4).
3. `ANALYSIS.md` — business findings and, more importantly, the data problems.
4. §6 below — the one thing a human must do before the project will open.

### Before you finish a run that touched the PBIP

Run the checker. It is fast, has no dependencies, and exists because a
wide-reaching mechanical edit (like the 0008 rename) is exactly where a single
missed reference hides:

```
python3 projects/bi-task-1/validate_tmdl.py
```

It implements the "Validating your own output" checklist from
`.claude/skills/pbip-tmdl-structure/SKILL.md` plus the PBIR equivalents:
table-name ↔ filename ↔ partition-name agreement; every relationship endpoint
exists and both ends share a data type; `ref table` completeness in both
directions; `PBI_QueryOrder` names real queries; `sortByColumn` targets;
`sourceColumn` presence; every DAX table, column and measure reference in
every measure and calculated table; M expression references; and every PBIR
visual's field bindings, page list and visual-name/folder agreement.

It checks **internal consistency only.** It is not a TMDL parser and cannot
tell you whether Desktop accepts a given keyword — see §6.1.

---

## 1. What the assignment asks for

| # | Task | Status |
|---|------|--------|
| 1 | Load the data sources | **Done** — 7 files → 4 model queries + 3 staging expressions |
| 2 | Power Query: remove `_` from `SupplierReference`; trim `ColorName` | **Done** — both, see §3 |
| 3 | Star schema; Date dimension as a **calculated table** | **Done** — `Date` is a DAX `CALENDAR()` calculated table, as mandated |
| 4 | Document granularity of every table in a separate file | **Done** — `GRAIN.md` |
| 5 | The 9 main KPIs | **Done** as measures; **draft** as visuals (§6.4) |
| 6 | Publish to Power BI Service | **Human follow-up** — out of agent scope |
| 7 | Present the report | **Human follow-up** — out of agent scope |

### The 9 KPIs → measures

| KPI | Measure(s) |
|---|---|
| Unique order count | `[Order Count]` = 67,628 |
| Average order amount in £ | `[Average Order Amount]` = £2,409.51 |
| YTD, MTD sales — all and by category | `[Sales YTD]`, `[Sales MTD]`, sliced by `Customer[Sales Channel]` (decision 0005) |
| YOY sales | `[Sales YoY %]`, `[Sales YoY Change]`, `[Sales LY (Like-for-Like)]` (decision 0007) |
| Online sales as % of overall | `[Online Sales %]` = 63.34%, plus `[Online Sales]` / `[Retail Sales]` |
| TOP customers by orders and turnover | `[Customer Rank by Sales]`, `[Customer Rank by Orders]` + `[Total Sales]` / `[Order Count]` |
| Quantity and Sales by Supplier Name and Supplier Category Name | `[Total Quantity]` / `[Total Sales]` by `Supplier` |
| Quantity and Sales by Category Names | by `Category[Category]` — **overlapping by design**, decision 0004 |
| Quantity and Sales by Package Types | by `Package Type[Package Type]` |

---

## 2. The model as built

```
                      Date          Customer
                       |                |
                       v                v
                 +---------------------------+
     Supplier -->|           Sales           |<-- Package Type
                 |  (one row per order line) |
                 +---------------------------+
                              ^
                              |
                           Product <--(bi-directional)--+
                                                        |
                                            Bridge Product Category
                                                        |
                                                        v
                                                     Category
```

| Table | Rows | Grain | Query type |
|---|---|---|---|
| `Sales` | 212,774 | one order line | M |
| `Date` | 1,461 | one day, 2013-01-01 → 2016-12-31 | **DAX calculated table** |
| `Customer` | 663 | one customer | M |
| `Product` | 227 | one stock item (colour merged in) | M |
| `Supplier` | 13 | one supplier (category merged in) | M |
| `Package Type` | 14 | one package type | M |
| `Category` | 9 | one product stock-group tag | M |
| `Bridge Product Category` | 441 | one product-category membership | M (hidden) |
| `_Measures` | 1 | none — holds the 22 measures | DAX calculated table |

Staging queries (M expressions, **not loaded as tables**): `SourceFolderPath`
(parameter), `stgColor`, `stgSupplierCategory`, `stgStockItem`.

Seven source files collapse to six loaded dimensions plus one bridge, because
Colour and Supplier Catalogue are flattened into their parents rather than
snowflaked.

### Figures the model must reproduce

Computed directly from the source files, independent of the model — use these
to check the refresh in Desktop:

| | |
|---|---|
| Total Sales | **£162,950,104.45** |
| Order Count | **67,628** |
| Order Line Count | 212,774 |
| Total Quantity | 8,504,253 |
| Average Order Amount | **£2,409.51** |
| Online Sales % | **63.34%** |
| Uninvoiced Sales | £4,868,616.00 (2,809 orders, 3.0%) |
| Last Sales Date | 2016-02-29 |
| `[Sales YoY %]` for 2016 | **−1.7%** (£8,711,620.80 vs £8,863,884.50) |
| `[Sales YoY %]` for 2015 | +8.4% (£55,817,887.45 vs £51,492,003.40) |
| Sum of category subtotals | £265,811,434.65 = **1.63×** the grand total (expected — decision 0004) |

Per-year: 2013 £46,928,592.80 / 19,450 orders · 2014 £51,492,003.40 / 21,199 ·
2015 £55,817,887.45 / 23,329 · 2016 (Jan–Feb) £8,711,620.80 / 3,650.

---

## 3. The two mandated Power Query fixes

Both confirmed necessary against the actual data.

1. **`SupplierReference`** (`Supplier`). **Correction to the earlier
   profile**, which said the underscore was always leading — it is not. 8 of
   the 13 values carry it in front (`_AA20384`), 5 carry it trailing
   (`082420938_`). A `Text.TrimStart(_, "_")` would have silently left five
   values dirty. Implemented as `Text.Remove(_, {"_"})`.
2. **`ColorName`** (`stgColor`). 21 of 36 values have leading and/or trailing
   whitespace. `Text.Trim` fixes it and does not create duplicates — all 36
   names stay unique. `"      Steel Gray"` has a legitimate internal space,
   which `Text.Trim` correctly leaves alone.

---

## 4. Resolved cross-roads

All six questions from the previous run were answered on issue #1 and are
logged permanently:

| Q | Decision | File |
|---|---|---|
| Q1 | Sales = `Quantity × Unit Price`, ex-tax, line grain | `docs/decisions/0002` |
| Q2 | Include uninvoiced orders; surface them in a visual and the analysis | `docs/decisions/0003` |
| Q3 | Categories are a many-to-many → `Category` + bridge, plus an additive `Category Group` | `docs/decisions/0004` |
| Q4 | "Categories" in the YTD/MTD KPI = `OnlineSalesConditional` → `Sales Channel` | `docs/decisions/0005` |
| Q5 | Flat star — Supplier and Package Type join the fact directly | `docs/decisions/0006` |
| Q6 | Like-for-like YoY, prior year cut at the same month/day | `docs/decisions/0007` |

Q3 and Q4 were delegated back to the agent ("use your skills to decide"). Q3
turned out to be settled by evidence rather than judgement — all 227 of 227
stock-item rows are alphabetically non-decreasing across `CategoryName1/2/3`,
which is not something a real hierarchy does. See `ANALYSIS.md` §3.1.

---

## 5. Self-check against the Development Checklist

From `docs/best-practices/power-bi-best-practices.md`, model-authoring items
only (the Desktop/Service/Release items are in §6).

| Item | Status |
|---|---|
| Power Query step names describe what they do | Yes — `Source`, `PromotedHeaders`, `SelectedColumns`, `CleanedSupplierReference`, …, ending in `Result` |
| Combine similar actions into one step | Yes — one `Table.RenameColumns` and one `Table.TransformColumnTypes` per query |
| Queries organised into folders | Yes — `Staging`, `Model\Facts`, `Model\Dimensions`. **See the caveat in §6.1** |
| Correct data type on every column | Yes — sources load with `delayTypes = true`, so nothing is auto-typed and every surviving column is typed explicitly |
| Use parameters | Yes — `SourceFolderPath`; no absolute path is hardcoded anywhere |
| Filter early | N/A — no rows are filtered out (decision 0003 keeps all of them). Column selection is done as early as possible |
| Query folding | N/A — `.xlsx` sources do not fold |
| Disable load for tables not needed | Yes — the 3 staging queries are M expressions with no table, so they cannot load |
| One-to-many Dim→Fact, star schema | Yes — all 7 relationships are many-to-one |
| Avoid bi-directional filters | **One deliberate exception** — the bridge. Documented in decision 0004; **needs a correctness test in Desktop**, see §6.2 |
| Avoid many-to-many | **One, inherent to the source data.** Same exception, same test |
| Be aware of report locale | Yes — model culture `en-GB`; dates parsed with an explicit `en-US` culture (the source format is US long-date); `FORMAT` calls in `Date` pass `"en-GB"` explicitly so month and day names do not shift with the machine |
| Custom Date table | Yes — `Date`, a DAX calculated table per the brief, marked as a date table (`dataCategory: Time` + `isKey` on `Date`) |
| Load only required columns | Yes — 35 source columns on `Sales.xlsx` reduce to 12; 36 on `Customer.xlsx` to 7; 24 on `Warehouse Stock Item.xlsx` to 9; 26 on `Purchasing Supplier.xlsx` to 5 |
| Hide fields not used in the report | Yes — every FK, `Line Amount`, `Quantity`, `Picked Quantity`, `Tax Rate`, `Order Date`, and the whole bridge table |
| Calculated column in Power Query, not DAX | Yes — `Line Amount` and `Category Group` are both M. The only DAX-computed table is `Date`, which the brief mandates |
| Auto-summarisation off for non-additive fields | Yes — `summarizeBy: none` on every ID, price and rate |
| Business names on fields and tables | Yes — renamed in Power Query, not cosmetically. Every renamed column carries its source name in a TMDL `///` description. Tables carry **no `Fact`/`Dim` prefix**, per decision 0008 |
| Don't store timestamps | Yes — `PickingCompletedWhen` and `ConfirmedDeliveryTime` both carry times and are not loaded |
| `Date` type, not `Date/Time` | Yes in M (`type date`). Note TMDL/TOM has only `dateTime`, so the columns read `dataType: dateTime` with a date-only `formatString` — that is the correct representation, not an oversight |
| Measures table, with subfolders | Yes — `_Measures`, 22 measures across `Sales`, `Sales\Time Intelligence`, `Sales\Channel`, `Sales\Order Fulfilment`, `Ranking` |
| Report page size 1920×1080 | Yes on all 6 pages, and every visual is verified in-bounds and non-overlapping |
| Always format DAX | Yes |
| No implicit measures | Yes — and enforced at model level with `discourageImplicitMeasures`, not just by convention. Every field on the canvas is either a dimension attribute or an explicit measure; no visual aggregates a fact column directly |
| Configure the default page | Yes — `activePageName: overview` |
| Could DAX transformations be Power Query instead? | Checked — only `Date` is DAX, and only because the brief requires it |

### Dataset size

`.SemanticModel/` is 84 KB and `.Report/` 604 KB on disk — PBIP stores no data,
so this is the definition only, and the report folder is large only because
PBIR writes one verbose JSON file per visual. The source workbooks total
34.5 MB, and the loaded model is one 212,774-row fact of 13 narrow,
low-cardinality columns plus six tiny dimensions. Nowhere near the 200 MB flag
threshold, and with the data window fixed at 2013–2016 there is no growth path
toward 1 GB. No optimisation warranted.

---

## 6. Human follow-up

### 6.1 Before the project will open — required

**Set the `SourceFolderPath` parameter.** It defaults to
`C:\repos\PBI-Agent\docs\sample-data\bi-task-1\`, which is almost certainly not
where your checkout is. In Desktop: *Transform data → Manage Parameters →
SourceFolderPath*. It needs a **trailing backslash**. Nothing else in the model
hardcodes a path.

**If Desktop rejects the query folders**, delete the `queryGroup:` lines from
the table partitions and expressions, and the `PBI_QueryGroups` annotation from
`model.tmdl`. That is the one construct here I could not verify against a real
Desktop export — it only affects how queries are grouped in the Power Query
navigator, so removing it costs nothing but the folder organisation.

**Honest statement of confidence:** this TMDL and PBIR were hand-authored on a
Linux CI runner with no Power BI Desktop available, so nothing here has ever
been round-tripped through Desktop. `validate_tmdl.py` confirms every
cross-reference resolves, but that checks *consistency*, not that Desktop
accepts every keyword. Expect the first open to surface syntax nits.

Ranked by how unsure I am, with the fallback for each:

| Construct | Where | If Desktop rejects it |
|---|---|---|
| PBIR `visual.json` bodies | `.Report/definition/pages/*/visuals/` | Delete the offending `visuals/<name>/` folder — the page survives. Delete `ToyCompanySales.Report/` entirely and Desktop regenerates a blank report; you lose the draft layout and nothing else |
| `sortDefinition` on a visual query | 20 visuals | Delete the `sortDefinition` block; the visual keeps its fields and just sorts by default |
| `visualContainerObjects.title` | every non-card visual | Delete the block; the visual falls back to Power BI's auto-generated title |
| `queryGroup` / `PBI_QueryGroups` | table partitions, `expressions.tmdl`, `model.tmdl` | Delete the `queryGroup:` lines and the annotation. Costs only the Power Query folder organisation |
| `discourageImplicitMeasures` | `model.tmdl` | Delete the line. All 22 measures are explicit anyway, so this only removes the guard rail |

The **semantic model is the valuable half** and the report layer is the
speculative half. If the two fight, keep the model and rebuild the report.

### 6.2 Test before trusting

**The category bridge.** It is the model's only bidirectional relationship and
only many-to-many. Check in Desktop that:
- `[Total Sales]` with no category filter = **£162,950,104.45**
- a table of `Category[Category]` × `[Total Sales]` sums to
  **£265,811,434.65** across the rows while the total row still shows
  £162,950,104.45 — that discrepancy is correct and expected (decision 0004)
- `Product[Category Group]` × `[Total Sales]` **does** sum to the grand
  total

### 6.3 Desktop settings (pre-development checklist)

Disable "Update or delete relationships when refreshing data", "Autodetect new
relationships after data is loaded", **"Auto date/time"** (the model sets
`__PBI_TimeIntelligenceEnabled = 0`, but confirm it in the UI — the brief
mandates a custom date table), Q&A if unused, and background data preview
download. Set Data Cache Management to max. Apply the client colour template.

### 6.4 Report layer — first-pass draft, needs a Desktop pass

**61 visuals across the six 1920×1080 pages.** Explicitly a rough draft
(requested as one): field bindings and layout are done, visual formatting is
almost entirely default.

| Page | Visuals | What is on it |
|---|---|---|
| Overview | 14 | 7 KPI cards, sales-by-month line, channel donut, sales-vs-prior-year columns, year-on-year table |
| Sales Trend & YoY | 11 | YTD/MTD/LY/YoY cards, Year slicer, monthly trend, combo chart with YoY % on a secondary axis, seasonality by month-of-year with Year as series |
| Customers | 12 | 6 cards, ranked customer table, sales by customer category, sales and orders by buying group |
| Products & Categories | 8 | Overlapping category tags (sales and quantity), the additive `Category Group` alongside them for contrast, product table, sales by colour |
| Suppliers & Packaging | 7 | Sales and quantity by supplier, by supplier category, package type as a table |
| Data Quality & Caveats | 9 | 4 cards, the deteriorating uninvoiced-share trend, unfulfilled orders by year, and a five-point caveats panel |

Checked mechanically, not just by eye: **all 22 measures appear on the canvas**
(`validate_tmdl.py` resolves every binding), no visual is off-canvas, no two
visuals on a page overlap, and every visual name matches its folder.

All four `ANALYSIS.md` §4 captions are on the canvas as textboxes. Caption 1 is
handled slightly better than asked: rather than typing "Data through 29
February 2016" into a textbox where it would go stale on the next refresh,
there is a **`[Last Sales Date]` card** on the Overview, and the textbox
explains how to read a two-month year.

**Known gaps a Desktop pass should close** — none of these are mistakes, they
are things deliberately left out of a hand-authored draft:

- **No Top-N filter on the customer table.** It is sorted by `[Total Sales]`
  descending and shows all 660 rows. A `filterConfig` TopN block is one of the
  most intricate structures in PBIR and a malformed one risks the whole visual;
  adding "Top 10 by Total Sales" in the filter pane is a few clicks. This is
  the single most worthwhile manual addition.
- **Formatting is default** — no theme colours, data labels, axis titles,
  number-format overrides, conditional formatting or field-level renaming on
  the canvas.
- **Only one slicer** (Year, on Sales Trend). The best-practices doc prefers
  the filter pane to on-canvas slicers anyway, but cross-page slicer sync is
  worth setting up.
- **No bookmarks, drillthrough, tooltips or page navigation.**
- Textbox heights are estimates. Long captions may clip or scroll at Desktop's
  actual font metrics — the caveats panel on Data Quality is the most likely to
  need resizing.
- Cards carry no explicit title; the classic card renders the measure name as
  its own label. If a card looks bare, that is why.

The visuals were generated from a throwaway script that was **not** committed,
deliberately: re-running it would delete the `visuals/` folders and destroy any
Desktop work. From here the JSON — and then Desktop — is the only source of
truth.

Also from the checklist, all human-only: test cross-page interactions, hide/lock
report-level filters, sync slicers where needed, prefer the filter pane over
on-canvas slicers, check whether custom visuals are allowed, configure RLS if
required.

### 6.5 Service / release (brief tasks 6 and 7)

Publish to the personal workspace, configure and test manual and scheduled
refresh, validate the data in the Service, configure user access, then present.
Note the refresh will fail in the Service until the source files are reachable
from there — the current setup is a manual file drop into the repo (see
`.claude/skills/sharepoint-data-ingestion/SKILL.md`).

---

## 7. Open items

None of these blocks anything — the requested scope is complete. They are
choices for the next run or the human, not unanswered cross-roads.

**Closed since the last run:** the naming-convention tension (decision 0008 —
prefixes dropped, this model renamed, skill file corrected) and the
`singleDirection` / `oneDirection` skill-file bug (fixed on `main` in
`fe64609`). Both are done; nothing to carry forward.

1. **The report layer needs a Desktop pass** — §6.4 lists exactly what is
   missing and §6.1 what might be rejected outright. Highest-value single
   addition: a Top-10 filter on the customer table.
2. **Model viewer layout tabs.** The team convention (one tab with all facts
   bottom / dims top, one tab per fact) is not expressible in hand-authored
   TMDL. Arrange in Desktop's model view.
3. **Business questions raised by the data**, listed in `ANALYSIS.md` §5 — the
   most useful being: request the underlying product-to-stock-group table
   instead of the flattened `CategoryName1/2/3` columns, and investigate why
   unpicked orders rose from 2.31% to 6.71% of the book in three years.

---

## 8. Run log

| Date | Run | What happened |
|---|---|---|
| 2026-09-01 | issue #1, "Start BI Task 1" | Discover + Profile only, as instructed. Profiled all 7 files, verified referential integrity and grain. Stopped before modeling; six questions posted. Branch `claude/issue-1-20260901-1007`. |
| 2026-09-01 | issue #1, answers to Q1–Q6 | Built the semantic model: PBIP scaffold, 4 model queries + 3 staging expressions, 7 relationships, `Date` calculated table, 22 measures. Logged decisions 0002–0007. Wrote `GRAIN.md` and `ANALYSIS.md`, rewrote this file. Determined Q3 from the data (categories are a many-to-many). Corrected the earlier `SupplierReference` finding. Report visuals not built. Branch `claude/issue-1-20260901-1026`. |
| 2026-09-01 | issue #1, "rename per 0008, then draft visuals" | **Rename:** dropped the `Fact`/`Dim` prefixes across `.tmdl` filenames, table and partition declarations, all 7 relationships (and their names), all 22 measures, the `Date` calculated table's DAX, `model.tmdl`'s `ref table` list and `PBI_QueryOrder`, every `///` description, and all three project docs. Added `validate_tmdl.py` and verified it fails on injected faults before trusting a clean pass. **Visuals:** 61 first-pass PBIR visuals across the 6 pages, all 22 measures on canvas, geometry verified. Branch `claude/issue-1-20260901-1203`. |

> **Note for the next run:** the first run's `NOTES.md` was left on its own
> branch and was **not** on `main`, so this run had to recover it with
> `git checkout origin/claude/issue-1-20260901-1007 -- projects/bi-task-1/NOTES.md`.
> Since `CLAUDE.md` §0 makes `NOTES.md` the only run-to-run memory, that memory
> is only actually durable once the branch is merged. **Merge the PR** — or, if
> a run finds no `NOTES.md` for a project that the issue thread clearly says has
> one, check the other `claude/*` branches before concluding the work never
> happened.

### Next run should

1. Read `docs/decisions/0002`–`0008` before touching anything — they encode
   choices that are expensive to unwind. Remember `0002`–`0007` still use the
   old prefixed table names in their examples; take current names from §2.
2. Run `python3 projects/bi-task-1/validate_tmdl.py` before **and** after any
   edit to the PBIP, so a break is attributable to this run rather than
   inherited.
3. **Ask before regenerating the report layer.** If the project has been opened
   in Desktop since 2026-09-01, the `.Report/` JSON is now human-edited work
   and overwriting it destroys that. Diff against this branch first.
4. Verify against the reconciliation figures in §2 if the model has been opened
   in Desktop by then, and against the bridge spot-check in §6.2.
