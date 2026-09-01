# BI Task 1 — NOTES

Run-to-run memory for this project (see `CLAUDE.md` §0). Every `@claude` run
starts here.

- **Project:** `projects/bi-task-1/`
- **Brief:** `docs/assignment/bi-task-1.pdf`
- **Source data:** `docs/sample-data/bi-task-1/` (7 `.xlsx` files)
- **Status:** Discover + Profile complete. **Modeling not started** — blocked
  on the open questions in the last section.

---

## 1. What the assignment actually asks for

Verbatim requirements extracted from the PDF, with what each one implies.

**Goal.** An interactive report on the general performance of a toy company —
"visually appealing and easy to navigate". Data covers several years of sales,
customers and suppliers.

| # | Task | Implication for this repo |
|---|------|---------------------------|
| 1 | Load the data sources | 7 Excel files → 7 Power Query queries |
| 2 | Power Query: remove `_` from `SupplierReference` (Purchasing Supplier); trim `ColorName` (Warehouse Color) | Two **explicitly mandated** transforms. Both confirmed necessary against the data (§3). |
| 3 | Create data model: dimensional **star schema**; Date dimension as a **calculated table** | Note: "calculated table" = DAX `CALENDAR`/`CALENDARAUTO`, *not* a Power Query query. That's an explicit instruction from the brief and it overrides the usual "prefer Power Query" default in `docs/best-practices/power-bi-best-practices.md`. |
| 4 | Outline and describe the **level of granularity for every table** in a separate file | Satisfied by §2 of this file + `ANALYSIS.md` (to be written). The brief says "different file, e.g. Excel, Word" — a markdown doc in the repo is the git-native equivalent. |
| 5 | Main KPIs (9 of them) | See table below |
| 6 | Publish to Power BI Service, personal workspace | **Human follow-up** — out of agent scope |
| 7 | Present the report | **Human follow-up** — out of agent scope |

### The 9 required KPIs

| KPI | Fully specified by the brief? |
|-----|-------------------------------|
| Unique order count | Yes — `DISTINCTCOUNT(Order ID)`. Data gives 67,628. |
| Average order amount in £ | Mostly — "per order", so sales ÷ distinct orders. Depends on Q1/Q2 below. |
| YTD, MTD sales — all and separated by categories (Online Sales Conditional) | Needs Q4 ("categories" is ambiguous — product category vs `OnlineSalesConditional`) |
| YOY Sales | Yes, mechanically — but see the 2016 partial-year warning in §4 |
| Online sales as a % of overall sales | Yes — `OnlineSalesConditional` is a **customer** attribute, not an order attribute (§3) |
| TOP customers by number of orders and turnover | Yes |
| Quantity and Sales by Supplier Name and Supplier Category Name | Yes |
| Quantity and Sales by Category Names | **Needs Q3** — there are three category columns and they are not a clean hierarchy |
| Quantity and Sales by Package Types | Yes |

Currency: the brief says £ and the source amounts are £-prefixed text. No FX
conversion is involved — it's a single-currency dataset.

---

## 2. Table-by-table profile

All row counts are data rows (header excluded). Every file has a single sheet
named `Sheet1`.

### 2.1 `Sales.xlsx` — 212,774 rows × 35 cols (34.2 MB)

**Grain: one row per order line.** `OrderLineID` is unique across all 212,774
rows — verified, zero duplicates, zero full-row duplicates.

This file is **pre-joined and denormalized**: it flattens four source grains
into one table — Order header → Order line → Invoice → Customer transaction.
That is the single most important thing to know about it.

