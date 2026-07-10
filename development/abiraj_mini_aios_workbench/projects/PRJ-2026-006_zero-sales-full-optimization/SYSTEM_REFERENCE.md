# SYSTEM_REFERENCE — ZSFO (Zero Sales Full Optimization)

Complete functional detail for the ZSFO weekly report. Derived from the canonical sources
(`utharsika task.xlsx` / `PH-2026-07-UTHAR04` / `PROJECT_CONTEXT.md`) and verified against the live
`order_management_copy` DB on 2026-07-10. This is the single reference a leader or new engineer
reads to understand what the system does.

## 1. What the report is
Every **Monday**, list the **Amazon-UK ASINs belonging to Utharsika** that had **zero units sold in
the last completed 30 days** (current day excluded), with the diagnostics to explain *why* — so dead
listings can be optimised. Zero-sale is measured across **all sale streams**: FBA + FBM
(`order_transaction`) **and** Vendor/1P (`vendor_sales`).

## 2. Population (universe)
- **Utharsika's Amazon-UK ASINs**, defined from `traffic_data`:
  `which_channel=1 AND market_place='UK' AND user_name='utharsika'` → **1,719** ASINs (2026-07-10).
- This is a **different, smaller population** than the full catalogue (`listing_data which_channel=1`
  → 30,782). Do not confuse the two; the report is *only* Utharsika's.

## 3. Window
- `[run_date − 30 days, run_date − 1 day]`; **current day excluded**.
- For run_date 2026-07-10 → **2026-06-10 … 2026-07-09**.
- Spec self-check: run Mon 2026-08-03 → 2026-07-04 … 2026-08-02.

## 4. Locked business rules
| Rule | Definition |
|---|---|
| **Zero-sale** | 0 units in window across `order_transaction` (FBA+FBM) **AND** `vendor_sales` (1P). |
| **Marketplace** | Amazon **UK** only. |
| **"Last Month Sales"** | the 30-day-window units = **0** (proof of qualification; **not** previous calendar month). |
| **Conversion Rate** | `conversion / clicks`. |
| **UK Warehouse stock** | `location_wise_inv_stock`, `location='UK'`, `SUM(stock)`, **exact SKU match** (never LIKE). |
| **Amazon FBM Stock** | `listing_data.quantity` where `fulfilment='merchant'` **AND not FBA**. FBA marker = last `_`-segment of `sku` starts with `AM`. |
| **SKU resolution** | `mapped_sku` if present (as-is), else clean `sku`: strip `-IDE/-CA/-IFR/-NL`, then `__seg`, then `_seg`; exclude `amzn.gr.*`. |

## 5. The two data gotchas (must be preserved)
1. **Utharsika's `listing_data` rows have `which_channel = NULL`** (not 1). Do **NOT** filter
   `which_channel=1` on `listing_data` for her — match on
   `ref_id + market_place='UK' + wrong_sku=0 + is_parent=0` only. (Filtering `=1` returns 0 rows and
   silently zeroes her stock/FBM.)
2. **`vendor_sales` periods can span multiple days** — match by **OVERLAP**:
   `NOT (end_time::date < ws OR start_time::date > we)`, not `start_time` alone. Neutral on
   Utharsika's row count (1,250 either way) but correct for other users; retained as the rule.

## 6. Data model (read-only source objects)
| Table | Use | Key filters / columns |
|---|---|---|
| `traffic_data` | universe + funnel | `ref_id`=ASIN, `which_channel=1`, `market_place='UK'`, `user_name='utharsika'`, `date`, `impression`, `click`, `conversion` |
| `order_transaction` | FBA+FBM sales | `source_name='AMAZON'`, `market_place='UK'`, `order_status='Completed'`, `asin`, `quantity`, `order_date` |
| `vendor_sales` | Vendor/1P sales | `asin`, `ordered_units`, `start_time`/`end_time` (overlap match); always UK/GBP |
| `listing_data` | SKU bridge + FBM qty | `ref_id`, `sku`, `mapped_sku`, `quantity`, `fulfilment`, `wrong_sku=0`, `is_parent=0` (which_channel NULL for her) |
| `location_wise_inv_stock` | UK warehouse stock | `sku` (exact), `stock`, `location='UK'` |

