# SKILL FILE — DAILY KNOWLEDGE EXTRACTION
# DIGITWEB LK LTD · Daily Skill Increment System · v3.0

---

## ── METADATA BLOCK ──────────────────────────────────────────────────────────

| Field | Value |
| :---- | :---- |
| **date** | 2026-07-17 |
| **developer** | abiraj |
| **project** | EBPD — eBay Account Performance Dashboard — monthly account KPIs across all eBay marketplaces (Sales · Advertising · Listings · Stock) for **Thinesh** (eBay marketplace operations) · LEDsONE analytics platform |
| **project\_code** | EBPD |
| **phase** | Phase — Dashboard build, multi-round live-data correction & publish (EBPD Stage 1 — first governed monthly account-performance dashboard) |
| **requirement\_id** | REQ-13 |
| **deliverable\_id** | REQ-13-D01 |
| **status** | **DELIVERED & PUBLISHED LIVE** (HTML dashboard pushed to 4 users via `tech_team_outputs.ph_task`, currently rows **329–332**), **then corrected across the day through five successive live-data reconciliations against the user's own MCP checks**. Onboarded the REQ-13 / EBPD stream from a mockup (`Thinesh task (1).xlsx`), resolved the account→store mapping, discovered the real scope is **12 active eBay accounts across 7 marketplaces** (mockup named only 4), built an Excel + interactive HTML dashboard, and then reworked the data method five times as the user flagged mismatches: (1) Revenue **product-only → product+template-postage → `SUM(order_total)`** (actual paid); (2) rows **whole-store → account × marketplace**; (3) New Listings **N/A → sourced from the ledsone DB**; (4) Conversion **ad-only → whole-account traffic**; (5) Ad **campaign-attributed → ad-level → ON_SITE-only + TACOS**. Every figure now reconciles to the user's independent checks (led_sone UK £28,975.37; so_926407 UK ON_SITE ad £884.07). **No source/application table mutated — read-only on all warehouse + ledsone data; the only write is the report HTML into `ph_task`.** **CARRIED-OPEN:** the **.xlsx** deliverable is NOT yet re-synced to the final method; the **orders-count definition** (distinct 1,517 vs line 1,619) is unconfirmed; the **conversion RAG threshold** needs recalibration — so **NOT yet closed**. |
| **evidence\_location** | Output artifacts (this session), all under `C:\Users\digit\Downloads\`: **`eBay Account Performance Dashboard - June 2026 - FINAL.html`** (live dashboard — 22 account×marketplace rows, order_total sales, ON_SITE ad + TACOS, filters, sticky headers, CSV export) · **`eBay Account Performance Dashboard - June 2026 (v2 - 12 accounts).xlsx`** (Excel — 3 sheets; on the *previous* method, NOT yet re-synced) · **`push_ebpd_dashboard.py`** (idempotent publisher to `ph_task`) · build generators in scratchpad (`build_html_v3.py`, `build_ebay_dash_v2.py`). Requirement source: `Thinesh task (1).xlsx` (sheet `eBay AccountPerformance Dashboa`). Morning requirement doc: `DigitWeb_Works_Abiraj/17_07_2026/2026-07-17_abiraj_REQ-ebpd_REQ-13-D01.md`. Clarification log: `2026-07-17_ebpd_questions-for-Thinesh.md`. Live publish target: `tech_team_outputs.ph_task` rows 329–332 (users Thinesh, Jarsini, kobiga, powsteena; `assigned_user_team='ebay_priors'`). |
| **blos\_keys\_used** | N/A — not a BLOS task. DB objects **READ** (read-only). **Warehouse `order_management_copy` (`public`):** `order_transaction`, `order_shipping_billing_detail`, `ppc_performance`, `ppc`, `traffic_data`, `listing_data`, `inv_final_stock`. **Ledsone DB:** `listings.ebay_listings`, `order_management.sub_source`. **WRITE (only):** `tech_team_outputs.ph_task` — the report HTML published to 4 assigned users (remote DB 149.28.134.54:5435, user `temp_user`). **No source/application table written; no DDL; no INSERT/UPDATE/DELETE on any warehouse table.** |
| **hardcoded\_thresholds** | Rules as-applied (Thinesh-confirmed, not invented): reporting month = **June 2026** (`order_date >= '2026-06-01' AND < '2026-07-01'`); Last Month = May 2026; Last Year = June 2025; channel = **eBay** (`source_name='EBAY'`); sale status = **`order_status='Completed'`** (Refunded/Cancelled excluded); **Revenue = `SUM(order_total)`** (eBay's actual order value incl. postage actually paid — NOT `item_price*quantity`, NOT `+shipping_template_price`); **rows = account (`ss_name`) × marketplace (`market_place`)**; **Conversion = `SUM(conversion)/SUM(click)`** from `traffic_data` `which_channel=2` (=eBay; 1=Amazon, 3=Shopify); **Ad Spend = eBay Promoted Listings `record_subtype='ON_SITE'` only** (Priority/Advanced; Standard `COST_PER_SALE` excluded), from `ppc_performance` (`record_type='campaign'`) joined to `ppc` on `record_id=parent_id`; **TACOS = Ad Spend ÷ total revenue** (RAG green <12% / amber 12–18% / red >18%); **Return = revenue ÷ Ad Spend** (green >8 / amber 5–8 / red <5); attributed Ad Sales/ACOS/ROAS **omitted** (over-count); **Active Listings = distinct `ref_id`** (`listing_data`, `which_channel_name='ebay'`, per `market_place`); **New Listings = distinct `item_id` created in June** (`listings.ebay_listings.created_at`, ledsone DB, per `site`); **Stock = `SUM(inv_final_stock.stock)`** for the site's SKUs (shared/overlapping); **Sales Rank = rows ranked by June revenue**; **PPC Rank = ad rows ranked by ON_SITE spend**. Account mapping: LEDSONE UK=`led_sone` · SUNSONE UK=`so_926407` · Electricalsone UK=`electricalsone` · LEDSONE DE=`ledsonede`. |
| **three\_am\_standard** | PASS |
| **llm\_queryable** | YES |
| **company\_knowledge\_candidate** | YES |
| **domain** | REPORTING \| POSTGRESQL \| EBAY \| MULTI-MARKETPLACE \| ADVERTISING-PPC \| PROMOTED-LISTINGS \| ACCOUNT-PERFORMANCE \| DATA-VISUALISATION \| AIOS \| PORTFOLIO-HOLDER-OPS |
| **user** | **Thinesh** (report owner / end user). Report also published to **Jarsini, kobiga, powsteena** (same `ebay_priors` team, matching yesterday's eBay Price Checker recipients). Not formally signed off. |
| **benefit\_status** | **DELIVERED (published live, with carried Excel re-sync).** (1) Replaces the manual monthly multi-tab pull of eBay account KPIs with one live, database-derived dashboard — per account × marketplace, with MoM/YoY, RAG scoring, filters, CSV export. (2) Truth is provable — every figure traces to a real `schema.table.column` and reconciles to the user's own independent MCP checks to the penny (led_sone UK £28,975.37; so_926407 UK ON_SITE ad £884.07). (3) Correctness beyond the first-pass query — five reconciliation rounds corrected the sales field (order_total), the marketplace scope, the ad-attribution over-count (→ TACOS / ON_SITE-only), the conversion basis (whole-account), and sourced New Listings from the ledsone DB. (4) Safe — read-only on all source data; the only write is the report HTML to `ph_task`. **Blocking item to reach CLOSED:** re-sync the .xlsx to the final method; confirm the orders-count definition; recalibrate the conversion threshold. |

## File path:
# 2026-07-17__abiraj__ebpd__REQ-13-D01.md
# DigitWeb_Works_Abiraj/17_07_2026/

---

## SECTION 1 · SYSTEM STATE

- **Start of today.** The eBay Account Performance Dashboard existed **only as a mockup** — `Thinesh task (1).xlsx` (sheet `eBay AccountPerformance Dashboa`) held a target layout with **dummy June figures**, KPI-threshold rules, summary cards and a filter list. No query, no automated feed, no governed dashboard. The morning requirement doc scoped REQ-13-D01: turn the mockup into a working, executed multi-table dashboard for June 2026 with real warehouse data, Excel first then HTML.
- **Trigger.** Open the new **REQ-13** stream as **REQ-13-D01**: a monthly eBay account-performance dashboard for PH **Thinesh** — Sales (rev/orders/units/AOV/conversion, MoM+YoY), Advertising (spend/efficiency), Listings (active/new) and Stock, across all eBay marketplaces.
- **What was working.** The warehouse held the domains needed — sales (`order_transaction`), advertising (`ppc_performance` + campaign metadata `ppc`), organic traffic (`traffic_data`), listings (`listing_data`), stock (`inv_final_stock`) — plus, discovered mid-task, buyer-paid postage (`order_shipping_billing_detail`) and, in a **separate ledsone DB**, the listing creation dates (`listings.ebay_listings`) and the account-name map (`order_management.sub_source`). Nothing about the application had to change; the task was to *read*, *report*, *reconcile*, *publish*.
- **Approach.** Read the mockup → lock every rule with Thinesh (never invent) → discover the true scope (12 accounts, 7 marketplaces) → build read-only multi-table dataset SQL → execute via the Postgres MCP → render Excel + interactive HTML → **reconcile against the user's own independent MCP checks** and correct on each mismatch → publish the HTML to the assigned users via `ph_task`. Touch no source data.

> **In plain terms:** Today I turned Thinesh's eBay dashboard mockup into a live, database-built dashboard and published it to four users. The hard part was not the first build — it was **five rounds of reconciliation** against numbers the user verified independently. Each round exposed a real definition trap: revenue had to come from eBay's actual order total (not a reconstructed product+postage sum); a "UK" account actually sells into many countries, so rows had to be per-marketplace; the eBay ad numbers over-count because eBay attributes one sale to every overlapping campaign, so I switched to real ad spend / TACOS and to the ON_SITE (Priority) campaign type only; conversion had to be whole-account traffic, not just ads; and the "new listings" date only exists in a different database. After each correction the numbers matched the user's checks exactly.

---

## SECTION 2 · WHAT CHANGED TODAY

A full reporting increment: a governed multi-table dataset (per account × marketplace) + an interactive HTML dashboard + an Excel workbook + a live publish to four users — reconciled and **corrected five times** against the user's own MCP verifications. First artifacts for the EBPD stream.

- **Change 1 — Onboarding + rule-lock + scope discovery.** Parsed the mockup; confirmed the account→store mapping with Thinesh (incl. the non-obvious **SUNSONE UK = `so_926407`**). Discovered the mockup's 4 accounts undersold reality: **12 eBay accounts had June activity** across **7 marketplaces** (UK, DE, FR, IT, IE, US, CA; UK+DE ≈ 99%, Ireland 0 orders).
- **Change 2 — First build (Excel + HTML), then Revenue corrected twice.** Initial Revenue = `SUM(item_price*quantity)`. Thinesh: "product + postage". First correction added `order_shipping_billing_detail.shipping_template_price`. The user then flagged a mismatch vs their own MCP check → **root cause: the correct field is `SUM(order_total)`** (eBay's actual paid order value); `shipping_template_price` is a *template* price that over-states postage not actually charged. Switched all revenue to `order_total`.
- **Change 3 — Rows restructured whole-store → account × marketplace.** A single eBay store sells into many marketplaces (led_sone sold into UK/DE/FR/US/IT). The whole-store row put led_sone's cross-border sales into a "UK" row (£36k vs the user's verified UK figure £28,975). Rebuilt the main table to **one row per account × marketplace** so each row matches the per-marketplace ground truth.
- **Change 4 — New Listings sourced from the ledsone DB.** Warehouse `listing_data` has no creation date (only `row_update`/`end_date`). Found `listings.ebay_listings.created_at` in the **ledsone DB** (genuine, spans 2015–2026); joined `order_management.sub_source` for the account name → New Listings = distinct `item_id` created in June (248 total).
- **Change 5 — Conversion switched to whole-account.** Was ad-orders ÷ ad-clicks (ad-only). Thinesh: "overall account, not just ads." Found **eBay traffic in `traffic_data.which_channel=2`** (channel 1=Amazon, 3=Shopify) → Conversion = `conversion ÷ click` (page-views), per account × marketplace, works for all accounts (not only advertisers).
- **Change 6 — Ad metric reworked three times → ON_SITE spend + TACOS.** (a) `ppc_performance` `record_type='campaign'` over-reports: attributed Ad Sales/Orders **exceed real revenue** because eBay attributes one order to every overlapping campaign (led_sone runs 116). (b) Dropped attributed sales; adopted **TACOS = Ad Spend ÷ total revenue** + **Return**. (c) User then showed a reference at **ON_SITE (Priority) level** = £884.07 for so_926407 UK; discovered the `ppc` metadata splits campaigns by `record_subtype` (**ON_SITE** vs **COST_PER_SALE** vs OFF_SITE) → filtered Ad Spend to **ON_SITE only** (join `ppc_performance.record_id = ppc.parent_id`).
- **Change 7 — Other corrections.** Removed the mockup's **duplicate second "AOV"** column (undefined, values ~11–12); **Sales Rank = by revenue** (Thinesh-confirmed it is a manual/derived rank); Sales = **Completed** only; RAG thresholds carried from the mockup with a flagged conversion-threshold caveat.
- **Change 8 — UI + publish.** Iterated the UI (slate+teal theme, removed the top hero bar, sticky grouped+column headers, pinned account column, Account/Marketplace/Sort filters + live search, CSV export, Print). Published the HTML to `tech_team_outputs.ph_task` — one row per assigned user (Thinesh, Jarsini, kobiga, powsteena), re-pushed on each correction.

### Deliverables (today)
- One **interactive HTML dashboard** (`...FINAL.html`, live) — 22 account×marketplace rows, order_total sales, ON_SITE ad + TACOS, filters, sticky headers, CSV.
- One **Excel workbook** (`...(v2 - 12 accounts).xlsx`) — 3 sheets — **on the previous method; carried for re-sync.**
- One **idempotent publisher** (`push_ebpd_dashboard.py`) + the morning requirement doc + the clarification log.
- **Live publish:** `ph_task` rows 329–332 (`released`, `ebay_priors`).

Evidence: led_sone UK June = **£28,975.37** (`order_total`, Completed) reconciles to the user's independent check; so_926407 UK ON_SITE ad = **£884.07 / 434 orders / 5,612 clicks / 3,032,285 impressions** matches the reference to the penny; every account×marketplace ON_SITE spend re-verified against the live DB. **No source-data change. No credentials in any deliverable file** (the publisher holds a DB password — see GAP).

---

## SECTION 3 · POSTGRESQL / MCP / DATABASE FINDING

> **This was a database + reporting + publishing task.** All source reads were against the live warehouse (`public`) and the ledsone DB via the Postgres MCP connectors (read-only). The only write is the report HTML into `tech_team_outputs.ph_task` (remote DB, `temp_user`).

**Objects touched today.** READ: `order_transaction`, `order_shipping_billing_detail`, `ppc_performance`, `ppc`, `traffic_data`, `listing_data`, `inv_final_stock` (warehouse); `listings.ebay_listings`, `order_management.sub_source` (ledsone DB). WRITE: `tech_team_outputs.ph_task` only.

- **Finding A — `order_total` is the correct eBay sales field, not `item_price*quantity` (+ never `+shipping_template_price`).** `order_total` is stored at line level and `SUM(order_total)` = eBay's actual paid order value incl. postage actually charged. It differs from `SUM(item_price*quantity)` by ~£100/account (led_sone UK: £28,873.00 product vs **£28,975.37** order_total). `order_shipping_billing_detail.shipping_template_price` is the listing's **template** postage — it over-states real postage (many orders ship free) and must NOT be added on top. Use `order_total`.
- **Finding B — A store's marketplace ≠ its home marketplace; attribute per `order_transaction.market_place`.** A single `ss_name` (e.g. `led_sone`, a UK store) sells into UK/DE/FR/US/IT. Aggregating whole-store inflates the "UK" account with cross-border sales. Correct model = **rows keyed by `ss_name` × `market_place`**; no double-count (each order has one `market_place`, and `led_sone` vs `ledsonede` are distinct accounts).
- **Finding C — eBay organic traffic lives in `traffic_data.which_channel = 2`.** Channel 1 = Amazon, 2 = eBay (4.7M rows for these accounts), 3 = Shopify/other. `traffic_data` carries `impression`, `click`, `conversion`, `market_place`, `sub_source_name` → whole-account eBay conversion = `SUM(conversion)/SUM(click)` (page-view based, ~1–3%). Traffic history starts 2025-04, so LY conversion exists only for accounts live since 2025-06.
- **Finding D — eBay listing *creation dates* are in the ledsone DB, not the warehouse.** Warehouse `listing_data` has only `row_update` + `end_date` (no created date). The **ledsone DB** `listings.ebay_listings.created_at` is a genuine creation timestamp (2015→2026); `sub_source` (int) → account name via `order_management.sub_source.name`; `site` gives the marketplace. New Listings = distinct `item_id` with `created_at` in the month. **Lesson: check the ledsone DB (schemas `listings`, `order_management`) for eBay-specific fields the warehouse lacks.**
- **Finding E — eBay Promoted Listings attributed Ad Sales/Orders OVER-COUNT.** In `ppc_performance` (`source_name='EBAY'`), `record_type='campaign'` sums each campaign's eBay-attributed sales; because one order is attributed to **every** overlapping campaign (led_sone runs 116), summed Ad Sales **exceed real revenue** (led_sone UK £32,152 > £28,975). Spend IS clean (one row per campaign per day, verified incremental). `record_type='ad'` is lower but still over-attributes orders. **Do not present attributed ACOS/ROAS; use real spend (TACOS).**
- **Finding F — eBay Promoted Listings has two products, split by `ppc.record_subtype`.** The campaign-metadata table `ppc` classifies campaigns as **`ON_SITE`** (Priority/Advanced, CPC) vs **`COST_PER_SALE`** (Standard, pay-%-of-sale) vs `OFF_SITE`. Join key: **`ppc_performance.record_id = ppc.parent_id`** where `ppc.record_main_type='campaign'` (campaign ids match; `child_id='0'` on both). Filtering `record_subtype='ON_SITE'` reproduces the user's reference exactly (so_926407 UK £884.07). To avoid join fan-out, filter via `record_id IN (SELECT DISTINCT parent_id FROM ppc WHERE record_subtype='ON_SITE')`.
- **Finding G — Publishing to `ph_task`: two schema traps.** (1) `tech_team_outputs.ph_task` has **no real `UNIQUE(task_id)`** despite the DDL comment — `INSERT ... ON CONFLICT (task_id)` fails ("no unique or exclusion constraint"); use **pre-DELETE by task_id + plain INSERT** (idempotent). (2) The table has an **`assigned_user_team`** column **not shown in the sample DDL** — it must be set (here `ebay_priors`, matching yesterday's eBay publish) or the report won't group under the right team. `action_took_by`/`action_took_date_time` correctly stay NULL until a user actions the report.

**Reconciliation chain (final method):** 12 accounts × their marketplaces = **22 rows**; June revenue (`order_total`, Completed) = **£95,455.18** / 4,625 orders / 7,330 units; ON_SITE ad spend = **£7,788.75** (overall TACOS 8.16%); active listings, new listings (248), stock all per marketplace. Spot-checks tie to the user's independent MCP figures to the penny.

---

## SECTION 4 · GAP FOUND

- **CARRIED (deliverable parity) — the `.xlsx` is not re-synced to the final method.** The Excel workbook still reflects the earlier method (whole-store scope, item_price+postage revenue, campaign-level ad). The **HTML** (published) is on the final method (per-marketplace, `order_total`, ON_SITE ad + TACOS). The two are out of sync; the Excel must be rebuilt to match before it is shared.
- **OPEN (definition) — orders-count basis unconfirmed.** `COUNT(DISTINCT order_id)` = 1,517 for led_sone UK (true distinct orders); the user's reference showed **1,619 = `COUNT(*)`** (order-line count; multi-item orders counted per line). The dashboard uses distinct; needs Thinesh's confirmation.
- **OPEN (RAG) — conversion threshold predates whole-account conversion.** The mockup's green >4.5% threshold suits ad-click conversion; whole-account (page-view) conversion is ~1–3%, so most cells read amber/red under the old threshold. Suggested recalibration (green >2.5% / amber 1.5–2.5% / red <1.5%) pending Thinesh.
- **Documented design decisions (informational, not gaps):** New Listings has no LY/creation for some rows → 0; some marketplaces have no ON_SITE campaign (led_sone-IT, electricalsone-US) → ad shown blank; `led_sone` Canada has **£10.29 ON_SITE spend but no Canada completed sales**, so it has no row to attach to (negligible, excluded); Stock is shared warehouse units per site (overlapping across a store's marketplace rows) — flagged, not deduped.

> `GAP: CARRIED — .xlsx not re-synced to the final method (per-marketplace + order_total + ON_SITE/TACOS); HTML is live and correct. OPEN — orders-count definition (distinct 1,517 vs line 1,619) and conversion RAG threshold recalibration, both pending Thinesh. No source-data gap; all figures reconcile to the user's live-DB checks.`

