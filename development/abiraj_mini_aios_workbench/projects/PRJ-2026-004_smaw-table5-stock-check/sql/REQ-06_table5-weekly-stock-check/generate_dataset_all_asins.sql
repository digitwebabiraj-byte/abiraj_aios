-- ============================================================================
-- Table 5 Weekly Stock Check — Thuwaraga — CORRECT & FINAL (live ∪ sold)
-- Universe = every Amazon-UK ASIN that EITHER has a live FBM listing OR sold in
-- the last 90 days -> a strict superset of the old "sellers only" report
-- (nothing dropped) PLUS all idle-stock ASINs.
-- Stock shows for ALL rows; velocity & days-of-stock only where there are sales;
-- ASINs with stock but no recent sales are flagged "No Recent Sales (Idle Stock)".
--
-- Connector: the "Postgresql" MCP (mcp.vintageinterior.co.uk) -> DB order_management_copy
-- READ-ONLY. Edit :as_of below to pin a historical date (default = today).
-- ============================================================================
WITH anchor AS (SELECT CURRENT_DATE AS d),          -- <- set to DATE '2026-07-08' to reproduce that day
her_uk AS (
  SELECT asin AS a FROM public.order_transaction WHERE lower(user_name)='thuwaraga' AND source_name='AMAZON' AND market_place='UK' AND asin<>''
  UNION SELECT asin FROM public.amz_fbm_performance_data WHERE lower(user_name)='thuwaraga' AND mp_text='UK' AND asin<>''
  UNION SELECT ref_id FROM analytics.ph_segment WHERE lower(user_name)='thuwaraga' AND which_channel::text='1' AND market_place='UK' AND ref_id<>''
),
inv AS (SELECT sku, stock::int AS uk_wh FROM public.location_wise_inv_stock WHERE location='UK'),
live AS (
  SELECT DISTINCT ON (ref_id, sub_source_name) ref_id AS asin, sub_source_name AS account,
         sku AS listing_sku, NULLIF(mapped_sku,'') AS mapped_sku, quantity::int AS amazon_fbm
  FROM public.listing_data
  WHERE which_channel=1 AND market_place='UK' AND wrong_sku=0 AND fulfilment='merchant' AND ref_id IN (SELECT a FROM her_uk)
  ORDER BY ref_id, sub_source_name, quantity DESC NULLS LAST
),
order_sku AS (
  SELECT DISTINCT ON (asin, ss_name) asin, ss_name AS account, sku AS o_sku
  FROM public.order_transaction WHERE lower(user_name)='thuwaraga' AND source_name='AMAZON' AND market_place='UK' AND asin<>'' AND sku<>''
  GROUP BY asin, ss_name, sku ORDER BY asin, ss_name, SUM(quantity) DESC
),
sales90 AS (
  SELECT asin, ss_name AS account, SUM(quantity)::int AS units_90
  FROM public.order_transaction, anchor
  WHERE lower(user_name)='thuwaraga' AND source_name='AMAZON' AND market_place='UK'
    AND order_status='Completed' AND COALESCE(fba_sales,false)=false
    AND order_date >= anchor.d - INTERVAL '90 days' AND order_date <= anchor.d AND asin<>''
  GROUP BY asin, ss_name
),
grain AS (   -- live listings UNION sold pairs (so no seller is ever dropped)
  SELECT asin, account, listing_sku, mapped_sku, amazon_fbm FROM live
  UNION
  SELECT s.asin, s.account, COALESCE(os.o_sku, s.asin) AS listing_sku, NULL::text AS mapped_sku, 0 AS amazon_fbm
  FROM sales90 s
  LEFT JOIN order_sku os ON os.asin=s.asin AND os.account=s.account
  WHERE NOT EXISTS (SELECT 1 FROM live l WHERE l.asin=s.asin AND l.account=s.account)
),
resolved AS (
  SELECT g.asin, g.account, g.listing_sku, g.amazon_fbm,
    COALESCE((SELECT i.sku FROM inv i WHERE i.sku=g.mapped_sku),
             (SELECT i.sku FROM inv i WHERE i.sku=os.o_sku),
             (SELECT i.sku FROM inv i WHERE i.sku=regexp_replace(g.listing_sku,'(_[0-9]+| [A-Za-z0-9]{1,3}|-[A-Za-z0-9]{1,3})$','')),
             os.o_sku, g.listing_sku) AS master_sku,
    COALESCE(s.units_90,0) AS units_90
  FROM grain g
  LEFT JOIN order_sku os ON os.asin=g.asin AND os.account=g.account
  LEFT JOIN sales90   s  ON s.asin=g.asin  AND s.account=g.account
),
incoming AS (
  SELECT oi.sku, SUM(COALESCE(oi.ctns,0)*COALESCE(oi.ctn_pcs,0))::int AS po_qty,
         STRING_AGG(DISTINCT sup.name,', ') AS suppliers, STRING_AGG(DISTINCT fc.name,', ') AS containers
  FROM supplier.order_items oi JOIN supplier.orders o ON o.id=oi.order_id
  JOIN supplier.suppliers sup ON sup.id=o.supplier_id
  LEFT JOIN supplier.final_containers fc ON fc.id=oi.final_container_id
  WHERE o.status_arrived=0 GROUP BY oi.sku
)
SELECT
  r.asin, r.account, r.listing_sku, r.master_sku, r.amazon_fbm,
  COALESCE(inv.uk_wh,0) AS uk_warehouse, r.units_90 AS order_count_90,
  CASE WHEN r.units_90>0 THEN ROUND((r.units_90/90.0)::numeric,2) END AS velocity,
  CASE WHEN r.units_90>0 AND COALESCE(inv.uk_wh,0)>0 THEN ROUND((COALESCE(inv.uk_wh,0)/(r.units_90/90.0))::numeric,0) END AS days_remaining,
  inc.suppliers, inc.po_qty, inc.containers,
  CASE WHEN r.units_90=0 AND COALESCE(inv.uk_wh,0)>0 THEN 'No Recent Sales (Idle Stock)'
       WHEN COALESCE(inv.uk_wh,0)<=0 THEN 'No Stock / Critical'
       WHEN (COALESCE(inv.uk_wh,0)/(r.units_90/90.0))<15 THEN 'No Stock / Critical'
       WHEN (COALESCE(inv.uk_wh,0)/(r.units_90/90.0))<=60 THEN 'Going Out of Stock'
       ELSE 'Healthy Stock' END AS stock_status
FROM resolved r
LEFT JOIN inv ON inv.sku=r.master_sku
LEFT JOIN incoming inc ON inc.sku=r.master_sku
WHERE r.master_sku NOT LIKE 'amzn.gr.%'
ORDER BY
  (CASE WHEN r.units_90>0 AND COALESCE(inv.uk_wh,0)<=0 THEN 0 WHEN r.units_90>0 THEN 1 ELSE 2 END),
  days_remaining ASC NULLS LAST, uk_warehouse DESC, r.asin;