| Column | Type | Notes |
|---|---|---|
| `OrderLineID` | int | **Primary key.** 212,774 distinct = row count |
| `OrderID` | int | 67,628 distinct → avg 3.15 lines/order |
| `CustomerID` | int | 660 distinct, all resolve to Customer |
| `SalespersonPersonID` | int | 10 distinct — **no lookup table supplied** |
| `PickedByPersonID` | float | 19 distinct, 21,667 blanks — no lookup table |
| `ContactPersonID` | int | 660 distinct — no lookup table |
| `BackorderOrderID` | float | populated on 18,957 rows (8.9%) — self-reference to another `OrderID` |
| `OrderDate` | **text** | `"Tuesday, January 1, 2013"` — must be parsed. 990 distinct dates, 2013-01-01 → 2016-02-29 |
| `ExpectedDeliveryDate` | **text** | same format; = OrderDate + 1 day on 73% of rows |
| `CustomerPurchaseOrderNumber` | int | 9,970 distinct — degenerate attribute |
| `IsUndersupplyBackordered` | text | **constant `"Yes"`** on every row → drop |
| `PickingCompletedWhen` | datetime | **has a time component** (11:00, 12:00 …); 2,710 blanks |
| `StockItemID` | int | 227 distinct — matches Stock Item exactly |
| `PackageTypeID` | int | 4 distinct. **Redundant** — equals `StockItem.UnitPackageID` on 212,774/212,774 rows |
| `Quantity` | int | total 8,504,253 |
| `UnitPrice` | **text** | `"£230.00"` — currency-formatted text |
| `UnitPrice.1` | float | **100% blank** → drop |
| `UnitPrice.2` | float | numeric duplicate of `UnitPrice`; verified identical on every row. **Use this one**, drop the text version |
| `TaxRate` | float | 0.15 or 0.10 |
| `PickedQuantity` | int | total 8,189,581 — differs from `Quantity` on 2,710 rows |
| `InvoiceID` | float | 64,819 distinct; **2,857 rows blank** (2,809 orders never invoiced) |
| `BillToCustomerID` | float | 260 distinct — the paying parent of `CustomerID` |
| `AccountsPersonID`, `PackedByPersonID` | float | no lookup tables |
| `InvoiceDate`, `TransactionDate`, `FinalizationDate` | **text** | same long-date format. `InvoiceDate == TransactionDate` on 100% of rows; `FinalizationDate == InvoiceDate + 1 day` on 100% of rows |
| `TotalDryItems` | float | 6 distinct |
| `ConfirmedDeliveryTime` | datetime | **has a time component** |
| `ConfirmedReceivedBy` | text | 660 distinct person names |
| `CustomerTransactionID` | float | 1:1 with `InvoiceID` |
| `AmountExcludingTax`, `TaxAmount`, `TransactionAmount` | **text** | `"£2,300.00"` — and see the grain warning immediately below |
| `SupplierID` | int | 7 distinct. **Redundant** — equals `StockItem.SupplierID` on 212,774/212,774 rows |

> #### ⚠️ Grain trap — the most important finding in this profile
>
> `AmountExcludingTax`, `TaxAmount` and `TransactionAmount` are at **invoice
> grain, repeated on every order line of that invoice**. Verified: across all
> 64,819 invoices, zero have more than one distinct `AmountExcludingTax`;
> invoices carry 1–5 lines each (only 5,135 are single-line).
>
> `SUM(AmountExcludingTax)` over the line-grain fact table returns
> **£583,888,532** against a true ex-tax total of **£158,081,488** — a
> **3.69× overstatement**, and it silently looks plausible.
>
> The safe line-grain measure is `Quantity * UnitPrice`. I verified this
> reconciles **exactly** (to the penny, all 64,819 invoices) to the invoice
> header amount: `AmountExcludingTax == SUM(Quantity * UnitPrice)` per invoice.
> So nothing is lost by computing sales at line grain.

### 2.2 `Customer.xlsx` — 663 rows × 36 cols

**Grain: one row per customer.** `CustomerID` unique. 660 of 663 have sales;
3 customers never ordered.

Already denormalized — it has `CustomerCategoryName`, `BuyingGroupName`,
`DealDescription` etc. flattened in, so no extra dimension tables are needed.

