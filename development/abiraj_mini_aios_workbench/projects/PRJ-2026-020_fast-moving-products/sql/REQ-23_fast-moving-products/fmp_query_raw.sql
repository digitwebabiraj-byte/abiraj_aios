-- REQ-23-D01 Fast Moving Products - canonical RAW query (mcp.ledsone: order_management + inventory)
-- Germany=market_place '10', channels Amazon=1/eBay=2/Shopify=3 via sub_source.source_id, status='Completed'.
-- Grain: per (Product ID, SKU) per channel; combined per shared SKU. Rolling 30/90d ending yesterday. EUR.
WITH base AS (
  SELECT ss.source_id chan, oi.item_sku sku, oi.item_asin, oi.item_id, oi.product_id, o.id oid,
    CASE WHEN o.order_date::date>=CURRENT_DATE-30 THEN COALESCE(NULLIF(oi.item_quantity,'')::numeric,0) ELSE 0 END q30,
    CASE WHEN o.order_date::date>=CURRENT_DATE-90 THEN COALESCE(NULLIF(oi.item_quantity,'')::numeric,0) ELSE 0 END q90,
    CASE WHEN o.order_date::date>=CURRENT_DATE-30 THEN COALESCE(NULLIF(oi.item_price,'')::numeric,0)*COALESCE(NULLIF(oi.item_quantity,'')::numeric,0) ELSE 0 END r30
  FROM order_management.orders o
  JOIN order_management.sub_source ss ON ss.id=o.sub_source_id
  JOIN order_management.order_item_info oi ON oi.order_id=o.id
  WHERE o.market_place='10' AND o.status='Completed' AND ss.source_id IN (1,2,3)
    AND o.order_date::date>=CURRENT_DATE-90 AND o.order_date::date<CURRENT_DATE
    AND oi.item_sku IS NOT NULL AND oi.item_sku<>''
),
stk AS (SELECT p.sku, SUM(COALESCE(s.stock,0)) stock FROM inventory.products p
        JOIN inventory.local_inventory_current_stock_location_wise s ON s.inventory_id=p.id
        WHERE s.warehouse_location='Germany' GROUP BY p.sku),
amz AS (SELECT sku, MAX(item_asin) pid, SUM(q30) q30,SUM(q90) q90,SUM(r30)::numeric(12,2) rev30,COUNT(DISTINCT CASE WHEN q30>0 THEN oid END) o30
        FROM base WHERE chan=1 GROUP BY sku, item_asin HAVING SUM(q30)>0),
eby AS (SELECT sku, MAX(item_id) pid, SUM(q30) q30,SUM(q90) q90,SUM(r30)::numeric(12,2) rev30,COUNT(DISTINCT CASE WHEN q30>0 THEN oid END) o30
        FROM base WHERE chan=2 GROUP BY sku, item_id HAVING SUM(q30)>0),
shp AS (SELECT sku, MAX(product_id) pid, SUM(q30) q30,SUM(q90) q90,SUM(r30)::numeric(12,2) rev30,COUNT(DISTINCT CASE WHEN q30>0 THEN oid END) o30
        FROM base WHERE chan=3 GROUP BY sku, product_id HAVING SUM(q30)>0),
comb AS (SELECT sku, SUM(CASE WHEN chan=1 THEN q30 ELSE 0 END) amz, SUM(CASE WHEN chan=2 THEN q30 ELSE 0 END) ebay,
   SUM(CASE WHEN chan=3 THEN q30 ELSE 0 END) shop, SUM(q30) tu, SUM(r30)::numeric(12,2) tr
   FROM base GROUP BY sku HAVING SUM(q30)>0)
SELECT json_build_object(
 'amazon',(SELECT json_agg(row_to_json(x)) FROM (SELECT a.sku,a.pid product_id,a.q30 qty30,a.q90 qty90,a.rev30,a.o30 orders30,COALESCE(stk.stock,0) current_stock FROM amz a LEFT JOIN stk ON stk.sku=a.sku ORDER BY a.q30 DESC,a.rev30 DESC LIMIT 25) x),
 'ebay',(SELECT json_agg(row_to_json(x)) FROM (SELECT e.sku,e.pid product_id,e.q30 qty30,e.q90 qty90,e.rev30,e.o30 orders30,COALESCE(stk.stock,0) current_stock FROM eby e LEFT JOIN stk ON stk.sku=e.sku ORDER BY e.q30 DESC,e.rev30 DESC LIMIT 25) x),
 'shopify',(SELECT json_agg(row_to_json(x)) FROM (SELECT s.sku,s.pid product_id,s.q30 qty30,s.q90 qty90,s.rev30,s.o30 orders30,COALESCE(stk.stock,0) current_stock FROM shp s LEFT JOIN stk ON stk.sku=s.sku ORDER BY s.q30 DESC,s.rev30 DESC LIMIT 25) x),
 'combined',(SELECT json_agg(row_to_json(x)) FROM (SELECT c.sku,c.amz,c.ebay,c.shop,c.tu total_units,c.tr total_rev,COALESCE(stk.stock,0) current_stock FROM comb c LEFT JOIN stk ON stk.sku=c.sku ORDER BY c.tu DESC,c.tr DESC LIMIT 25) x),
 'meta',json_build_object('generated',CURRENT_DATE::text,'win30_start',(CURRENT_DATE-30)::text,'win90_start',(CURRENT_DATE-90)::text,'win_end',(CURRENT_DATE-1)::text)
) payload;
