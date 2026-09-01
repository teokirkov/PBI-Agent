# BI Task 1 — Analysis

Written findings from the seven source files and the model built on them. All
figures are ex-tax, at order-line grain, and include the never-invoiced orders
(`docs/decisions/0002`, `0003`). Data covers **1 January 2013 → 29 February
2016**.

Two halves: what the business looks like, then what is wrong with the data. The
second half matters as much as the first — a couple of the assignment's KPIs
ask for things this dataset cannot honestly deliver, and it is better to say so
than to produce a confident-looking chart.

---

## 1. Headline

| Measure | Value |
|---|---|
| Total sales | **£162,950,104.45** |
| Unique orders | **67,628** |
| Order lines | 212,774 |
| Average order amount | **£2,409.51** |
| Units ordered | 8,504,253 |
| Active customers | 660 (of 663 on file) |
| Products sold | 227 (all of them) |
| Online sales share | **63.34%** |

### Growth is steady, and 2016 is not a collapse

| Year | Orders | Sales | Avg order | YoY (like-for-like) |
|---|---|---|---|---|
| 2013 | 19,450 | £46,928,592.80 | £2,412.78 | — |
| 2014 | 21,199 | £51,492,003.40 | £2,428.98 | +9.7% |
| 2015 | 23,329 | £55,817,887.45 | £2,392.64 | +8.4% |
| 2016 (Jan–Feb) | 3,650 | £8,711,620.80 | £2,386.75 | **−1.7%** |

The 2016 row is the one to read carefully. Compared against a full 2015 it
reads **−84.4%**, which is meaningless — it only says the year is two months
long. Against the same 1 January – 28/29 February window in 2015
(£8,863,884.50) it is **−1.7%**: flat, slightly soft, not a collapse. That
like-for-like cut is what `[Sales YoY %]` implements (`docs/decisions/0007`).

Growth is coming almost entirely from **order volume, not order size** — orders
grew 9.0% then 10.1% while average order value stayed within £40 of £2,410
across all four years. Whatever is driving the business, it is not basket size.

---

## 2. What the business looks like

### The online share is quietly shrinking

This is the clearest genuine trend in the data:

| Year | Online | Retail | Online share |
|---|---|---|---|
| 2013 | £30,954,508 | £15,974,085 | **65.96%** |
| 2014 | £32,729,644 | £18,762,359 | 63.56% |
| 2015 | £34,218,805 | £21,599,082 | 61.30% |
| 2016 (Jan–Feb) | £5,313,531 | £3,398,090 | 60.99% |

Retail-type customers grew their spend 35% over 2013–2015 while online-type
customers grew 11%. Online is still the larger half, but it has lost five
percentage points of share in three years. Whether that is a strategic shift or
a neglected channel is a question for the business, but it is the finding most
worth putting in front of them.

**Important caveat on this whole section**, see §3.2: the online/retail split is
a *customer* attribute, not a per-order channel flag. This measures sales to
online-type customers, not orders actually placed online.

### Sales are concentrated in packaging, not toys

| Category tag | Quantity | Sales |
|---|---|---|
| Packaging Materials | 5,374,949 | £93,889,093.65 |
| Clothing | 2,619,564 | £46,441,923.00 |
| Computing Novelties | 2,009,366 | £38,170,902.60 |
| Novelty Items | 1,002,767 | £31,489,359.80 |
| T-Shirts | 1,658,268 | £29,848,824.00 |
| Toys | 111,866 | £13,880,224.00 |
| Furry Footwear | 362,751 | £4,717,524.00 |
| USB Novelties | 74,927 | £4,449,870.60 |
| Mugs | 224,901 | £2,923,713.00 |

*(These overlap — see §3.1. Each row is correct; they do not sum to the total.)*

For a company the brief describes as a toy company, **the single biggest
product line is bubble wrap.** Packaging Materials alone is £93.9m, 58% of all
sales, and the top eight products by revenue are all packaging supplies (air
cushion machines, anti-static bubble wrap, double-sided bubble wrap). Toys are
£13.9m. One supplier, Litware Inc., accounts for £93.9m of turnover on its own.

That may be exactly right — a toy wholesaler shipping fragile goods sells a lot
of packaging — but it is worth confirming, because if packaging is meant to be a
cost line rather than a revenue line then something upstream has merged two
different kinds of transaction into one file.

### Supplier concentration is extreme

