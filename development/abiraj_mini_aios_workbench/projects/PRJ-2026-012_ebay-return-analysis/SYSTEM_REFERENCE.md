# SYSTEM_REFERENCE — eBay Return Analysis Dashboard (PRJ-2026-012)

Complete functional detail of what this system does, derived from the two canonical handoff documents
and the SQL. Plain-markdown, for a leader or a new engineer. Project-level (describes the whole system),
so it lives at the project root, not inside the `REQ-14` task folder.

Canonical sources:
`evidence/source_documents/REQ-14_.../CLAUDE_CODE_HANDOFF.md` (RUNBOOK + acceptance),
`evidence/source_documents/REQ-14_.../eBay_Return_Analysis_HANDOFF.md` (derivations),
`sql/REQ-14_.../ebay_return_analysis.sql` (source of truth for the data).

---

## 1. What it produces
A single Excel worksheet, "eBay Return Analysis", with:
1. A **per-SKU table** — exactly 19 columns, one row per **variant SKU** that had ≥ 1 eBay return in
   the reporting period, ordered by Returns desc then Refund desc, with a TOTAL / AVG row.
2. A **Return-Reason Breakdown** table (reason · returns · % of returns).
3. A **Filter Options** block (the mockup's filter spec — Date Range, Account, Return Status, Return
   Reason, SKU, Category, Brand).
4. A **Before / After efficiency** table (manual-workflow minutes vs automated).

The reference build is **June 2026**. The system is re-runnable for any month by changing six dates.

## 2. Scope & parameters (agreed with Thinesh)
| Parameter | Decision |
|---|---|
| Channel | **eBay only** — all eBay accounts and marketplaces (UK, DE). |
| Period (reference) | **June 2026** (`2026-06-01` → `2026-07-01`, start inclusive, end exclusive). Return Rate = period returns ÷ period units ordered. |
| Return Cost | **eBay refund fees + selling fees** (REFUND + FINAL_VALUE_FEE on returned orders). |
| Ad columns | A single **Ad Spend / Ad Sales / ACOS / ROAS** set (exact task-sheet layout), **combining CPC + CPS**. |
| Comparison windows | Last Month = May 2026 (`2026-05-01`→`2026-06-01`); Last Year = June 2025 (`2025-06-01`→`2025-07-01`). |
| Grain | One row per variant SKU with a period return. |
| Stock | Live snapshot — always "now", never period-bound. |

## 3. The 19 columns and how each is derived
Order is fixed by the mockup and must not change.

| # | Column | Source & logic |
|---|---|---|
| 1 | SKU | `ebay_returns.transaction_id` → `order_management.order_item_info.item_transaction_id` → `real_sku` (fallback `item_sku`). 100% match; the exact variant. |
| 2 | Product Title | same bridge → `item_title`. |
| 3 | Account | `ebay_returns.sub_source` → `order_management.sub_source.map_name` (staff-facing name; raw usernames are random strings), `INITCAP`. |
| 4 | Orders | Units sold on eBay in the period per SKU: `orders` ⋈ `sub_source` ⋈ `source (=EBAY)` ⋈ `order_item_info`; `item_quantity` is TEXT → cast to numeric. |
| 5 | Returns | Distinct `return_id` in the period (case rows where `reason` is populated). |
| 6 | Return Rate | Returns ÷ Orders. **Blank** where period orders = 0. |
| 7 | Last Month Returns | Same return logic, May 2026 window. |
| 8 | Last Year Returns | Same return logic, June 2025 window. |
| 9 | Refund (£) | Sum `seller_refund_amount` for the SKU's period returns. |
| 10 | Return Cost (£) | `accounting.ebay_order_expenses` on the returned orders: `transaction_type='REFUND'` OR `fee_type IN (FINAL_VALUE_FEE, FINAL_VALUE_FEE_FIXED_PER_ORDER)`. |
| 11 | Main Return Reason | Most frequent reason in the period per SKU (`mode()`), eBay codes mapped to readable labels. |
| 12 | Return Rank | `RANK()` by period return count, ties broken by refund £; rendered `#n`. |
| 13 | Negative Feedback | `customer_service.ebay_orders_customer_feedbacks` `type='Negative'` in the period, mapped to SKU via `transaction_id`. |
| 14 | Open Cases | Period returns whose latest `to_state` ≠ `CLOSED`. |
| 15 | Stock | Live snapshot: `inventory.products.sku` → `local_inventory_current_stock_location_wise` (all locations). Not period-bound. |
| 16 | Ad Spend (£) | **CPC + CPS combined** — see §4. |
| 17 | Ad Sales (£) | **CPC attributed sales + CPS line revenue on ad-charged orders** — see §4. |
| 18 | ACOS | Ad Spend ÷ Ad Sales. **Blank** where Ad Sales = 0. |
| 19 | ROAS | Ad Sales ÷ Ad Spend, rendered `x`. **Blank** where Ad Spend = 0. |

Main-reason / breakdown label map (eBay code → label): `WRONG_SIZE`→Wrong Size, `ORDERED_WRONG_ITEM`→
Ordered Wrong Item, `NOT_AS_DESCRIBED`→Not as Described, `NO_LONGER_NEED_ITEM`→No Longer Needed,
`DEFECTIVE_ITEM`→Defective Item, `ORDERED_DIFFERENT_ITEM`→Ordered Different Item,
`ORDERED_ACCIDENTALLY`→Ordered Accidentally, `ARRIVED_DAMAGED`→Arrived Damaged, `BUYER_NO_SHOW`→Buyer
No-Show, `NO_REASON`→No Reason Given, `WITHDRAW_FROM_PURCHASE_CONTRACT`→Withdrawn from Purchase; else
`INITCAP(REPLACE(code,'_',' '))`.

