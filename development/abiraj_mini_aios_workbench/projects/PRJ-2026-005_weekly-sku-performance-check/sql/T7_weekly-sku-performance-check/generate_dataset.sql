-- ============================================================================
-- Table 7 - Weekly SKU Performance Check | Thuwaraga (PH-2026-07-THUW07)
-- Canonical dataset rebuild query.  READ-ONLY.  DB: order_management_copy
--
-- Produces one row per listing (blue "ASIN detail") for Thuwaraga's UK universe
-- across Amazon / eBay / B&Q, with the rolling-7-day Completed-order count and
-- the resolved base SKU + product name.  The purple "SKU SUMMARY" rows and the
-- colour bands are assembled by the renderer (build_html.py / build_report.py),
-- grouping these rows by base_sku - kept out of SQL exactly as the Table 5
-- sibling (REQ-06) keeps row colouring out of SQL scope.
--
-- WINDOW (business rule): runs every Thursday; window = rolling 7 days ending
-- the day BEFORE the run date.  For a Thursday run this is last Thu .. last Wed.
-- Set it dynamically at run time instead of the hard-coded dates below, e.g.:
--     ws = (CURRENT_DATE - INTERVAL '7 day')::date   -- inclusive start
--     we = (CURRENT_DATE - INTERVAL '1 day')::date   -- inclusive end
-- Snapshot used for the 2026-07-09 run: 2026-07-02 .. 2026-07-08.
--
-- LOCKED DATA RULES (verified against live DB - see SYSTEM_REFERENCE.md):
--   * PH filter  : LOWER(user_name) = LOWER('thuwaraga')  (DB spelling; NOT 'thuwaraka')
--   * Marketplace: market_place = 'UK'
--   * Platforms  : source_name IN ('AMAZON','EBAY','B&Q')  (excl. SHOPIFY, WAYFAIR)
--   * Order count: COUNT(DISTINCT order_item_info) WHERE order_status='Completed'
--   * Listing ref: COALESCE(NULLIF(asin,''), NULLIF(item_id,''))  (NULL for B&Q -> group on sku)
--   * Base SKU   : mapped_sku if present/non-empty else sku  (listing_data, wrong_sku=0)
--                  -> flag rows where the mapped base differs from sku (dirty mapped_sku)
--   * Product nm : listing_data.title if present else MODE(order_transaction.category_name)
--   * amzn.gr.*  : Amazon internal group-id pseudo-SKUs - excluded by the renderer
--                  (all zero-order for this PH); keep visible here for auditability.
-- ============================================================================

WITH win AS (
    SELECT DATE '2026-07-02' AS ws, DATE '2026-07-08' AS we   -- <<< set dynamically each Thursday
),
-- Step 1 - universe: every distinct listing Thuwaraga holds on UK Amazon/eBay/B&Q
universe AS (
    SELECT DISTINCT
        ot."sku"                                                AS sku,
        COALESCE(NULLIF(ot."asin",''), NULLIF(ot."item_id",'')) AS ref,
        ot."source_name"                                        AS platform,
        ot."ss_name"                                            AS account
    FROM public.order_transaction ot
    WHERE LOWER(ot."user_name") = LOWER('thuwaraga')
      AND ot."market_place" = 'UK'
      AND ot."source_name" IN ('AMAZON','EBAY','B&Q')
),
-- Step 2 - this week's Completed-order count per listing
orders AS (
    SELECT
        ot."sku"                                                AS sku,
        COALESCE(NULLIF(ot."asin",''), NULLIF(ot."item_id",'')) AS ref,
        ot."source_name"                                        AS platform,
        ot."ss_name"                                            AS account,
        COUNT(DISTINCT ot."order_item_info")                    AS orders
    FROM public.order_transaction ot, win
    WHERE LOWER(ot."user_name") = LOWER('thuwaraga')
      AND ot."market_place" = 'UK'
      AND ot."source_name" IN ('AMAZON','EBAY','B&Q')
      AND ot."order_status" = 'Completed'
      AND ot."order_date"::date BETWEEN win.ws AND win.we
    GROUP BY 1,2,3,4
),
-- base SKU + product title, resolved per sku from the listing registry
ld_agg AS (
    SELECT ld."sku"                                             AS sku,
           COALESCE(NULLIF(MAX(NULLIF(ld."mapped_sku",'')),''), ld."sku") AS base_sku,
           MAX(NULLIF(ld."title",''))                           AS title
    FROM public.listing_data ld
    WHERE ld."wrong_sku" = 0
    GROUP BY ld."sku"
),
-- category fallback for product name when no listing title exists
cat AS (
    SELECT ot."sku" AS sku,
           MODE() WITHIN GROUP (ORDER BY ot."category_name") AS category
    FROM public.order_transaction ot
    WHERE LOWER(ot."user_name") = LOWER('thuwaraga')
      AND ot."category_name" IS NOT NULL AND ot."category_name" <> ''
    GROUP BY ot."sku"
)
-- Step 3 - one blue "ASIN detail" row per listing (LEFT JOIN keeps zero-order rows)
SELECT
    u."sku"                                                     AS sku,
    u."ref"                                                     AS ref_id,          -- ASIN / item_id (NULL => B&Q, group on sku)
    u."platform",
    u."account",
    COALESCE(la.base_sku, u."sku")                             AS base_sku,
    CASE WHEN la.base_sku IS NOT NULL AND la.base_sku <> u."sku"
         THEN 1 ELSE 0 END                                      AS mapped_flag,     -- 1 => mapped_sku differs (verify grouping)
    COALESCE(NULLIF(la.title,''), c.category, '')              AS product_name,
    COALESCE(o.orders, 0)                                       AS orders,          -- this listing's Completed orders in-window
    win.ws                                                      AS week_start,
    win.we                                                      AS week_end
FROM universe u
CROSS JOIN win
LEFT JOIN orders o
       ON o.sku      IS NOT DISTINCT FROM u."sku"
      AND o.ref      IS NOT DISTINCT FROM u."ref"
      AND o.platform =  u."platform"
      AND o.account  IS NOT DISTINCT FROM u."account"
LEFT JOIN ld_agg la ON la.sku = u."sku"
LEFT JOIN cat    c  ON c.sku  = u."sku"
ORDER BY base_sku, u."platform", u."ref";
