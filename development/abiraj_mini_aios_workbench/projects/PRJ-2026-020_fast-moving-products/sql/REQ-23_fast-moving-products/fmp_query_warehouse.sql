-- REQ-23-D01 Fast Moving Products — canonical warehouse query (Germany / DE)
-- Run against the curated WAREHOUSE (public.order_transaction …), the source the report is
-- validated against. Returns one JSON payload with amazon/ebay/shopify (top 25 by 30-day units)
-- + combined (top 25 by 30-day units) + meta. Feed into build_fmp_d01.py.
-- Windows: 30d = last 30 complete days, 90d = last 90 complete days, ending yesterday.
-- Currency: Germany = EUR. Revenue = SUM(item_price*quantity) (per-product item revenue).
WITH cat AS (SELECT DISTINCT ON ("sku") "sku","category_name" FROM public.order_transaction WHERE "category_name" IS NOT NULL AND "category_name"<>'' ORDER BY "sku","order_date" DESC),
ldr1 AS (SELECT "ref_id", MIN(NULLIF("title",'')) t FROM public.listing_data WHERE "which_channel"=1 AND "title"<>'' GROUP BY "ref_id"),
ldr2 AS (SELECT "ref_id", MIN(NULLIF("title",'')) t FROM public.listing_data WHERE "which_channel"=2 AND "title"<>'' GROUP BY "ref_id"),
ldr3 AS (SELECT "ref_id", MIN(NULLIF("title",'')) t FROM public.listing_data WHERE "which_channel"=3 AND "title"<>'' GROUP BY "ref_id"),
lds AS (SELECT "sku", MIN(NULLIF("title",'')) t FROM public.listing_data WHERE "title"<>'' GROUP BY "sku"),
ip AS (SELECT "sku", MIN(NULLIF("title",'')) t FROM public.inv_products GROUP BY "sku"),
stk AS (SELECT "sku", SUM(COALESCE("stock",0)) stock FROM public.location_wise_inv_stock WHERE "location"='Germany' GROUP BY "sku"),
o AS (
  SELECT "asin","item_id","product_id","sku","source_name",
    CASE WHEN "order_date"::date>=CURRENT_DATE-30 THEN COALESCE("quantity",0) ELSE 0 END q30,
    CASE WHEN "order_date"::date>=CURRENT_DATE-90 THEN COALESCE("quantity",0) ELSE 0 END q90,
    CASE WHEN "order_date"::date>=CURRENT_DATE-30 THEN COALESCE("item_price",0)*COALESCE("quantity",0) ELSE 0 END r30,
    "order_id"
  FROM public.order_transaction
  WHERE "market_place"='Germany' AND "order_status"='Completed' AND "source_name" IN ('AMAZON','EBAY','SHOPIFY')
    AND "order_date"::date>=CURRENT_DATE-90 AND "order_date"::date<CURRENT_DATE AND "sku"<>''
),
amz AS (SELECT "sku","asin" pid, SUM(q30) qty30, SUM(q90) qty90, SUM(r30)::numeric(12,2) rev30, COUNT(DISTINCT CASE WHEN q30>0 THEN "order_id" END) orders30 FROM o WHERE "source_name"='AMAZON' GROUP BY "sku","asin" HAVING SUM(q30)>0),
eby AS (SELECT "sku","item_id" pid, SUM(q30) qty30, SUM(q90) qty90, SUM(r30)::numeric(12,2) rev30, COUNT(DISTINCT CASE WHEN q30>0 THEN "order_id" END) orders30 FROM o WHERE "source_name"='EBAY' GROUP BY "sku","item_id" HAVING SUM(q30)>0),
shp AS (SELECT "sku","product_id" pid, SUM(q30) qty30, SUM(q90) qty90, SUM(r30)::numeric(12,2) rev30, COUNT(DISTINCT CASE WHEN q30>0 THEN "order_id" END) orders30 FROM o WHERE "source_name"='SHOPIFY' GROUP BY "sku","product_id" HAVING SUM(q30)>0),
comb AS (SELECT "sku",
    SUM(CASE WHEN "source_name"='AMAZON' THEN q30 ELSE 0 END) amz,
    SUM(CASE WHEN "source_name"='EBAY' THEN q30 ELSE 0 END) ebay,
    SUM(CASE WHEN "source_name"='SHOPIFY' THEN q30 ELSE 0 END) shop,
    SUM(q30) total_units, SUM(r30)::numeric(12,2) total_rev
  FROM o GROUP BY "sku" HAVING SUM(q30)>0)