## 7. Report columns
**Spec columns:** `ASIN · SKU · Last Month Sales (=0) · Local UK Warehouse stock · Amazon FBM Stock ·
Impressions · Clicks · Conversion Rate`.
**Added diagnostics:** `Root-cause hint · Last Amazon Sale (lifetime) · Last Vendor Sale (lifetime) ·
Vendor Units (lifetime) · week-by-week Impressions/Clicks` in 5 buckets
(10–16 Jun · 17–23 · 24–30 · 1–7 Jul · 8–9 Jul).

## 8. Root-cause hint (derived, priority order)
1. **Out of stock — no UK warehouse + no FBM** (UK stock = 0 AND FBM = 0)
2. **Zero impressions — listing not surfacing** (impressions = 0)
3. **Impressions but 0 clicks — main image / title / price** (clicks = 0)
4. **Clicks but 0 sales — detail page / price / reviews** (otherwise)

## 9. Lifetime-vs-window clarity (design decision)
The earlier "vendor shows wrong data" report was a **period mismatch**, not a bug: an ASIN can have
large *lifetime* vendor sales yet **0 in the 30-day window** (e.g. `B093T3TR2Y` = 1,142 lifetime,
last 2025-10-29, 0 in window). The report therefore surfaces **Last Vendor Sale**, **Last Amazon
Sale** and **Vendor Units (lifetime)** so a big lifetime figure with an old date is never misread as
an in-window sale.

## 10. Reconciliation (2026-07-10)
1,719 universe → 1,250 zero-sale · sold FBA/FBM 469 · vendor in-window 34 (all inside the 469) ·
0 vendor-only false exclusions · max in-window units in the report = 0/0. Independent 6-check pack
(`ZSFO_VERIFICATION_PACK.md`) = **6/6 PASS**.

## 11. Regeneration / re-run
1. Edit `sql/REQ-08_.../generate_dataset.sql`: set `run_date` (bounds CTE) and the five week-bucket
   date ranges in the `tw` CTE to the new Monday's window.
2. Run it via the Postgres MCP (read-only); save the `json_agg` result.
3. `parse` → `data.json`, then `python build_report.py` and `python build_html.py`.
4. Re-run `ZSFO_VERIFICATION_PACK.md`'s six checks; require 6/6 PASS before release.

## 12. Known limits
- Business edge cases (order-status set; universe definition) **await Satheesvaran sign-off**.
- Stock is **live as-of-today** (no historical snapshot); window is historical.
- Scheduling not wired — window is currently set in SQL, not computed from `CURRENT_DATE`.

## 13. Per-ASIN vs per-product (D02, Amazon `AMZ_2026` cross-check)
ZSFO D01 measures at the **individual ASIN, UK** level. Amazon's own "Ordered Product Sales" report
(`AMZ_2026` tab of the team KPI sheet) measures at the **product** level, rolling up all sibling/
child ASINs that share a SKU (and across marketplaces). Cross-checking D01's 1,250 against `AMZ_2026`
Jun/Jul: **191 ASINs (items>0) → corrected 1,059**; ~1,065 in the planner's file.

**Root mechanism = listing sprawl, NOT a data gap.** For those 191 (live DB): **147 (77%)** sold via
a **UK seller (3P) sibling ASIN** already in `order_transaction`, 19 via a non-UK sibling, **0 via
vendor**, 25 with no DB trace. Impressions accrue to the "hero" ASIN (e.g. `B093T3TR2Y`, 221k impr,
0 sales) while conversions land on a sibling listing (e.g. `B0CPBX49HJ`). The revised handoff's
claim of a missing **`vendor_sales`** (1P) gap is **incorrect** — `vendor_sales` holds 2026 rows
through 2026-07-08, and none of the 191 are vendor-explained.

**Decision still open (owner / Satheesvaran):**
- **Per-ASIN** ("dead listings") — keep all 1,250; add a `sells under sibling ASIN (B0…)` flag +
  `AMZ Jun/Jul` columns. Best for listing consolidation. *(recommended)*
- **Per-product** ("dead SKUs") — exclude the ~191 (the D02 view). Needs a chosen exclusion rule
  (AMZ items>0 vs £>0: 1,059 / 1,112 / 1,176) and a fix for the `AMZ_2026` June "£0 but positive
  items" anomaly.
Do **not** re-sync `vendor_sales` — it would not change the result and is outside read-only scope.
