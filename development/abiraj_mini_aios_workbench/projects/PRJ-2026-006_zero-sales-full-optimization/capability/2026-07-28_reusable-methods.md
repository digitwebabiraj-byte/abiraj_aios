# ZSFO — Zero Sales Full Optimization — Reusable Methods (Capability Extract)

> Reusable, generalisable techniques extracted from this project. ZSFO produces a scheduled
> **Amazon-UK zero-sale + diagnostics report** for a Portfolio Holder: which ASINs sold **0 units
> in the last completed 30 days** across all sale streams, plus the stock/traffic diagnostics that
> explain *why* each listing is dead so it can be optimised.
> **Source:** `PROJECT_HOME.md`, `SYSTEM_REFERENCE.md`, `automation/AUTOMATION_README.md`,
> `validation/REQ-08_.../2026-07-10*.md` (read 2026-07-28).

## Reusable rules / methods

### 1. Zero-sale universe = traffic-derived, per owner, per marketplace
Define the population from `traffic_data`, not the full catalogue:
`which_channel=1 AND market_place='UK' AND user_name=<PH>` (Utharsika → 1,719 ASINs, vs 30,782 for
the whole catalogue). The universe is the owner's ASINs; then subtract those with any in-window sale.

### 2. Zero-sale spans ALL sale streams (FBA + FBM **AND** Vendor/1P)
An ASIN qualifies only if it has **0 units in the window across `order_transaction` (FBA+FBM,
`order_status='Completed'`) AND `vendor_sales` (1P)**. Checking only the 3P order table falsely marks
1P-selling ASINs as dead. In this run 469 sold FBA/FBM, 34 vendor in-window (all inside the 469),
0 vendor-only false exclusions.

### 3. Vendor OVERLAP match, not start_time
`vendor_sales` rows can span multiple days. Match the window by **overlap**:
`NOT (end_time::date < ws OR start_time::date > we)` — never `start_time` alone. Neutral on this PH's
count but correct for others; retained as the rule.

### 4. NULL-channel bridge for the PH's listing rows
The PH's `listing_data` rows carry `which_channel = NULL` (not 1). Join her stock/FBM on
`ref_id + market_place='UK' + wrong_sku=0 + is_parent=0` only. Filtering `which_channel=1` returns
0 rows and silently zeroes her stock/FBM.

### 5. Derived root-cause hint (priority order)
Turn the diagnostics into one actionable label, first match wins:
1. **Out of stock** — UK warehouse stock = 0 AND FBM = 0
2. **Zero impressions** — not surfacing (impressions = 0)
3. **Impressions but 0 clicks** — image / title / price (clicks = 0)
4. **Clicks but 0 sales** — detail page / price / reviews (otherwise)

### 6. Per-ASIN vs per-product attribution — decide it explicitly
The report measures at the **individual ASIN** level; Amazon's own "Ordered Product Sales" rolls up
sibling/child ASINs sharing a SKU across marketplaces. A "dead" hero ASIN may simply have its
conversions landing on a sibling listing (listing sprawl). State which grain you report and, if
excluding siblings, choose the exclusion rule (AMZ items>0 vs £>0 swings ~120 ASINs) — an owner call.

### 7. Lifetime vs in-window fields surfaced side by side
Show **Last Amazon Sale**, **Last Vendor Sale**, **Vendor Units (lifetime)** next to the in-window
figures so a large lifetime number with an old date is never misread as an in-window sale (e.g.
`B093T3TR2Y` = 1,142 lifetime, last 2025-10-29, 0 in window).

## Gotchas / traps

- **"Missing vendor 1P data" is usually a misdiagnosis.** A handoff blamed a `vendor_sales` gap and
  prescribed a re-sync; verification found **0 of 191** were vendor — 87% were 3P **sibling-ASIN**
  sales already in the DB. `vendor_sales` had rows through 2026-07-08. Do not schedule a re-sync.
- **Stock is live-as-of-today, not a window snapshot.** `location_wise_inv_stock` has no history, so
  the 30-day window is historical but stock is current. Document it on the footer/subtitle; don't
  treat the mismatch as a defect.
- **FBM = 0 for bundle SKUs** — the FBA test `is_fba=false` dropped rows whose SKU has no `_AM`
  segment (test returns NULL). Fix: `COALESCE(is_fba,false)=false`. Corrected 885 of 1,115 June rows
  (FBM 5,215 → 34,422 units).
- **Parent-row exclusion** — some ASINs hold merchant qty on an `is_parent=1` row, excluded by
  design → FBM shows 0. Flagged, not fixed.
- **Stale `listing_data.quantity`** — some rows hold 0 while Amazon shows stock; a source-refresh
  issue, not a query bug. Won't reconcile 100% against the KPI-sheet snapshot.
- **Exact SKU match for warehouse stock** — `location='UK'`, `SUM(stock)`, exact SKU (never LIKE).

## Key sources (schema.table.column)

- `public.traffic_data` — `ref_id`(ASIN), `which_channel`, `market_place`, `user_name`, `date`,
  `impression`, `click`, `conversion` (universe + funnel; CVR = `conversion/click`).
- `public.order_transaction` — `source_name='AMAZON'`, `market_place`, `order_status='Completed'`,
  `asin`, `quantity`, `order_date` (FBA+FBM).
- `public.vendor_sales` — `asin`, `ordered_units`, `start_time`/`end_time` (overlap; always UK/GBP).
- `public.listing_data` — `ref_id`, `sku`, `mapped_sku`, `quantity`, `fulfilment`, `wrong_sku=0`,
  `is_parent=0` (which_channel NULL for the PH).
- `public.location_wise_inv_stock` — `sku`(exact), `stock`, `location='UK'`.
- Publish target: `tech_team_outputs.ph_task` (DB `order_management_copy`), **row id 167**.

## Automation pattern

- **Task `ZSFO_Monthly_ZeroSales`, monthly day 4, 09:00** (clear of the other monthly jobs).
- **Window computed from `CURRENT_DATE`**: `[run_date-30, run_date-1]`, current day excluded. The
  runner substitutes the SQL's hardcoded `run_date` + five weekly traffic-bucket literals; a guard
  aborts if any reference literal survives substitution (would silently report the wrong week).
- **Reuses signed-off assets** — reads `generate_dataset.sql`, maps its 21 columns to `data.json`
  keys, runs the existing `build_html.py` via `ZSFO_DATA`/`ZSFO_OUT` env overrides. No duplication.
- **Publish grain = REPLACE in place**: `task_id=ZSFO_utharsika_zero_sales_dashboard-V1`, one row
  (backup-first, md5-verified).
- **Fail-closed gates before any write**: PGPASSWORD set · universe floor · zero-row floor ·
  collapse-vs-last-good (40% max drop) · reference check (`--date 2026-07-10` must reproduce 1,250
  rows exactly) · mapped-key + md5 check. Exit 2 = a gate failed, nothing published, last run stays
  live; `ZSFO_ALERT_FAILED.txt` appears on Desktop until the next success.
- Proven 2026-07-24: `--date 2026-07-10` reproduced 1,250 rows exactly (universe drift +1 tolerated).
