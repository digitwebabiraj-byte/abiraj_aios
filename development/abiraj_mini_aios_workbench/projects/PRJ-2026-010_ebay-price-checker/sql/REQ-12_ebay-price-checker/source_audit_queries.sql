-- REQ-12-D01  Source audit / discovery queries  |  READ-ONLY
-- Two databases were swept (the REQ-11 lesson: a negative sweep is only valid for the DB you name):
--   ledsone               (Ledsone-db-mcp, host 10.8.0.5)      -> the price data
--   order_management_copy (Postgres MCP, host 10.8.0.3)         -> the existing pricing pilot + ph_task
-- Each result is annotated inline with what it returned on 2026-07-16.

-- 1. Price-column sweep, BOTH databases (find any price/repric/target/rrp/msrp/cost column).
--    ledsone result: the `listings` schema (amazon_listings/ebay_listings/shopify_listings) holds price.
--    order_management_copy result: staging_ai.pricing_safe_* pilot (21 SKUs / 63 rows) + ph_action_board.
SELECT table_schema, table_name, string_agg(column_name, ', ' ORDER BY column_name) AS price_cols
FROM information_schema.columns
WHERE table_schema NOT IN ('pg_catalog','information_schema')
  AND column_name ~* '(price|rrp|msrp|cost)'
GROUP BY 1,2 ORDER BY 1,2;

-- 2. The three price sources on ledsone (all refreshed 2026-07-15).
--    amazon_listings 130,296 rows / 124,750 priced / 11 currencies
--    ebay_listings   298,386 rows / 298,383 priced /  4 currencies   <- price per variant row
--    shopify_listings 68,198 rows /  53,819 priced /  0 currencies    <- currency column EMPTY (item C)
SELECT 'amazon_listings' t, count(*) rows, count(*) FILTER (WHERE price>0) priced, count(DISTINCT currency) curr FROM listings.amazon_listings
UNION ALL SELECT 'ebay_listings',    count(*), count(*) FILTER (WHERE price>0), count(DISTINCT currency) FROM listings.ebay_listings
UNION ALL SELECT 'shopify_listings', count(*), count(*) FILTER (WHERE price>0), count(DISTINCT currency) FROM listings.shopify_listings;

-- 3. The AIOS SKU-normalisation tables exist and are usable.
--    inventory.products: 43,709 rows, 10,083 ENC codes ALL with sku_original.
--    inventory.product_pk: 28 pack-char -> pack-qty decodes.
SELECT (SELECT count(*) FROM inventory.products) products,
       (SELECT count(*) FROM inventory.products WHERE sku LIKE 'ENC%') enc,
       (SELECT count(*) FROM inventory.products WHERE sku LIKE 'ENC%' AND sku_original<>'') enc_with_original,
       (SELECT count(*) FROM inventory.product_pk) product_pk;

-- 4. all_list=1 vs the naive filter (why the corrected build has MORE rows).
--    documented (all_list=1): 82,518 UK  |  naive (wrong_sku=0,is_child=1,is_ended=0): 76,126 -> 6,392 lost
SELECT 'all_list=1' k, count(*) FROM listings.ebay_listings WHERE all_list=1 AND site='UK' AND price>0 AND btrim(sku)<>''
UNION ALL SELECT 'naive', count(*) FROM listings.ebay_listings
  WHERE wrong_sku=0 AND is_child=1 AND COALESCE(is_ended,0)=0 AND site='UK' AND price>0 AND btrim(sku)<>'';

-- 5. The 13 eBay accounts x site grid (resolves Thinesh's labels; Sunsone=so_926407, Retro LED=re6865
--    are the only accounts that fit the UK/DE split and reconcile the counts).
SELECT s.name db_account, e.site, count(*) rows
FROM listings.ebay_listings e JOIN order_management.sub_source s ON s.id=e.sub_source
WHERE e.all_list=1 AND e.site IN ('UK','Germany') AND e.price>0
GROUP BY 1,2 ORDER BY 1,2;

-- 6. Drift check that VINDICATES the rule (refutes the earlier VAT/postage-artifact hypothesis).
--    median eBay vs raw Amazon = -9.11% (rule targets -10%); median drift from target = +0.98% (~zero).
--    => rule is well-centred; the 70% flag rate is real price dispersion vs a tight +/-5% tolerance,
--    NOT a systematic basis error on the Amazon path.
WITH e AS (SELECT btrim(sku) k, price::numeric p FROM listings.ebay_listings
             WHERE all_list=1 AND site='UK' AND price>0 AND btrim(sku)<>''),
     a AS (SELECT btrim(COALESCE(NULLIF(mapped_sku,''),sku)) k, count(DISTINCT price) np, min(price)::numeric p
             FROM listings.amazon_listings WHERE all_list=1 AND site='UK' AND sub_source=8 AND price>0 GROUP BY 1)
SELECT round(percentile_cont(0.5) WITHIN GROUP (ORDER BY (e.p-round(a.p*0.9,2))/round(a.p*0.9,2))::numeric,4) median_drift_from_target,
       round(percentile_cont(0.5) WITHIN GROUP (ORDER BY (e.p-a.p)/a.p)::numeric,4) median_ebay_vs_amazon
FROM e JOIN a ON a.k=e.k AND a.np=1;

-- ⚠ SHIPPING (AIOS business/rules/cross-platform-pricing-markup.md): a price check without shipping
-- "will misreport correctly-priced listings as violations". Shipping source NOT yet identified
-- (amazon_listings.shipping_id is an undocumented FK). Status/Priority/Action are therefore SHIPPING-BLIND.
