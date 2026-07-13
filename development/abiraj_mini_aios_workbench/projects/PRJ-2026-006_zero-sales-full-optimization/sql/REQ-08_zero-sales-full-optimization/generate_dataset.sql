-- =====================================================================================
-- ZSFO  Zero Sales Full Optimization  weekly report  canonical rebuild query
-- Project : PRJ-2026-006_zero-sales-full-optimization
-- Task    : REQ-08_zero-sales-full-optimization  (source project_code PH-2026-07-UTHAR04)
-- Dev     : abiraj      Portfolio Holder / end user : utharsika      Marketplace : Amazon UK
-- Database: order_management_copy (production)  READ-ONLY  run via the Postgres MCP execute_sql
--
-- WHAT IT RETURNS
--   One row per Amazon-UK ASIN belonging to utharsika that had ZERO units sold in the last
--   completed 30 days, across order_transaction (FBA+FBM, Completed) AND vendor_sales (1P).
--   Plus the diagnostics needed to explain WHY (traffic funnel + stock + last-sale recency).
--
-- HOW TO SET THE RUN DATE  (the report Monday)
--   This file is written for run_date = 2026-07-10. To run a different Monday, replace every
--   occurrence of DATE '2026-07-10' below (bounds CTE) AND the five week-bucket date ranges
--   in the tw CTE. In psql you may instead use:  \set run_date '2026-07-10'  and swap the
--   literal for :'run_date'. Window is always [run_date-30, run_date-1]; current day excluded.
--
-- LOCKED RULES (do not change without owner sign-off  see SYSTEM_REFERENCE.md)
--   * Zero-sale       = 0 units in window across order_transaction AND vendor_sales.
--   * Window          = [run_date-30 days, run_date-1 day], current day excluded.
--   * Universe        = utharsika's Amazon-UK ASINs, defined from traffic_data
--                       (which_channel=1, market_place='UK', user_name='utharsika').
--   * Vendor match    = OVERLAP  NOT (end_time < ws OR start_time > we)  NOT start_time alone.
--   * listing_data    = utharsika's rows have which_channel = NULL  DO NOT filter which_channel;
--                       match on ref_id + market_place='UK' + wrong_sku=0 + is_parent=0.
--   * UK stock        = location_wise_inv_stock, location='UK', SUM(stock), EXACT sku match.
--   * Amazon FBM      = listing_data.quantity where fulfilment='merchant' AND NOT FBA
--                       (FBA marker = last _-segment of sku starts with 'AM').
--   * SKU resolution  = mapped_sku if present (as-is) else clean sku: strip -IDE/-CA/-IFR/-NL,
--                       then __seg, then _seg; exclude amzn.gr.*.
--   * Conversion Rate = conversion / clicks.
--   * "Last Month Sales" column is the 30-day-window units = 0 (proof of qualification).
--
-- EXPECTED for run_date 2026-07-10: 1,719 universe ASINs -> 1,250 zero-sale rows.
-- =====================================================================================

