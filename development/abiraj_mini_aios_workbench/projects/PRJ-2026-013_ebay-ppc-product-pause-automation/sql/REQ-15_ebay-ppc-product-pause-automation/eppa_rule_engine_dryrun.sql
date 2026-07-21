-- REQ-15 eBay PPC Product Pause Automation — rule-engine dry run
-- Executed read-only 2026-07-21 against the live warehouse (order_management_copy).
-- Purpose: prove the mockup's engine can be driven from live data at listing grain.
--
-- Scope: LEDSone (ss_name='led_sone') · eBay (source=2) · UK · running ON_SITE campaigns only.
--   ON_SITE only  -> Advanced/CPC and Standard/CPS use incompatible pricing models and must never
--                    be combined; Rule 1's ACOS ceiling does not transfer to CPS. See Gap B.
--   Note          -> ON_SITE SMART campaigns return no ad-grain rows and are absent here. See Gap A.
--
-- Thresholds below are the mockup's `Pause Rules` values. They are RECORDED here, not endorsed --
-- in the delivered build they must come from a config table/sheet, never hardcoded.
--   stock floor 5 units | Rule 1 ACOS ceiling 40% | Rule 1 7D rescue 20%
--   Rule 2 min 14D clicks 20 | Rule 2 14D spend floor GBP 2.50
--
-- Grain of the output: item_id x campaign_id (one listing can run in several campaigns).
-- Stock is LIVE (no history) even though spend is windowed -- state this on any report.

WITH anchor AS (   -- latest COMPLETE day: MAX(date) is today once the sync has run, and today
                   -- is only part-populated, which understates every window. See the validation
                   -- record 2026-07-21_live_data_verification.md section 5.
  SELECT CASE WHEN MAX(date) < CURRENT_DATE THEN MAX(date) ELSE MAX(date) - 1 END AS d
  FROM public.ppc_performance
  WHERE source = 2 AND ss_name = 'led_sone' AND marketplace = 'UK'
),
perf AS (                                          -- (1) all three windows in one pass
  SELECT pp.ref_id AS item_id, pp.parent_id AS campaign_id, pp.sub_source_id, pp.marketplace,
    SUM(pp.spend)  FILTER (WHERE pp.date > a.d - 30) AS spend30,
    SUM(pp.sales)  FILTER (WHERE pp.date > a.d - 30) AS sales30,
    SUM(pp.orders) FILTER (WHERE pp.date > a.d - 30) AS ord30,
    SUM(pp.spend)  FILTER (WHERE pp.date > a.d - 7)  AS spend7,
    SUM(pp.sales)  FILTER (WHERE pp.date > a.d - 7)  AS sales7,
    SUM(pp.orders) FILTER (WHERE pp.date > a.d - 14) AS ord14,
    SUM(pp.clicks) FILTER (WHERE pp.date > a.d - 14) AS clicks14,
    SUM(pp.spend)  FILTER (WHERE pp.date > a.d - 14) AS spend14
  FROM public.ppc_performance pp
  CROSS JOIN anchor a
  JOIN public.ppc p
    ON p.parent_id = pp.parent_id AND p.record_main_type = 'campaign' AND p.source = 2
  WHERE pp.source = 2 AND pp.ss_name = 'led_sone' AND pp.marketplace = 'UK'
    AND pp.record_type = 'ad' AND pp.ref_id <> '0'
    AND pp.date > a.d - 30 AND pp.date <= a.d
    AND p.record_subtype = 'ON_SITE' AND p.record_status = 'running'
  GROUP BY 1,2,3,4
),
skus AS (                                          -- (2) bridge item_id -> inventory SKU(s)
  SELECT DISTINCT pf.item_id, COALESCE(NULLIF(ld.mapped_sku,''), ld.sku) AS sku
  FROM perf pf
  JOIN public.listing_data ld
    ON ld.ref_id = pf.item_id AND ld.which_channel = 2
   AND ld.market_place = pf.marketplace AND ld.sub_source = pf.sub_source_id
   AND ld.wrong_sku = 0
),
stock AS (                                         -- (3) stock per listing, kept in its own CTE so
  SELECT s.item_id,                                --     the 1->many bridge cannot inflate spend
         SUM(COALESCE(l.stock,0)) AS units,
         COUNT(DISTINCT s.sku)    AS n_skus        -- >1 means Gap C applies to this row
  FROM skus s
  LEFT JOIN public.location_wise_inv_stock l ON l.sku = s.sku AND l.location = 'UK'
  GROUP BY s.item_id
),
calc AS (
  SELECT pf.*, st.units, st.n_skus,
    (pf.spend30 / NULLIF(pf.sales30,0) * 100)::numeric AS acos30,
    (pf.spend7  / NULLIF(pf.sales7 ,0) * 100)::numeric AS acos7
  FROM perf pf
  LEFT JOIN stock st ON st.item_id = pf.item_id     -- LEFT JOIN: unbridged listings must survive
)                                                   -- as "no data", never collapse to 0 = auto-pause
SELECT
  CASE
    WHEN units IS NULL                          THEN 'NO STOCK DATA (unbridged)'
    WHEN units < 5                              THEN 'PAUSE - Stock'
    WHEN ord30 > 0 AND acos30 >= 40
         AND NOT (acos7 < 20)                   THEN 'PAUSE - Rule 1'
    WHEN ord14 = 0 AND clicks14 >= 20
         AND NOT (spend14 < 2.50)               THEN 'PAUSE - Rule 2'
    ELSE 'Keep running'
  END                       AS decision,
  COUNT(*)                  AS listings,
  SUM(spend30)::numeric(10,2) AS spend30_at_stake
FROM calc
GROUP BY 1
ORDER BY 3 DESC NULLS LAST;

-- Result 2026-07-21 (anchor date 2026-07-20):
--   Keep running               678   GBP 1658.64
--   PAUSE - Rule 2               8   GBP   57.25
--   PAUSE - Rule 1               3   GBP   48.49
--   NO STOCK DATA (unbridged)   33   GBP   30.82
--   PAUSE - Stock               10   GBP   11.38