| Supplier | Category | Quantity | Sales |
|---|---|---|---|
| Litware, Inc. | Packaging Supplier | 5,374,949 | £93,889,093.65 |
| Fabrikam, Inc. | Clothing Supplier | 2,619,564 | £46,441,923.00 |
| Northwind Electric Cars | Toy Supplier | 96,022 | £13,626,720.00 |
| The Phone Company | Novelty Goods Supplier | 126,197 | £5,398,365.60 |
| Graphic Design Institute | Novelty Goods Supplier | 224,901 | £2,923,713.00 |
| A Datum Corporation | Novelty Goods Supplier | 46,776 | £416,785.20 |
| Contoso, Ltd. | Novelty Goods Supplier | 15,844 | £253,504.00 |

Two suppliers are **86% of turnover**. Six of the 13 suppliers on file have no
sales at all. That is a concentration risk worth naming even though the brief
did not ask for it.

### Package type is not a useful dimension

The brief asks for quantity and sales by package type, so the model supports it,
but the answer is nearly degenerate: only 4 of 14 package types appear, and
"Each" is £158.5m of the £163.0m (97%). The other three — Packet £2.7m, Pair
£1.3m, Bag £0.4m — round to nothing on a chart. Expect this visual to look
broken; it is not.

### Trading pattern

The company **never trades on a Sunday** — all 165 missing calendar days in the
window are Sundays, without exception. Saturday runs at about half a weekday
(£14.8m against £29–30m for each of Monday–Friday). Monday to Friday are within
4% of each other. This is encoded as `Dim Date[Is Trading Day]`, and it is why
the Date dimension had to be a generated contiguous calendar rather than a
distinct list of order dates — otherwise `SAMEPERIODLASTYEAR` would have been
walking a calendar with holes in it.

Monthly seasonality is mild: indexed against the average month across the three
complete years, February is the low point at 0.83 and July the high at 1.15.
Nothing that would justify a seasonal adjustment.

---

## 3. Data problems

### 3.1 Product categories are a broken many-to-many — the significant one

The brief asks for "Quantity and Sales by **Category Names**". The source
supplies three columns, `CategoryName1/2/3`, and they are **not a hierarchy**.
They are an **alphabetically sorted, repetition-padded flattening of a
product-to-stock-group many-to-many**, squeezed into three fixed slots.

The evidence is not ambiguous:

- **All 227 of 227 rows are alphabetically non-decreasing** across the three
  columns. Every one of the 12 distinct combinations satisfies C1 ≤ C2 ≤ C3. A
  real hierarchy would not be accidentally alphabetical 227 times running.
- **94 rows repeat a single value three times** (`Packaging Materials`,
  `Packaging Materials`, `Packaging Materials`) and 52 more repeat one of two
  values. That is padding, not three levels of meaning.
- The semantics only parse as sibling tags. A DBA joke mug is `Computing
  Novelties / Mugs / Novelty Items`. A joke t-shirt is `Clothing / Computing
  Novelties / T-Shirts`. Read as a drill path, the second one claims T-shirts
  are a kind of computing novelty which is a kind of clothing.
- The union of the three columns is one shared domain of **9 values**, not three
  domains of 5, 6 and 7.

So 227 products carry **441 category memberships** (94 products have one tag, 52
have two, 81 have three), and the model reconstructs that as `Dim Category` +
`Bridge Product Category` (`docs/decisions/0004`).

**Three things follow, and all three need saying out loud on the report page:**

1. **Category subtotals overlap and will not add up.** Sales by category sums to
   £265,811,435 against a grand total of £162,950,104 — an overlap factor of
   **1.63×** — because a three-tag product is counted under each of its tags.
   Every individual category figure is right; the column just does not
   reconcile, and Power BI's total row will correctly show £162.95m while the
   visible rows sum to more. Anyone who needs a breakdown that reconciles must
   use `Dim Product[Category Group]` instead, which gives each product exactly
   one label built from its full tag set.

2. **Picking any one of the three columns as "the" category would have
   misstated most categories badly.** By `CategoryName1` alone, Computing
   Novelties is £8.3m; as a tag it is £38.2m — a 4.6× understatement, purely
   because "Computing Novelties" happens to sort after "Clothing" for 26 of the
   products carrying it. Slot 1 is not "the primary category", it is "the
   alphabetically first tag". This is the trap the flattening sets.

