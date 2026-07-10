# ⚠️ CRITICAL (added 2026-07-10): vendor_sales is INCOMPLETE for 2026

The team's KPI sheet is backed by Amazon's own "Ordered Product Sales" report (tab `AMZ_2026`).
Cross-check found **189 of 1,254 "zero-sale" ASINs actually sold £12,394.76 in Jun/Jul 2026**
per Amazon — sales our postgres `vendor_sales` table is MISSING. Seller (FBA/FBM) ASINs match
our DB exactly; the gap is entirely on **vendor (1P)** ASINs (e.g. B093T3TR2Y: Amazon £2,659, our DB £0).

**Consequence:** the zero-sale report built on postgres alone is OVER-inclusive.
**Corrected report = 1,065** (zero in BOTH postgres AND Amazon's AMZ_2026). Files:
`ZSFO_Utharsika_report_CORRECTED.xlsx` + `ZSFO_Utharsika_dashboard.html`.

**Two fixes needed:**
1. Re-sync `vendor_sales` (and verify `order_transaction`) so the DB matches Amazon's report.
2. Until then, use `AMZ_2026` (June+July achieved sales) as the sales source of truth for the zero-sale filter.

Note: the KPI-sheet's *Utharsika tab* cached values are stale IMPORTRANGE (unreliable in a
downloaded xlsx). The `AMZ_2026`/`AMZ_2025` source tabs hold the real data.

---

# ZSFO Project — Handoff for Claude Code

> Drop this file into the repo. It is self-contained: a fresh session can continue from here.

## 1. What we're building
The **Zero Sales Full Optimization (ZSFO)** weekly report.
Spec: `utharsika_task.xlsx`, task `PH-2026-07-UTHAR04`, developer **abiraj**, requirement **REQ-08-D01**.

Every **Monday**, list the Amazon-UK ASINs that had **zero sales in the last completed 30 days**, with the diagnostics needed to find *why* (traffic + stock), so listings can be optimised.

**Scope: exclusively Utharsika's ASINs** → `user_name = 'utharsika'`.
Current run (run_date 2026-07-10): **1,719 Amazon-UK ASINs → 1,250 zero-sale** (the report).

## 2. Database (Postgres — MCP connector name: `Postgresql`)
All read-only. Key tables/columns:

| Table | Use | Key filters |
|---|---|---|
| `order_transaction` | FBA+FBM sales | `source_name='AMAZON'`, `market_place='UK'`, `order_status='Completed'`; `asin`, `quantity`, `order_date` |
| `vendor_sales` | Amazon Vendor/1P sales | `asin`, `ordered_units`, `start_time`/`end_time` (**daily, but 712 rows span multiple days**), **always UK/GBP**, `user_name` |
| `traffic_data` | impressions/clicks/conversion | `ref_id`=ASIN, `which_channel=1`, `market_place='UK'`, `date`, `user_name` |
| `listing_data` | ASIN→SKU bridge + FBM qty | `ref_id`, `sku`, `mapped_sku`, `quantity`, `fulfilment`, `wrong_sku=0`, `is_parent=0` |
| `location_wise_inv_stock` | UK warehouse stock | `sku`, `stock`, `location='UK'` |

### ⚠️ Two data gotchas (already solved — keep them)
1. **Utharsika's `listing_data` rows have `which_channel = NULL`** (not 1). Do **NOT** filter `which_channel=1` on listing_data for her — match on `ref_id + market_place='UK' + wrong_sku=0 + is_parent=0` only.
2. **`vendor_sales` periods can span days** — match by **overlap**: `NOT (end_time::date < ws OR start_time::date > we)`, not `start_time` alone. (0 impact on Utharsika, but correct for other users.)

## 3. Locked business rules (confirmed by dev)
- **Zero-sale** = 0 units in window across **FBA + FBM (`order_transaction`) AND Vendor (`vendor_sales`)**.
- **Window** = `[run_date − 30 days, run_date − 1 day]`; **current day excluded**. (Spec example: run Mon 3 Aug → 4 Jul–2 Aug.)
- **Marketplace** = Amazon **UK** only.
- **"Last Month Sales"** column = 30-day-window units = **0** (proof of qualification; do not use previous calendar month).
- **Conversion Rate** = `conversion / clicks`.
- **UK Warehouse stock** = `location_wise_inv_stock`, `location='UK'`, `SUM(stock)`, **exact SKU match** (never LIKE).
- **Amazon FBM Stock** = `listing_data.quantity` where `fulfilment='merchant'` AND **not AM-family (FBA)**. FBA marker = last `_`-segment of `sku` starts with `AM` (AMD, AMN…).
- **SKU resolution** = `mapped_sku` if present (use as-is), else clean `sku`: strip `-IDE/-CA/-IFR/-NL`, then `__seg`, then `_seg`; exclude `amzn.gr.*`.

## 4. Report columns (match the task sheet)
`ASIN | SKU | Last Month Sales (=0) | Local UK Warehouse stock | Amazon FBM Stock | Impressions | Clicks | Conversion Rate`
Added helpers: `Root-cause hint`, and week-by-week impressions/clicks (5 buckets: 10–16 Jun, 17–23, 24–30, 1–7 Jul, 8–9 Jul).