Useful columns: `CustomerID` (PK), `CustomerName` (663 distinct),
`CustomerCategoryName` (5: Novelty Shop 459, Supermarket 58, Computer Store 51,
Gift Store 48, Corporate 47), `OnlineSalesConditional` (2: Online Sale 402,
Retail Sale 261), `BuyingGroupName` (Tailspin Toys / Wingtip Toys / blank),
`AccountOpenedDate` (date), `CreditLimit`, `BillToCustomerID`, delivery/postal
address fields.

Data quality:
- **`OnlineSalesConditional` is a customer attribute, not a per-order flag.**
  It is perfectly determined by `BuyingGroupName`: all 402 customers with a
  buying group are "Online Sale", all 261 without are "Retail Sale". So
  "online sales %" means *sales to online-type customers*, and computes to
  **63.34%** of turnover (£103.2m of £163.0m). Flagging this because the KPI
  wording implies an order-level flag, and there isn't one.
- **7 constant or empty columns** → drop: `DeliveryMethodID` (always 3),
  `StandardDiscountPercentage` (always 0), `IsStatementSent` (always False),
  `IsOnCreditHold` (always False), `PaymentDays` (always 7), `DeliveryRun`
  (100% blank), `RunPosition` (100% blank).
- `BillToCustomerID` self-references `CustomerID` (263 distinct parents, 263
  rows are their own bill-to) — a customer-hierarchy snowflake.
- `CreditLimit` blank on 402/663; `BuyingGroupID`, `SpecialDealID`,
  `DealDescription`, `StartDate`, `EndDate`, `DiscountPercentage` blank on
  261/663 (exactly the Retail Sale customers).
- `DeliveryCityID` / `PostalCityID` present (655 distinct) but **no City
  lookup table was supplied** → no geography analysis is possible.
- `DeliveryLocation` is WKT text (`POINT (-102.62 41.50)`) — not directly
  usable by Power BI map visuals without parsing.

### 2.3 `Warehouse Stock Item.xlsx` — 227 rows × 24 cols

**Grain: one row per stock item (product).** `StockItemID` unique. All 227 are
used in Sales.

Key columns: `StockItemID` (PK), `StockItemName` (227 distinct), `SupplierID`
(7 distinct), `ColorID` (7 distinct, **99/227 blank**), `UnitPackageID` (4),
`OuterPackageID` (3), `Size` (43 distinct, 64 blank), `UnitPrice`,
`RecommendedRetailPrice`, `TaxRate`, `TypicalWeightPerUnit`, `LeadTimeDays`,
`QuantityPerOuter`, `IsChillerStock`, and `CategoryName1/2/3`.

Data quality:
- `InternalComments` **100% blank** → drop. `Brand` populated on only 18/227
  (all "Northwind"). `Barcode` populated on only 8/227.
- `CustomFields` is a JSON string (`{"CountryOfManufacture": "China", …}`) and
  `Tags` is a JSON array string — parseable in Power Query if wanted, but not
  required by any KPI.
- **`CategoryName1/2/3` are not a clean hierarchy** — see Q3 in §5. C1 has 5
  values, C2 has 6, C3 has 7; 2 C2-values roll up to more than one C1, and 3
  C3-values roll up to more than one C2. Actual combinations present:

  ```
  Clothing            → Clothing            → Clothing            (16)
  Clothing            → Clothing            → Furry Footwear      (24)
  Clothing            → Clothing            → Novelty Items       ( 8)
  Clothing            → Computing Novelties → T-Shirts            (26)
  Computing Novelties → Computing Novelties → Novelty Items       ( 1)
  Computing Novelties → Computing Novelties → USB Novelties       ( 1)
  Computing Novelties → Mugs                → Novelty Items       (42)
  Computing Novelties → Novelty Items       → USB Novelties       (13)
  Novelty Items       → Novelty Items       → Novelty Items       ( 8)
  Novelty Items       → Novelty Items       → Toys                (18)
  Packaging Materials → Packaging Materials → Packaging Materials (67)
  Toys                → Toys                → Toys                ( 3)
  ```
  `Clothing → Computing Novelties → T-Shirts` in particular reads like three
  independent labels, not a drill path.

