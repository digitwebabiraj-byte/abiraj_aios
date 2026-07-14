-- FRRC — FBA Returns Root-Cause report (REQ-10-D01) — canonical read-only query
-- Source of truth: HANDOFF_FRRC_REQ-10-D01.md §5 (final, executed & validated).
-- READ-ONLY. No INSERT/UPDATE/DELETE, no DDL. SQL is never the final answer — it MUST be
-- executed via the Postgres MCP and real rows returned (per SKILL_multi_table.md).
--
-- Window: last 30 days ending the day BEFORE the run; current-day partial data excluded.
--   Fixed 2026-07-14 run  => 2026-06-14 .. 2026-07-13 inclusive.
--   To make it roll automatically, replace every  DATE '2026-07-14'  with  CURRENT_DATE.
-- Grain: one row per returning ASIN (Amazon FBA). Return-driven: start from returns, LEFT JOIN sales.
-- Join: returns.sku <> sales.sku (returns carry listing-variant SKUs, sales carry base SKUs), so
--   anchor on ASIN and resolve the display SKU through the listing_data bridge.
-- Aggregate-first (never join raw tables before aggregating — row explosion).

WITH returns_agg AS (
  SELECT asin,
    mode() WITHIN GROUP (ORDER BY sku) AS return_sku,
    SUM(qty) AS total_returns,
    COALESCE(SUM(qty) FILTER (WHERE reason IN ('NOT_COMPATIBLE','NOT_AS_DESCRIBED')),0) AS listing_qty,
    COALESCE(SUM(qty) FILTER (WHERE reason IN ('QUALITY_UNACCEPTABLE','DEFECTIVE','DAMAGED_BY_FC','DAMAGED_BY_CARRIER')),0) AS quality_qty,
    COALESCE(SUM(qty) FILTER (WHERE reason IN ('UNWANTED_ITEM','FOUND_BETTER_PRICE','ORDERED_WRONG_ITEM')),0) AS buyer_qty,
    COALESCE(SUM(qty) FILTER (WHERE reason IN ('UNDELIVERABLE_UNKNOWN','UNDELIVERABLE_REFUSED')),0) AS shipping_qty,
    -- NO_REASON_GIVEN + (HELD) rare codes not in the tracker map, parked under Unknown so buckets reconcile:
    COALESCE(SUM(qty) FILTER (WHERE reason IN ('NO_REASON_GIVEN','MISSING_PARTS','SWITCHEROO','MISSED_ESTIMATED_DELIVERY','POOR_FIT','MISORDERED','UNAUTHORIZED_PURCHASE')),0) AS unknown_qty,
    mode() WITHIN GROUP (ORDER BY reason) AS top_reason
  FROM public.amazon_returns
  WHERE fulfilment = 'fba'                              -- lowercase in the data
    AND request_date >= DATE '2026-07-14' - INTERVAL '30 days'
    AND request_date <  DATE '2026-07-14'               -- current day excluded
  GROUP BY asin
),
sales_agg AS (
  SELECT asin, SUM(quantity) AS units_sold,
    mode() WITHIN GROUP (ORDER BY user_name) AS responsible_ph
  FROM public.order_transaction
  WHERE source_name = 'AMAZON' AND fba_sales = TRUE AND market_place = 'UK'
    AND order_status = 'Completed'                      -- FBA-UK Completed (confirmed); see held items
    AND order_date >= DATE '2026-07-14' - INTERVAL '30 days'
    AND order_date <  DATE '2026-07-14'
  GROUP BY asin
),
bridge AS (
  SELECT ref_id AS asin,
    mode() WITHIN GROUP (ORDER BY COALESCE(NULLIF(mapped_sku,''), sku)) AS inv_sku
  FROM public.listing_data
  WHERE which_channel = 1 AND wrong_sku = 0 AND COALESCE(is_parent,0) <> 1 AND market_place = 'UK'
  GROUP BY ref_id
)
SELECT
  COALESCE(b.inv_sku, r.return_sku) AS sku,
  r.asin,
  COALESCE(s.units_sold,0)::int AS units_sold,
  r.total_returns::int, r.listing_qty::int, r.quality_qty::int, r.buyer_qty::int,
  r.shipping_qty::int, r.unknown_qty::int, r.top_reason, s.responsible_ph,
  r.return_sku, b.inv_sku
FROM returns_agg r
LEFT JOIN sales_agg s ON s.asin = r.asin
LEFT JOIN bridge    b ON b.asin = r.asin
ORDER BY r.total_returns DESC, COALESCE(s.units_sold,0) ASC, r.asin;

-- To capture the pull as the governed dataset frrc30.json, wrap the SELECT:
--   SELECT json_agg(t)::text FROM ( <the SELECT above> ) t;
--
-- Flag Status / Root Cause / Recommended Action are NOT computed in SQL — they are applied
-- from the editable Thresholds tab in the render layer (build_frrc30.py / build_console.py),
-- so nothing is hardcoded into the row query. See SYSTEM_REFERENCE.md §5-§6.
