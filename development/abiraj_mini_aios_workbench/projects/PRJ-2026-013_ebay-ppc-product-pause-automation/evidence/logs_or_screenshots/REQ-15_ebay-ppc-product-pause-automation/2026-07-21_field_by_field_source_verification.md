# Field-by-Field Source Verification — REQ-15 eBay PPC Product Pause Automation

**Executed:** 2026-07-21 · read-only
**Sources used:** AIOS knowledge base MCP (`docs.ledsone.co.uk/mcp`) + Ledsone raw Postgres MCP
(`mcp.ledsone.co.uk/mcp`, db `ledsone`, user `dbhub_readonly`, PG 18.4)
**Supersedes:** the warehouse-only audit of the same date, on three points (marked 🔴 below).

**Purpose:** check every column the task sheet's `Input Data` tab expects, one at a time, against
the real sources — no assumptions, no inference from the mockup.

**Scope:** LEDSone eBay UK = `ebay_campaigns.campaigns.marketplace_id='EBAY_GB'`,
`sub_source=1` (seller_store_id 1), `deleted=false`.

---

## Cross-validation of the two databases

The raw DB independently reproduces the warehouse's campaign census exactly — 23 running ON_SITE
MANUAL, 8 running ON_SITE SMART, 73 running COST_PER_SALE. Spend agrees to the window
(raw £1,918.00 to 2026-07-21 vs warehouse £1,873.46 to 2026-07-20). **The two sources agree.**

---

## The 14 Input Data columns

| # | Task-sheet column | Available? | Source (verified) | Notes |
|---|---|---|---|---|
| 1 | Campaign / Listing | ✅ YES | `ebay_campaigns.campaigns.campaign_name` | 1:1 with the mockup's names |
| 2 | Item ID | ✅ YES | `performance_data.ebay_listing_id` / `ads.ebay_listing_id` | Real eBay item IDs |
| 3 | Type (Manual/Smart) | ✅ YES | `campaigns.campaign_target_type` | `MANUAL` / `SMART`; NULL for CPS |
| 4 | Units in stock | ⚠ PARTIAL | `ebay_listings.sku` → `inventory.products.id` → `local_inventory_current_stock_location_wise` (`warehouse_location='UK'`) | Chain works — **99.7% of item×SKU pairs have a stock row**. But see Gap C: the grain is wrong. |
| 5 | 30D ACOS | ✅ YES | `SUM(ad_fees_payout_currency) / SUM(sale_amount_payout_currency) * 100` | Derived, per window |
| 6 | 7D ACOS | ✅ YES | same, 7-day window | **Genuinely independent of 30D** — the mockup's was not |
| 7 | 30D orders | ✅ YES | `SUM(attributed_sales)` | Count of attributed sales |
| 8 | 14D orders | ✅ YES | same, 14-day window | |
| 9 | 14D clicks | ✅ YES | `SUM(clicks)` (`cpc_clicks`) | |
| 10 | 14D spend | ✅ YES | `SUM(ad_fees_payout_currency)` | ⚠ zero for CPS — see Gap B |
| 11 | 30D spend | ✅ YES | same, 30-day window | |
| 12 | **Listing price** | ✅ **YES** 🔴 | `listings.ebay_listings.price` (+ `currency`) | **730/730 found listings carry a real price.** My warehouse-only audit said this did not exist. It does — in the raw DB. |
| 13 | Campaign state | ✅ YES | `campaigns.campaign_status` | `RUNNING` / `PAUSED` / `ENDED` — richer than the mockup's ON/OFF |
| 14 | **Listing state** | ❌ **NO** (partial substitute) | — | See Gap D below. `is_ended` is available; true ad on/off is not. |

**Verdict: 12 of 14 columns are fully available, 1 partial, 1 unavailable.**

---

## Corrections to the earlier warehouse-only audit 🔴

