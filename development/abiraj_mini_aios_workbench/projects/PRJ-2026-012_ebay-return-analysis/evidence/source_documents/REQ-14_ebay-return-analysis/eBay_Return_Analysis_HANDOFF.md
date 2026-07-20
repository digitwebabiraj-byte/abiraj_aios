# eBay Return Analysis Dashboard — Task Handoff

**Deliverable:** a per-SKU eBay returns dashboard (Excel) matching the task-sheet
mockup, populated from the live Ledsone PostgreSQL database.
**Reporting period built:** June 2026. **Grain:** one row per variant SKU that had
at least one eBay return in the period.
**Files:** `eBay_Return_Analysis_June2026.xlsx` (deliverable) ·
`ebay_return_analysis.sql` (the query) · this handoff.

---

## 1. Scope & parameters (agreed)

| Parameter | Decision |
|---|---|
| Channel | **eBay only** — all eBay accounts and marketplaces (UK, DE). |
| Period | **June 2026** (`2026-06-01` → `2026-07-01`). Return Rate = period returns ÷ period units ordered. |
| Return Cost | **eBay refund fees + selling fees** (REFUND + FINAL_VALUE_FEE on returned orders). |
| Ad columns | Single **Ad Spend / Ad Sales / ACOS / ROAS** set (exact task-sheet layout), combining CPC + CPS. |
| Last Month / Last Year | May 2026 / June 2025 (same month prior year). |

---

## 2. Output columns (exactly the task sheet, 19)

`SKU · Product Title · Account · Orders · Returns · Return Rate ·
Last Month Returns · Last Year Returns · Refund (£) · Return Cost (£) ·
Main Return Reason · Return Rank · Negative Feedback · Open Cases · Stock ·
Ad Spend (£) · Ad Sales (£) · ACOS · ROAS`

Plus, on the same sheet, the **Return-Reason Breakdown** table, the **Filter
Options** block, and the **Before/After efficiency** table — as in the mockup.

---

## 3. Data sources & column derivation

Correct DB = the normalised domain-schema database (`mcp.ledsone.co.uk`), **not**
the `public.*` denormalised layer (that belongs to a different DB and returns nothing here).

| Column | Source & logic |
|---|---|
| SKU / Product Title | `ebay_returns.transaction_id` → `order_management.order_item_info.item_transaction_id` → `real_sku` / `item_title`. **100% match** on all returns; gives the exact variant. |
| Account | `ebay_returns.sub_source` → `order_management.sub_source.map_name` (staff-facing name; usernames are random strings). |
| Orders | Units sold on eBay in the period per SKU: `orders` ⋈ `sub_source` ⋈ `source (=EBAY)` ⋈ `order_item_info`. `item_quantity` is **TEXT** → cast to numeric. |
| Returns | Distinct `return_id` in the period (case rows where `reason` is populated). |
| Return Rate | Returns ÷ Orders. Blank where period orders = 0. |
| Last Month / Last Year Returns | Same logic, May 2026 / June 2025 windows. |
| Refund (£) | Sum `seller_refund_amount` for the SKU's period returns. |
| Return Cost (£) | `accounting.ebay_order_expenses` on returned orders: `transaction_type='REFUND'` + `fee_type IN (FINAL_VALUE_FEE, FINAL_VALUE_FEE_FIXED_PER_ORDER)`. |
| Main Return Reason | Most frequent reason in the period; eBay codes mapped to readable labels. |
| Return Rank | Rank by period return count (ties broken by refund £). |
| Negative Feedback | `customer_service.ebay_orders_customer_feedbacks` `type='Negative'` in period, mapped to SKU via `transaction_id`. |
| Open Cases | Period returns whose latest `to_state` ≠ `CLOSED`. |
| Stock | Live snapshot: `inventory.products.sku` → `local_inventory_current_stock_location_wise`. Not period-bound. |
| Ad Spend / Ad Sales | **CPC + CPS combined** — see §4. |
| ACOS / ROAS | ACOS = Spend ÷ Sales; ROAS = Sales ÷ Spend. Blank where a denominator is 0. |

---

## 4. The advertising gotcha (important)

eBay has two ad models and they live in **different tables**:

- **CPC / Advanced (`ON_SITE`)** — recorded in `ebay_campaigns.performance_data`.
  Note: every value column there is sourced from `cpc_*` fields, so this table is
  **CPC-only**. Join `performance_data.ebay_listing_id` = eBay `item_id` →
  `listings.ebay_listings.item_id` (`wrong_sku=0`) → `sku`; spend/sales are per
  listing, so they're **spread across the listing's variant SKUs**.
- **CPS / Standard (`COST_PER_SALE`)** — **not** in `performance_data` (its rows
  there are all zero). The cost is charged per sale as an ad fee in
  `accounting.ebay_order_expenses` (`fee_type IN (AD_FEE, PREMIUM_AD_FEES)`).
  Attributed to the SKU by splitting each order's fee across its lines by line value.

**Ad Spend = CPC spend + CPS ad fee. Ad Sales = CPC attributed sales + CPS line
revenue on ad-charged orders.** If you only read `performance_data`, the CPS half
is silently missing (this was the cause of the earlier empty ad columns).

---

## 5. Assumptions & caveats

- **CPS attribution** (per-order fee → per-SKU) is a reasonable split, not an exact
  eBay-reported figure. Ad Sales for CPS ≈ the SKU's line revenue on ad-charged orders.
- **Return Cost coverage** ≈ 65% of returned orders have matching fee rows; some SKUs
  legitimately show £0.
- **Return Rate** can exceed 100% or be blank when a SKU has period returns but few/zero
  period orders (item bought earlier).
- **Currency** is mixed — GBP (UK) + EUR (DE), **not FX-normalised**.
- **Blanks that are real, not errors:** blank Return Rate = no period orders; blank
  ACOS/ROAS = zero ad spend or sales that row.

---

## 6. How to re-run for another month

1. Open `ebay_return_analysis.sql`. At the top, change the **six dates** (reporting
   period, last month, last year). They appear as `'2026-06-01'` / `'2026-07-01'` etc.
2. Run the **first statement** → the 19-column dataset. Run the **second statement**
   (bottom of the file) → the return-reason breakdown table.
3. Drop the results into the workbook (or regenerate it). Stock is always "now".

Sanity check for June 2026: **144 SKU rows · 153 returns · £2,937.37 refunds ·
£1,387.96 ad spend · £9,343.63 ad sales (14.9% ACOS, 6.73x ROAS)**, blended return
rate 17.7%.

---

## 7. Key pitfalls to avoid (for whoever picks this up)

- **Don't join returns to SKU on `item_id`** — 1,331 return `item_id`s map to multiple
  variants. Use `transaction_id` → `order_item_info`.
- **`item_quantity` / `real_qty` / prices are TEXT** — cast with `NULLIF(x,'')::numeric`.
- **`ebay_order_expenses.order_id` = the eBay order reference** (`orders.order_id`,
  varchar), **not** the internal `orders.id`.
- **Case fields** (reason, `seller_refund_amount`) live only on the **earliest** row
  per `return_id`; latest **state** is the **newest** row. Hence the two `DISTINCT ON`.
- **`performance_data` is CPC-only** — see §4.