### 2.4 `Purchasing Supplier.xlsx` — 13 rows × 26 cols

**Grain: one row per supplier.** `SupplierID` unique. Only **7 of 13** suppliers
appear in Sales — the other 6 will show blank in any supplier visual unless
filtered out.

Key columns: `SupplierID` (PK), `SupplierName` (13 distinct), `SupplierCategoryID`
(8 distinct → FK to the catalogue table), `SupplierReference`, `PaymentDays`,
bank details, contact details, addresses.

Data quality:
- **`SupplierReference` has a leading underscore on all 13 rows** (`_AA20384`,
  `_B2084020`, …) → the brief's mandated `Text.Remove`/`Text.TrimStart` fix.
  Confirmed necessary.
- `InternalComments` populated on 2/13; `DeliveryMethodID` blank on 4/13;
  `DeliveryAddressLine1` blank on 4/13.
- Bank account columns (`BankAccountNumber`, `BankAccountCode`,
  `BankInternationalCode`, `BankAccountName`, `BankAccountBranch`) are not
  needed for any KPI and are mildly sensitive — recommend not loading them
  (also satisfies "load only required columns").

### 2.5 `Purchasing Supplier Catalogue.xlsx` — 9 rows × 2 cols

**Grain: one row per supplier category.** `SupplierCategoryID` (PK) +
`SupplierCategoryName`. All 8 categories used by suppliers resolve; 1 category
is unused.

