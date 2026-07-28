# eBay PPC Product Pause Automation (EPPA) — Reusable Methods (Capability Extract)

> Reusable, generalisable techniques from this project (`PRJ-2026-013`, code `eppa`).
> One line: a rule engine that recommends which LEDSone eBay UK Promoted Listings to
> pause — out of stock, low stock, above ACOS ceiling, or clicks-without-sales — and how
> much monthly spend that recovers. **It recommends; a human executes in Seller Hub.**
> **Sources:** `SYSTEM_REFERENCE.md`, `PROJECT_HOME.md`, `automation/AUTOMATION_README.md`.

## Reusable rules / methods

### 1. Ordered pause rule engine — first match wins, availability beats performance
Evaluate ordered gates per listing, top to bottom; the first match wins and later gates are
not consulted. A listing that cannot be bought is paused before any efficiency rule runs.
- **Gate 0 — State check:** if the campaign/listing is OFF, it is `ALREADY OFF` and not evaluated.
- **Gate 1 — Stock:** `units < stock_floor (5)` → PAUSE. `units=0` = "Out of stock" (always High);
  `0 < units < 5` = "Low stock".
- **Gate 2 — Rule 1 (high ACOS):** scope `30D orders > 0`; `30D ACOS >= 40%` → PAUSE;
  rescue `7D ACOS < 20%` (improving trend) → do not pause.
- **Gate 3 — Rule 2 (clicks without sales):** scope `14D orders = 0`; `14D clicks >= 20` → PAUSE;
  rescue `14D spend < £2.50` (cheap organic-ranking clicks) → do not pause.
- **Priority (paused rows only):** stock+units=0 → High; 30D spend ≥40 → High; ≥15 → Medium; else Low.
*Reusable pattern for any "should we stop spending on X" queue.*

### 2. Thresholds are configuration, never code
All five operating values (stock floor 5, ACOS ceiling 40%, ACOS rescue 20%, clicks min 20,
spend floor £2.50) stay editable inputs from the source's `Pause Rules` sheet — never hardcoded.

### 3. Anchor windows to the data, not the clock
Window anchor = `MAX(date)` of the loaded PPC data, not `CURRENT_DATE` — otherwise a late ETL
run yields a short, ragged final day.

### 4. Source from the RAW `ledsone` DB, not the warehouse
Build against the raw `ledsone` DB (`mcp.ledsone.co.uk/mcp`), not the warehouse. It is fresher
(hourly sync), carries listing price, and is the **only** source exposing SMART campaigns at
listing grain — the warehouse silently drops 179 SMART listings / £751.09 per 30D. Scope key:
`campaigns.marketplace_id='EBAY_GB'` + `sub_source=1` + `deleted=false`.

### 5. Collapse guard, not just an absolute floor
Guard each refresh against a gradual half-emptying feed (e.g. 2,166→400 listings) by comparing to
the last good run (`MAX_DROP` 40%), on top of an absolute `MIN_CAMPAIGNS` floor. Invented here and
backported to T7, EPC, EBPD, ERA.

## Gotchas / traps

- **CPS logs £0 spend/sales:** COST_PER_SALE campaigns record £0 in `performance_data` (all money
  columns are `cpc_*`); cost-per-sale fees land in `accounting`. Rule 1 is uncomputable and Rule 2
  is permanently rescued — CPS is out of scope until money is sourced elsewhere.
- **~89% multi-SKU listings:** 89.2% of listings map to >1 SKU (max 245) even after `all_list=1`,
  so a campaign rarely maps to one product — "units in stock per listing" needs an explicit rule
  (Decision C closed as SUM-across-variants: out of stock only when every variant is zero).
- **`ebay_listings.status` is 99.4% NULL** and self-contradictory — never use it as a live/ended
  filter; use `is_ended` for ended, campaign state for on/off.
- **Unbridged ≠ 0 stock:** a SKU that fails to bridge is *unknown*, not out of stock — render
  **NO DATA**, never 0. A 0 would auto-pause a possibly well-stocked listing.
- **`all_list = 1` mandatory** on every listing-table query, else parent variation containers
  inflate SKU-level results. Also **never** use `campaigns.state` (undecoded numeric) — use
  `campaigns.campaign_status`.

## Key sources (schema.table.column)

- Listing id: `performance_data.ebay_listing_id`
- Campaign id/name/state: `campaigns.campaign_id` / `.campaign_name` / `.campaign_status`
- Type / class: `campaigns.campaign_target_type` (MANUAL/SMART) · `campaigns.campaign_type` (ON_SITE/COST_PER_SALE/OFF_SITE)
- Spend / sales / orders / clicks (per window): `SUM(performance_data.ad_fees_payout_currency)` ·
  `SUM(performance_data.sale_amount_payout_currency)` · `SUM(performance_data.attributed_sales)` ·
  `SUM(performance_data.clicks)`; ACOS = `ad_fees / sale_amount * 100` (derived, never stored)
- Listing price: `listings.ebay_listings.price` (+`currency`), `all_list=1`
- Units in stock: `ebay_listings.sku` (`all_list=1`, `wrong_sku=0`) → `inventory.products.id` →
  `inventory.local_inventory_current_stock_location_wise` (`warehouse_location='UK'`)

## Automation pattern

- Task `EPPA_Weekly_Pause_Report`, **Mondays 11:00**, anchored on the most recent complete PPC day.
- Reads `ledsone` READ-ONLY; writes **one** row to `tech_team_outputs.ph_task` (`eppa`).
- Fail-closed gates before any disk/`ph_task` write: missing credential, 0 campaigns,
  below `MIN_CAMPAIGNS` (20), collapse vs last good run (`MAX_DROP` 40%), total 30D spend = 0,
  md5 of stored row vs file. On failure a Desktop alert fires and the previous report stays live.
- Credentials from the global store; `version_status` deliberately not asserted (recipients marking
  their own task `completed` is normal workflow).
- First live run 2026-07-21: 45 campaigns · 15 paused · 8 stock-flagged · £1,403.54 spend-at-risk,
  published as ph_task id 405. Same five-stage pattern as PRJ-2026-008/010/011/012.
