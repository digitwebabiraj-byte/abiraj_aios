# TASK REGISTER — PRJ-2026-019 eBay Product Net Sales

Canonical index of tasks/deliverables within this project. Detail lives in `PROJECT_HOME.md` /
`SYSTEM_REFERENCE.md`.

| Task | Deliverable | Description | Status |
|---|---|---|---|
| REQ-22 | **REQ-22-D01** | Per-order eBay **Net Sales (NNV)** report — one deliverable rendered several ways from one data layer: **(a)** Excel workbook, Tab 1 Net Sales (Order ID · SKU · Account · Marketplace · Currency · Date · Fees Settled · Gross · VAT 20% est · Promotion · Final Value Fee · Product Cost 20% est · Postage · PPC · General · Net Sales NNV · Net Profit est) + **Tab 2 Net Sales Lookup** (any Order ID → breakdown, INDEX/MATCH); **(b)** interactive HTML dashboard (gradient/glass, embedded Sora/Manrope fonts, per-currency KPIs, search/sort/filter, CSV, full-screen); **(c)** static no-JS portal HTML published to `ph_task`; **(d)** weekly scheduled auto-refresh. One row per settled eBay order, last 30 days, per marketplace currency. | ✅ **CLOSED — DELIVERED · PUBLISHED · AUTOMATED · SIGNED OFF (Kobiga) 2026-08-03.** 4,072 settled orders from live ledsone; NNV = Gross − FVF − General(AD_FEE) reconciles to the worked example (22.39) & eBay payout. Published to `ph_task` ids 594–599 (`ebay_priors`). Weekly auto-refresh `EPNS_Weekly_Net_Sales` (Wed 11:30, proven). Git `main` `91103b5`. |

## Publish record — ph_task (2026-08-03)
Published the HTML dashboard to `tech_team_outputs.ph_task` (warehouse `order_management_copy`) for the
**ebay_priors** audience (6 users) via guarded per-user upsert (`automation/publish_epns_ph_task.py`).

| id | assigned_user | task_id | version |
|---|---|---|---|
| 594 | Thinesh | epns_Thinesh_ebay_product_net_sales | 1 (released) |
| 595 | Jarsini | epns_Jarsini_ebay_product_net_sales | 1 (released) |
| 596 | kobiga | epns_kobiga_ebay_product_net_sales | 1 (released) |
| 597 | powsteena | epns_powsteena_ebay_product_net_sales | 1 (released) |
| 598 | Sharmilan | epns_Sharmilan_ebay_product_net_sales | 1 (released) |
| 599 | Sivajitha | epns_Sivajitha_ebay_product_net_sales | 1 (released) |

**Updated to v3 (2026-08-03):** set **`assigned_user_team='ebay_priors'`** on all 6 rows — the portal
("Ebay Priors") filters on this column, which the sample DDL omits; leaving it NULL made the rows invisible
in the portal despite existing. This was the reason the report didn't appear. Publish script now always sets it.

**Updated to v2 (2026-08-03):** re-published the **static-first portal build** (`render_epns_portal.py` →
`REQ-22-D01_ph_task.html`) — all KPI tiles and 4,072 rows are server-rendered into the HTML, so the report
renders in the portal **even with no JavaScript** (the JS-only dashboard showed blank in the portal tile).
JS (search/sort) is progressive enhancement only. Rows verified: v2, `has_static_table=True`, anchor row present.

## Build refinements (2026-08-03)
- **Settled-only** — includes an order only once eBay books its fees (settlement lag); adds a `Fees Settled` column. Fixes the fee-deviation vs eBay on recent orders. ~4,072 settled orders.
- **Product Cost** now the EPPR 20%-of-price proxy (was NO DATA) → adds `Net Profit [est]`.
- Dashboard table shows all 12 source columns incl. Promotion + Postage (were initially missing).
- **Automation** (component of D01): Windows task **`EPNS_Weekly_Net_Sales`**, **every Wednesday 11:30** (free slot, clear of the fleet's 09:00–11:00). Fail-closed gates (row-floor 1,500 · collapse guard 60% · Desktop alert · status file), git-ignored secrets, live ledsone `169.58.91.229`. Proven: manual run OK + **Start-ScheduledTask → LastTaskResult 0** (4,072 rows). Sets `assigned_user_team='ebay_priors'`. See `automation/AUTOMATION_README.md`.
- **Fee mapping (corrected):** General = `AD_FEE` (Promoted Listings General fee, per order); PPC = `PREMIUM_AD_FEES` (CPC, listing-allocated). NNV = Gross − FVF − General; premium ad spend → Net Profit.

## Source
`evidence/source_documents/REQ-22_.../Kobiga task.xlsx` (SHA-256 in `SOURCE_MANIFEST.md`, imported 2026-08-03).

## Open items (all non-blocking — task CLOSED & signed off)
- Confirm the provisional IDs: `PRJ-2026-019` / `REQ-22` / code `epns` (cosmetic).
- Reviewer gates: Sajeesan (technical), Tamil Selvan (queryability).
- Optional: supply a real COGS source to make Product Cost / Net Profit booked instead of estimated; write `verify_epns_d01.py`.

## Sign-off
✅ **Kobiga (Business Validator) — SIGNED OFF 2026-08-03.** See `closure/REQ-22_.../2026-08-03_closure_signoff.md`.