WITH bounds AS (
  SELECT DATE '2026-07-10' AS run_date,
         (DATE '2026-07-10' - INTERVAL '30 days')::date AS ws,   -- 2026-06-10
         (DATE '2026-07-10' - INTERVAL '1 day')::date  AS we     -- 2026-07-09
),
-- Universe: utharsika's Amazon-UK ASINs (traffic_data is the authoritative user->ASIN map)
uthar AS (
  SELECT DISTINCT ref_id AS asin
  FROM public.traffic_data
  WHERE which_channel = 1 AND market_place = 'UK' AND user_name = 'utharsika'
),
-- Listings bridge  NOTE: no which_channel filter (utharsika's listing_data rows are NULL)
listings AS (
  SELECT ld.ref_id AS asin, ld.sku, ld.mapped_sku, ld.fulfilment, ld.quantity,
         regexp_replace(trim(ld.sku), '(-IDE|-CA|-IFR|-NL)$', '') AS sku_nomkt
  FROM public.listing_data ld
  JOIN uthar u ON u.asin = ld.ref_id
  WHERE ld.market_place = 'UK' AND ld.wrong_sku = 0 AND ld.is_parent = 0
    AND COALESCE(ld.sku, '') NOT LIKE 'amzn.gr.%'
),
resolved AS (
  SELECT l.*,
    (substring(l.sku_nomkt from '_([A-Za-z0-9]+)$') ILIKE 'AM%') AS is_fba,
    CASE WHEN COALESCE(l.mapped_sku, '') <> '' THEN trim(l.mapped_sku)
         ELSE regexp_replace(regexp_replace(l.sku_nomkt, '__[^_]*$', ''), '_[^_]*$', '') END AS base_sku
  FROM listings l
),
-- FBA + FBM sales in window
sold AS (
  SELECT ot.asin, SUM(ot.quantity) AS u
  FROM public.order_transaction ot, bounds b
  WHERE ot.source_name = 'AMAZON' AND ot.market_place = 'UK' AND ot.order_status = 'Completed'
    AND ot.order_date::date BETWEEN b.ws AND b.we
  GROUP BY ot.asin
),
-- Vendor (1P) sales in window  OVERLAP match (periods can span days)
vendor AS (
  SELECT vs.asin, SUM(vs.ordered_units) AS vu
  FROM public.vendor_sales vs, bounds b
  WHERE NOT (vs.end_time::date < b.ws OR vs.start_time::date > b.we)
  GROUP BY vs.asin
),
-- Recency diagnostics (LIFETIME, not windowed)  clarifies lifetime-vs-window confusion
lastvendor AS (
  SELECT vs.asin, MAX(vs.end_time::date) AS last_vendor_date, SUM(vs.ordered_units) AS vendor_units_lifetime
  FROM public.vendor_sales vs GROUP BY vs.asin
),
lastorder AS (
  SELECT ot.asin, MAX(ot.order_date::date) AS last_order_date
  FROM public.order_transaction ot
  WHERE ot.source_name = 'AMAZON' AND ot.market_place = 'UK' AND ot.order_status = 'Completed'
  GROUP BY ot.asin
),
-- Traffic funnel (window totals + 5 weekly buckets)
tw AS (
  SELECT td.ref_id AS asin,
    SUM(td.impression) AS impr, SUM(td.click) AS clk, SUM(td.conversion) AS conv,
    SUM(td.impression) FILTER (WHERE td.date BETWEEN DATE '2026-06-10' AND DATE '2026-06-16') AS w1i,
    SUM(td.click)      FILTER (WHERE td.date BETWEEN DATE '2026-06-10' AND DATE '2026-06-16') AS w1c,
    SUM(td.impression) FILTER (WHERE td.date BETWEEN DATE '2026-06-17' AND DATE '2026-06-23') AS w2i,
    SUM(td.click)      FILTER (WHERE td.date BETWEEN DATE '2026-06-17' AND DATE '2026-06-23') AS w2c,
    SUM(td.impression) FILTER (WHERE td.date BETWEEN DATE '2026-06-24' AND DATE '2026-06-30') AS w3i,
    SUM(td.click)      FILTER (WHERE td.date BETWEEN DATE '2026-06-24' AND DATE '2026-06-30') AS w3c,
    SUM(td.impression) FILTER (WHERE td.date BETWEEN DATE '2026-07-01' AND DATE '2026-07-07') AS w4i,
    SUM(td.click)      FILTER (WHERE td.date BETWEEN DATE '2026-07-01' AND DATE '2026-07-07') AS w4c,
    SUM(td.impression) FILTER (WHERE td.date BETWEEN DATE '2026-07-08' AND DATE '2026-07-09') AS w5i,
    SUM(td.click)      FILTER (WHERE td.date BETWEEN DATE '2026-07-08' AND DATE '2026-07-09') AS w5c
  FROM public.traffic_data td, bounds b
  WHERE td.which_channel = 1 AND td.market_place = 'UK' AND td.date BETWEEN b.ws AND b.we
  GROUP BY td.ref_id
),
fbm AS (
  -- FBM = merchant-fulfilled listing qty, excluding CONFIRMED FBA (AM-family) SKUs.
  -- Use COALESCE(is_fba,false): bundle SKUs (no `_AM` segment) yield is_fba=NULL, and
  -- `is_fba = false` would WRONGLY drop them (NULL <> false) -> FBM understated to 0.
  SELECT asin, SUM(COALESCE(quantity, 0)) AS fbm
  FROM resolved WHERE fulfilment = 'merchant' AND COALESCE(is_fba, false) = false GROUP BY asin
),
uk AS (
  SELECT r.asin, SUM(COALESCE(s.stock, 0)) AS uk
  FROM (SELECT DISTINCT asin, base_sku FROM resolved) r
  JOIN public.location_wise_inv_stock s ON s.sku = r.base_sku AND s.location = 'UK'
  GROUP BY r.asin
),
sd AS (
  SELECT asin, string_agg(DISTINCT base_sku, ' + ') AS sku FROM resolved GROUP BY asin
)
SELECT
  l.asin                                             AS "ASIN",
  sd.sku                                             AS "SKU",
  0                                                  AS "Last Month Sales",
  COALESCE(uk.uk, 0)                                 AS "Local UK Warehouse stock",
  COALESCE(fbm.fbm, 0)                               AS "Amazon FBM Stock",
  COALESCE(tw.impr, 0)                               AS "Impressions",
  COALESCE(tw.clk, 0)                                AS "Clicks",
  ROUND(COALESCE(tw.conv, 0)::numeric / NULLIF(tw.clk, 0), 4) AS "Conversion Rate",
  lo.last_order_date                                 AS "Last Amazon Sale (lifetime)",
  lv.last_vendor_date                                AS "Last Vendor Sale (lifetime)",
  COALESCE(lv.vendor_units_lifetime, 0)              AS "Vendor Units (lifetime)",
  -- weekly buckets: 10-16 Jun | 17-23 | 24-30 | 01-07 Jul | 08-09 Jul
  COALESCE(tw.w1i,0) AS "W1 Impr", COALESCE(tw.w1c,0) AS "W1 Clk",
  COALESCE(tw.w2i,0) AS "W2 Impr", COALESCE(tw.w2c,0) AS "W2 Clk",
  COALESCE(tw.w3i,0) AS "W3 Impr", COALESCE(tw.w3c,0) AS "W3 Clk",
  COALESCE(tw.w4i,0) AS "W4 Impr", COALESCE(tw.w4c,0) AS "W4 Clk",
  COALESCE(tw.w5i,0) AS "W5 Impr", COALESCE(tw.w5c,0) AS "W5 Clk",
  CASE
    WHEN COALESCE(uk.uk,0)=0 AND COALESCE(fbm.fbm,0)=0 THEN 'Out of stock  no UK warehouse + no FBM'
    WHEN COALESCE(tw.impr,0)=0                          THEN 'Zero impressions  listing not surfacing (index / suppressed)'
    WHEN COALESCE(tw.clk,0)=0                           THEN 'Impressions but 0 clicks  main image / title / price'
    ELSE                                                    'Clicks but 0 sales  detail page / price / reviews'
  END                                                AS "Root-cause hint"
FROM uthar l
LEFT JOIN sold      sw ON sw.asin = l.asin
LEFT JOIN vendor    v  ON v.asin  = l.asin
LEFT JOIN tw           ON tw.asin = l.asin
LEFT JOIN fbm          ON fbm.asin = l.asin
LEFT JOIN uk           ON uk.asin  = l.asin
LEFT JOIN sd           ON sd.asin  = l.asin
LEFT JOIN lastorder lo ON lo.asin = l.asin
LEFT JOIN lastvendor lv ON lv.asin = l.asin
WHERE COALESCE(sw.u, 0) = 0 AND COALESCE(v.vu, 0) = 0   -- zero across FBA/FBM AND vendor
ORDER BY "Impressions" DESC, l.asin;
