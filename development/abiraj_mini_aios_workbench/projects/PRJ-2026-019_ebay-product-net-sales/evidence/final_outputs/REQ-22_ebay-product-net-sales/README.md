# Deliverables — REQ-22-D01 eBay Product Net Sales

## What will land here
The per-order Net Sales Excel workbook produced by the single generator
`sql/REQ-22_.../epns_build_d01.py`.

| Artefact | File | Contents |
|---|---|---|
| Reviewer workbook | `REQ-22-D01_ebay_product_net_sales.xlsx` *(pending build)* | 12 columns, one row per eBay order line, last 30 days, money per marketplace currency. Tab 1 = Net Sales; Tab 2 = Net Sales Lookup (single Order ID). |

## Disclosure requirements — these must ship *inside* the workbook (top-row note), not only in governance files
- **`NO DATA` columns are shown, not omitted** — Product Cost (no COGS in any DB) and anything derived
  from it, until a real cost basis is supplied.
- **Net Sales formula is stated on the sheet** exactly as agreed with Kobiga, including which deductions
  are and are not included.
- **Currency is per marketplace** — UK £ / DE €, never blended.
- **VAT** is a standard-rate estimate (20% of revenue), not a booked figure.
- **Source & window** — built from `ledsone`, last 30 days ending the last complete day.

**EMPTY until built.**
