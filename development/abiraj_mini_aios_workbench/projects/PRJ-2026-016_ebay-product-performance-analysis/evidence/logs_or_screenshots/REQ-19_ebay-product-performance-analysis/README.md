# Evidence — logs & audits · REQ-19 eBay Product Performance Analysis

## What lands here

The read-only data-availability sweep behind every source claim in `SYSTEM_REFERENCE.md`.

## Audit summary (run live 2026-07-27, warehouse `order_management_copy`; `ledsone` was DOWN)

- **Universe:** eBay `which_channel=2, all_list=1, wrong_sku=0, is_child=1`, UK+DE → **116,614 child
  rows / 9,781 distinct item_ids** across 15 accounts. Report grain = item_id (9,781 rows).
- **Verdict: AMBER** — 28 of 35 columns sourceable warehouse-only; 7 `NO DATA`.
- **Cost Price:** swept every schema for `cost/cogs/purchase/landed`. `development.sku_cogs` is
  **EMPTY (0 rows)**; `development.channel_vat_log` EMPTY; only `slow_stock_snapshot` cost (8.7%).
  `staging_ai.sku_selling_cost_rates_v1` gives selling-cost %, not product COGS. ⇒ profit block `NO DATA`.
- **Brand:** exists in `staging_ai.salesprot_account_brand_map_v1` (by account) — pinned into the
  builder because `temp_user` can't read `staging_ai`.
- **Shipping:** `order_shipping_billing_detail.carrier_charge` — 98% of eBay orders have it.
- **Category name:** `order_transaction.category_name` (~38% for eBay) → falls back to `category_id`.
- **Title:** `inv_products.title` via SKU bridge (86%).
- **Traffic:** `traffic_data` (which_channel=2) — impression/click/conversion; eBay reports one
  click/view metric (Views=Clicks). Feed has known day-gaps (26 Jun, 29 Jun–1 Jul, 18 Jul).
- **Watch Count:** no `watch` column in any table (eBay Trading API only).
- **PPC Campaign:** `ppc.record_name` exists but the listing→campaign link resolves only ~29% in the
  warehouse (broken hierarchy — the reason EPPA used ledsone).
- **Reconciliation:** revenue on active listings UK £54,286 / DE €25,341 (≈93–94% of the full eBay
  window total; remainder = sales from now-inactive listings).

## Still to add
- A dated, saved copy of the full audit transcript (`2026-07-27_data_availability_audit.md`).
- Connectivity note: MCP `ledsone` (`10.8.0.5:5432`) and direct (`207.148.78.148:5432`) both timed out.
