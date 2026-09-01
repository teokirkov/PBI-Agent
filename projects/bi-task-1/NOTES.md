# BI Task 1 — NOTES

Run-to-run memory for this project (see `CLAUDE.md` §0). Every `@claude` run
starts here.

- **Project:** `projects/bi-task-1/`
- **Deliverable:** `ToyCompanySales.pbip` (+ `.SemanticModel/`, `.Report/`)
- **Brief:** `docs/assignment/bi-task-1.pdf`
- **Source data:** `docs/sample-data/bi-task-1/` (7 `.xlsx` files)
- **Status:** **Semantic model complete** — Power Query, star schema,
  relationships and all 22 measures are written. Report visuals are **not**
  built (scaffolded pages only). Nothing is blocked; see §7 for what is open.

### Read these first

1. `docs/decisions/0002` … `0007` — the six answered cross-roads. They are the
   reason the model looks the way it does.
2. `GRAIN.md` — grain of every source file and every model table
   (assignment task 4).
3. `ANALYSIS.md` — business findings and, more importantly, the data problems.
4. §6 below — the one thing a human must do before the project will open.

---

## 1. What the assignment asks for

| # | Task | Status |
|---|------|--------|
| 1 | Load the data sources | **Done** — 7 files → 4 model queries + 3 staging expressions |
| 2 | Power Query: remove `_` from `SupplierReference`; trim `ColorName` | **Done** — both, see §3 |
| 3 | Star schema; Date dimension as a **calculated table** | **Done** — `Dim Date` is a DAX `CALENDAR()` calculated table, as mandated |
| 4 | Document granularity of every table in a separate file | **Done** — `GRAIN.md` |
| 5 | The 9 main KPIs | **Done** as measures; **not** as visuals |
| 6 | Publish to Power BI Service | **Human follow-up** — out of agent scope |
| 7 | Present the report | **Human follow-up** — out of agent scope |

### The 9 KPIs → measures

| KPI | Measure(s) |
|---|---|
| Unique order count | `[Order Count]` = 67,628 |
| Average order amount in £ | `[Average Order Amount]` = £2,409.51 |
| YTD, MTD sales — all and by category | `[Sales YTD]`, `[Sales MTD]`, sliced by `Dim Customer[Sales Channel]` (decision 0005) |
| YOY sales | `[Sales YoY %]`, `[Sales YoY Change]`, `[Sales LY (Like-for-Like)]` (decision 0007) |
| Online sales as % of overall | `[Online Sales %]` = 63.34%, plus `[Online Sales]` / `[Retail Sales]` |
| TOP customers by orders and turnover | `[Customer Rank by Sales]`, `[Customer Rank by Orders]` + `[Total Sales]` / `[Order Count]` |
| Quantity and Sales by Supplier Name and Supplier Category Name | `[Total Quantity]` / `[Total Sales]` by `Dim Supplier` |
| Quantity and Sales by Category Names | by `Dim Category[Category]` — **overlapping by design**, decision 0004 |
| Quantity and Sales by Package Types | by `Dim Package Type[Package Type]` |

---

## 2. The model as built

```
                   Dim Date        Dim Customer
                       |                |
                       v                v
                 +---------------------------+
   Dim Supplier ->|       Fact Sales          |<- Dim Package Type
                 |  (one row per order line) |
                 +---------------------------+
                             ^
                             |
                        Dim Product  <--(bi-directional)--  Bridge Product
                                                            Category
                                                                 |
                                                                 v
                                                            Dim Category
```

| Table | Rows | Grain | Query type |
|---|---|---|---|
| `Fact Sales` | 212,774 | one order line | M |
| `Dim Date` | 1,461 | one day, 2013-01-01 → 2016-12-31 | **DAX calculated table** |
| `Dim Customer` | 663 | one customer | M |
| `Dim Product` | 227 | one stock item (colour merged in) | M |
| `Dim Supplier` | 13 | one supplier (category merged in) | M |
| `Dim Package Type` | 14 | one package type | M |
| `Dim Category` | 9 | one product stock-group tag | M |
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

