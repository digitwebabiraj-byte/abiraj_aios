# Source audit + AIOS-rules correction — REQ-12-D01 (2026-07-16, read-only)

The confirmed rule named its sources only as "the approved Amazon/website PostgreSQL source." This audit
identified the real objects, and — critically — corrected a **matching layer that had been built wrong**
before the AIOS knowledge base was consulted.

## 1. Sources identified (ledsone DB, Ledsone-db-mcp, read-only, refreshed 2026-07-15)
| Confirmed-rule name | Real object | Notes |
|---|---|---|
| Approved Amazon source | `listings.amazon_listings`, `site` UK/Germany, `sub_source=8` ('amazon Ledsone') | Thinesh Q3. Lowest price on a duplicate (Q1). 130,296 rows / 124,750 priced |
| Approved website source | `listings.shopify_listings`, `sub_source=104` ('ledsone', UK) / `108` ('ledsone-de', DE) | Thinesh confirmed = "the website". ⚠ `currency` column EMPTY on all rows → `website_currency` derived from site, not read |
| Current eBay price | `listings.ebay_listings`, `site` UK/Germany | Price **per variant row** (298,383/298,386 priced) — resolves the REQ-11 item-K multi-variant worry favourably: one row per SKU already has its own price |
| SKU normalisation | `inventory.products` (10,083 ENC → `sku_original`), `inventory.product_pk` (28 pack decodes) | Both live and usable |

## 2. Existing-asset sweep — BOTH databases named (the REQ-11 lesson)
- **ledsone** — no price-checker asset; the `listings` schema is the price data.
- **order_management_copy** (Postgres MCP, host 10.8.0.3) — a pricing pilot exists,
  `staging_ai.pricing_safe_*` + `v_ph_daily_action_center_v1`, but it is a **21-SKU / 63-row pilot** with
  `target_price` all NULL / `DATA_GAP_NO_TARGET_SOURCE`, not a portfolio price checker. **Not a
  duplicate.** ⚠ It **does** carry a live pricing status vocabulary
  (`staging_ai.pricing_safe_status_reason_catalog_v1`, 8 values incl. `PRICE_TOO_LOW`) — the Q8 collision;
  route to **Sajeesan** before adding the two new status values.
- ⚠ Note: `order_management_copy` was earlier used as a data *source*, which the owner questioned; its
  only legitimate role here is the **`ph_task` publish target** and this existing-asset check.

## 3. ⚠ THE CORRECTION — the matching layer was built wrong, then fixed against the AIOS KB
The first builds (v1–v2, in the daily-work scratch) ignored the AIOS knowledge base and got the SKU
matching wrong. Reading `Ledsone-aios-mcp` (`docs.ledsone.co.uk`) surfaced four documented rules that
change the result materially:

| AIOS rule (doc) | What was wrong | Fix | Impact |
|---|---|---|---|
| `ebay-listing-sku-filter.md` — **`all_list=1` always** | used `wrong_sku=0 AND is_child=1 AND is_ended=0` | `all_list=1` | **+6,392 UK rows** were being silently dropped |
| `sku-format-rules.md` — Amazon `_` marketplace suffix | matched raw Amazon SKUs | strip from first `_` | **12,461** Amazon SKUs were wrongly not matching |
| `sku-format-rules.md` — **ENC** shortened SKUs | treated `ENC…` as plain | resolve via `inventory.products.sku_original` | **32,474** eBay ENC SKUs were mis-handled |
| `sku-format-rules.md` — **`<char>PK`** pack qty | ignored pack quantity in bundle sums | decode via `inventory.product_pk`, multiply | bundle sums were quantity-blind |

Direct Amazon matches rose **30,039 → 36,656 (+22%)** after the fix. **Lesson (promote): read the AIOS
knowledge base BEFORE building — Existing-Asset-First applies to documented rules, not just data.**

## 4. ⚠ SHIPPING-BLIND — the standing caveat (AIOS `business/rules/cross-platform-pricing-markup.md`)
The KB documents the company markup policy (website base · eBay = base ×1.10 · Amazon = base ×1.20) and
**explicitly warns**: *"Any future 'expected vs actual price' check … must incorporate shipping price per
channel/marketplace, not just item price, or it will misreport correctly-priced listings as violations.
Shipping price data source not yet identified — check `amazon_listings.shipping_id` (FK, not yet
documented)…"* This report compares **item price only**. ⇒ **Status / Priority / Action are
shipping-blind — use for ranking, not repricing.** An earlier "VAT/postage artifact" hypothesis was
**refuted** (median drift from target +0.98%), but the KB's shipping caveat stands and is the real reason
Status is not sign-off-ready. Note too: Thinesh's Amazon ×0.90 = base ×**1.08**, vs the documented eBay
target of base ×**1.10** — a ~2% difference to reconcile with him.

## 5. Grain / currency
One row per eBay listing SKU (`item_id` + `sku`). UK = £, Germany = €; **no FX applied** (Q7 said "same
rules"; no rate given) — German £-denominated tolerances are applied as EUR. If Thinesh meant £ tolerances
against EUR prices, every German row is wrong.
