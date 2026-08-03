# eBay Product Net Sales (epns) — PRJ-2026-019

Concise landing page. Full context in `PROJECT_HOME.md`; execution rules in `CLAUDE.md`; field-by-field
source map in `SYSTEM_REFERENCE.md`.

## What
A per-order eBay **Net Sales (NNV)** report for **Kobiga**: for each eBay order in the last 30 days, its
identity (Order ID, SKU, Account) and the full deduction stack — Gross Sales, VAT (20%), Promotion,
Final Value Fee, Product Cost, Postage, PPC Cost, General — resolving to **Net Sales (NNV)**. Plus a
**Net Sales Lookup** tab to look up any single Order ID.

## Status
🟡 **ONBOARDED — DISCOVERY · BUILD PENDING.** Requirement captured from `Kobiga task.xlsx` (imported
2026-08-03). Structure scaffolded to the workbench standard. **Not built, not published, not committed,
not signed off.** IDs provisional (see below).

## The formula (from the source)
`Net Sales (NNV) = Gross Sales − VAT (20%) − Promotion − Final Value Fee − Product Cost − Postage − PPC Cost − General`
Window = last 30 days of order data.

> ⚠ **Product Cost has no source** — no per-SKU COGS exists in any database (the EPPR / `sku_cogs`-empty
> lesson). This is the primary open blocker: either a real cost basis is supplied, or the column is
> flagged `NO DATA` / an owner-agreed estimate. Do **not** silently guess it.

## Deliverable (planned)
`evidence/final_outputs/REQ-22_.../REQ-22-D01_ebay_product_net_sales.xlsx` — Net Sales table + Net Sales
Lookup tab (build pending).

## Authoritative documents
- `PROJECT_HOME.md` — canonical project truth
- `SYSTEM_REFERENCE.md` — the column → `schema.table.column` map (draft, to verify against `ledsone`)
- `CLAUDE.md` — execution rules
- `TASK_REGISTER.md` — task/deliverable index

## Next step
Discovery: confirm scope/IDs with Varmen, resolve the **Product Cost** source with Kobiga, then read the
AIOS knowledge base and map every column live against `ledsone` before building.
