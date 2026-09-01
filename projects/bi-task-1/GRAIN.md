# BI Task 1 — Table granularity

This file answers **assignment task 4**: "outline and describe the level of
granularity for every table in a separate file." The brief suggests Excel or
Word; in this repo the git-native equivalent is a markdown file that diffs and
reviews alongside the model it describes.

Two sections: the seven source workbooks as delivered, then the nine tables
that actually exist in the semantic model.

---

## 1. Source files as delivered

| File | Rows | Grain — one row per… | Primary key |
|---|---|---|---|
| `Sales.xlsx` | 212,774 | **order line** | `OrderLineID` |
| `Customer.xlsx` | 663 | customer | `CustomerID` |
| `Warehouse Stock Item.xlsx` | 227 | stock item (product) | `StockItemID` |
| `Purchasing Supplier.xlsx` | 13 | supplier | `SupplierID` |
| `Purchasing Supplier Catalogue.xlsx` | 9 | supplier category | `SupplierCategoryID` |
| `Warehouse Color.xlsx` | 36 | colour | `ColorID` |
| `Warehouse Package Type.xlsx` | 14 | package type | `PackageTypeID` |

### `Sales.xlsx` — the one that needs care

Its stated grain is one order line, and `OrderLineID` is genuinely unique
across all 212,774 rows. But the file is a **pre-joined flattening of four
different grains**, and three of its columns never descended to line grain:

| Columns | Actual grain | Rows they repeat across |
|---|---|---|
| `OrderID`, `OrderDate`, `ExpectedDeliveryDate`, `CustomerPurchaseOrderNumber`, `SalespersonPersonID`, `BackorderOrderID` | order header | 3.15 lines per order on average |
| `OrderLineID`, `StockItemID`, `Quantity`, `UnitPrice`, `TaxRate`, `PickedQuantity`, `PackageTypeID` | **order line** | — this is the file's grain |
| `InvoiceID`, `InvoiceDate`, `BillToCustomerID`, `TotalDryItems`, `ConfirmedDeliveryTime` | invoice | 1–5 lines per invoice |
| `CustomerTransactionID`, `TransactionDate`, **`AmountExcludingTax`**, **`TaxAmount`**, **`TransactionAmount`**, `FinalizationDate` | customer transaction (1:1 with invoice) | 1–5 lines per invoice |

The three money columns in bold are the trap. Summing `AmountExcludingTax` at
line grain gives **£583,888,532** against a true ex-tax total of
**£158,081,488** — a 3.69× overstatement that looks perfectly plausible on a
chart. They are therefore **not loaded into the model at all**. Sales is
computed at the fact's own grain as `Quantity × Unit Price`, which was verified
to reconcile to the penny against the invoice header amount on all 64,819
invoices. See `docs/decisions/0002`.

### `Warehouse Stock Item.xlsx` — a hidden second grain

The file's grain is one stock item, correctly. But `CategoryName1/2/3` are not
three attributes of the product — they are a **flattening of a
product-to-stock-group many-to-many** into three fixed slots, sorted
alphabetically and padded by repetition where a product has fewer than three
tags. The true grain of that information is *one product-category membership*
(441 rows across 227 products), which is why the model splits it out into
`Bridge Product Category`. See `docs/decisions/0004`.

---

## 2. Semantic model tables

### Fact

| Table | Rows | Grain | Key | Additive measures |
|---|---|---|---|---|
| `Fact Sales` | 212,774 | **one order line** — one product on one order | `Order Line ID` (degenerate) | `Quantity`, `Picked Quantity`, `Line Amount` |

`Order ID` is also a degenerate dimension on this table (67,628 distinct
values), because there is no separate order header table — the "unique order
count" KPI is a `DISTINCTCOUNT` over it, not a row count.

Non-additive columns on the fact: `Unit Price` and `Tax Rate`, both set to
`summarizeBy: none` so they cannot be accidentally summed.

### Dimensions

| Table | Rows | Grain | Key | Source |
|---|---|---|---|---|
| `Dim Date` | 1,461 | **one calendar day**, 2013-01-01 → 2016-12-31 | `Date` | DAX calculated table (`CALENDAR`) |
| `Dim Customer` | 663 | **one customer** | `Customer ID` | `Customer.xlsx` |
| `Dim Product` | 227 | **one stock item** | `Stock Item ID` | `Warehouse Stock Item.xlsx` + `Warehouse Color.xlsx` merged |
| `Dim Supplier` | 13 | **one supplier** | `Supplier ID` | `Purchasing Supplier.xlsx` + `Purchasing Supplier Catalogue.xlsx` merged |
| `Dim Package Type` | 14 | **one package type** | `Package Type ID` | `Warehouse Package Type.xlsx` |
| `Dim Category` | 9 | **one product stock-group tag** | `Category` | union of `CategoryName1/2/3` |

`Dim Date` spans whole calendar years rather than the observed order-date range
(2013-01-01 → 2016-02-29) so that time intelligence has complete years to work
with. It is contiguous by construction, which matters here: the company never
trades on a Sunday, so 165 days are absent from the order dates and a
distinct-date list would have silently broken `SAMEPERIODLASTYEAR`.

### Bridge

| Table | Rows | Grain | Keys |
|---|---|---|---|
| `Bridge Product Category` | 441 | **one product-to-category membership** | `Stock Item ID` + `Category` |

94 products carry one tag, 52 carry two, 81 carry three. This table is hidden;
report authors use `Dim Category[Category]`.

### Measures

| Table | Rows | Grain |
|---|---|---|
| `_Measures` | 1 | none — a placeholder row so the table can exist. It holds all 22 explicit measures and no data. |

---

## 3. Relationship grain summary

Every relationship is **many-to-one**, fact or bridge on the many side:

| From (many) | To (one) | Direction |
|---|---|---|
| `Fact Sales[Order Date]` | `Dim Date[Date]` | single |
| `Fact Sales[Customer ID]` | `Dim Customer[Customer ID]` | single |
| `Fact Sales[Stock Item ID]` | `Dim Product[Stock Item ID]` | single |
| `Fact Sales[Supplier ID]` | `Dim Supplier[Supplier ID]` | single |
| `Fact Sales[Package Type ID]` | `Dim Package Type[Package Type ID]` | single |
| `Bridge Product Category[Stock Item ID]` | `Dim Product[Stock Item ID]` | **both** |
| `Bridge Product Category[Category]` | `Dim Category[Category]` | single |

Referential integrity was verified across all ten candidate joins in the source
data: **zero orphans on every one**. The single bidirectional relationship is
the standard bridge pattern and is justified in `docs/decisions/0004`.
