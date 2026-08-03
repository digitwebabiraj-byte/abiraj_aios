# TASK REGISTER — PRJ-2026-019 eBay Product Net Sales

Canonical index of tasks/deliverables within this project. Detail lives in `PROJECT_HOME.md` /
`SYSTEM_REFERENCE.md`.

| Task | Deliverable | Description | Status |
|---|---|---|---|
| REQ-22 | **REQ-22-D01** | Per-order eBay **Net Sales (NNV)** report (Excel): Order ID · SKU · Account · Marketplace · Currency · Order Date · Gross Sales · VAT (20%, est) · Promotion · Final Value Fee · Product Cost (NO DATA) · Postage · PPC Cost · General · Net Sales (NNV), one row per eBay order, last 30 days, per marketplace currency. | ✅ **BUILT · DELIVERED 2026-08-03.** 4,432 orders from raw ledsone; reconciles to worked example (22.39) & eBay payout. Not yet published / committed / signed off. |
| REQ-22 | **REQ-22-D02** | **Net Sales Lookup** tab — enter any single Order ID, return its Net Sales and full deduction breakdown (INDEX/MATCH). | ✅ **BUILT · DELIVERED 2026-08-03** (Tab 2 of the D01 workbook). |
| REQ-22 | **REQ-22-D03** | **HTML dashboard** — self-contained modern light-theme UI (gradient/glass, embedded Sora/Manrope fonts), animated per-currency KPI tiles, searchable/sortable/filterable table (all 12 source columns), CSV export, full-screen. | ✅ **BUILT · DELIVERED 2026-08-03** (`REQ-22-D01_dashboard.html`, renderer `render_epns_dashboard.py`). Interactive JS version for local review; static no-JS portal version TBD if `ph_task` publish is approved. |

## Build refinements (2026-08-03)
- **Settled-only** — includes an order only once eBay books its fees (settlement lag); adds a `Fees Settled` column. Fixes the fee-deviation vs eBay on recent orders. ~4,072 settled orders.
- **Product Cost** now the EPPR 20%-of-price proxy (was NO DATA) → adds `Net Profit [est]`.
- Dashboard table shows all 12 source columns incl. Promotion + Postage (were initially missing).
| REQ-22 | *(future)* | Scheduled refresh (automation), if requested after sign-off. | ⚪ Not requested. |

## Source
`evidence/source_documents/REQ-22_.../Kobiga task.xlsx` (SHA-256 in `SOURCE_MANIFEST.md`, imported 2026-08-03).

## Open items
- 🔴 **Product Cost source** — no per-SKU COGS in any DB (`sku_cogs` empty). Blocks column 8 and the
  Net Sales value. Needs a cost basis from Kobiga or an explicit owner decision (`NO DATA` vs estimate).
- 🟠 **Deduction set / grain confirmation** — the exact deductions, their sign, `Promotion %` vs amount,
  the `General` bucket definition, and grain (order vs order-line vs SKU) must be confirmed with Kobiga.
- 🟠 **Marketplace scope** — UK only vs UK+DE (drives currency handling).
- Confirm IDs (Varmen): `PRJ-2026-019` / `REQ-22` / code `epns`.
- Reviewer gates: Sajeesan (technical), Tamil Selvan (queryability), Kobiga (business).
- Publish audience (`ph_task`, likely `ebay_priors`) not decided; no publish, no git commit yet.
- Validation harness (`verify_epns_d01.py`) — TODO once built.