---

## SECTION 5 · VALIDATION RULE ADDED OR CHANGED

- **Use the platform's own "actually-paid" total for revenue, not a reconstructed product+postage sum (NEW / hard-won).** For eBay, `order_total` is the paid order value incl. real postage; `item_price*quantity` is product-only and `shipping_template_price` is a listing template that over-states postage. Reconstructing "product + postage" from separate fields double-counts or over-states; take the platform's single settled total.
- **Attributed advertising metrics over-count and must not drive efficiency KPIs (NEW).** eBay (and marketplace ad platforms generally) attribute one sale to every campaign in the buyer's journey and within a look-back window; summed attributed Sales/Orders can exceed real sales. Use **real ad spend against real total revenue (TACOS)**, never ACOS/ROAS on attributed sales.
- **Filter marketplace ads by campaign product-type, confirmed against the platform's own segmentation (NEW).** eBay Promoted Listings = ON_SITE (Priority/Advanced) + COST_PER_SALE (Standard); "the eBay ads" the team reports may mean one subtype. Join the performance table to the campaign-metadata table (`ppc.record_subtype`) and confirm the exact segment before totalling.
- **A store's account row ≠ one marketplace; attribute per the order's marketplace (NEW).** Never assume "LEDSONE UK" = UK sales; a store sells cross-border. Report per `account × market_place` (or aggregate deliberately, clearly labelled).
- **eBay-specific facts may live outside the warehouse (reinforced).** Listing creation dates were absent from the warehouse but present in the ledsone DB. Before declaring a field "not derivable", check the platform-specific database.
- **Publish idempotently against tables whose stated constraints may not exist (reinforced).** `ph_task` lacks the `UNIQUE(task_id)` its DDL implies; use pre-delete + insert, and always set hidden-but-required columns (`assigned_user_team`).

