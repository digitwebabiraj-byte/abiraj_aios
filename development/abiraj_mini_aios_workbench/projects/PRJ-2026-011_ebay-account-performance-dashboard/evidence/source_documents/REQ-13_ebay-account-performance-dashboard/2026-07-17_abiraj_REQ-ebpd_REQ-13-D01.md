# **Daily Requirement Document**

## **1. Metadata Block**

| Field | Value |
| ----- | ----- |
| daily_requirement_submitted_date | 2026-07-17 |
| expected_deadline_date | 2026-07-17 |
| end_user | Thinesh (report owner/persona), the eBay account-management & marketplace-operations team, department leaders, developers or MD — anyone who must monitor and act on eBay account performance across marketplaces |
| expected_roi | Replaces the manual, multi-tab monthly pull of eBay account KPIs with **one automated account-performance dashboard**. For each eBay store it lays Sales (revenue, orders, units, AOV, conversion — with Last-Month and Last-Year comparisons), Advertising (spend, ad-sales, ACOS, ROAS) and Listings/Stock side by side, RAG-scored against fixed thresholds, so the team can see at a glance which account is growing, which is over-spending on ads, and which is losing listings — instead of assembling it by hand. The automation table in the source spec estimates ~13–82 min saved per process run (Account Health Check, Sales Report, PPC Review, Listing Analysis, Stock Monitoring, Return & SKU reports) |
| developer | abiraj |
| project | eBay Account Performance Dashboard (monthly eBay account KPI dashboard across all eBay marketplaces) — LEDsONE analytics platform |
| project_code | ebpd |
| phase | Phase — Dashboard build (EBPD Stage 1 — canonical monthly account-performance table, first deliverable REQ-13-D01, shipped in two formats: Excel .xlsx + HTML .html) |
| requirement_id | REQ-13 |
| deliverable_id | REQ-13-D01 |
| blos_keys | Reporting month — **June 2026** (Last Month = May 2026, Last Year = June 2025). Advertising rolled up at **campaign level** (record_type='campaign') to avoid double-counting the nested 'ad' rows. Sales = Completed orders only. Reporting-only — no source table is mutated |
| domain | Analytics — eBay Marketplace — Account Performance — Text-to-SQL Reporting |
| daily_planned_benefits | (1) One canonical **eBay Account Performance dashboard (Excel)** reproducing the requester's mockup layout but populated entirely from the live warehouse · (2) Correct **account→store mapping** confirmed with Thinesh (LEDSONE UK=led_sone, SUNSONE UK=so_926407, Electricalsone UK=electricalsone, LEDSONE DE=ledsonede) · (3) Correct **advertising aggregation** — campaign-level rollup after detecting that summing the nested keyword/'ad' rows double-counts Ad Sales above true revenue · (4) Full **7-marketplace coverage** (UK, DE, FR, IT, IE, US, CA) with the default view aggregating all marketplaces per account and a marketplace filter to drill in · (5) Every unclear or non-existent metric **flagged to Thinesh and parked**, never invented — read-only against all source tables |

---

# **2. Today Requirement Block**

### **Purpose**

Defines which part of the complete EBPD requirement is to be executed today. The source specification (`Thinesh task (1).xlsx`, sheet `eBay AccountPerformance Dashboa`) defines a recurring **eBay Account Performance Dashboard** but **no runnable dashboard exists yet** — the workbook holds only the target layout, the KPI thresholds, sample cards and a set of illustrative June figures (round placeholder numbers). Today's scope: turn that specification into a **working, executed multi-table report** for the eBay store accounts, populating the Sales / Advertising / Listings / Stock grid for **June 2026** with Last-Month and Last-Year comparisons, RAG-scored against the workbook's thresholds, and deliver it as an **Excel workbook first** (HTML dashboard to follow as a separate deliverable). The source tables, application data and database are **read-only** — nothing is written back to any source table; the only outputs are the Excel dashboard and this planning record.

## **2.1 Today Requirement**

### **Task Name:**

