-- REQ-13-D01 · eBay Account Performance Dashboard · canonical read-only pulls (June 2026)
-- Warehouse order_management_copy unless noted. All READ-ONLY. Executed via Postgres MCP; real rows returned.
-- 12 accounts: led_sone, so_926407, electricalsone, ledsonede, huettenlampen, coventrylights,
--              vintageinterior, dctransformer, re6865, neighbourmarket, lighting_sone, homin_gmbh
-- Windows: June 2026 [2026-06-01, 2026-07-01) · LM May 2026 · LY June 2025.

-- =====================================================================================
-- 1. SALES by account × marketplace × period  (Revenue = SUM(order_total), Completed)
-- =====================================================================================
SELECT ss_name, market_place,
  CASE WHEN order_date>='2026-06-01' AND order_date<'2026-07-01' THEN 'jun'
       WHEN order_date>='2026-05-01' AND order_date<'2026-06-01' THEN 'may'
       WHEN order_date>='2025-06-01' AND order_date<'2025-07-01' THEN 'ly' END p,
  COUNT(DISTINCT order_id) orders, SUM(quantity) units,
  ROUND(SUM(order_total)::numeric,2) revenue           -- settled paid value (NOT item_price*qty, NOT +template postage)
FROM order_transaction
WHERE source_name='EBAY' AND order_status='Completed' AND market_place IS NOT NULL
  AND ss_name IN ('led_sone','so_926407','electricalsone','ledsonede','huettenlampen','coventrylights',
                  'vintageinterior','dctransformer','re6865','neighbourmarket','lighting_sone','homin_gmbh')
  AND ((order_date>='2026-06-01' AND order_date<'2026-07-01')
    OR (order_date>='2026-05-01' AND order_date<'2026-06-01')
    OR (order_date>='2025-06-01' AND order_date<'2025-07-01'))
GROUP BY ss_name, market_place, p
ORDER BY ss_name, market_place, p;

-- =====================================================================================
-- 2. ADVERTISING — eBay Promoted Listings ON_SITE (Priority) ONLY, by account × marketplace, June
--    Join ppc_performance.record_id = ppc.parent_id ; filter record_subtype='ON_SITE'
--    (IN-subquery avoids join fan-out). Standard COST_PER_SALE excluded per Thinesh.
-- =====================================================================================
SELECT pp.ss_name, pp.marketplace,
  ROUND(SUM(pp.spend)::numeric,2) onsite_spend,
  ROUND(SUM(pp.sales)::numeric,2) onsite_ad_sales,     -- eBay-attributed; stays < revenue at ON_SITE scope
  SUM(pp.orders) ad_orders, SUM(pp.clicks) clicks
FROM ppc_performance pp
WHERE pp.source_name='EBAY' AND pp.record_type='campaign'
  AND pp.ss_name IN ('led_sone','so_926407','electricalsone','ledsonede','huettenlampen')  -- only 5 accounts advertise
  AND pp.date>='2026-06-01' AND pp.date<'2026-07-01'
  AND pp.record_id IN (SELECT DISTINCT parent_id FROM ppc
                       WHERE source_name ILIKE '%ebay%' AND record_main_type='campaign'
                         AND record_subtype='ON_SITE')
GROUP BY pp.ss_name, pp.marketplace HAVING SUM(pp.spend)>0
ORDER BY pp.ss_name, onsite_spend DESC;
-- TACOS = onsite_spend / total revenue ; Return = total revenue / onsite_spend (computed in the dashboard).
-- NOTE: record_type='campaign' summed ALL types over-counts attributed sales (one order attributed to every
-- overlapping campaign) — never present ACOS/ROAS on attributed sales; use TACOS on real spend.

-- =====================================================================================
-- 3. CONVERSION — whole-account eBay traffic, by account × marketplace × period
--    eBay = traffic_data.which_channel = 2  (1=Amazon, 3=Shopify/other)
-- =====================================================================================
SELECT sub_source_name AS acct, market_place,
  CASE WHEN date>='2026-06-01' AND date<'2026-07-01' THEN 'jun'
       WHEN date>='2026-05-01' AND date<'2026-06-01' THEN 'may'
       WHEN date>='2025-06-01' AND date<'2025-07-01' THEN 'ly' END p,
  SUM(conversion) conv, SUM(click) clk,
  ROUND((SUM(conversion)/NULLIF(SUM(click),0))::numeric,4) conv_rate
