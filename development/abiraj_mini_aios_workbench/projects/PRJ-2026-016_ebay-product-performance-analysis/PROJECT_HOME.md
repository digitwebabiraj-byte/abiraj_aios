# PROJECT_HOME — eBay Product Performance Analysis (eppr)

| Field | Value |
|---|---|
| **Project ID** | `PRJ-2026-016_ebay-product-performance-analysis` |
| **Project code** | `eppr` *(provisional — pending Varmen)* |
| **Task ID** | `REQ-19_ebay-product-performance-analysis` *(provisional)* |
| **Status** | **REQ-19-D01 BUILT (warehouse-only interim) 2026-07-27** — per-listing dashboard, **9,781 live eBay UK+DE listings**, 35 columns, **28 populated / 7 NO DATA**. Not published, not signed off, not automated. Build is **interim** because `ledsone` was unreachable and product **Cost Price** is absent from the warehouse. |
| **Opened** | 2026-07-27 |
| **Owner** | Abiraj |
| **Coordinator** | Varmen |
| **Technical Reviewer** | Sajeesan |
| **Queryability Reviewer** | Tamil Selvan |
| **Business Validator** | **Thinesh** (requester; identity verified live for REQ-16 — `public."user"` id 63, Active). Publish audience NOT decided; candidate `ebay_priors`. |

> ⚠ **IDs provisional.** The source carries no requirement number. REQ-17 = `dst`, **REQ-18 = `fauto`**,
> so this takes **REQ-19** / **PRJ-2026-016** / code **eppr** — all pending owner confirmation.

## Business question

> For each eBay listing, across all accounts on UK + Germany: what does it cost to sell, what does it
> earn after costs, how is it selling, how is it being seen, and where is it in its lifecycle?

The genuinely new element vs every prior eBay report is a **per-listing profit-and-loss line**
(Cost → eBay Fees → Ad Cost → VAT → Gross / Net / Margin). That P&L is exactly what the warehouse
cannot yet complete — see below.

## Grain: one row per eBay LISTING (item_id)

**9,781 rows** — every active eBay listing (UK+DE, `all_list=1`), 15 accounts. Chosen because sales,
fees, ad-cost and traffic all attribute at item_id grain **without the SKU-sprawl double-count** (one
SKU is listed under many item_ids; joining sales by SKU alone overstates revenue ~13×).

## 🔒 Source lock this build ran under (2026-07-27)

**Warehouse `order_management_copy` ONLY.** `ledsone` (the intended build source) was unreachable all
day — both the MCP (VPN host `10.8.0.5:5432`) and the direct public host (`207.148.78.148:5432`) timed
out. Bulk data pulled via **direct psycopg2 as `temp_user`** (the MCP returns text, unusable at 9,781
rows). The warehouse read confirmed identical counts to the MCP.

## 🔴 The blocker: no product cost anywhere in the warehouse

`development.sku_cogs` (the designated COGS table) is **EMPTY (0 rows)**; `development.channel_vat_log`
is empty; the only populated cost is a slow-stock snapshot (8.7% coverage). `sku_selling_cost_rates_v1`
gives *selling-cost %*, not product COGS. **Therefore Cost Price, Gross Profit, Net Profit and Profit
Margin cannot be computed truthfully and ship as `NO DATA` — never fabricated.**

## Column status — 28 populated / 7 NO DATA (measured 2026-07-27)

**Populated:** Image, SKU, Parent SKU, Item ID, Title (86%), Brand (100%, `salesprot` map),
Category (name→id, 100%), Marketplace, Account, Listing Date, Listing Status, Selling Price, Shipping
Cost, eBay Fees, Ad Cost, VAT (std 20/19%), Available Stock, Units, Orders, Revenue, Impressions,
Views, Clicks, CTR %, Conversion Rate %, Last Sold, Days Active, Promotion Status.

**NO DATA (with proven reason):** Cost Price · Gross Profit · Net Profit · Profit Margin % (all need
COGS) · Watch Count (eBay Trading API only, in no table) · PPC Campaign (item→campaign link 29% in
warehouse) · Sales Trend (undefined business rule).

Full field-by-field source map: `SYSTEM_REFERENCE.md`.

## Money is per marketplace currency — never blended

UK rows render **£ (GBP)**, DE rows render **€ (EUR)** via per-cell format; no total blends currencies
(the DST lesson). Revenue reconciles to the live 30-day window: **UK £54,286 · DE €25,341** (≈93–94% of
the all-eBay window total; the remainder is sales from now-inactive listings, correctly excluded).

## Deliverable

`evidence/final_outputs/REQ-19_.../REQ-19-D01_ebay_product_performance_v4_final.xlsx` — 35 columns,
9,781 rows, per-row currency. Built by `sql/REQ-19_.../eppr_build_d01.py` (single module, direct
psycopg2, read-only).

## Known limitations (disclosed on the deliverable)

- **eBay Fees / Shipping** attribute per item_id, but eBay books many fees at order/payout level, so a
  sold listing can legitimately read £0 there (they default to 0, like Ad Cost/Revenue).
- **Product Title** 86% (via `inv_products` SKU bridge); **Category name** falls back to `category_id`
  where the name is absent (~38% carry a name).
- **`listing_data.created_at`** used as Listing Date may be an ETL date, not the original listing date —
  unverified.

## Register links

- Task index: `TASK_REGISTER.md` · Execution rules: `CLAUDE.md` · Functional detail: `SYSTEM_REFERENCE.md`
- Portfolio row: `../../PROJECT_REGISTER.md`
- Source manifest: `evidence/source_documents/REQ-19_.../SOURCE_MANIFEST.md`
- Requirement doc: `DigitWeb_Works_Abiraj/27_07_2026/2026-07-27_abiraj_REQ-eppr_REQ-19-D01.md`

## Next actions

1. Get **`ledsone`** back or a **Cost Price** source from Thinesh → unlocks the 4 profit columns (26→30+).
2. Route the decision sheet to Thinesh (cost semantics, scope/window confirmation, Sales-Trend bands,
   Watchers/Clicks handling).
3. Reviewer gates (Sajeesan / Tamil Selvan / Thinesh) + confirm IDs (Varmen).
4. Then consider publish (`ph_task`) and automation (REQ-19-D02) — neither started.
