# Handoff: Weekly SKU Performance Check — Thuwaraka (Table 7)

## Project Summary
Automate a recurring weekly report: **Table 7 — Weekly SKU Performance Check | All Platforms UK (Amazon · eBay · B&Q)**, owned by **Thuwaraka**. The report groups all of Thuwaraka's UK listings by SKU and shows a rolling 7-day order count per platform, flagging any listing with zero orders.

Reference file (original manual template): `WEEKLY_SKU_PERFORMANCE_CHECK_____All_Platforms_UK___Amazon___eBay___B_Q__-_Frequency_-_Weekly_-Thuwaraka.xlsx`

## Business Rule
- **Runs every Thursday.**
- **Report window** = rolling 7 days ending the day *before* the run date (run Thu → window is last Thu through last Wed).
- Example: run date 09-Jul-2026 → window = **02-Jul-2026 to 08-Jul-2026**.

## Data Source
Postgres tables (see full schemas in project files `TABLE_order_transaction.md` and `TABLE_listing_data.md`):

- `public.order_transaction` — orders, one row per line item
  - Key columns: `sku`, `asin`, `item_id`, `source_name`, `ss_name`, `market_place`, `order_status`, `order_date`, `order_item_info`, `user_name`
  - `user_name` = portfolio holder. **Note actual DB spelling is `thuwaraga`**, not "thuwaraka" — always filter case-insensitively: `LOWER("user_name") = LOWER('thuwaraga')`.
  - `source_name` values: `AMAZON`, `EBAY`, `B&Q` (also `SHOPIFY`, `WAYFAIR` — exclude for this report).
  - B&Q has **no ASIN/item_id**, only `sku` — must be matched/grouped on `sku` directly.
  - Orders counted as: `order_status = 'Completed'` AND `COUNT(DISTINCT order_item_info)`.

- `public.listing_data` — SKU/ASIN registry, used to resolve base SKU → SKU family and pull product titles
  - Key columns: `ref_id`, `sku`, `mapped_sku`, `which_channel`, `market_place`, `sub_source_name`, `wrong_sku`
  - Always filter `wrong_sku = 0`.
  - Resolve SKU family: use `mapped_sku` if present/non-empty, else `sku`.

## Pipeline

### Step 1 — Universe: all of Thuwaraka's UK listings
```sql
SELECT DISTINCT
    "sku", "asin", "item_id", "source_name", "ss_name", "market_place"
FROM public.order_transaction
WHERE LOWER("user_name") = LOWER('thuwaraga')
  AND "market_place" = 'UK'
  AND "source_name" IN ('AMAZON','EBAY','B&Q');
```

### Step 2 — This week's order counts per listing per platform
```sql
SELECT
    COALESCE("sku", '') AS sku,
    COALESCE("asin", "item_id") AS ref_id,
    "source_name",
    "ss_name",
    COUNT(DISTINCT "order_item_info") AS orders
FROM public.order_transaction
WHERE LOWER("user_name") = LOWER('thuwaraga')
  AND "market_place" = 'UK'
  AND "order_status" = 'Completed'
  AND "order_date"::date >= :week_start
  AND "order_date"::date <= :week_end
GROUP BY sku, ref_id, "source_name", "ss_name";
```
LEFT JOIN this back onto the Step 1 universe so zero-order listings still appear as 0, not dropped.

### Step 3 — Blue "ASIN detail" rows (one per listing)
| Field | Logic |
|---|---|
| SKU/ASIN | ref_id (ASIN/item_id), or sku for B&Q |
| Row Type | ref_id |
| Product Name | from `listing_data.title` if available, else category |
| Platform | Amazon / eBay / B&Q |
| Account Name | ss_name |
| Week Start/End | window dates |
| Amazon/eBay/B&Q Orders | count per platform, 0 if none |
| TOTAL Orders | sum of the three |
| Performing? | `YES ✅` if TOTAL > 0 else `NO ❌` |
| Action Required | `—` if performing else `Investigate & fix listing` |

### Step 4 — Purple "SKU SUMMARY" rows (group by resolved base SKU)
| Field | Logic |
|---|---|
| SKU/ASIN | base SKU |
| Row Type | `SKU SUMMARY` |
| Platform | `All Platforms` |
| Amazon/eBay/B&Q/TOTAL Orders | sum across all ASINs in the SKU family |
| Performing? | `X / Y ASINs performing ⚠️`, or `✅ All performing`, or `🔴 0/Y performing` |
| Action Required | `See ASIN rows below ↓` if X < Y else `—` |

### Step 5 — Output
Purple summary row immediately followed by its blue ASIN rows, per SKU group, matching the original template's column order:

`SKU/ASIN | Row Type | Product Name | Platform | Account Name | Week Start | Week End | Amazon Orders | eBay Orders | B&Q Orders | TOTAL Orders | Performing? | Action Required`

Plus a short summary: total SKUs checked, total ASINs with 0 orders this week, list of items needing investigation.

## Open Items for Claude Code
1. **DB connection**: needs a Postgres connector/credentials configured (this chat had no live SQL execution tool — Claude Code environment should wire up `postgres:execute_sql` or equivalent).
2. **Scheduling**: needs a Thursday trigger (cron / scheduled task) that computes `week_start`/`week_end` dynamically from run date, not hardcoded.
3. **Output delivery**: decide format — write back into the original xlsx template, post to Slack/email, or generate a fresh sheet each week.
4. **Product Name resolution**: confirm whether `listing_data.title` is reliably populated for all of Thuwaraka's SKUs, or fall back to `category_name`.
5. **Verify user_name spelling**: `thuwaraga` confirmed from the project's reference user list — double-check against live DB before first run.
