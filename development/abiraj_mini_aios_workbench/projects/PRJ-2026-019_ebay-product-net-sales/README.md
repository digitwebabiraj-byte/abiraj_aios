# eBay Product Net Sales (epns) — PRJ-2026-019

Concise landing page. Full context in `PROJECT_HOME.md`; execution rules in `CLAUDE.md`; field-by-field
source map in `SYSTEM_REFERENCE.md`.

## What
A per-order eBay **Net Sales (NNV)** report for **Kobiga**: for each eBay order in the last 30 days, its
identity (Order ID, SKU, Account) and the full deduction stack — Gross Sales, VAT (20%), Promotion,
Final Value Fee, Product Cost, Postage, PPC Cost, General — resolving to **Net Sales (NNV)**. Plus a
**Net Sales Lookup** tab to look up any single Order ID.

## Status
✅ **BUILT · DELIVERED (2026-08-03).** Built from the **raw ledsone** DB (read-only), **4,432 eBay orders**
over the last 30 days. Reconciles to the penny to the source worked example (order `02-14934-76138` →
Net **22.39**) and to eBay's own payout (`ebay_order_expenses` SALE `transaction_amount`). **Not yet
published (ph_task) / committed / signed off** — IDs provisional; publish audience + the profit-definition
decision pending Kobiga.

## The formula (reconciled against live data)
`Net Sales (NNV) = Gross Sales − Final Value Fee − PPC Cost − General` (= eBay net payout).
Gross Sales = `orders.total` (already net of promotion). Window = last 30 days ending the last complete day.

> ⚠ **Product Cost = ESTIMATE (20% of selling price)** — the owner-agreed proxy already used in EPPR
> (PRJ-2026-016); no real per-SKU COGS exists in any ledsone schema (swept 2026-08-03). **VAT (20%)** is a
> derived estimate. **Net Profit [est] = NNV − VAT − Product Cost** — a derived estimate (inherits both
> proxies), flagged on the sheet; not a booked figure. Replace the 20% with a real COGS source to make it booked.

## Deliverable
[REQ-22-D01_ebay_product_net_sales.xlsx](evidence/final_outputs/REQ-22_ebay-product-net-sales/REQ-22-D01_ebay_product_net_sales.xlsx)
— **Tab 1 Net Sales** (12 source columns + Marketplace/Currency/Order Date, 4,432 orders) · **Tab 2 Net
Sales Lookup** (enter any Order ID → its Net Sales + full breakdown via INDEX/MATCH). Builder:
[epns_build_d01.py](sql/REQ-22_ebay-product-net-sales/epns_build_d01.py). Reconciliation:
[evidence/logs_or_screenshots/…/2026-08-03_build_and_reconciliation.md](evidence/logs_or_screenshots/REQ-22_ebay-product-net-sales/2026-08-03_build_and_reconciliation.md).

## Authoritative documents
- `PROJECT_HOME.md` — canonical project truth
- `SYSTEM_REFERENCE.md` — the column → `schema.table.column` map (draft, to verify against `ledsone`)
- `CLAUDE.md` — execution rules
- `TASK_REGISTER.md` — task/deliverable index

## Next step
Discovery: confirm scope/IDs with Varmen, resolve the **Product Cost** source with Kobiga, then read the
AIOS knowledge base and map every column live against `ledsone` before building.
