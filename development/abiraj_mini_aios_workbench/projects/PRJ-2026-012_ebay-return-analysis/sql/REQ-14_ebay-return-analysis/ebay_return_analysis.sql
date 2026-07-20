/* ============================================================================
   eBay Return Analysis — master query
   Produces the 19-column per-SKU dataset for the Return Analysis dashboard.
   Grain: one row per variant SKU that had >= 1 eBay return in the period.
   Database: live Ledsone PostgreSQL (mcp.ledsone.co.uk)

   TO RUN FOR A DIFFERENT MONTH, change only these six dates:
     Reporting period : 2026-06-01  ->  2026-07-01   (start inclusive, end exclusive)
     Last Month       : 2026-05-01  ->  2026-06-01
     Last Year        : 2025-06-01  ->  2025-07-01
   Live/current-state columns (Stock) are always "now", not period-bound.
   ============================================================================ */

WITH
-- first/case row per return: reason + refund live only on the earliest row
fr AS (
  SELECT DISTINCT ON (return_id)
         return_id, transaction_id, order_id, reason,
         seller_refund_amount, sub_source, request_date
  FROM customer_service.ebay_returns
  WHERE reason IS NOT NULL
  ORDER BY return_id, id ASC
),
-- latest state per return: newest row's to_state
ls AS (
  SELECT DISTINCT ON (return_id) return_id, to_state
  FROM customer_service.ebay_returns
  ORDER BY return_id, id DESC
),
-- transaction_id -> exact variant SKU + title (100% match; avoids item_id ambiguity)
oii_tx AS (
  SELECT DISTINCT ON (item_transaction_id)
         item_transaction_id,
         COALESCE(NULLIF(real_sku,''), item_sku) AS sku,
         item_title
  FROM order_management.order_item_info
  WHERE COALESCE(item_transaction_id,'') <> ''
  ORDER BY item_transaction_id, id DESC
),
-- resolved returns (all-time), with SKU + friendly account name
rr AS (
  SELECT fr.return_id, o.sku, o.item_title AS title,
         INITCAP(COALESCE(ss.map_name, ss.name)) AS account,
         fr.reason, COALESCE(fr.seller_refund_amount,0) AS refund,
         fr.request_date, fr.order_id, ls.to_state
  FROM fr
  JOIN oii_tx o           ON o.item_transaction_id::text = fr.transaction_id::text
  LEFT JOIN order_management.sub_source ss ON ss.id = fr.sub_source
  LEFT JOIN ls            ON ls.return_id = fr.return_id
  WHERE o.sku IS NOT NULL
),
-- universe: SKUs with a return in the reporting period
june_skus AS (
  SELECT DISTINCT sku FROM rr
  WHERE request_date >= '2026-06-01' AND request_date < '2026-07-01'
),
-- return aggregates per SKU (period + comparison windows)
ret_agg AS (
  SELECT r.sku, max(r.title) AS title, max(r.account) AS account,
    count(DISTINCT r.return_id) FILTER (WHERE r.request_date>='2026-06-01' AND r.request_date<'2026-07-01') AS returns_p,
    count(DISTINCT r.return_id) FILTER (WHERE r.request_date>='2026-05-01' AND r.request_date<'2026-06-01') AS returns_lm,
    count(DISTINCT r.return_id) FILTER (WHERE r.request_date>='2025-06-01' AND r.request_date<'2025-07-01') AS returns_ly,
    sum(r.refund)               FILTER (WHERE r.request_date>='2026-06-01' AND r.request_date<'2026-07-01') AS refund_p,
    count(DISTINCT r.return_id) FILTER (WHERE r.request_date>='2026-06-01' AND r.request_date<'2026-07-01'
                                          AND r.to_state IS DISTINCT FROM 'CLOSED') AS open_cases
  FROM rr r JOIN june_skus j ON j.sku=r.sku
  GROUP BY r.sku
),
-- most common reason in the period per SKU
main_reason AS (
  SELECT sku, mode() WITHIN GROUP (ORDER BY reason) AS mr
  FROM rr WHERE request_date>='2026-06-01' AND request_date<'2026-07-01'
  GROUP BY sku
),
-- all eBay orders in the period (internal id + eBay order reference)
june_ebay_orders AS (
  SELECT o.id AS oid, o.order_id AS eref
  FROM order_management.orders o
  JOIN order_management.sub_source ss ON ss.id=o.sub_source_id
  JOIN order_management.source s      ON s.id=ss.source_id
  WHERE s.source_name='EBAY'
    AND o.order_date>='2026-06-01' AND o.order_date<'2026-07-01'
),
-- order lines with computed line value (real_* preferred, item_* fallback); qty is TEXT -> cast
lines AS (
  SELECT oi.order_id AS oid,
         COALESCE(NULLIF(oi.real_sku,''),oi.item_sku) AS sku,
         COALESCE(NULLIF(oi.real_price,'')::numeric, NULLIF(oi.item_price,'')::numeric, 0)
           * COALESCE(NULLIF(oi.real_qty,'')::numeric, NULLIF(oi.item_quantity,'')::numeric, 0) AS line_val,
         COALESCE(NULLIF(oi.real_qty,'')::numeric, NULLIF(oi.item_quantity,'')::numeric, 0) AS qty
  FROM order_management.order_item_info oi
  WHERE oi.order_id IN (SELECT oid FROM june_ebay_orders)
),
-- Orders column = units sold in the period per SKU
orders_june AS (
  SELECT sku, SUM(qty) AS orders_units
  FROM lines WHERE sku IN (SELECT sku FROM june_skus) GROUP BY sku
),
order_tot AS (SELECT oid, SUM(line_val) AS tot FROM lines GROUP BY oid),
-- Standard/CPS ad fees are booked per order in accounting (NOT in performance_data)
adfee_ord AS (
  SELECT order_id::text AS eref,
         SUM(COALESCE(fee,0)) FILTER (WHERE fee_type IN ('AD_FEE','PREMIUM_AD_FEES')) AS adfee
  FROM accounting.ebay_order_expenses GROUP BY order_id::text
),
-- CPS spend split across order lines by line value; CPS sales = line revenue on ad-charged orders
cps AS (
  SELECT l.sku,
    SUM(COALESCE(af.adfee,0) * l.line_val / NULLIF(ot.tot,0))              AS cps_spend,
    SUM(CASE WHEN COALESCE(af.adfee,0)>0 THEN l.line_val ELSE 0 END)       AS cps_sales
  FROM lines l
  JOIN june_ebay_orders jo ON jo.oid=l.oid
  JOIN order_tot ot        ON ot.oid=l.oid
  LEFT JOIN adfee_ord af   ON af.eref=jo.eref
  WHERE l.sku IN (SELECT sku FROM june_skus)
  GROUP BY l.sku
),
-- live stock snapshot per SKU (all locations)
stock AS (
  SELECT p.sku, SUM(COALESCE(st.stock,0)) AS stock
  FROM inventory.products p
  JOIN inventory.local_inventory_current_stock_location_wise st ON st.inventory_id=p.id
  WHERE p.sku IN (SELECT sku FROM june_skus) GROUP BY p.sku
),
-- negative feedback in the period per SKU (via transaction_id)
neg_fb AS (
  SELECT o.sku, count(*) AS nf
  FROM customer_service.ebay_orders_customer_feedbacks f
  JOIN oii_tx o ON o.item_transaction_id::text=f.transaction_id::text
  WHERE f.type='Negative' AND f.date>='2026-06-01' AND f.date<'2026-07-01'
    AND o.sku IN (SELECT sku FROM june_skus) GROUP BY o.sku
),
-- Return Cost = eBay refund fees + selling fees on the returned orders
ret_orders AS (
  SELECT DISTINCT sku, order_id FROM rr
  WHERE request_date>='2026-06-01' AND request_date<'2026-07-01'
),
order_fees AS (
  SELECT order_id::text AS order_id,
         SUM(COALESCE(fee,0)) FILTER (WHERE transaction_type='REFUND'
              OR fee_type IN ('FINAL_VALUE_FEE','FINAL_VALUE_FEE_FIXED_PER_ORDER')) AS fees
  FROM accounting.ebay_order_expenses GROUP BY order_id::text
),
return_cost AS (
  SELECT ro.sku, SUM(COALESCE(ofe.fees,0)) AS return_cost
  FROM ret_orders ro LEFT JOIN order_fees ofe ON ofe.order_id=ro.order_id::text
  GROUP BY ro.sku
),
-- CPC/Advanced ad performance: performance_data is CPC-only; spread listing spend across variants
listing_variants AS (
  SELECT item_id::text AS item_id, sku, count(*) OVER (PARTITION BY item_id) AS nvar
  FROM (SELECT DISTINCT item_id, sku FROM listings.ebay_listings
        WHERE wrong_sku=0 AND COALESCE(sku,'')<>'') d
),
ad_perf AS (
  SELECT pd.ebay_listing_id::text AS item_id,
    SUM(COALESCE(pd.ad_fees_payout_currency,0))   FILTER (WHERE c.campaign_type='ON_SITE') AS spend,
    SUM(COALESCE(pd.sale_amount_payout_currency,0)) FILTER (WHERE c.campaign_type='ON_SITE') AS sales
  FROM ebay_campaigns.performance_data pd
  JOIN ebay_campaigns.campaigns c ON c.campaign_id=pd.campaign_id
  WHERE pd.date>='2026-06-01' AND pd.date<'2026-07-01'
  GROUP BY pd.ebay_listing_id::text
),
cpc AS (
  SELECT lv.sku,
    SUM(ap.spend/NULLIF(lv.nvar,0)) AS cpc_spend,
    SUM(ap.sales/NULLIF(lv.nvar,0)) AS cpc_sales
  FROM ad_perf ap JOIN listing_variants lv ON lv.item_id=ap.item_id
  WHERE lv.sku IN (SELECT sku FROM june_skus) GROUP BY lv.sku
),
final AS (
  SELECT a.sku, a.title, a.account,
    COALESCE(o.orders_units,0)::numeric AS orders,
    a.returns_p AS returns,
    round((a.returns_p::numeric / NULLIF(o.orders_units,0))::numeric,4) AS return_rate,
    a.returns_lm AS lmr, a.returns_ly AS lyr,
    round(a.refund_p::numeric,2) AS refund,
    round(rc.return_cost::numeric,2) AS return_cost,
    a.returns_p AS _r, mr.mr AS reason_code,
    RANK() OVER (ORDER BY a.returns_p DESC, a.refund_p DESC) AS rank,
    COALESCE(nf.nf,0) AS negfb, a.open_cases, COALESCE(s.stock,0) AS stock,
    round((COALESCE(cpc.cpc_spend,0)+COALESCE(cps.cps_spend,0))::numeric,2) AS ad_spend,
    round((COALESCE(cpc.cpc_sales,0)+COALESCE(cps.cps_sales,0))::numeric,2) AS ad_sales
  FROM ret_agg a
  LEFT JOIN main_reason mr ON mr.sku=a.sku
  LEFT JOIN orders_june o  ON o.sku=a.sku
  LEFT JOIN stock s        ON s.sku=a.sku
  LEFT JOIN neg_fb nf      ON nf.sku=a.sku
  LEFT JOIN return_cost rc ON rc.sku=a.sku
  LEFT JOIN cpc            ON cpc.sku=a.sku
  LEFT JOIN cps            ON cps.sku=a.sku
)
SELECT
  sku                                                        AS "SKU",
  title                                                      AS "Product Title",
  account                                                    AS "Account",
  orders                                                     AS "Orders",
  returns                                                    AS "Returns",
  return_rate                                                AS "Return Rate",
  lmr                                                        AS "Last Month Returns",
  lyr                                                        AS "Last Year Returns",
  refund                                                     AS "Refund (£)",
  return_cost                                                AS "Return Cost (£)",
  CASE reason_code
    WHEN 'WRONG_SIZE' THEN 'Wrong Size'
    WHEN 'ORDERED_WRONG_ITEM' THEN 'Ordered Wrong Item'
    WHEN 'NOT_AS_DESCRIBED' THEN 'Not as Described'
    WHEN 'NO_LONGER_NEED_ITEM' THEN 'No Longer Needed'
    WHEN 'DEFECTIVE_ITEM' THEN 'Defective Item'
    WHEN 'ORDERED_DIFFERENT_ITEM' THEN 'Ordered Different Item'
    WHEN 'ORDERED_ACCIDENTALLY' THEN 'Ordered Accidentally'
    WHEN 'ARRIVED_DAMAGED' THEN 'Arrived Damaged'
    WHEN 'BUYER_NO_SHOW' THEN 'Buyer No-Show'
    WHEN 'NO_REASON' THEN 'No Reason Given'
    WHEN 'WITHDRAW_FROM_PURCHASE_CONTRACT' THEN 'Withdrawn from Purchase'
    ELSE initcap(replace(reason_code,'_',' '))
  END                                                        AS "Main Return Reason",
  '#' || rank::text                                          AS "Return Rank",
  negfb                                                      AS "Negative Feedback",
  open_cases                                                 AS "Open Cases",
  stock                                                      AS "Stock",
  ad_spend                                                   AS "Ad Spend (£)",
  ad_sales                                                   AS "Ad Sales (£)",
  round((ad_spend/NULLIF(ad_sales,0))::numeric,4)            AS "ACOS",
  round((ad_sales/NULLIF(ad_spend,0))::numeric,2)            AS "ROAS"