1. **`SupplierReference`** (`Dim Supplier`). **Correction to the earlier
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
| Q3 | Categories are a many-to-many → `Dim Category` + bridge, plus an additive `Category Group` | `docs/decisions/0004` |
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
| Be aware of report locale | Yes — model culture `en-GB`; dates parsed with an explicit `en-US` culture (the source format is US long-date); `FORMAT` calls in `Dim Date` pass `"en-GB"` explicitly so month and day names do not shift with the machine |
| Custom Date table | Yes — `Dim Date`, a DAX calculated table per the brief, marked as a date table (`dataCategory: Time` + `isKey` on `Date`) |
| Load only required columns | Yes — 35 source columns on `Sales.xlsx` reduce to 12; 36 on `Customer.xlsx` to 7; 24 on `Warehouse Stock Item.xlsx` to 9; 26 on `Purchasing Supplier.xlsx` to 5 |
| Hide fields not used in the report | Yes — every FK, `Line Amount`, `Quantity`, `Picked Quantity`, `Tax Rate`, `Order Date`, and the whole bridge table |
| Calculated column in Power Query, not DAX | Yes — `Line Amount` and `Category Group` are both M. The only DAX-computed table is `Dim Date`, which the brief mandates |
| Auto-summarisation off for non-additive fields | Yes — `summarizeBy: none` on every ID, price and rate |
| Business names on fields and tables | Yes — renamed in Power Query, not cosmetically. Every renamed column carries its source name in a TMDL `///` description |
| Don't store timestamps | Yes — `PickingCompletedWhen` and `ConfirmedDeliveryTime` both carry times and are not loaded |
| `Date` type, not `Date/Time` | Yes in M (`type date`). Note TMDL/TOM has only `dateTime`, so the columns read `dataType: dateTime` with a date-only `formatString` — that is the correct representation, not an oversight |
| Measures table, with subfolders | Yes — `_Measures`, 22 measures across `Sales`, `Sales\Time Intelligence`, `Sales\Channel`, `Sales\Order Fulfilment`, `Ranking` |
| Report page size 1920×1080 | Yes on all 6 scaffold pages |
| Always format DAX | Yes |
| No implicit measures | Yes — and enforced at model level with `discourageImplicitMeasures`, not just by convention |
| Configure the default page | Yes — `activePageName: overview` |
| Could DAX transformations be Power Query instead? | Checked — only `Dim Date` is DAX, and only because the brief requires it |

### Dataset size

`.SemanticModel/` is 43 KB and `.Report/` 2.7 KB on disk — PBIP stores no data,
so this is the definition only. The source workbooks total 34.5 MB, and the
loaded model is one 212,774-row fact of 13 narrow, low-cardinality columns plus
six tiny dimensions. Nowhere near the 200 MB flag threshold, and with the data
window fixed at 2013–2016 there is no growth path toward 1 GB. No optimisation
warranted.

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

**Honest statement of confidence:** this TMDL was hand-authored on a Linux CI
runner with no Power BI Desktop available, so it has never been round-tripped
through Desktop. Cross-references were validated by script (every relationship
column, every measure reference, every `sortByColumn` target, every M
expression reference and every `sourceColumn` resolves), but that checks
consistency, not that Desktop accepts every keyword. Expect the first open to
possibly surface syntax nits. The constructs I am least certain of, in order:
`queryGroup` / `PBI_QueryGroups`; `discourageImplicitMeasures`; the `.Report`
PBIR JSON. If the report folder is the problem, deleting
`ToyCompanySales.Report/` and letting Desktop regenerate a blank report loses
nothing — it holds six empty pages and no visuals.

### 6.2 Test before trusting

**The category bridge.** It is the model's only bidirectional relationship and
only many-to-many. Check in Desktop that:
- `[Total Sales]` with no category filter = **£162,950,104.45**
- a table of `Dim Category[Category]` × `[Total Sales]` sums to
  **£265,811,434.65** across the rows while the total row still shows
  £162,950,104.45 — that discrepancy is correct and expected (decision 0004)
- `Dim Product[Category Group]` × `[Total Sales]` **does** sum to the grand
  total

### 6.3 Desktop settings (pre-development checklist)