3. **There is an unmeasurable data loss and it cannot be fixed downstream.** The
   flattening stops at three slots. 81 products fill all three. If any of those
   originally belonged to a *fourth* stock group, that membership was discarded
   before the file reached us, and there is nothing in this extract that could
   detect it — the three columns look equally full whether the product had three
   tags or seven.

   **Recommendation:** ask for the underlying product-to-stock-group table
   instead of the flattened `CategoryName1/2/3` columns. That is a one-line
   change at source and it removes the guesswork, the padding, and the
   truncation risk in one go. Until then, treat category figures as a floor.

### 3.2 The "online sales" KPI measures something other than what it says

`OnlineSalesConditional` sits on the **customer**, not the order. It is also
perfectly determined by `BuyingGroupName` — all 402 customers with a buying
group are "Online Sale", all 261 without are "Retail Sale", with no exceptions.
It is a customer segmentation label, not a transaction channel.

There is **no order-level channel flag anywhere in the seven files.** So the
"online sales as a % of overall sales" KPI can only be answered as *sales to
online-type customers* (63.34%), and the model names the column `Sales Channel`
with that caveat in its description. A genuine online-vs-offline split would
need a field that does not exist in this extract.

### 3.3 The uninvoiced orders are unfulfilled orders, and the rate is climbing

2,809 orders (£4,868,616, 3.0% of sales) were never invoiced. Per
`docs/decisions/0003` they are included in every sales figure, with
`[Uninvoiced Sales]`, `[Uninvoiced Orders]` and `[Uninvoiced Sales %]` exposed
so the report can show what that is worth.

Digging into *why* they are uninvoiced turned up something the profiling run had
not connected. Three facts line up exactly:

- 2,710 order lines have `PickedQuantity = 0`.
- Those same 2,710 lines are the only ones with no `PickingCompletedWhen`.
- **All 2,710 of them are uninvoiced.** Not one picked line went un-invoiced
  except the 147 noted below.

So the £4.87m is not an invoicing backlog — it is **£4.68m of orders that were
never picked**, plus £0.19m across 147 lines that were picked in full and then
still not invoiced. 2,662 of the 2,809 uninvoiced orders were never picked at
all.

And the rate is deteriorating year on year:

| Year | Uninvoiced orders | Share of that year's orders | Uninvoiced sales |
|---|---|---|---|
| 2013 | 449 | 2.31% | £853,229.60 |
| 2014 | 797 | 3.76% | £1,474,185.20 |
| 2015 | 1,318 | **5.65%** | £2,161,665.10 |
| 2016 (Jan–Feb) | 245 | **6.71%** | £379,536.10 |

Unfulfilled orders have nearly tripled as a share of the book in three years.
That is an operational finding, not a data-quality one, and it is arguably more
actionable than anything in §2 — it is the one place in this dataset where
something is clearly getting worse. It is also the reason the "Data Quality &
Caveats" report page is worth building properly rather than treating as a
footnote.

One consequence for interpreting the headline: because these orders are
included, `[Total Sales]` counts £4.87m of goods that were, as far as the data
shows, never shipped. That is the user's decision and it is the right one for an
*order*-based report, but it should not be read as revenue.

### 3.4 The invoice-grain trap in `Sales.xlsx`

Covered in full in `docs/decisions/0002` and `GRAIN.md`; repeated here because
it is the single easiest way to get this dataset badly wrong.
`AmountExcludingTax`, `TaxAmount` and `TransactionAmount` are at invoice grain,
repeated on every order line of that invoice. Summing `AmountExcludingTax`
across the 212,774-row fact returns **£583,888,532** against a true ex-tax total
of **£158,081,488** — 3.69× too high, with nothing about the number that looks
suspicious. The three columns are not loaded into the model at all, so the
mistake is now unavailable.

### 3.5 Smaller items, for completeness

- **Five date columns arrive as text** in US long-date form
  (`"Tuesday, January 1, 2013"`). Parsed with an explicit `en-US` culture, so the
  refresh does not depend on the machine's regional settings. Only `OrderDate`
  is loaded; `InvoiceDate`, `TransactionDate` and `FinalizationDate` are
  arithmetically derivable from it and from each other
  (`InvoiceDate == TransactionDate` on 100% of rows,
  `FinalizationDate == InvoiceDate + 1 day` on 100% of rows).
- **Money columns arrive as text** (`"£2,300.00"`). Sidestepped: `Sales.xlsx`
  has three columns all headed `UnitPrice` — currency text, always empty, and
  numeric — and the numeric one is identical to the text one on every row, so
  the model reads that and never parses currency strings.
- **`SupplierReference`'s underscore is not always leading.** The earlier
  profile said it was; it is not. 8 of the 13 values carry it in front
  (`_AA20384`) and 5 carry it trailing (`082420938_`). A `Text.TrimStart` would
  have silently left five values dirty, so the fix is
  `Text.Remove(_, {"_"})`.