Build and execute the EBPD monthly dashboard (Excel) — eBay store accounts with June-2026 Sales (revenue, orders, units, AOV, conversion + Last-Month + Last-Year), Advertising (spend, ad-sales, ACOS, ROAS), and Listings/Stock, RAG-scored and matching the requester's mockup layout, covering all 7 eBay marketplaces.

### **Business Purpose:**

The eBay account team currently assembles account KPIs by hand across several exports each month. Today's work is to produce **one canonical dashboard** that answers, from the governed data alone: for each eBay store account — what was its **revenue, orders, units, AOV and conversion** in June 2026 (and how do they compare to May 2026 and June 2025); what were its **ad spend, ad sales, ACOS and ROAS**; and how many **active listings** and how much **backing stock** it has. This lets a reviewer immediately see growth vs decline, ad efficiency and listing health per account, and act. Where the source spec's layout asks for a metric that has **no live eBay source** (New Listings creation count, native Sales Rank / PPC Rank, a site-session conversion rate, an account-exclusive stock number), the gap is to be **recorded and escalated to Thinesh** — never silently invented. The sample June figures in the workbook are **illustrative only** and must not be reproduced as the answer.

---

### **Source Information**

Source System:

Postgres analytics warehouse `order_management_copy` (READ-ONLY for this task)

Requirement source (READ-ONLY):
`Thinesh task (1).xlsx` — sheet `eBay AccountPerformance Dashboa` (target layout + KPI thresholds + illustrative figures)

Governing skills (READ-ONLY):
`postgres-warehouse-sql` (routing, per-table schema references, mandatory postgres execution)
`SKILL_multi_table.md` (multi-domain join path — sales → advertising → listings → stock)
`SKILL_ppc_stock_lookup.md` (account/SKU bridge, mapped_sku fallback, clean-SKU step)

Tables to be read (READ-ONLY):

`public.order_transaction` — sales (ss_name, order_id, item_price, quantity, order_status, order_date, source_name, market_place)
`public.ppc_performance` — advertising (ss_name, date, spend, sales, orders, clicks, impressions, record_type, marketplace)
`public.listing_data` — active-listing count (ref_id, which_channel_name, sub_source_name, mapped_sku, sku, wrong_sku, market_place)
`public.inv_final_stock` — stock by SKU (sku, stock, warehouse_name)

---

### **Filter Conditions**

Write scope: **Excel dashboard / dataset output ONLY** — no write to any source table, no schema change, no seed
Task ID: `REQ-ebpd_ebay-account-performance-dashboard` — deliverable **REQ-13-D01** (first deliverable of the REQ-13 / EBPD stream)
Channel scope: **eBay only** — `order_transaction.source_name='EBAY'`, `ppc_performance.source_name ILIKE '%ebay%'`, `listing_data.which_channel_name='ebay'`
Account scope (confirmed by Thinesh): **LEDSONE UK=led_sone · SUNSONE UK=so_926407 · Electricalsone UK=electricalsone · LEDSONE DE=ledsonede**
Marketplace scope: **all 7 eBay marketplaces** — UK, Germany (DE), France (FR), Italy (IT), Ireland (IE), United States (US), Canada (CA). Default view aggregates all marketplaces per account; a marketplace filter drills into any one. (UK + DE ≈ 99% of activity; US/FR/IT/CA are tiny; **Ireland had 0 orders in June 2026**.)
Reporting period: **June 2026** — the named reporting month. **Last Month = May 2026**, **Last Year = June 2025**.
Sales definition: revenue = `SUM(item_price*quantity)` on `order_status='Completed'` (Refunded & Cancelled excluded); orders = `COUNT(DISTINCT order_id)`; units = `SUM(quantity)`; AOV = revenue/orders
Advertising definition: `ppc_performance` filtered to **record_type='campaign'** (campaign-level rollup) to avoid double-counting the nested 'ad' sub-rows; ACOS = spend/ad-sales, ROAS = ad-sales/spend
Execution rule: SQL is never the final answer — it **must be executed via the Postgres MCP `execute_sql`** and the real rows returned
Stop conditions: account→store mapping unconfirmed · Sales-status filter or marketplace scope in dispute · a metric with no live source (New Listings, Sales Rank, PPC Rank, site conversion) treated as real without Thinesh's sign-off · a write would land on any source table