This is a pure lookup — a snowflake level above Supplier. Per the modeling
skill ("flatten dimension hierarchies into one dimension table rather than
normalizing further" for small assignment datasets), I plan to **merge
`SupplierCategoryName` into the Supplier dimension in Power Query** and not
load this table separately.

### 2.6 `Warehouse Color.xlsx` — 36 rows × 5 cols

**Grain: one row per colour.** `ColorID` (PK) + `ColorName`. Only **7 of 36**
colours are used by stock items, and 99/227 stock items have no colour at all.

Data quality:
- **21 of 36 `ColorName` values have leading and/or trailing whitespace**
  (`"Azure      "`, `"      Black"`) → the brief's mandated `Text.Trim`.
  Confirmed necessary. After trimming, all 36 names are still unique (trimming
  does not create duplicates).
- `ValidFrom` is **text with two inconsistent formats** — `"1/1/2013"` and
  `"1/1/2016 4:00:00 PM"`. `ValidTo` is `9999-12-31` on all rows. These are
  SCD bookkeeping columns; nothing depends on them and I plan to drop them
  (also avoids the "don't store timestamps" rule).
- `LastEditedBy` — audit column, drop.

### 2.7 `Warehouse Package Type.xlsx` — 14 rows × 2 cols

**Grain: one row per package type.** `PackageTypeID` (PK) + `PackageTypeName`
(Bag, Block, Bottle, …). Only **4 of 14** appear in Sales.

---

## 3. Referential integrity — all clean

Checked every candidate join. **Zero orphans anywhere**:

| Relationship | Distinct FK values | Orphans | Unused dim members |
|---|---|---|---|
| Sales.CustomerID → Customer.CustomerID | 660 | 0 | 3 |
| Sales.StockItemID → StockItem.StockItemID | 227 | 0 | 0 |
| Sales.PackageTypeID → PackageType.PackageTypeID | 4 | 0 | 10 |
| Sales.SupplierID → Supplier.SupplierID | 7 | 0 | 6 |
| Sales.BillToCustomerID → Customer.CustomerID | 260 | 0 | 403 |
| StockItem.SupplierID → Supplier.SupplierID | 7 | 0 | 6 |
| StockItem.ColorID → Color.ColorID | 7 | 0 | 29 |
| StockItem.UnitPackageID → PackageType.PackageTypeID | 4 | 0 | 10 |
| StockItem.OuterPackageID → PackageType.PackageTypeID | 3 | 0 | 11 |
| Supplier.SupplierCategoryID → Catalogue.SupplierCategoryID | 8 | 0 | 1 |

Two **redundant FKs on the fact** worth noting — both are 100% derivable from
`StockItemID`:
- `Sales.SupplierID` == `StockItem.SupplierID` on all 212,774 rows
- `Sales.PackageTypeID` == `StockItem.UnitPackageID` on all 212,774 rows
  (it matches `OuterPackageID` on only 174,853 — so it is specifically the
  *unit* package)

Keeping them as direct fact→dim relationships is fine and avoids snowflaking
through Stock Item; they carry no extra information but they do make the star
flatter. See Q5.

## 4. Date coverage

- Order dates run **2013-01-01 → 2016-02-29**, 990 distinct dates over a
  1,155-day span.
- The 165 missing days are **all Sundays** — the company doesn't trade on
  Sundays. This is normal and is exactly why the Date dimension must be a
  generated contiguous calendar rather than a distinct list of order dates.
- **2016 is a partial year** (2 months only). Headline yearly figures:

  | Year | Orders | Lines | Quantity | Sales (ex-tax) | Avg order |
  |---|---|---|---|---|---|
  | 2013 | 19,450 | 61,655 | 2,473,653 | £46,928,592.80 | £2,412.78 |
  | 2014 | 21,199 | 66,852 | 2,672,973 | £51,492,003.40 | £2,428.98 |
  | 2015 | 23,329 | 73,003 | 2,873,250 | £55,817,887.45 | £2,392.64 |
  | 2016 | 3,650 | 11,264 | 484,377 | £8,711,620.80 | £2,386.75 |

  **YoY for 2016 will look catastrophic (-84%) and will be wrong as a business
  statement.** The report needs either a same-period-last-year comparison or a
  visible "data through 2016-02-29" caveat. Raising now rather than after the
  measures are built.
- `PickingCompletedWhen` extends to 2016-05-30, past the last order date.
- Date dimension should therefore span **2013-01-01 → 2016-12-31** (full years,
  per the usual rule that a date table covers whole years).

Sanity-check figures the finished model should reproduce (line grain, ex-tax,
all lines including uninvoiced):
- Unique orders: **67,628**
- Total sales: **£162,950,104.45**
- Average order amount: **£2,409.51**
- Online sales share: **63.34%**
- Top customer by turnover: Mauno Laurila, £360,352.70 across 112 orders

## 5. Proposed model — star schema

One fact, five dimensions. `Sales.xlsx` is already close to a star once the
invoice-grain columns are handled, so no bridge tables are needed.

```
              Dim Date        Dim Customer
                  |                |
                  v                v
              +---------------------------+
Dim Supplier->|      Fact Sales           |<- Dim Package Type
              |  (one row per order line) |
              +---------------------------+
                            ^
                            |
                      Dim Product
                    (+ Colour merged in)
```

### Fact Sales — grain: **one row per order line** (212,774 rows)

Keys: `OrderLineID` (degenerate PK), `OrderID` (degenerate, for distinct order
count), `CustomerID`, `StockItemID`, `SupplierID`, `PackageTypeID`, `OrderDate`
(→ Dim Date).

Measures/numerics: `Quantity`, `PickedQuantity`, `UnitPrice` (from
`UnitPrice.2`), `TaxRate`, and a **Power Query calculated column
`Line Amount = Quantity * UnitPrice`** (per the best-practices rule preferring
Power Query calculated columns over DAX ones).

Dropped from the fact: `UnitPrice` (text), `UnitPrice.1` (empty),
`IsUndersupplyBackordered` (constant), `AmountExcludingTax` / `TaxAmount` /
`TransactionAmount` (invoice grain — the trap in §2.1), `InvoiceDate` /
`TransactionDate` / `FinalizationDate` (all derivable from each other and
near-identical to `OrderDate`), the five unresolvable person IDs,
`ConfirmedReceivedBy`, `ConfirmedDeliveryTime`, `PickingCompletedWhen`,
`TotalDryItems`, `CustomerTransactionID`, `BillToCustomerID`,
`CustomerPurchaseOrderNumber` — none is needed by any of the 9 KPIs. Easy to
add back if wanted; listing them so the omission is a visible choice.

### Dimensions

| Dimension | Source | Grain | Key | Rows |
|---|---|---|---|---|
| **Dim Date** | DAX calculated table (`CALENDAR`) | one row per day | `Date` | 1,461 (2013-01-01 → 2016-12-31) |
| **Dim Customer** | `Customer.xlsx` | one row per customer | `CustomerID` | 663 |
| **Dim Product** | `Warehouse Stock Item.xlsx` + `Warehouse Color.xlsx` merged | one row per stock item | `StockItemID` | 227 |
| **Dim Supplier** | `Purchasing Supplier.xlsx` + `Purchasing Supplier Catalogue.xlsx` merged | one row per supplier | `SupplierID` | 13 |
| **Dim Package Type** | `Warehouse Package Type.xlsx` | one row per package type | `PackageTypeID` | 14 |

Plus a **Measures** table (empty table holding all explicit measures), per the
best-practices Development Checklist.

All relationships single-direction, many (fact) → one (dim), no bidirectional
filtering, no many-to-many. **7 source files → 5 loaded dimensions**, because
Colour and Supplier Catalogue are merged into their parents in Power Query
(flatten-don't-snowflake, per the modeling skill) and their queries have load
disabled.

### Power Query work required

Mandated by the brief:
1. `Purchasing Supplier`: strip leading `_` from `SupplierReference`
2. `Warehouse Color`: `Text.Trim` on `ColorName`

Required by the data (not in the brief, but necessary):
3. Parse the five text date columns from `"Tuesday, January 1, 2013"` — needs
   an explicit locale (`en-US`/`en-GB`) in `Date.FromText`, otherwise this
   breaks on a differently-localed machine. Best-practices doc calls out
   locale awareness specifically.
4. Parse `"£2,300.00"`-style currency text to decimal — or sidestep it entirely
   by using `UnitPrice.2` (already numeric) and computing `Line Amount`
   ourselves, which is what I propose.
5. Type every column explicitly; `Date` type (not `Date/Time`) on all dates.
6. Drop the constant/empty columns listed in §2.
7. Merge Colour → Stock Item, Supplier Catalogue → Supplier.
8. Group queries into folders (Facts / Dimensions / Staging).

---

## 6. Open questions — blocking, per `CLAUDE.md` §1

Posted on issue #1. Modeling does not start until these are answered; each one
would be expensive to unwind after measures and visuals are built on top.

**Q1 — Which sales amount is "sales"?** Confirmed above that
`AmountExcludingTax` is invoice grain (3.69× inflation if summed at line
grain), and that `Quantity * UnitPrice` reconciles to it exactly per invoice.
My recommendation: define **Total Sales = SUMX(Fact Sales, Quantity *
UnitPrice)**, ex-tax, at line grain. Alternative: define sales tax-inclusive
(`TransactionAmount` equivalent, +10–15%). The brief says "Average order amount
in £" without specifying — I need gross-vs-net confirmed before writing any
measure, because all 9 KPIs depend on it.

**Q2 — Include the 2,857 uninvoiced order lines (2,809 orders)?** These are
ordered but never invoiced. Including them: 67,628 orders / £162,950,104.
Excluding them: 64,819 orders / £158,081,488 — a £4.87m (3.0%) difference.
"Unique order count" and "Average order amount" both move. My recommendation:
**include them** and treat the metric as order-based (the brief says "order
count", not "invoice count"), but this is a business call.

**Q3 — "Quantity and Sales by Category Names" — which category?** There are
three columns (`CategoryName1/2/3`) and they are **not a valid hierarchy** (§2.3:
2 C2-values roll up to multiple C1-values, 3 C3-values roll up to multiple
C2-values; `Clothing → Computing Novelties → T-Shirts` is the clearest
example). Options: (a) expose all three as three independent attributes on Dim
Product and let the user pick — my recommendation, it's honest about the data;
(b) pick one as *the* category; (c) build a proper category dimension +
bridge, accepting a many-to-many and its double-counting risk. The plural
"Category Names" in the brief hints at (a). Per the modeling skill, "a product
in multiple categories" is an explicit escalation trigger — not mine to decide.

**Q4 — "YTD, MTD sales – all and separated by categories (Online Sales
Conditional)".** The parenthetical suggests "categories" here means
`OnlineSalesConditional` (Online Sale / Retail Sale), but "categories" could
equally mean `CustomerCategoryName` (5 values) or the product categories from
Q3. My reading: **`OnlineSalesConditional`**, since the brief names it
explicitly. Confirming because it changes how many measure variants get built.

**Q5 — Keep `SupplierID` and `PackageTypeID` as direct fact→dim
relationships, or snowflake through Dim Product?** Both are 100% derivable from
`StockItemID` (§3), so either is correct — no data is at risk. Direct
relationships give a flatter star and simpler DAX; going through Dim Product
gives a smaller fact table and one obvious source of truth per attribute. My
recommendation: **keep both as direct fact→dim relationships** (flatter star,
matches how the brief phrases the KPIs). Low-stakes, but it changes the model
diagram, so worth one line of confirmation rather than a later rebuild.

**Q6 (non-blocking, flagging early) — 2016 is a partial year** (ends
2016-02-29). YoY 2016 vs 2015 reads as -84% and is meaningless as stated. Do
you want the YoY measure to compare like-for-like periods
(`DATESINPERIOD`/same-period-last-year to the same cut-off), or plain
`SAMEPERIODLASTYEAR` with a caveat on the report page? Won't block modeling —
I'll build plain YoY and note it — but it affects the analysis write-up.

---

## 7. Human follow-up (out of agent scope)

From `docs/best-practices/power-bi-best-practices.md`, the items this agent
cannot do — for the human opening the `.pbip` in Desktop:

**Pre-development (Desktop settings):** disable "Update or delete relationships
when refreshing data", "Autodetect new relationships after data is loaded",
**"Auto date/time"** (important — the brief mandates a custom Date table),
Q&A if unused, and background data preview download; set Data Cache Management
to max; apply the client colour template.

**Report layer:** per `CLAUDE.md` §2, TMDL does not describe visuals reliably.
Whatever report definition gets generated needs a human pass in Desktop —
page size 1920×1080, filter pane over on-canvas slicers, test cross-page
interactions, configure the default page.

**Service / release (brief tasks 6 and 7):** publish to the personal workspace,
configure and test refresh, validate the data in the Service, configure user
access, then present.

---

## 8. Run log

| Date | Run | What happened |
|---|---|---|
| 2026-09-01 | issue #1, "Start BI Task 1" | Discover + Profile only, as instructed. Read the brief, profiled all 7 files, verified referential integrity and grain, wrote this file. **Stopped before modeling** — six open questions posted to issue #1. No PBIP/TMDL created yet. |

### Next run should

1. Read the answers to Q1–Q6 in issue #1.
2. Record each as a numbered file in `docs/decisions/` (template:
   `docs/decisions/0000-template.md`). Note `0001` is taken (bash scope).
3. Update §6 of this file to mark them resolved, and update §5 if the answers
   change the proposed model.
4. Then, and only then, start on the PBIP/TMDL per
   `.claude/skills/pbip-tmdl-structure/SKILL.md`.