FROM final
ORDER BY returns DESC, refund DESC;


/* ----------------------------------------------------------------------------
   BONUS: Return-Reason breakdown table (the second block on the dashboard)
   ---------------------------------------------------------------------------- */
WITH fr AS (
  SELECT DISTINCT ON (return_id) return_id, reason, request_date
  FROM customer_service.ebay_returns
  WHERE reason IS NOT NULL
  ORDER BY return_id, id ASC
)
SELECT
  CASE reason
    WHEN 'WRONG_SIZE' THEN 'Wrong Size'
    WHEN 'ORDERED_WRONG_ITEM' THEN 'Ordered Wrong Item'
    WHEN 'NOT_AS_DESCRIBED' THEN 'Not as Described'
    WHEN 'NO_LONGER_NEED_ITEM' THEN 'No Longer Needed'
    WHEN 'DEFECTIVE_ITEM' THEN 'Defective Item'
    WHEN 'ORDERED_DIFFERENT_ITEM' THEN 'Ordered Different Item'
    WHEN 'ORDERED_ACCIDENTALLY' THEN 'Ordered Accidentally'
    WHEN 'ARRIVED_DAMAGED' THEN 'Arrived Damaged'
    WHEN 'BUYER_NO_SHOW' THEN 'Buyer No-Show'
    WHEN 'NO_REASON' THEN 'No Reason Given'
    WHEN 'WITHDRAW_FROM_PURCHASE_CONTRACT' THEN 'Withdrawn from Purchase'
    ELSE initcap(replace(reason,'_',' '))
  END AS "Return Reason",
  count(*) AS "Returns",
  round(100.0 * count(*) / SUM(count(*)) OVER (), 1) AS "Pct"
FROM fr
WHERE request_date >= '2026-06-01' AND request_date < '2026-07-01'
GROUP BY reason
ORDER BY "Returns" DESC;