## 4. The advertising rule (CPC + CPS) — the key gotcha
eBay has two ad models in **different tables**; using only one silently drops half the ad cost.
- **CPC / Advanced (`ON_SITE`)** — `ebay_campaigns.performance_data` (every value column is `cpc_*`, so
  the table is **CPC-only**). Join `performance_data.ebay_listing_id` = eBay `item_id` →
  `listings.ebay_listings.item_id` (`wrong_sku=0`) → `sku`; spend/sales are per listing, so they are
  **spread across the listing's variant SKUs** (÷ number of variants).
- **CPS / Standard (`COST_PER_SALE`)** — **not** in `performance_data` (its rows there are zero). The
  cost is a per-sale ad fee in `accounting.ebay_order_expenses` (`fee_type IN (AD_FEE,
  PREMIUM_AD_FEES)`), attributed to the SKU by splitting each order's fee across its lines by line value.

**Ad Spend = CPC spend + CPS ad fee. Ad Sales = CPC attributed sales + CPS line revenue on ad-charged
orders.** Reading only `performance_data` was the cause of the earlier empty ad columns.

## 5. Data model / joins (live Ledsone PostgreSQL — normalised domain schemas)
Correct DB = the normalised domain-schema database (via the **Ledsone Database MCP**), **not** the
`public.*` denormalised layer (a different DB, returns nothing here).

- **Returns:** `customer_service.ebay_returns`. Two `DISTINCT ON (return_id)` CTEs — one on `id ASC`
  (earliest row = reason + `seller_refund_amount`), one on `id DESC` (newest row = latest `to_state`).
- **SKU bridge:** `order_management.order_item_info` on `item_transaction_id = ebay_returns.transaction_id`
  (**never** `item_id` — 1,331 `item_id`s map to multiple variants).
- **Account name:** `order_management.sub_source.map_name`.
- **eBay orders:** `order_management.orders` ⋈ `sub_source` ⋈ `source (source_name='EBAY')`, period on
  `order_date`. Line value = `COALESCE(real_price,item_price)::numeric × COALESCE(real_qty,item_quantity)::numeric`.
- **Fees:** `accounting.ebay_order_expenses`, keyed on `order_id::text` = the **eBay order reference**
  (`orders.order_id`, varchar) — **not** internal `orders.id`.
- **CPC ads:** `ebay_campaigns.performance_data` ⋈ `campaigns` (`campaign_type='ON_SITE'`), date-bound;
  listing→variant spread via `listings.ebay_listings`.
- **Stock:** `inventory.products` ⋈ `inventory.local_inventory_current_stock_location_wise`.
- **Negative feedback:** `customer_service.ebay_orders_customer_feedbacks` via the same `transaction_id`
  bridge, `type='Negative'`, date-bound.

## 6. Intentional blanks & caveats (real, not errors)
- **Return Rate** blank on ~17 SKUs = zero period orders (item bought in an earlier period). Verified.
- **ACOS** blank / **ROAS** blank = no ad-attributed sales / no ad spend for that SKU. Verified.
- Count / £ columns DO show real `0` / `£0.00` — do **not** format zeros as dashes (that made columns
  look empty).
- **Return Cost = £0** on some SKUs = no matching fee row upstream (~65% fee coverage) — a data
  limitation, not a bug.
- **CPS attribution** (per-order fee → per-SKU by line value) is a reasonable split, not an exact
  eBay-reported figure.
- **Currency is mixed** — GBP (UK) + EUR (DE), **not FX-normalised**.
- **Return Rate can exceed 100%** when a SKU has period returns but few/zero period orders.

## 7. Acceptance criteria (June 2026 — must match the reference file)
- **144** SKU rows; **19** columns in the exact order of §3.
- TOTAL row: **153** returns · blended return rate **17.7%** · Refund **£2,937.37** · Return Cost
  **£869.39** · Ad Spend **£1,387.96** · Ad Sales **£9,343.63** · ACOS **14.9%** · ROAS **6.73x**.
- Return-Reason Breakdown sums to **153** (Wrong Size 47 / Ordered Wrong Item 28 / Not as Described 21 / …).
- Zero recalc errors.

## 8. Build & re-run procedure
1. Run **statement 1** of the SQL via the Ledsone DB MCP → `main.tsv` (tab-separated, no header, NULLs
   as empty string). Friendly Account, mapped reason labels and `#n` rank are produced by the SQL — do
   not post-process.
2. Run **statement 2** → `reason_breakdown.tsv` (`Return Reason<TAB>Returns<TAB>Pct`).
3. `pip install openpyxl`; `python build_dashboard.py main.tsv reason_breakdown.tsv <output>.xlsx`.
4. **Recalculate** with LibreOffice headless (openpyxl writes formulas with no cached values); confirm
   `total_errors == 0`.
5. **Diff against the reference** figures in §7 before acceptance.
- **Another month:** change the six dates at the top of the SQL (reporting / last month / last year) and
  `PERIOD_LABEL` in `build_dashboard.py`. Stock is always a live snapshot.

## 9. What is NOT done yet (from this workbench)
- No live DB query has been executed here; the imported `eBay_Return_Analysis_June2026.xlsx` is the
  **reference** produced in the prior chat session, kept as the diff target — **not** a workbench-produced
  deliverable.
- Nothing has been published to `tech_team_outputs.ph_task`.
- `REQ-14` / `ERA` are working defaults pending owner confirmation.
- Reviewer (Sajeesan, Tamil Selvan) and business (Thinesh) sign-offs are pending.