FROM traffic_data
WHERE which_channel=2 AND market_place IS NOT NULL
  AND sub_source_name IN ('led_sone','so_926407','electricalsone','ledsonede','huettenlampen','coventrylights',
                          'vintageinterior','dctransformer','re6865','neighbourmarket','lighting_sone','homin_gmbh')
  AND ((date>='2026-06-01' AND date<'2026-07-01') OR (date>='2026-05-01' AND date<'2026-06-01')
    OR (date>='2025-06-01' AND date<'2025-07-01'))
GROUP BY sub_source_name, market_place, p HAVING SUM(click)>0
ORDER BY sub_source_name, market_place, p;

-- =====================================================================================
-- 4. LISTINGS (active) + STOCK by account × marketplace  (warehouse)
-- =====================================================================================
WITH accts AS (SELECT unnest(ARRAY['led_sone','so_926407','electricalsone','ledsonede','huettenlampen',
   'coventrylights','vintageinterior','dctransformer','re6865','neighbourmarket','lighting_sone','homin_gmbh']) a),
la AS (SELECT sub_source_name acct, market_place, COUNT(DISTINCT ref_id) active
       FROM listing_data WHERE which_channel_name='ebay' AND sub_source_name = ANY(SELECT a FROM accts)
         AND market_place IS NOT NULL GROUP BY sub_source_name, market_place),
sk AS (SELECT DISTINCT sub_source_name acct, market_place, COALESCE(NULLIF(mapped_sku,''),sku) sku
       FROM listing_data WHERE which_channel_name='ebay' AND sub_source_name = ANY(SELECT a FROM accts)
         AND market_place IS NOT NULL AND COALESCE(wrong_sku,0)=0),
st AS (SELECT sk.acct, sk.market_place, SUM(i.stock) stock FROM sk JOIN inv_final_stock i ON i.sku=sk.sku
       GROUP BY sk.acct, sk.market_place)
SELECT la.acct, la.market_place, la.active, COALESCE(st.stock,0) stock
FROM la LEFT JOIN st ON st.acct=la.acct AND st.market_place=la.market_place
WHERE la.market_place IN ('UK','Germany','France','Italy','Ireland','US','Canada')
ORDER BY la.acct, la.active DESC;

-- =====================================================================================
-- 5. NEW LISTINGS — LEDSONE (ledsone) DATABASE, not the warehouse
--    Warehouse listing_data has NO creation date; ledsone listings.ebay_listings.created_at does.
--    (run via Ledsone-db-mcp)
-- =====================================================================================
-- SELECT ss.name AS acct, el.site, COUNT(DISTINCT el.item_id) AS new_listings
-- FROM listings.ebay_listings el
-- JOIN order_management.sub_source ss ON ss.id = el.sub_source
-- WHERE el.created_at >= '2026-06-01' AND el.created_at < '2026-07-01'
--   AND ss.name IN (... 12 accounts ...)
-- GROUP BY ss.name, el.site ORDER BY ss.name, new_listings DESC;

-- =====================================================================================
-- 6. POSTAGE-vs-order_total proof (why revenue = order_total, not item_price*qty + template postage)
-- =====================================================================================
-- SELECT source_name,
--   COUNT(DISTINCT order_id) distinct_orders, COUNT(*) line_rows, SUM(quantity) units,
--   ROUND(SUM(item_price*quantity)::numeric,2) sales_ipq,     -- product only
--   ROUND(SUM(order_total)::numeric,2)          sales_order_total  -- = the owner's verified figure
-- FROM order_transaction
-- WHERE ss_name='led_sone' AND market_place='UK' AND order_status='Completed'
--   AND order_date>='2026-06-01' AND order_date<'2026-07-01' GROUP BY source_name;
-- => led_sone UK: distinct 1517 / lines 1619 / ipq £28,873.00 / order_total £28,975.37 (owner check).
