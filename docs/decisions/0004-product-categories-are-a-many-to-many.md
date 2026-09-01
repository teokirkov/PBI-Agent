# 0004 — Product categories are a many-to-many, modelled with a bridge

- **Project:** `projects/bi-task-1/`
- **Date:** 2026-09-01
- **Status:** decided

## The fork in the road

The assignment asks for "Quantity and Sales by **Category Names**".
`Warehouse Stock Item.xlsx` has three category columns, and the profiling run
flagged that they do not form a clean hierarchy: two `CategoryName2` values
roll up to more than one `CategoryName1`, and three `CategoryName3` values roll
up to more than one `CategoryName2`. `Clothing → Computing Novelties →
T-Shirts` was the clearest tell.

This run established **what the three columns actually are**, which changes the
answer from a judgement call into a reading of the data. Four pieces of
evidence, all from the 227 stock items:

1. **All 227 rows are alphabetically non-decreasing across the three columns.**
   Every one of the 12 distinct combinations satisfies C1 ≤ C2 ≤ C3. A genuine
   hierarchy would not be accidentally alphabetical 227 times out of 227.
2. **94 rows repeat a single value three times** (e.g. `Packaging Materials`
   ×3), and 52 more repeat one of two values — consistent with padding, not
   with three levels of meaning.
3. **The semantics only work as sibling tags.** A DBA joke mug is
   `Computing Novelties / Mugs / Novelty Items`; a joke t-shirt is
   `Clothing / Computing Novelties / T-Shirts`. Those read as three labels
   applied to one product, not as a drill path.
4. The union of the three columns is a single shared domain of **9 values**,
   not three separate domains of 5, 6 and 7.

So the columns are an **alphabetically sorted, repetition-padded flattening of
a product-to-stock-group many-to-many**, squashed into three fixed slots.
227 products carry 441 memberships (94 have one tag, 52 have two, 81 have
three).

The realistic options were:

1. Expose all three columns as independent product attributes. Rejected: slot
   number carries no meaning, so "CategoryName1" is just "the alphabetically
   first tag" and slicing by it is meaningless.
2. Pick one column as *the* category. Rejected, and the numbers show why — by
   `CategoryName1` alone, Computing Novelties is £8.3m; as a tag it is £38.2m.
   Choosing a column would misstate most categories by a wide margin.
3. Rebuild the many-to-many properly with a bridge table. Correct, but pulls in
   a bidirectional relationship and overlapping subtotals.

## What was decided

**Option 3, plus an additive fallback.**

- `Dim Category` — 9 rows, the union of the three columns.
- `Bridge Product Category` — 441 rows, produced by unpivoting the three
  columns and deduplicating the padding (227 × 3 = 681 → 441). Hidden.
- Relationships: `Bridge → Dim Category` single-direction;
  `Bridge → Dim Product` **bidirectional**, which is what lets a category
  filter reach the fact.
- `Dim Product[Category Group]` — the product's full tag set as one label
  (12 distinct values, e.g. "Computing Novelties, Mugs, Novelty Items"). Every
  product has exactly one, so this slices sales **additively** and its
  subtotals reconcile to the grand total.

The bidirectional relationship is the team's documented exception case, not a
default: the bridge touches only `Dim Category` and `Dim Product`, never the
fact, so there is no filter loop and no ambiguous path. It still needs a
correctness spot-check in Desktop — see `NOTES.md`.

## Why

User's answer on issue #1: "analyze the data and use your skills to decide here
— If you think there is a problem with the data, voice it in the analysis at
the end." The decision therefore follows the evidence above rather than a
stated preference, and the data problem is written up in
`projects/bi-task-1/ANALYSIS.md`.

## Consequences

- **Category subtotals overlap and do not sum to the grand total.** Sales by
  category sums to £265,811,435 against a grand total of £162,950,104 — an
  overlap factor of **1.63×**, because a multi-tagged product counts under each
  of its tags. Each individual category figure is correct; the column will just
  not add up, and Power BI's total row will show the correct £162.95m. This has
  to be stated on the report page, not left for a reader to trip over.
- Anyone who needs a reconciling breakdown must use
  `Dim Product[Category Group]` instead.
- **Unquantifiable risk, flagged not solved:** the source caps the flattening
  at three slots. If any product originally belonged to a fourth stock group,
  that membership was silently lost before the file reached us, and nothing in
  this extract can detect it. The fix is upstream — request the underlying
  product-to-stock-group table rather than the flattened columns.
- This is the model's only bidirectional relationship and its only
  many-to-many.