---

### **Required Data Output**

| Field | Purpose |
| ----- | ----- |
| EBPD dashboard (Excel — main deliverable) | One row per eBay store account, matching the mockup: `Account` · Sales (`Revenue`, `Last Month Revenue`, `Last Year Revenue`, `Orders`+LM+LY, `Units`+LM+LY, `AOV`+LM+LY, `Conversion Rate`+LM+LY) · Advertising (`Ad Spend`, `Ad Sales`, `ACOS`, `ROAS`, `PPC Rank`) · Listings (`Active Listings`, `New Listings`, `Sales Rank`, `Stock`) · plus KPI-threshold block, summary cards, filters, automation table and a Definitions/Assumptions block |
| Executed SQL + real results | The per-domain queries (sales, advertising, listings, stock), **run** against the warehouse, with the actual returned rows (not queries shown alone) |
| Reporting-period proof | The exact windows used — June 2026 (2026-06-01…2026-06-30), May 2026, June 2025 — for Last-Month / Last-Year comparisons |
| Account → store mapping note | How each mockup account name resolved to its `ss_name` (Thinesh-confirmed), incl. the ambiguous SUNSONE UK → `so_926407` |
| Advertising-grain note | Why advertising is rolled up at campaign level (record_type='campaign'), with the double-counting evidence (Ad Sales exceeding revenue when both levels summed) |
| Open-logic / held-items note | Every non-existent or derived metric (New Listings creation count, Sales Rank, PPC Rank, site-session conversion, account-exclusive stock, LEDSONE DE Last-Year ads, mockup 'AOV' cols Q–S) parked for Thinesh — flagged, not invented |
| Scope note | `huettenlampen` (DE, larger June revenue than LEDSONE DE) is present in the data but not in the mockup's 4 accounts — flagged for possible inclusion |
| report_period | 2026-06 |

---

# **Business Logic Block**

Purpose:
Defines how today's dashboard is to be built and evaluated. Only an Excel dashboard/dataset is to be produced — nothing in any source table is to be changed.

## **Account Scope & Mapping**

Rule:

- Exactly four store accounts from the mockup are populated: **LEDSONE UK=led_sone · SUNSONE UK=so_926407 · Electricalsone UK=electricalsone · LEDSONE DE=ledsonede**, confirmed by Thinesh.
- SUNSONE UK had **no matching store name** in the warehouse; `so_926407` (the largest otherwise-unmapped UK eBay store) was confirmed as the mapping — not guessed.
- Any additional major account (e.g. `huettenlampen`) is **flagged for Thinesh**, not added silently.

## **Reporting Period (June 2026, with comparisons)**

Rule:

- The reporting month is **June 2026** (2026-06-01 to 2026-06-30 inclusive).
- **Last Month = May 2026**; **Last Year = June 2025**. Sales comparisons are computed for all three windows.
- Advertising comparisons: May 2026 and June 2025 where data exists. **LEDSONE DE (ledsonede) has NO June-2025 advertising** — eBay ad history begins 2025-09 — so its Last-Year ad cells are left blank, not zero-filled.

## **Sales, Advertising, Conversion**

Rule:

- **Sales** from `order_transaction`, `source_name='EBAY'`, `order_status='Completed'` (Refunded/Cancelled excluded): Revenue = SUM(item_price*quantity), Orders = COUNT(DISTINCT order_id), Units = SUM(quantity), AOV = Revenue/Orders.
- **Advertising** from `ppc_performance`, `record_type='campaign'` only (campaign-level) to avoid double-counting the nested 'ad' rows: ACOS = Spend/AdSales, ROAS = AdSales/Spend. Ad Sales is eBay-attributed and may slightly exceed net completed revenue due to attribution window + shipping inclusion — noted, not corrected.
- **Conversion Rate** = ad orders ÷ ad clicks (campaign-level). eBay exposes no site-session data, so this is **ad-driven** conversion — the definition is recorded and flagged for Thinesh's confirmation.