> `VALIDATION RULE: a marketplace account-performance report ships only when revenue uses the platform's settled order total (order_total, not reconstructed product+postage), account rows are attributed per marketplace, advertising efficiency uses real spend/TACOS (never attributed ACOS/ROAS), the ad segment (ON_SITE vs Standard) is confirmed against the platform's own campaign-type metadata, platform-specific fields are sought in the platform DB not only the warehouse, and every headline figure is reconciled to the owner's independent live-DB check.`

---

## SECTION 6 · FAILURE MODE OR EDGE CASE

- **Template postage mistaken for charged postage (encountered, root-caused).** Adding `shipping_template_price` over-stated revenue vs the user's check; `order_total` is the settled figure. Mitigation: switch revenue to `order_total`.
- **Attributed ad sales exceeding real revenue (encountered, root-caused).** Campaign-level Ad Sales £32,152 > revenue £28,975 for led_sone UK — impossible for a subset; caused by multi-campaign attribution. Mitigation: drop attributed sales, use TACOS on real spend.
- **Whole-store aggregation inflating a "UK" row with cross-border sales (encountered, fixed).** led_sone "UK" row read £36k vs verified £28,975. Mitigation: per-marketplace rows.
- **Channel code guessed wrong / missing (prevented).** `traffic_data.which_channel` is numeric (1/2/3); eBay = 2, verified before use rather than assumed.
- **"Not derivable" declared too early (encountered, corrected).** New Listings was called N/A from the warehouse; the ledsone DB had `created_at`. Mitigation: search the platform DB before concluding.
- **`ON CONFLICT` on a non-existent unique constraint (encountered, fixed).** `ph_task` insert failed; switched to pre-delete + plain insert.
- **Hidden required column left NULL (encountered, fixed).** First publish left `assigned_user_team` NULL (would mis-group the report); re-pushed with `ebay_priors`.
- **Browser pane can't preview `file://` (handled).** Verified the HTML by `node --check` on the extracted script + a data-reconciliation run + a local `http.server` + DOM-driven checks, not by screenshotting the file URL.

