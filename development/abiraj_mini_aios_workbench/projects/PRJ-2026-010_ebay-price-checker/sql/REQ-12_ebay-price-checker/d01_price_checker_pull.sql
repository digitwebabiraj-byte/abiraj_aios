-- REQ-12-D01  eBay Price Checker  |  canonical extraction query
-- Database: ledsone  (Ledsone-db-mcp / mcp.ledsone.co.uk, user dbhub_readonly, host 10.8.0.5)
-- READ-ONLY. Produces one row per live eBay listing SKU (UK + Germany) across Thinesh's 13 accounts.
-- Owner CONFIRMED BUSINESS RULE 2026-07-16 + Thinesh Q1-Q8. SKU-normalised per the AIOS knowledge base:
--   all_list = 1  (ebay-listing-sku-filter.md)  |  Amazon '_' marketplace suffix stripped,
--   ENC codes -> inventory.products.sku_original, PK pack quantity via inventory.product_pk
--   (sku-format-rules.md).
-- The report application layer (build_price_checker_xlsx.py / build_dashboard_html.py) then applies:
--   Target = Amazon(amazon Ledsone, sub_source 8, LOWEST) x0.90 ; else website(shopify 104/108) x1.10 ;
--   else DATA MISSING (split into NO COMPARATOR vs BUNDLE).  Tolerance +/-0.50 / +/-1.00 at the 20 band.
-- NOTE: chunked in the delivery run (row_number windows of 15,000) only because the read-only MCP caps
-- result size; on a direct connection this runs whole.

WITH enc AS (
  SELECT sku, sku_original FROM inventory.products WHERE sku LIKE 'ENC%' AND sku_original <> ''
),
pk AS (SELECT pack_char, pack_qty FROM inventory.product_pk),
eb AS (   -- live eBay listing SKUs, UK + Germany, ENC-resolved
  SELECT e.item_id, e.sku AS raw_sku, e.price::numeric AS ebay_price, e.site,
         COALESCE(e.main_image_url,'') AS img, COALESCE(s.name,'') AS acct,
         COALESCE(en.sku_original, e.sku) AS nsku
  FROM listings.ebay_listings e
  LEFT JOIN order_management.sub_source s ON s.id = e.sub_source
  LEFT JOIN enc en ON en.sku = e.sku
  WHERE e.all_list = 1 AND e.site IN ('UK','Germany')
    AND e.price > 0 AND btrim(e.sku) <> ''
),
am AS (   -- approved Amazon source: amazon Ledsone (sub_source 8), '_' suffix stripped, ENC-resolved
  SELECT a.site, COALESCE(en.sku_original, split_part(a.sku,'_',1)) AS nsku,
         min(a.price)::numeric AS price,          -- Thinesh Q1: LOWEST on a duplicate match
         max(a.updated_at) AS a_upd
  FROM listings.amazon_listings a
  LEFT JOIN enc en ON en.sku = split_part(a.sku,'_',1)
  WHERE a.all_list = 1 AND a.sub_source = 8 AND a.site IN ('UK','Germany') AND a.price > 0
  GROUP BY 1,2
),
wb AS (   -- approved website source: Shopify ledsone (104, UK) / ledsone-de (108, DE)
  SELECT CASE WHEN w.sub_source = 104 THEN 'UK' ELSE 'Germany' END AS site,
         COALESCE(en.sku_original, w.sku) AS nsku, min(w.price)::numeric AS price, max(w.updated_at) AS w_upd
  FROM listings.shopify_listings w
  LEFT JOIN enc en ON en.sku = w.sku
  WHERE w.all_list = 1 AND w.sub_source IN (104,108) AND w.price > 0
  GROUP BY 1,2
),
-- Q2 bundles: split '+' SKUs into components, decode PK pack qty, sum component prices
combo AS (SELECT DISTINCT nsku, site FROM eb WHERE nsku LIKE '%+%'),
comp AS (
  SELECT c.nsku, c.site,
    CASE WHEN btrim(x.p) ~ '.[A-Za-z0-9]PK$' THEN substring(btrim(x.p),1,length(btrim(x.p))-3) ELSE btrim(x.p) END AS base,
    CASE WHEN btrim(x.p) ~ '.[A-Za-z0-9]PK$' THEN substring(btrim(x.p),length(btrim(x.p))-2,1) ELSE NULL END AS pchar
  FROM combo c, LATERAL unnest(string_to_array(c.nsku,'+')) AS x(p)
),
comp2 AS (SELECT c.*, COALESCE(pk.pack_qty,1) AS qty FROM comp c LEFT JOIN pk ON pk.pack_char = c.pchar),
bag AS (
  SELECT c.nsku, c.site, count(*) AS n_comp, count(am.price) AS n_amz, count(wb.price) AS n_web,
         sum(am.price*c.qty) AS sum_amz, sum(wb.price*c.qty) AS sum_web
  FROM comp2 c
  LEFT JOIN am ON am.nsku = c.base AND am.site = c.site
  LEFT JOIN wb ON wb.nsku = c.base AND wb.site = c.site
  GROUP BY 1,2
)
SELECT e.item_id, e.raw_sku AS sku, e.img AS product_image, e.acct AS db_account, e.site,
       COALESCE(am.price, CASE WHEN b.n_amz = b.n_comp THEN b.sum_amz END) AS amazon_price,
       COALESCE(w.price,  CASE WHEN b.n_web = b.n_comp THEN b.sum_web END) AS website_price,
       CASE WHEN am.price IS NOT NULL              THEN round(am.price*0.90, 2)
            WHEN w.price  IS NOT NULL              THEN round(w.price *1.10, 2)
            WHEN b.n_amz = b.n_comp AND b.sum_amz>0 THEN round(b.sum_amz*0.90, 2)
            WHEN b.n_web = b.n_comp AND b.sum_web>0 THEN round(b.sum_web*1.10, 2)
       END AS target_ebay_price,
       e.ebay_price AS current_ebay_price
FROM eb e
LEFT JOIN am ON am.nsku = e.nsku AND am.site = e.site
LEFT JOIN wb w ON w.nsku = e.nsku AND w.site = e.site
LEFT JOIN bag b ON b.nsku = e.nsku AND b.site = e.site
ORDER BY e.site, e.item_id, e.raw_sku, e.ebay_price;

-- Account filter (applied in the report layer): keep only Thinesh's 13 (account, site) pairs;
-- drop dctransformer/UK, bestbringer/UK, ledsonede/UK (17) = 4,266 rows he did not name.
-- 130,336 live eBay UK+DE listing rows -> 126,070 in the delivered report.
