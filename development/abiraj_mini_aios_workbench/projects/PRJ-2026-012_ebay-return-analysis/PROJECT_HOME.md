# PROJECT_HOME — eBay Return Analysis Dashboard (Thinesh)

## Project ID
PRJ-2026-012_ebay-return-analysis

## Project Name
eBay Return Analysis Dashboard | a per-SKU eBay returns dashboard (Excel) — one row per variant SKU
that had at least one eBay return in the reporting period, with returns, rate, refund/return-cost,
main reason, negative feedback, open cases, stock and advertising efficiency, across every eBay store
and marketplace (LEDsONE analytics platform).

## Purpose
For every eBay variant SKU that was returned in the period, present the return picture on one line —
Orders, Returns, Return Rate, Last Month / Last Year Returns, Refund (£), Return Cost (£), Main Return
Reason, Return Rank, Negative Feedback, Open Cases, Stock, and Ad Spend / Ad Sales / ACOS / ROAS — plus
a Return-Reason Breakdown table, a Filter Options block and a Before/After efficiency table, so Thinesh
and the account managers see which products drive eBay returns and what they cost, not a mocked proxy.

**This project is a READ-ONLY REPORT** (like PRJ-2026-004→008, 010, 011), **unlike PRJ-2026-009**
which is a gated build. No DDL, no sync, no writes to source tables. The only write, when a live build
is later authorised, is the guarded publish of the finished dashboard to `tech_team_outputs.ph_task`.

## Business Question
Across our eBay stores and marketplaces (UK, DE), which variant SKUs are being returned, how often
relative to sales, why, and at what refund/fee cost — so the owner can see the worst-returning products
for the period (reference build: June 2026)?

Status: **CONFIRMED** in shape by the mockup (`Thinesh task (2).xlsx`, 19-column layout) and detailed
in the two handoff documents (scope, parameters, column derivation, the CPC+CPS advertising rule,
intentional blanks). **Built live against the Ledsone DB, published, automated, and signed off
2026-07-20** (see Status).

## Owner and Reviewers
- Owner / Developer: **Abiraj**
- Requester / report owner: **Thinesh** (+ the eBay account managers; report viewers Jarsini,
  kobiga, powsteena, Sharmilan, Sivajitha — the 6 ebay_priors recipients)
- Coordinator: Varmen
- Technical Reviewer: **Sajeesan** — **signed off 2026-07-20**
- Queryability Reviewer: **Tamil Selvan** — **signed off 2026-07-20**
- Business Validator: **Thinesh** — **signed off 2026-07-20**

## Governance Identity (confirmed by owner 2026-07-20)
- **project:** eBay Return Analysis
- **project_code:** `ERA`
- **phase:** Phase — Reporting & Presentation (eBay Return Analysis Dashboard — first governed report)
- **requirement_id:** `REQ-14`   ·   **deliverable_id:** `REQ-14-D01`

## Original Requirement
- **REQ-14 (2026-07-20)** — reproduce the per-SKU eBay Return Analysis dashboard from the live
  Ledsone PostgreSQL, per `Thinesh task (2).xlsx` (target layout) and the two handoff documents.
  Task ID `REQ-14_ebay-return-analysis`, **deliverable `REQ-14-D01`**, `project_code=ERA` — **confirmed
  by the owner 2026-07-20** (the source carried no requirement id; `REQ-14`/`ERA` adopted as the governed
  identity).
- **REQ-14-D01** — the delivered read-only dashboard, built live against `ledsone`, published to the 4
  eBay users, and set to auto-refresh monthly (see Status).

## Approved Scope
- Maintain this project folder (`projects/PRJ-2026-012_ebay-return-analysis/`).
- Read-only against the live **Ledsone PostgreSQL** normalised domain schemas (`customer_service`,
  `order_management`, `listings`, `inventory`, `ebay_campaigns`, `accounting`) via the **Ledsone
  Database MCP** for a live build.
- The **single approved write** (only when a live build is explicitly authorised): the guarded publish
  of the finished dashboard to `tech_team_outputs.ph_task`. **Not yet done.**

## Prohibited Scope
- No write to any **source** table; no DDL; no schema change; no automation.
- Do **not** use the `public.*` denormalised layer as a data source — it belongs to a different DB and
  returns nothing here (handoff §3).
