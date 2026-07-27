# Deliverables — REQ-19-D01 eBay Product Performance Analysis

## What lands here

REQ-19-D01 is the per-listing Excel workbook produced by the single generator
`sql/REQ-19_.../eppr_build_d01.py`.

| Artefact | File | Contents |
|---|---|---|
| Reviewer workbook | `REQ-19-D01_ebay_product_performance_v4_final.xlsx` | **The definitive file.** 35 columns, **9,781 live eBay UK+DE listings**, one row per item_id, money per marketplace currency (£/€). |

⚠ Earlier versions (`…_v2_brand`, `…_v3`, `…_currency`, and the un-suffixed original) are **superseded**
and pending deletion — they remained only because they were open/locked in Excel during the build.
`…_v4_final.xlsx` is canonical.

## Disclosure requirements — these ship *inside* the workbook (top-row note), not only in governance files

- **`NO DATA` columns are shown, not omitted:** Cost Price, Gross/Net Profit, Profit Margin (no COGS in
  the warehouse — `sku_cogs` empty), Watch Count (eBay API only), PPC Campaign (item→campaign link 29%),
  Sales Trend (undefined rule).
- **Currency is per marketplace** — UK £ / DE €, never blended.
- **eBay Fees / Shipping** attribute per item_id; eBay books many fees at order/payout level, so a sold
  listing can legitimately read £0.
- **VAT** is a standard-rate estimate (20% UK / 19% DE of revenue), not a booked figure.
- **Warehouse-only, interim** — `ledsone` was unreachable 2026-07-27; Title 86%, Category name ~38%.