### 🔴 Correction 1 — SMART campaigns DO have listing-level data
The warehouse returned **0** item_ids for ON_SITE SMART, which I reported as Gap A ("SMART cannot
be evaluated per listing"). **That was a warehouse ETL artefact, not reality.** The raw source has
per-listing rows for SMART:

| Target type | Status | Campaigns | Listings with perf | 30D ad fees | 30D clicks | 30D orders |
|---|---|---|---|---|---|---|
| MANUAL | RUNNING | 23 | 802 | £1,918.00 | 10,280 | 646 |
| **SMART** | **RUNNING** | **8** | **179** | **£751.09** | **3,734** | **193** |

**Gap A is withdrawn.** SMART listings can be evaluated individually, from the raw DB. Building on
the warehouse would have silently dropped £751/30D of SMART spend from the pause engine.

### 🔴 Correction 2 — Listing price exists
Available on `ebay_listings.price` for every listing that resolves. Matters because the mockup's
Custom Rules offer `price` as a rule metric.

### 🔴 Correction 3 — More history in the warehouse, fresher data in the raw DB
- Raw `ebay_campaigns.performance_data`: **2026-05-18 → 2026-07-21 (65 days)** — a documented
  **60-day rolling window**, *not fully backfilled* (690K of ~6.7M source rows).
- Warehouse `ppc_performance`: from 2026-04-22 (~90 days).

30D and 14D windows are safe in both. **Anything beyond ~60 days must not use the raw table.**
The raw DB is fresher (hourly sync, has 2026-07-21; warehouse ends 2026-07-20).

---

## Gaps that survive verification

### Gap B — CONFIRMED and now explained mechanically 🔴
For the 73 running COST_PER_SALE campaigns over 30D:
```
clicks 5,492 · attributed orders 1,069 · ad_fees £0.00 · sale_amount £0.00
```
`performance_data`'s money columns are all `cpc_*` (cost-per-click) fields, so **CPS campaigns
record zero spend and zero sales there**. Consequences for the rule engine:
- **Rule 1 (ACOS) cannot be computed for CPS at all** — the denominator is zero.
- **Rule 2 would misfire**: its rescue is "14D spend < £2.50 → do not pause". CPS spend always reads
  £0.00, so every CPS listing is permanently rescued and Rule 2 can never fire.

CPS money lives elsewhere (`campaign_report_data`, or `accounting.ebay_order_expenses`) and has not
been wired up. **CPS must stay out of scope until this is resolved** — a silent £0 is worse than an
exclusion.

### Gap C — CONFIRMED and WORSE than first measured 🔴
The `all_list = 1` rule (mandatory per `business/rules/ebay-listing-sku-filter.md`) removes parent
container rows — but a variation listing's *children* are all real listable SKUs sharing one
`item_id`, so it does **not** collapse the many-SKU problem:

| Measure | Value |
|---|---|
| Advertised ON_SITE running listings (30D) | 888 |
| Resolve to `ebay_listings` (`all_list=1`) | 730 (82.2%) |
| **Still map to >1 SKU after `all_list=1`** | **651 of 730 = 89.2%** |
| Max SKUs on one listing | **245** |
| item × SKU pairs generated | **9,323** (avg 12.8 per listing) |

**"Units in stock" for a listing remains undefined.** Decision C is unchanged and is the single
biggest open item.

Stock chain itself is healthy: **9,299 of 9,323 pairs (99.7%) have a UK stock row.**
Stock values come from `GetInvStock` logic (combo `min()` across components, pack-size division,
CL cable-pack exception) — documented in `business/rules/stock-calculation-logic.md`. Standing
exclusions apply: `warehouse_location != 'Canada'`, and exclude `Netherlands1` /
`Duisburg warehouse` on any warehouse-level join.

### Gap D — CONFIRMED, and the obvious substitute is a trap 🔴
The mockup's "Listing ON / Listing OFF" line has **no clean source**:
- `ebay_campaigns.ads.state` — raw numeric code (1–6). The knowledge base states plainly there is
  **no lookup table to decode it for eBay**; meaning unconfirmed. Unusable.
- `listings.ebay_listings.status` — **99.4% NULL**. Of 186,691 `all_list=1` rows for sub_source 1,
  only 1,260 carry any value. Worse, **137 items are `status='Active'` while `is_ended=1`** — the
  column contradicts itself. **Do not use `status`.**
- `listings.ebay_listings.is_ended` — populated 0/1 on every row. **This is the only trustworthy
  listing-level state**, but it means "listing ended", not "ad paused".

**158 of 888 (17.8%) advertised listings do not appear in `ebay_listings` at all** — expected per
the knowledge base, which documents ~34% distinct-ID resolution because `ebay_listings` mirrors
only active listings while ad history covers ended ones. Those 158 have **no stock and no price**
and must render as **NO DATA**, never as zero.

---

## Data-quality notes worth recording

1. **Documentation conflict on `all_list`.** The business rule says `1 = real listable SKU`; the
   column comment in the DB says "flag indicating whether this listing is fully synced". The
   business rule is authoritative (it is the one the platform sync obeys), but the column comment
   should be corrected.
2. `wrong_sku=1` appears on 5 of the advertised listings — must be filtered out of SKU work.
3. `ads.ad_group_id = 0` on 85% of rows is a **sentinel** ("no ad group assigned", typical of SMART),
   not a broken FK. Never treat it as a join failure.
4. OAuth tokens are deliberately excluded from `seller_stores` — no secrets in this DB.

---

## Net effect on the delivered build

**Build from the raw `ledsone` DB, not the warehouse** — it is fresher, it carries listing price,
and it is the only one that exposes SMART campaigns at listing grain. Keep the warehouse only if
>60 days of ad history is ever needed.

Revised field availability: **12/14 columns fully sourced.** The two genuine blockers are
**Gap C (stock grain — a business decision)** and **Gap D (listing state — not in the data at all)**.
Gap B keeps CPS out of scope.

All figures above produced by executed read-only queries on 2026-07-21. No writes, no DDL, no publish.