## 5. Canonical query (Utharsika, corrected — vendor OVERLAP, NULL-channel bridge)
```sql
WITH bounds AS (SELECT DATE :run_date AS run_date,
       (DATE :run_date - INTERVAL '30 days')::date AS ws,
       (DATE :run_date - INTERVAL '1 day')::date AS we),
uthar AS (SELECT DISTINCT ref_id AS asin FROM public.traffic_data
          WHERE which_channel=1 AND market_place='UK' AND user_name='utharsika'),
listings AS (   -- NOTE: no which_channel filter (hers are NULL)
  SELECT ld.ref_id AS asin, ld.sku, ld.mapped_sku, ld.fulfilment, ld.quantity,
         regexp_replace(trim(ld.sku),'(-IDE|-CA|-IFR|-NL)$','') AS sku_nomkt
  FROM public.listing_data ld JOIN uthar u ON u.asin=ld.ref_id
  WHERE ld.market_place='UK' AND ld.wrong_sku=0 AND ld.is_parent=0
    AND COALESCE(ld.sku,'') NOT LIKE 'amzn.gr.%'),
resolved AS (SELECT l.*,
    (substring(l.sku_nomkt from '_([A-Za-z0-9]+)$') ILIKE 'AM%') AS is_fba,
    CASE WHEN COALESCE(l.mapped_sku,'')<>'' THEN trim(l.mapped_sku)
         ELSE regexp_replace(regexp_replace(l.sku_nomkt,'__[^_]*$',''),'_[^_]*$','') END AS base_sku
  FROM listings l),
sold AS (SELECT ot.asin, SUM(ot.quantity) u FROM public.order_transaction ot, bounds b
  WHERE ot.source_name='AMAZON' AND ot.market_place='UK' AND ot.order_status='Completed'
    AND ot.order_date::date BETWEEN b.ws AND b.we GROUP BY ot.asin),
vendor AS (SELECT vs.asin, SUM(vs.ordered_units) vu FROM public.vendor_sales vs, bounds b
  WHERE NOT (vs.end_time::date < b.ws OR vs.start_time::date > b.we) GROUP BY vs.asin), -- OVERLAP
tw AS (SELECT td.ref_id AS asin, SUM(td.impression) impr, SUM(td.click) clk, SUM(td.conversion) conv
  FROM public.traffic_data td, bounds b
  WHERE td.which_channel=1 AND td.market_place='UK' AND td.date BETWEEN b.ws AND b.we GROUP BY td.ref_id),
fbm AS (SELECT asin, SUM(COALESCE(quantity,0)) fbm FROM resolved
        WHERE fulfilment='merchant' AND is_fba=false GROUP BY asin),
uk AS (SELECT r.asin, SUM(COALESCE(s.stock,0)) uk FROM (SELECT DISTINCT asin,base_sku FROM resolved) r
       JOIN public.location_wise_inv_stock s ON s.sku=r.base_sku AND s.location='UK' GROUP BY r.asin),
sd AS (SELECT asin, string_agg(DISTINCT base_sku,' + ') sku FROM resolved GROUP BY asin)
SELECT l.asin AS "ASIN", sd.sku AS "SKU", 0 AS "Last Month Sales",
  COALESCE(uk.uk,0) AS "Local UK Warehouse stock",
  COALESCE(fbm.fbm,0) AS "Amazon FBM Stock",
  COALESCE(tw.impr,0) AS "Impressions", COALESCE(tw.clk,0) AS "Clicks",
  ROUND(COALESCE(tw.conv,0)/NULLIF(tw.clk,0),4) AS "Conversion Rate"
FROM uthar l
LEFT JOIN sold sw ON sw.asin=l.asin
LEFT JOIN vendor v ON v.asin=l.asin
LEFT JOIN tw ON tw.asin=l.asin
LEFT JOIN fbm ON fbm.asin=l.asin
LEFT JOIN uk ON uk.asin=l.asin
LEFT JOIN sd ON sd.asin=l.asin
WHERE COALESCE(sw.u,0)=0 AND COALESCE(v.vu,0)=0     -- zero across FBA/FBM AND vendor
ORDER BY "Impressions" DESC, l.asin;
```
Set `:run_date` to the Monday. Expected for 2026-07-10: **1,250 rows**.

## 6. Reconciliation numbers (for sanity checks)
- Utharsika Amazon-UK ASINs: **1,719** → zero-sale **1,250**, sold 469, in vendor 329.
- Full catalogue (`which_channel=1`, NOT Utharsika): 30,782 listings → 28,318 zero-sale (different population — don't confuse).
- Vendor in-window sellers: 169 total, 34 are Utharsika's — all correctly excluded (0 false positives).

## 7. Files already produced (attach or reference)
- `PROJECT_CONTEXT.md` (this file)
- `ZSFO_report.sql` — master query (⚠️ still uses start_time vendor logic — replace with §5 overlap version)
- `ZSFO_Utharsika_dashboard.html` — full-screen dashboard (1,250 rows, week-by-week sparklines, root-cause filters)
- `Utharsika_Amazon_UK_ASINs.xlsx` — 1,719 ASINs + zero-sale flags
- `Utharsika_all_ASINs.xlsx` — all 1,907 IDs across marketplaces/channels
- `ZSFO_VERIFICATION_PACK.md` — independent cross-check queries (hand to a 2nd dev)
- `2026-07-10_abiraj_REQ-zsfo_REQ-08-D01.md` — requirement doc

## 8. Open TODOs
1. **Apply §5 vendor-overlap fix** to `ZSFO_report.sql` (currently start_time only).
2. **Add "Last vendor sale date" column** to report/dashboard (prevents lifetime-vs-window confusion the user hit).
3. **Parameterise `run_date`** + schedule the Monday run.
4. **Confirm with Satheesvaran** any remaining rule edge cases (order-status set, universe definition).
5. Decide final deliverable format for the user: **HTML dashboard** vs **xlsx** (both exist).

## 9. Status
Logic verified 3 ways (window matches spec example; 0/1,250 have any window sales incl. vendor; end-to-end trace of top ASIN matches source). The "vendor shows wrong data" report was a **period mismatch** (lifetime vendor sales vs 30-day window), not a bug — report is correct.