---

## SECTION 7 · DECISIONS MADE TODAY

- **D-1 (executed) — New stream, first deliverable.** Opened REQ-13 / **REQ-13-D01** for EBPD; PH = Thinesh; project_code `ebpd`.
- **D-2 (executed) — Rules locked with Thinesh, never invented.** Completed-only; Revenue = `order_total`; all 12 accounts; Stock = total warehouse units; Sales Rank = by revenue.
- **D-3 (executed) — Rows = account × marketplace** (per the user's choice after seeing the whole-store vs UK-slice reconciliation).
- **D-4 (executed) — Conversion = whole-account traffic** (`traffic_data` `which_channel=2`), not ad-only.
- **D-5 (executed) — New Listings from the ledsone DB** (`listings.ebay_listings.created_at`), not warehouse.
- **D-6 (executed) — Advertising = ON_SITE (Priority) spend only, shown as TACOS + Return;** attributed Ad Sales/ACOS/ROAS omitted.
- **D-7 (executed) — Removed the duplicate mockup AOV column;** flagged the conversion-threshold mismatch.
- **D-8 (executed) — Published live to 4 users via `ph_task`** with pre-delete+insert and `assigned_user_team='ebay_priors'`; re-pushed on every correction (rows 309→…→329–332).
- **D-9 (deferred) — Excel re-sync + orders-count definition + threshold recalibration** carried to next session.

---

## SECTION 8 · COMPANY KNOWLEDGE EXTRACT

### Business Rule
A **marketplace account-performance** report is trustworthy only when every headline reconciles to the **platform's own settled figures** and to the owner's independent check — not just to a self-consistent internal query. For eBay: **Revenue = `order_total`** (the settled paid value, incl. real postage), attributed to the **buyer's marketplace**; **advertising efficiency = TACOS** (real spend ÷ real revenue), because attributed ad sales over-count; the **ad segment** (ON_SITE/Priority vs Standard COST_PER_SALE) must be confirmed against the platform's campaign-type metadata; **conversion = whole-account page-view conversion**, not ad-click conversion. A store account is **not** one marketplace — report per account × marketplace or aggregate deliberately.

### Operational Assumption
**Reconstructing a metric from component fields is riskier than taking the platform's own total.** Product-price + a postage field over-stated revenue; the platform's `order_total` was correct. Likewise **attributed marketplace-ad metrics are not real sales** — they double-count across overlapping campaigns. And **eBay-specific facts (listing creation dates) may live only in the platform DB**, not the analytics warehouse.

### Reusable Logic / Formula
- **Governed eBay account×marketplace pipeline:** lock rules with the owner → resolve the account→store map + the active account/marketplace set from `order_transaction` → read-only dataset (Revenue=`SUM(order_total)` Completed, per `ss_name × market_place`, June/LM/LY) → whole-account conversion from `traffic_data which_channel=2` → **ON_SITE** ad spend from `ppc_performance`⨝`ppc(record_subtype='ON_SITE')` on `record_id=parent_id` → active listings (`listing_data` distinct `ref_id`, per site) + new listings (ledsone `listings.ebay_listings.created_at`) + stock (`inv_final_stock`) → TACOS/Return → dashboard + xlsx → **reconcile to the owner's live-DB check** → publish to `ph_task` (pre-delete+insert, set `assigned_user_team`).
- **eBay ad handling:** `ppc_performance` `record_type='campaign'`, filter to `record_subtype='ON_SITE'` via `ppc.parent_id`; report spend + TACOS, never attributed ACOS/ROAS.
- **eBay revenue:** `SUM(order_total)` (Completed) — the single settled total; do not reconstruct.
- **eBay traffic channel map:** `traffic_data.which_channel` 1=Amazon, 2=eBay, 3=Shopify.
- **Cross-DB rule:** platform-specific fields → check the platform DB (`listings`, `order_management` schemas), not only the warehouse.

### Canonical Vocabulary
| Term | Meaning |
| :---- | :---- |
| order_total | eBay's settled paid order value (product + real postage) — the revenue basis |
| account × marketplace | a store (`ss_name`) attributed by the buyer's `market_place` (the row grain) |
| TACOS | ad spend ÷ **total** revenue (real efficiency; replaces attributed ACOS/ROAS) |
| ON_SITE / Priority | eBay Promoted Listings Advanced (CPC) — `ppc.record_subtype='ON_SITE'` |
| COST_PER_SALE | eBay Promoted Listings Standard (pay-%-of-sale) — excluded from the ad count per Thinesh |
| attributed over-count | one order counted by every overlapping campaign → ad sales > real sales |
| whole-account conversion | `conversion ÷ click` from `traffic_data which_channel=2` (all traffic, not ads) |
| ebay_priors | the `ph_task.assigned_user_team` group for eBay reports (hidden-but-required column) |

### Cross-Project Applicability
- **Platform-settled-total rule** — any marketplace revenue report (use the platform's order total, not reconstructed components).
- **TACOS-over-attributed-ACOS** — any Amazon/eBay/Shopify PPC report where attributed sales can exceed real sales.
- **Ad-segment confirmation** — any Promoted-Listings/Sponsored report where "ads" may mean a specific campaign type.
- **Account × marketplace attribution** — any multi-marketplace store report.
- **Cross-DB field discovery + `ph_task` publish gotchas** — any AIOS report published to portfolio holders.

---

## SECTION 9 · LLM STANDARD CHECK

| Check | YES / NO |
| :---- | :---- |
| Could an unknown developer continue from this file without reading source code? | ✅ YES — metadata + S3 give the tables, join keys (`ppc_performance.record_id=ppc.parent_id`), filters, the `order_total`/`which_channel=2`/`record_subtype='ON_SITE'` rules, and the `ph_task` publish method |
| Is every business threshold visible (not buried in code)? | ✅ YES — window, sale status, revenue field, ad segment, conversion basis, TACOS RAG, rank rules all in metadata + S3 |
| Is the GAP FOUND section completed or marked NONE? | ✅ YES — CARRIED (.xlsx re-sync) + OPEN (orders-count, conversion threshold) recorded with mitigation |
| Is the COMPANY KNOWLEDGE EXTRACT section substantive? | ✅ YES |
| Are evidence locations referenced? | ✅ YES — artifact list, reconciliation figures (£28,975.37; £884.07; £95,455.18), `ph_task` rows 329–332 |
| Is metadata complete (incl. blos_keys_used + hardcoded_thresholds)? | ✅ YES — `blos_keys_used` N/A (non-BLOS) with READ/WRITE objects listed; `hardcoded_thresholds` = the report rules |
| Are section names per standard template (1–9)? | ✅ YES (S3 = PostgreSQL/MCP/Database — real DB findings; this was a DB + reporting + publish task) |
| Is this extracting knowledge — not just logging activity? | ✅ YES |

### Three-AM Standard Self-Assessment
- **WHAT** — built the first governed **eBay Account Performance dashboard** for PH Thinesh (June 2026): a read-only multi-table dataset (per account × marketplace) + interactive HTML + Excel, **published live to 4 users** via `ph_task`. Corrected the method five times against the user's own MCP checks — Revenue → `order_total`; rows → account × marketplace; Conversion → whole-account traffic; New Listings → ledsone DB; Advertising → ON_SITE spend + TACOS. Every headline reconciles to the user's figures to the penny.
- **NOT DONE (carried)** — (1) **re-sync the `.xlsx`** to the final method; (2) **confirm the orders-count** definition (distinct 1,517 vs line 1,619); (3) **recalibrate the conversion RAG threshold** for whole-account conversion; (4) formal **sign-off** from Thinesh.
- **WHY** — Thinesh had no live, reconcilable eBay account dashboard; this delivers one whose every number ties to the platform's settled data and to his own checks — and, en route, hardened the company's eBay reporting rules (order_total, TACOS, ON_SITE, whole-account conversion, cross-DB fields).
- **WHO / WHERE / NEXT** — owner/developer abiraj; end user Thinesh (+ Jarsini, kobiga, powsteena as viewers); reviewer gates Tamil Selvan (queryability) + Sajeesan (technical). Artifacts this session (see `evidence_location`); live at `ph_task` 329–332. **NEXT:** rebuild the .xlsx to match → confirm orders-count → recalibrate the conversion threshold → obtain sign-off → schedule the monthly refresh.

---

## ── SUBMISSION CHECKLIST ─────────────────────────────────────────────────────

- [x] File named correctly: `2026-07-17__abiraj__ebpd__REQ-13-D01.md`
- [x] Saved under dated folder `DigitWeb_Works_Abiraj/17_07_2026/`
- [x] Metadata complete — incl. `blos_keys_used` (N/A, non-BLOS; READ/WRITE objects listed), `hardcoded_thresholds` (report rules), `user`, `benefit_status`
- [x] Section 3 present under the standard heading (PostgreSQL/MCP/Database) — real DB findings (all source reads read-only; only write is the report HTML to `ph_task`)
- [x] Section names 1–9 match standard template
- [x] **No credentials, passwords, or API keys included in this skill file** (note: the publisher `push_ebpd_dashboard.py` embeds a `temp_user` DB password — flagged for migration to an env var / secret store)
- [x] LLM Standard Check table completed
- [x] Three-AM Standard self-assessment written (WHAT / NOT DONE / WHY / WHO-WHERE-NEXT)
- [x] Evidence referenced (artifact list, reconciliation figures, `ph_task` rows 329–332)
- [x] ✅ **DONE TODAY:** onboarding + rule-lock + 12-account/7-marketplace scope discovery · Excel + HTML built · Revenue corrected to `order_total` · rows → account × marketplace · New Listings sourced from ledsone DB · Conversion → whole-account traffic · Advertising → ON_SITE spend + TACOS · duplicate AOV removed · UI (theme, sticky headers, filters, CSV) · **published live to 4 users (`ph_task` 329–332)** · every headline reconciled to the user's own MCP checks
- [ ] ⚠️ **NOT CLOSED — carried:** re-sync the `.xlsx` to the final method · confirm orders-count definition · recalibrate conversion RAG threshold · migrate the publisher DB password to a secret
- [ ] ⏳ **VALIDATION PENDING** — not yet formally signed off by Thinesh
- [x] **NEXT STEPS:** (1) rebuild the Excel to per-marketplace + `order_total` + ON_SITE/TACOS · (2) confirm orders-count with Thinesh · (3) recalibrate the conversion threshold · (4) obtain sign-off · (5) schedule the monthly refresh
