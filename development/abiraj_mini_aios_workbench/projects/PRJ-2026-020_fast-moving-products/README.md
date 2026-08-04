# Fast Moving Products (fmp) — PRJ-2026-020

Concise landing page. Full context in `PROJECT_HOME.md`; execution rules in `CLAUDE.md`; field-by-field
source map in `SYSTEM_REFERENCE.md`.

## What
A **channel-wise top-selling ("fast moving") products** report for **Mahima**, covering the DE market
across all three sales channels — **Shopify DE, Amazon DE, eBay DE** — plus a **Final Combined Top
Products (All Channels)** table. For each channel it ranks the fastest-moving SKUs by units sold, with a
velocity/stock picture (30-day & 90-day sold qty, revenue €, orders, avg order qty, current stock, stock
cover days, trend) and a recommended **Action** (Maintain / Promote / Reorder / Restock / Monitor …). The
combined table rolls the three channels up per SKU into total units, total revenue and a final decision.

## Status
🟡 **ONBOARDING — folder scaffolded 2026-08-04.** Source workbook (`mahima task.xlsx`) imported to
`evidence/source_documents/`. **NOT started, NOT built, NOT published, NOT signed off.** Identity
(`PRJ-2026-020` / `REQ-23` / code `fmp`) is provisional — the source is a spec mock-up with sample rows,
no requirement number. Next step is discovery with Mahima, then read the AIOS KB and map every column live.

> ⚠ Every number in the source workbook is an **illustrative sample** (LDMST64E27 etc.), not real data.
> It defines the desired columns and layout only. Nothing here is reconciled against `ledsone` yet.

## Deliverable (planned)
- **REQ-23-D01** — Fast Moving Products report, one data layer rendered as:
  - **Excel** — one tab per channel (Shopify DE, Amazon DE, eBay DE) + a **Combined** tab.
  - **HTML dashboard** (optional, per the house pattern) — per-channel KPIs, searchable/sortable table.
  - Builder: single read-only module in `sql/REQ-23_fast-moving-products/`.

## The report shape (from the source workbook)
Four tables — see `PROJECT_HOME.md` for the exact column list per channel:
1. **Fast Moving Products – Shopify DE** (Rank · SKU · Product ID · Category · Sold Qty 30d/90d · Revenue € · Orders · Avg Order Qty · Current Stock · Stock Cover Days · Trend · Action)
2. **Fast Moving Products – Amazon DE** (adds Product Name; Product ID = ASIN)
3. **Fast Moving Products – eBay DE** (Product ID = eBay Listing ID)
4. **Final Combined Top Products (All Channels)** (Overall Rank · SKU · Category · Amazon/eBay/Shopify sold qty · Total Units · Total Revenue € · Current Stock · Stock Cover · Final Decision)

`Stock Cover Days = Current Stock ÷ Average Daily Sales` (formula stated in the source).

## Authoritative documents
- `PROJECT_HOME.md` — canonical project truth
- `SYSTEM_REFERENCE.md` — the column → `schema.table.column` map (DRAFT — to verify live)
- `CLAUDE.md` — execution rules
- `TASK_REGISTER.md` — task/deliverable index

## Next step
Discovery decision sheet to Mahima (scope, market, window, ranking metric, stock source, combined-table
logic), then read the AIOS knowledge base (`docs.ledsone.co.uk/mcp`) and map every column live against
`ledsone` / the warehouse before building anything.