- The mockup's dummy rows (LS1001 "Industrial Pendant Light", etc.) are **illustrative only** — never
  the answer.
- Do not publish to `ph_task` or commit/push without explicit owner instruction.

## Systems and Sources (for a live build — read-only)
- **Live Ledsone PostgreSQL** via **Ledsone Database MCP** (`execute_sql`, `search_objects`):
  - `customer_service.ebay_returns` — return cases (reason + refund on the **earliest** row per
    `return_id`; latest STATE on the **newest** row), `customer_service.ebay_orders_customer_feedbacks`
    (negative feedback).
  - `order_management.order_item_info` — `transaction_id`→variant SKU/title bridge (the correct join,
    **not** `item_id`); `order_management.orders` / `source` / `sub_source` — eBay orders + friendly
    account name.
  - `accounting.ebay_order_expenses` — refund/selling fees (Return Cost) + CPS ad fees
    (`AD_FEE` / `PREMIUM_AD_FEES`); keyed on the **eBay order reference** (`orders.order_id`, varchar).
  - `ebay_campaigns.performance_data` + `campaigns` — CPC/Advanced (`ON_SITE`) ad spend/sales
    (**CPC-only** table).
  - `listings.ebay_listings` — `item_id`→SKU for spreading CPC spend across variants.
  - `inventory.products` + `local_inventory_current_stock_location_wise` — live Stock snapshot.
- **`tech_team_outputs.ph_task`** — the publish target only (when authorised).

## Reference figures (June 2026 — from the imported reference build, to diff against)
144 SKU rows · 153 returns · blended return rate **17.7%** · Refund **£2,937.37** · Return Cost
**£869.39** · Ad Spend **£1,387.96** · Ad Sales **£9,343.63** · ACOS **14.9%** · ROAS **6.73x**.
Reason breakdown sums to 153 (Wrong Size 47 / Ordered Wrong Item 28 / Not as Described 21 / …). A live
build must match these for June 2026 before it is accepted.

## Status
**REQ-14-D01 DELIVERED · PUBLISHED (6 users) · REQ-14-D02 AUTOMATION LIVE — 2026-07-20.**
- Handoff bundle imported COPY-only + SHA-256; canonical SQL **live-verified** against `ledsone` (direct
  read-only psycopg2, no MCP) — reproduces the June-2026 reference to the penny (144 SKUs · 153 returns ·
  17.7% · Refund £2,937.37 · Return Cost £869.39 · Ad Spend £1,387.96 · Ad Sales £9,343.63 · ACOS 14.9% ·
  ROAS 6.73x). See `validation/REQ-14_.../2026-07-20_live_count_verification.md`.
- **REQ-14-D01** — light-theme HTML dashboard (EBPD house style) with a **date-range dropdown** (Full
  month / 1st–2nd half / Week 1–4, each re-scoping the whole dashboard from live per-window pulls; pure-CSS
  so it works in the no-JS ph_task viewer), rendered **full-width / full-screen**. **PUBLISHED per-user to
  `tech_team_outputs.ph_task` — ids 518 (Thinesh), 519 (Jarsini), 520 (kobiga), 521 (powsteena), 522 (Sharmilan), 523 (Sivajitha)**, all
  `project_code=ERA`, `assigned_user_team=ebay_priors`, `released`. (Row ids incremented on each layout
  refresh + the ebra→ERA re-key; the old ebra-coded rows were retired.)
- **REQ-14-D02** — fully autonomous **monthly** refresh: Windows Task **`ERA_Monthly_Dashboard`**, **day 5
  of every month, 09:30** (next run 2026-08-05), reports the last complete month, direct psycopg2 (no MCP),
  month-keyed publish, status file + Desktop failure alert; all passwords in the git-ignored
  `automation/era_secrets.bat`.
- **Sign-offs — ALL RECEIVED 2026-07-20:** Sajeesan (technical), Tamil Selvan (queryability), Thinesh
  (business). Governance identity confirmed (`ERA` / `REQ-14` / `REQ-14-D01`). Optional future: cross-month
  ranges (Last 90 Days / Last Year — accepted as out of scope for now).
- **Not yet committed to git.**

## One Next Action
Commit the branch to git (pending owner instruction). Otherwise **COMPLETE** — delivered, published (ids
518–523), automated (monthly, 5th), and signed off.