## **Listings & Stock**

Rule:

- **Active Listings** = distinct `ref_id` in `listing_data` (`which_channel_name='ebay'`) per account — a **current live snapshot**, not a June-specific historical count (`offer_id`, `is_ended`, `is_deleted`, `status` are unpopulated).
- **New Listings** = **N/A**: `listing_data` has no creation date (only last-update), so a "created-in-June" count cannot be derived from the live DB.
- **Sales Rank / PPC Rank**: eBay has no native rank fields — shown as **derived** ranks (by June Revenue and by June Ad Sales respectively), clearly labelled.
- **Stock** = SUM(`inv_final_stock` units) for the SKUs each account lists (via `listing_data` bridge, wrong_sku=0, mapped_sku fallback). Physical inventory is **shared** across accounts/channels, so this is gross backing stock, not account-exclusive; the overlap is stated.

## **KPI RAG Scoring**

Rule:

- The workbook's fixed thresholds are applied as cell colouring: Revenue Growth MoM (>10% green / 0–10% yellow / <0% red), Conversion (>4.5% / 3–4.5% / <3%), ACOS (<12% / 12–18% / >18%), ROAS (>8 / 5–8 / <5). Thresholds are the requester's, not invented.

## **Safety**

Rule:

- **Read-only against all source data.** No INSERT/UPDATE/DELETE on `order_transaction`, `ppc_performance`, `listing_data`, `inv_final_stock` or any other table; no schema change; no seeding; no application/config/deployment change.
- The dashboard documents behaviour **from the data as it stands** — no invented metrics and no business-rule decisions. Where the mockup asks for something with no live source, it is **flagged and parked**, not fabricated.
- SQL alone is never the deliverable — each query **must be executed** and real rows returned.
- Reviewer gates: Queryability (Tamil Selvan) and Technical (Sajeesan) sign-off to follow; business-logic and metric-definition clarifications routed to **Thinesh** (report owner).

---

# **Data Enrichment Block**

Purpose:
Record the join path and the resolution trail so a reviewer can re-trace every column in the dashboard.

Source:

`public.order_transaction`  — sales per store account (eBay), the central account identifier (`ss_name`)
`public.ppc_performance`  — spend / ad-sales / clicks / orders, campaign-level (record_type='campaign'), matched on `ss_name` + date window
`public.listing_data`  — active-listing count (distinct `ref_id`) and the account→SKU bridge (wrong_sku=0, mapped_sku fallback)
`public.inv_final_stock`  — stock by SKU (shared physical inventory)

Required Data:

| Field | Reason |
| ----- | ----- |
| Per-domain executed queries | Sales (3 windows) · Advertising (campaign-level, 3 windows) · Active listings (snapshot) · Stock (SKU bridge) — each run via the Postgres MCP `execute_sql` |
| Reporting-window record | The exact June 2026 / May 2026 / June 2025 windows used, proving the Last-Month and Last-Year comparisons |
| Account → store mapping trail | Per account: mockup name → `ss_name`, including the Thinesh-confirmed SUNSONE UK → `so_926407` |
| Advertising-grain evidence | The campaign-vs-ad double-count check (Ad Sales exceeding revenue when both levels summed) justifying record_type='campaign' |
| Assumptions / held-items note | New Listings (no creation date), Sales Rank / PPC Rank (derived), site-session conversion (unavailable), shared stock, LEDSONE DE Last-Year ads (none pre-2025-09), mockup 'AOV' cols Q–S (ambiguous) — each parked for Thinesh, not fixed today |
| Deliverable formats | REQ-13-D01 ships in **two formats from the same governed queries**: an Excel workbook (.xlsx) and a self-contained HTML dashboard (.html). Both are this one deliverable, not separate D-numbers |
| report_period | 2026-06 |
