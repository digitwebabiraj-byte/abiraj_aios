-- FRRC REQ-10-D02 refreshed pull (same window 2026-06-14..2026-07-13) + account enrichment

WITH returns_agg AS (
  SELECT asin,
    mode() WITHIN GROUP (ORDER BY sku) AS return_sku,
    SUM(qty) AS total_returns,
    COALESCE(SUM(qty) FILTER (WHERE reason IN ('NOT_COMPATIBLE','NOT_AS_DESCRIBED')),0) AS listing_qty,
    COALESCE(SUM(qty) FILTER (WHERE reason IN ('QUALITY_UNACCEPTABLE','DEFECTIVE','DAMAGED_BY_FC','DAMAGED_BY_CARRIER')),0) AS quality_qty,
    COALESCE(SUM(qty) FILTER (WHERE reason IN ('UNWANTED_ITEM','FOUND_BETTER_PRICE','ORDERED_WRONG_ITEM')),0) AS buyer_qty,
    COALESCE(SUM(qty) FILTER (WHERE reason IN ('UNDELIVERABLE_UNKNOWN','UNDELIVERABLE_REFUSED')),0) AS shipping_qty,
    COALESCE(SUM(qty) FILTER (WHERE reason IN ('NO_REASON_GIVEN','MISSING_PARTS','SWITCHEROO','MISSED_ESTIMATED_DELIVERY','POOR_FIT','MISORDERED','UNAUTHORIZED_PURCHASE')),0) AS unknown_qty,
    mode() WITHIN GROUP (ORDER BY reason) AS top_reason,
    mode() WITHIN GROUP (ORDER BY CASE WHEN sub_source_name ILIKE '%ledsone%' THEN 'LEDSone'
                                       WHEN sub_source_name ILIKE '%dcvoltage%' THEN 'DCVoltage'
                                       ELSE sub_source_name END) AS account,
    COUNT(DISTINCT sub_source_name) AS n_accounts
  FROM public.amazon_returns
  WHERE fulfilment='fba'
    AND request_date >= DATE '2026-07-14' - INTERVAL '30 days'
    AND request_date <  DATE '2026-07-14'
  GROUP BY asin
),
sales_agg AS (
  SELECT asin, SUM(quantity) AS units_sold,
    mode() WITHIN GROUP (ORDER BY user_name) AS responsible_ph
  FROM public.order_transaction
  WHERE source_name='AMAZON' AND fba_sales=TRUE AND market_place='UK'
    AND order_status='Completed'
    AND order_date >= DATE '2026-07-14' - INTERVAL '30 days'
    AND order_date <  DATE '2026-07-14'
  GROUP BY asin
),
bridge AS (
  SELECT ref_id AS asin,
    mode() WITHIN GROUP (ORDER BY COALESCE(NULLIF(mapped_sku,''), sku)) AS inv_sku
  FROM public.listing_data
  WHERE which_channel=1 AND wrong_sku=0 AND COALESCE(is_parent,0)<>1 AND market_place='UK'
  GROUP BY ref_id
)
SELECT COALESCE(b.inv_sku, r.return_sku) AS sku, r.asin, r.account, r.n_accounts,
  COALESCE(s.units_sold,0)::int AS units_sold,
  r.total_returns::int, r.listing_qty::int, r.quality_qty::int, r.buyer_qty::int,
  r.shipping_qty::int, r.unknown_qty::int, r.top_reason, s.responsible_ph,
  r.return_sku, b.inv_sku
FROM returns_agg r
LEFT JOIN sales_agg s ON s.asin = r.asin
LEFT JOIN bridge    b ON b.asin = r.asin
ORDER BY r.total_returns DESC, COALESCE(s.units_sold,0) ASC, r.asin
