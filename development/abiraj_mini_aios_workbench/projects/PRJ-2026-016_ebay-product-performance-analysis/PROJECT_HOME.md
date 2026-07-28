# PROJECT_HOME — eBay Product Performance Analysis (eppr)

| Field | Value |
|---|---|
| **Project ID** | `PRJ-2026-016_ebay-product-performance-analysis` |
| **Project code** | `eppr` *(provisional — pending Varmen)* |
| **Task ID** | `REQ-19_ebay-product-performance-analysis` *(provisional)* |
| **Status** | ✅ **CLOSED — DELIVERED · PUBLISHED · SIGNED OFF 2026-07-28.** Per-listing eBay report, **11,123 live listings (UK+DE)**, 34 columns, **34/34 populated (no empty columns)**. Built from **raw `ledsone`** (+ warehouse for organic traffic only). Published to `tech_team_outputs.ph_task` **ids 472–475** (`ebay_priors`), v3, static no-JS HTML. **Signed off by Thinesh (business).** Not automated (REQ-19-D02 optional/future). |
| **Opened / Published** | 2026-07-27 · **Signed off 2026-07-28** |
| **Owner** | Abiraj · **Coordinator** Varmen · **Tech** Sajeesan · **Queryability** Tamil Selvan |
| **Business Validator** | **Thinesh** (requester) — ✅ **SIGNED OFF 2026-07-28.** Publish audience = `ebay_priors` (Thinesh · Jarsini · kobiga · powsteena). |

> ⚠ IDs provisional (source has no requirement number; REQ-18 = `fauto`).

## Business question
For each eBay listing (UK+DE, all accounts): what it costs to sell, what it earns after costs, how it
sells, how it's seen, and where it sits in its lifecycle — 34 columns, one row per listing.

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

## Column coverage — 34/34 populated (no empty columns)
The report is **34 columns** — Watch Count was **removed 2026-07-28** (eBay Trading API only, in no DB, so it could never be filled).
- **From `ledsone`:** Image, SKU, Parent SKU, Item ID, **Title ~99%**, Brand, **Category name**, Marketplace,
  Account, Listing Date, Status, Selling Price, Shipping, eBay Fees, Ad Cost, VAT, Stock, Units, Orders,
  Revenue, Last Sold, Days Active, Promotion, **PPC Campaign ~65%**.
- **Derived from the 20% cost estimate:** Cost Price, Gross Profit, Net Profit, Profit Margin %.
- **From warehouse traffic feed:** Impressions, Views, Clicks, CTR %, Conversion Rate %.
- **Derived:** **Sales Trend** — this-30-day units vs the prior 30 days, ±5% band (editable): **Up / Stable / Down**, or **"No sales"** where a listing sold nothing in either window (77% — the long tail).
- ✅ **No empty columns. Per-row blanks are legitimate** (e.g. a listing that never sold has no Last Sold Date or Profit Margin).

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
✅ **CLOSED — signed off by Thinesh 2026-07-28.** No outstanding required actions.

✅ **REQ-19-D02 AUTOMATED 2026-07-28** — Windows task `EPPR_Monthly_Product_Performance`, **2nd Wednesday of each month 10:00** (next 2026-08-12), fail-closed, status file + Desktop alert, proven end-to-end (LastTaskResult 0). The fleet's **10th** scheduled job; 10:00 chosen clear of the other 9 (09:00–09:45 + Mon/Thu 10:30–11:00) on the shared `temp_user` pool. See `automation/AUTOMATION_README.md`.

Optional / future (not blocking):
- Replace the 20% cost estimate with a real cost basis if one is ever supplied (profit would become booked, not estimated).
- ✅ Sales Trend now derived (±5% band, editable) — done 2026-07-28.
- Housekeeping: write `verify_eppr_d01.py`; delete the superseded `.xlsx` versions; rotate the `temp_user` password (pre-existing in git history).
