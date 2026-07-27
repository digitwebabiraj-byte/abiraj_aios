# SOURCE MANIFEST — REQ-19 eBay Product Performance Analysis

COPY-only import. The original in Downloads is untouched; this is a byte-identical copy.

| Field | Value |
|---|---|
| File | `Thinesh task (5).xlsx` |
| Sheet | `eBay Product Performance Analysis` (one sheet) |
| SHA-256 | `dbba8101372656e6ee8d6a9ce24e2ce90761c4bcc06042ac6b9c11fc54647171` |
| Imported | 2026-07-27 |
| Origin | `C:\Users\digit\Downloads\Thinesh task (5).xlsx` (Thinesh) |

## What is canonical in this source

- **Row 1 (35 headers) is canonical** for column shape and order.
- **Only two arithmetic relationships were re-derived and hold on all 5 sample rows** and may be
  trusted: **Revenue = Selling Price × Units Sold**, and **Profit Margin % = Net Profit ÷ Revenue**.
- **Everything else in the sample is FABRICATED.** Every apparent formula cell is a typed constant
  (e.g. row 6 shows −£3.10 net profit on 0 units). Gross Profit and Net Profit tie to no formula,
  and the cost columns' per-unit-vs-total meaning is undefined. **The sample values can never be a
  reconciliation baseline, and the profit logic must be decided with the requester, never inferred.**

## The 35 columns (canonical order)

Product Image · SKU · Parent SKU · eBay Item ID · Product Title · Brand · Category · Marketplace ·
Account · Listing Date · Listing Status · Selling Price (£) · Cost Price (£) · Shipping Cost (£) ·
eBay Fees (£) · Ad Cost (£) · VAT (£) · Available Stock · Units Sold · Orders · Revenue (£) ·
Gross Profit (£) · Net Profit (£) · Profit Margin % · Impressions · Views · Clicks · CTR % ·
Conversion Rate % · Watch Count · Last Sold Date · Days Active · Promotion Status · PPC Campaign ·
Sales Trend
