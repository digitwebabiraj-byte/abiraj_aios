-- ============================================================================
-- Weekly Stock Check (Table 5) — PH: Thuwaraga — dataset generator
-- Run against the PRODUCTION Postgres (order_management_copy) via the
-- "Postgresql" MCP connector (mcp.vintageinterior.co.uk).
-- Produces one row per (ASIN, account). Wrap in json_agg(...) if you want JSON.
--
-- KEY RULE: UK stock comes from location_wise_inv_stock (the feed that matches
-- the live inventory UI), NOT inv_final_stock (stale). Master SKU is resolved
-- mapped_sku -> order-table sku -> suffix-stripped listing sku.
-- KNOWN GAP: legacy->canonical "Mapping SKU" (e.g. LDMA60E274 -> LDMA60E274WW)
-- is NOT in this DB; those rows still read the legacy (0-stock) SKU. See HANDOFF.
-- ============================================================================
WITH inv AS (
  SELECT sku, stock::int AS uk_wh
  FROM public.location_wise_inv_stock WHERE location='UK'
),
sales_tot AS (
  SELECT asin, ss_name AS account,
         SUM(quantity)::int AS units_90, COUNT(DISTINCT order_id) AS orders_90
  FROM public.order_transaction
  WHERE user_name='thuwaraga' AND source_name='AMAZON' AND market_place='UK'
    AND order_status='Completed' AND COALESCE(fba_sales,false)=false
    AND order_date >= CURRENT_DATE - INTERVAL '90 days'
    AND asin IS NOT NULL AND asin<>''
  GROUP BY asin, ss_name
),
sku_pick AS (               -- primary internal SKU per (asin, account) = most units
  SELECT DISTINCT ON (asin, ss_name) asin, ss_name AS account, sku AS order_sku
  FROM public.order_transaction
  WHERE user_name='thuwaraga' AND source_name='AMAZON' AND market_place='UK'
    AND order_status='Completed' AND COALESCE(fba_sales,false)=false
    AND order_date >= CURRENT_DATE - INTERVAL '90 days'
    AND asin IS NOT NULL AND asin<>'' AND sku IS NOT NULL AND sku<>''
  GROUP BY asin, ss_name, sku
  ORDER BY asin, ss_name, SUM(quantity) DESC
),
ld AS (                     -- one listing row per (asin, account)
  SELECT DISTINCT ON (ref_id, sub_source_name) ref_id AS asin, sub_source_name AS account,
         sku AS listing_sku, NULLIF(mapped_sku,'') AS mapped_sku, quantity AS amazon_fbm
  FROM public.listing_data
  WHERE which_channel=1 AND market_place='UK' AND wrong_sku=0 AND fulfilment='merchant'
  ORDER BY ref_id, sub_source_name, quantity DESC NULLS LAST
),
resolved AS (
  SELECT st.asin, st.account, st.units_90, st.orders_90,
         COALESCE(ld.listing_sku, sp.order_sku)  AS listing_sku,
         COALESCE(ld.amazon_fbm, 0)::int         AS amazon_fbm,
         COALESCE(
           (SELECT i.sku FROM inv i WHERE i.sku = ld.mapped_sku),
           (SELECT i.sku FROM inv i WHERE i.sku = sp.order_sku),
           (SELECT i.sku FROM inv i WHERE i.sku = regexp_replace(ld.listing_sku,'(_[0-9]+| [A-Za-z0-9]{1,3}|-[A-Za-z0-9]{1,3})$','')),
           sp.order_sku
         ) AS master_sku
  FROM sales_tot st
  LEFT JOIN sku_pick sp ON sp.asin=st.asin AND sp.account=st.account
  LEFT JOIN ld        ON ld.asin=st.asin AND ld.account=st.account
),
incoming AS (               -- open supplier POs (not yet arrived)
  SELECT oi.sku,
         SUM(COALESCE(oi.ctns,0)*COALESCE(oi.ctn_pcs,0))::int AS po_qty,
         STRING_AGG(DISTINCT s.name,', ')  AS suppliers,
         STRING_AGG(DISTINCT fc.name,', ') AS containers
  FROM supplier.order_items oi
  JOIN supplier.orders o    ON o.id=oi.order_id
  JOIN supplier.suppliers s ON s.id=o.supplier_id
  LEFT JOIN supplier.final_containers fc ON fc.id=oi.final_container_id
  WHERE o.status_arrived=0
  GROUP BY oi.sku
)
SELECT
  r.asin, r.account, r.listing_sku, r.master_sku,
  r.amazon_fbm,
  COALESCE(inv.uk_wh,0)                          AS uk_warehouse,
  r.units_90                                     AS order_count_90,
  ROUND((r.units_90/90.0)::numeric,2)            AS velocity,
  CASE WHEN COALESCE(inv.uk_wh,0)<=0 OR r.units_90=0 THEN 0
       ELSE ROUND((COALESCE(inv.uk_wh,0)/(r.units_90/90.0))::numeric,0) END AS days_remaining,
  inc.suppliers, inc.po_qty, inc.containers,
  CASE
    WHEN COALESCE(inv.uk_wh,0)<=0 THEN 'No Stock / Critical'
    WHEN (COALESCE(inv.uk_wh,0)/(r.units_90/90.0)) < 15 THEN 'No Stock / Critical'
    WHEN (COALESCE(inv.uk_wh,0)/(r.units_90/90.0)) <= 60 THEN 'Going Out of Stock'
    ELSE 'Healthy Stock'
  END AS stock_status
FROM resolved r
LEFT JOIN inv      ON inv.sku = r.master_sku
LEFT JOIN incoming inc ON inc.sku = r.master_sku
WHERE r.master_sku NOT LIKE 'amzn.gr.%'
ORDER BY (CASE WHEN COALESCE(inv.uk_wh,0)<=0 THEN 0 ELSE 1 END), days_remaining ASC;