Disable "Update or delete relationships when refreshing data", "Autodetect new
relationships after data is loaded", **"Auto date/time"** (the model sets
`__PBI_TimeIntelligenceEnabled = 0`, but confirm it in the UI — the brief
mandates a custom date table), Q&A if unused, and background data preview
download. Set Data Cache Management to max. Apply the client colour template.

### 6.4 Report layer

Six pages exist with correct 1920×1080 sizing and **no visuals**:
*Overview*, *Sales Trend & YoY*, *Customers*, *Products & Categories*,
*Suppliers & Packaging*, *Data Quality & Caveats*. Per `CLAUDE.md` §2, TMDL/PBIR
does not describe visuals in a way that is practical to hand-author reliably,
and the trigger comment asked for the model layer. Building them out is either a
human pass in Desktop or a follow-up run — see §7.

`ANALYSIS.md` §4 lists four captions that should go **on the canvas**, not just
in the docs. The most important is "Data through 29 February 2016".

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

1. **Build the report visuals?** Not requested in this run's trigger comment
   and not attempted. If a future run should attempt them, say so explicitly,
   because the confidence caveat in §6.1 applies double to PBIR visual JSON.
2. **Naming convention tension, worth one line of confirmation.**
   `docs/best-practices/power-bi-best-practices.md` says tables need clear
   business names with "no `DIM`/`FACT` prefix needed", while
   `.claude/skills/pbip-tmdl-structure/SKILL.md` mandates `Fact <Subject>` /
   `Dim <Subject>`. The best-practices doc is supposed to win on conflict, but
   the previous run proposed `Fact Sales` / `Dim Customer` naming and that
   proposal was approved on issue #1, so this model uses the prefixes. If the
   best-practices reading is the intended one, renaming is cheap now and
   expensive after visuals are bound to field names. **One of the two documents
   should be corrected either way.**
3. **Skill file bug.** `.claude/skills/pbip-tmdl-structure/SKILL.md` gives
   `crossFilteringBehavior: singleDirection` as the single-direction value. The
   TOM enum is `oneDirection`. This model sidesteps it by omitting the property
   wherever the default (one direction) is wanted and only stating
   `bothDirections` explicitly, but the skill file should be fixed.
4. **Model viewer layout tabs.** The team convention (one tab with all facts
   bottom / dims top, one tab per fact) is not expressible in hand-authored
   TMDL. Arrange in Desktop's model view.
5. **Business questions raised by the data**, listed in `ANALYSIS.md` §5 — the
   most useful being: request the underlying product-to-stock-group table
   instead of the flattened `CategoryName1/2/3` columns, and investigate why
   unpicked orders rose from 2.31% to 6.71% of the book in three years.

---

## 8. Run log

| Date | Run | What happened |
|---|---|---|
| 2026-09-01 | issue #1, "Start BI Task 1" | Discover + Profile only, as instructed. Profiled all 7 files, verified referential integrity and grain. Stopped before modeling; six questions posted. Branch `claude/issue-1-20260901-1007`. |
| 2026-09-01 | issue #1, answers to Q1–Q6 | Built the semantic model: PBIP scaffold, 4 model queries + 3 staging expressions, 7 relationships, `Dim Date` calculated table, 22 measures. Logged decisions 0002–0007. Wrote `GRAIN.md` and `ANALYSIS.md`, rewrote this file. Determined Q3 from the data (categories are a many-to-many). Corrected the earlier `SupplierReference` finding. Report visuals not built. Branch `claude/issue-1-20260901-1026`. |

> **Note for the next run:** the first run's `NOTES.md` was left on its own
> branch and was **not** on `main`, so this run had to recover it with
> `git checkout origin/claude/issue-1-20260901-1007 -- projects/bi-task-1/NOTES.md`.
> Since `CLAUDE.md` §0 makes `NOTES.md` the only run-to-run memory, that memory
> is only actually durable once the branch is merged. **Merge the PR** — or, if
> a run finds no `NOTES.md` for a project that the issue thread clearly says has
> one, check the other `claude/*` branches before concluding the work never
> happened.

### Next run should

1. Read `docs/decisions/0002`–`0007` before touching anything — they encode
   choices that are expensive to unwind.
2. Confirm whether report visuals are wanted (§7.1) before attempting them.
3. Verify against the reconciliation figures in §2 if the model has been opened
   in Desktop by then.
