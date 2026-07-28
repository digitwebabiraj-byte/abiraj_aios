# PROJECT_HOME — eBay Product Performance Analysis (eppr)

| Field | Value |
|---|---|
| **Project ID** | `PRJ-2026-016_ebay-product-performance-analysis` |
| **Project code** | `eppr` *(provisional — pending Varmen)* |
| **Task ID** | `REQ-19_ebay-product-performance-analysis` *(provisional)* |
| **Status** | **REQ-19-D01 BUILT · PUBLISHED 2026-07-27.** Per-listing eBay dashboard, **11,123 live listings (UK+DE)**, 35 columns, **33/35 populated**. Built from **raw `ledsone`** (+ warehouse for organic traffic only). Published to `tech_team_outputs.ph_task` **ids 472–475** (`ebay_priors`: Thinesh, Jarsini, kobiga, powsteena), v3, static no-JS HTML. **Not signed off, not automated.** |
| **Opened / Published** | 2026-07-27 |
| **Owner** | Abiraj · **Coordinator** Varmen · **Tech** Sajeesan · **Queryability** Tamil Selvan |
| **Business Validator** | **Thinesh** (requester). Publish audience = `ebay_priors` (Thinesh · Jarsini · kobiga · powsteena). |

> ⚠ IDs provisional (source has no requirement number; REQ-18 = `fauto`).

## Business question
For each eBay listing (UK+DE, all accounts): what it costs to sell, what it earns after costs, how it
sells, how it's seen, and where it sits in its lifecycle — 35 columns, one row per listing.

## Grain & window
One row per eBay **listing (item_id)**; **11,123** active listings (`all_list=1`, UK+DE). Rolling **30
days** ending the last complete day. Money **per marketplace currency** (UK £ / DE €), never blended.

## 🔒 Source (owner instruction — the two ledsone MCPs)
- **Raw `ledsone` Postgres** (`mcp.ledsone.co.uk`, `dbhub_readonly`) — **every column** except organic traffic.
- **AIOS knowledge base** (`docs.ledsone.co.uk`) — read before SQL (`all_list=1`, `source_id=2`, VARCHAR casts).
- **Warehouse** (`order_management_copy`) — used for **ONE feed only**: eBay **organic traffic**
  (Impressions/Views/Conversion), which has no `ledsone` source (the ESNM two-DB pattern). Publish target
  (`ph_task`) is also the warehouse — the source lock governs data retrieval, not the output step.

## 🟠 Cost Price is an ESTIMATE (owner decision 2026-07-27)
No real product COGS exists in any database (`ledsone.inventory.products` has no cost; warehouse
`sku_cogs` empty; `suppliers.invoices.unit_price` isn't SKU-keyed). Owner decision: **Cost Price = 20% of
Selling Price**. **Gross Profit, Net Profit and Profit Margin are derived from it and are therefore
ESTIMATES, not booked figures** — flagged on every artefact (Excel note, dashboard footer, portal footer).

## Column coverage — 33/35 populated
- **From `ledsone`:** Image, SKU, Parent SKU, Item ID, **Title ~99%**, Brand, **Category name**, Marketplace,
  Account, Listing Date, Status, Selling Price, Shipping, eBay Fees, Ad Cost, VAT, Stock, Units, Orders,
  Revenue, Last Sold, Days Active, Promotion, **PPC Campaign ~65%**.
- **Derived from the 20% cost estimate:** Cost Price, Gross Profit, Net Profit, Profit Margin %.
- **From warehouse traffic feed:** Impressions, Views, Clicks, CTR %, Conversion Rate %.
- 🔴 **NO DATA (2):** **Watch Count** (eBay Trading API only, in no DB) · **Sales Trend** (undefined bands — decision).

Full field→source map: `SYSTEM_REFERENCE.md`.

## Deliverables
- Excel: `evidence/final_outputs/REQ-19_.../REQ-19-D01_ebay_product_performance_v4_final.xlsx`
- Interactive dashboard (local review, JS): `.../REQ-19-D01_dashboard.html`
- **Static no-JS portal report (published):** `.../REQ-19-D01_ph_task.html`
- Data layer: `sql/REQ-19_.../eppr_build_d01.py` (`fetch_records()` — single source for all three outputs)
- Dashboard renderer: `sql/REQ-19_.../render_eppr_dashboard.py`
- Portal renderer: `automation/render_eppr_static.py` · Publisher: `automation/publish_eppr_ph_task.py`

## Publish record (ph_task, 2026-07-27)
Guarded publish as `temp_user` (SELECT-then-INSERT/UPDATE — live table has **no** working `UNIQUE(task_id)`;
sets `assigned_user_team`, which the sample DDL omits). Dry-run shown before commit. Rows 472–475, v3.

## Reconciliation
Revenue on active listings: **UK £59,526 · DE €26,634** (30-day window). Money per currency, never blended.

## Next actions
1. **Reviewer sign-off** — Sajeesan (technical), Tamil Selvan (queryability), Thinesh (business).
2. **Confirm IDs** (Varmen): `PRJ-2026-016` / `REQ-19` / code `eppr`.
3. Optional: replace the 20% cost estimate with a real cost basis if Thinesh supplies one; define **Sales
   Trend** bands to fill the last data column; automate (REQ-19-D02).