- **`ColorName` padding**: 21 of 36 values have leading and/or trailing
  whitespace. `Text.Trim` fixes it and does not create duplicates — all 36 names
  stay unique. Note `"      Steel Gray"` has a legitimate internal space, which
  `Text.Trim` correctly leaves alone.
- **Constant and empty columns dropped**: `IsUndersupplyBackordered` (always
  `"Yes"`), `UnitPrice.1` (100% blank), and seven on `Customer.xlsx`
  (`DeliveryMethodID`, `StandardDiscountPercentage`, `IsStatementSent`,
  `IsOnCreditHold`, `PaymentDays`, `DeliveryRun`, `RunPosition`).
- **Five person-ID columns have no lookup table** (`SalespersonPersonID`,
  `PickedByPersonID`, `ContactPersonID`, `AccountsPersonID`,
  `PackedByPersonID`). Sales-by-salesperson would be a reasonable thing to want
  from a report like this and it is not possible — there are 10 salespeople but
  no names. Worth requesting.
- **No City lookup table was supplied**, so `DeliveryCityID` / `PostalCityID`
  (655 distinct) are unusable and there is no geography analysis in this report
  at all. `DeliveryLocation` is WKT text (`POINT (-102.62 41.50)`) which Power
  BI map visuals cannot consume without parsing. Also worth requesting.
- **Special-deal columns are dated outside the data window** — every
  `StartDate`/`EndDate` on `Customer.xlsx` falls in 2016 Q2, after the last
  order date. No discount in this file was ever applicable to any order in it,
  so discount analysis is not possible and the columns are not loaded.
- **Referential integrity is clean.** All ten candidate joins were checked and
  every one has **zero orphans**. Unused dimension members are common though —
  6 of 13 suppliers, 10 of 14 package types, 29 of 36 colours and 3 of 663
  customers never appear in Sales.

### 3.6 A caution about how uniform this data is

Several distributions are flatter than real trading data ever is, and it changes
how much weight the KPIs can carry:

- **660 customers, and the largest is 0.22% of sales.** The top 10 customers are
  **2.1%** of turnover; the top 100 are 19.2%. The smallest active customer still
  spent £11,011. Real B2B books are Pareto-shaped; this one is almost perfectly
  even.
- Average order value varies by less than £40 across four years.
- Monthly seasonality spans only 0.83–1.15.

The practical consequence is for the **"TOP customers by number of orders and
turnover" KPI**. The model builds it (`[Customer Rank by Sales]`,
`[Customer Rank by Orders]`) and it is mechanically correct, but with a 0.22%
leader the ranking is close to noise — first and tenth place differ by 8%, and
the ordering would likely reshuffle with a month more data. Present it as a
league table if the brief requires it, but do not build a narrative on who is at
the top.

This pattern is consistent with a generated or heavily anonymised dataset, which
would be unsurprising for an assignment. It does not affect whether the model is
correct — it affects which conclusions are safe to draw from it.

---

## 4. What a reader of the report should be told

Four captions worth putting on the canvas rather than leaving in this file:

1. **"Data through 29 February 2016."** `[Last Sales Date]` is a measure for
   exactly this. Without it, every 2016 figure invites a wrong conclusion.
2. **"YoY compares like-for-like periods."** Otherwise a reader who checks the
   arithmetic against full-year 2015 will think the measure is broken.
3. **"A product can carry up to 3 category tags, so category figures overlap and
   do not sum to the total."** On the Products & Categories page, next to the
   category visual.
4. **"Sales include £4.9m of orders that were never invoiced (3.0%), most of
   which were never picked."** On the Overview page, not buried on the data
   quality page.

## 5. Open items for the business

1. **Request the product-to-stock-group table** instead of the flattened
   `CategoryName1/2/3` columns (§3.1). Highest-value single fix.
2. **Confirm whether packaging materials belong in this revenue file** (§2).
   58% of "toy company" sales being bubble wrap is either the real business or a
   merged transaction type.
3. **Investigate the unpicked-order trend** (§3.3). 2.31% → 6.71% in three
   years, £4.7m outstanding.
4. **Supply a City lookup table and a Person/Salesperson table** if geography or
   salesperson performance is ever wanted (§3.5).
5. **Clarify whether an order-level online/offline flag exists upstream**
   (§3.2). If it does, the online sales KPI becomes what the brief actually asks
   for.