SELECT json_build_object(
 'amazon',(SELECT json_agg(row_to_json(x)) FROM (SELECT a."sku",a.pid product_id,COALESCE(ldr1.t,lds.t,NULLIF(ip.t,'Combo Default Title.'),ip.t) title,COALESCE(cat."category_name",'Uncategorised') category,a.qty30,a.qty90,a.rev30,a.orders30,COALESCE(stk.stock,0) current_stock FROM amz a LEFT JOIN cat ON cat."sku"=a."sku" LEFT JOIN ldr1 ON ldr1."ref_id"=a.pid LEFT JOIN lds ON lds."sku"=a."sku" LEFT JOIN ip ON ip."sku"=a."sku" LEFT JOIN stk ON stk."sku"=a."sku" ORDER BY a.qty30 DESC,a.rev30 DESC LIMIT 25) x),
 'ebay',(SELECT json_agg(row_to_json(x)) FROM (SELECT e."sku",e.pid product_id,COALESCE(ldr2.t,lds.t,NULLIF(ip.t,'Combo Default Title.'),ip.t) title,COALESCE(cat."category_name",'Uncategorised') category,e.qty30,e.qty90,e.rev30,e.orders30,COALESCE(stk.stock,0) current_stock FROM eby e LEFT JOIN cat ON cat."sku"=e."sku" LEFT JOIN ldr2 ON ldr2."ref_id"=e.pid LEFT JOIN lds ON lds."sku"=e."sku" LEFT JOIN ip ON ip."sku"=e."sku" LEFT JOIN stk ON stk."sku"=e."sku" ORDER BY e.qty30 DESC,e.rev30 DESC LIMIT 25) x),
 'shopify',(SELECT json_agg(row_to_json(x)) FROM (SELECT s."sku",s.pid product_id,COALESCE(ldr3.t,lds.t,NULLIF(ip.t,'Combo Default Title.'),ip.t) title,COALESCE(cat."category_name",'Uncategorised') category,s.qty30,s.qty90,s.rev30,s.orders30,COALESCE(stk.stock,0) current_stock FROM shp s LEFT JOIN cat ON cat."sku"=s."sku" LEFT JOIN ldr3 ON ldr3."ref_id"=s.pid LEFT JOIN lds ON lds."sku"=s."sku" LEFT JOIN ip ON ip."sku"=s."sku" LEFT JOIN stk ON stk."sku"=s."sku" ORDER BY s.qty30 DESC,s.rev30 DESC LIMIT 25) x),
 'combined',(SELECT json_agg(row_to_json(x)) FROM (SELECT c."sku",COALESCE(NULLIF(ip.t,'Combo Default Title.'),lds.t,ip.t) title,COALESCE(cat."category_name",'Uncategorised') category,c.amz,c.ebay,c.shop,c.total_units,c.total_rev,COALESCE(stk.stock,0) current_stock FROM comb c LEFT JOIN cat ON cat."sku"=c."sku" LEFT JOIN lds ON lds."sku"=c."sku" LEFT JOIN ip ON ip."sku"=c."sku" LEFT JOIN stk ON stk."sku"=c."sku" ORDER BY c.total_units DESC,c.total_rev DESC LIMIT 25) x),
 'meta',json_build_object('generated', CURRENT_DATE::text,'win30_start',(CURRENT_DATE-30)::text,'win90_start',(CURRENT_DATE-90)::text,'win_end',(CURRENT_DATE-1)::text)
) AS payload;
