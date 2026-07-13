-- ============================================================================
-- 03 — VALIDATE COUNTS (segment distribution + per-PH + grand total)
-- Read-only recompute of the WHOLE portfolio in one query (the "light" query:
-- classification only, NO movement, NO sku), used to (a) get the authoritative
-- corrected counts and (b) cross-check the built HTML cell-by-cell.
-- This is the SAME engine logic as 01_recompute_per_ph.sql, aggregated.
-- ----------------------------------------------------------------------------
-- WINDOW (rn = the last complete Saturday-weeks in traffic_data, newest = rn 1):
--   Normal monthly roll-forward : cur = rn 1..4   (this is the default below)
--   Same-period CORRECTION      : cur = rn 2..5   (drops the just-loaded newest
--                                 week so the window == the published report's)
-- Change the two "BETWEEN 1 AND 4" below to "BETWEEN 2 AND 5" for a correction.
-- 2026-07-10 correction result (RATE-based conversion rule — this was the LIVE D10 build):
--   9,947 ASINs / 30 PHs · HHH 42 · HHL 580 · HLH 173 · LHH 10 · LLH 626 · LLL 8516
-- *** CONVERSION RULE NOW = COUNT-BASED (Bietrick-approved 2026-07-10) *** — this file was switched
-- to conv COUNT (a.conv >= b.bcv) below, same as 01/02. Re-running WILL change the distribution
-- above (some HHL Leaky Buckets -> HHH Champions); it no longer reproduces the D10 build. Old rate
-- rule kept for revert: (CASE WHEN a.conv>=b.bcv THEN 'H' ELSE 'L' END).
-- ============================================================================
WITH sats AS (
  SELECT date, ROW_NUMBER() OVER (ORDER BY date DESC) rn
  FROM (SELECT DISTINCT date FROM public.traffic_data
        WHERE which_channel=1 AND market_place='UK') d),
cur_weeks AS (SELECT date d FROM sats WHERE rn BETWEEN 1 AND 4),   -- <-- window
cur_sig AS (
  SELECT user_name, ref_id, sub_source_name,
    SUM(impression) imp, SUM(click) clk, SUM(conversion) conv,
    CASE WHEN SUM(click)>0 THEN SUM(conversion)::numeric/SUM(click) ELSE 0 END cvr
  FROM public.traffic_data
  WHERE which_channel=1 AND market_place='UK' AND user_name IS NOT NULL AND date IN (SELECT d FROM cur_weeks)
  GROUP BY 1,2,3),
cur_cat AS (
  SELECT user_name, ref_id, sub_source_name, category_name,
    ROW_NUMBER() OVER (PARTITION BY user_name,ref_id,sub_source_name ORDER BY SUM(impression) DESC, category_name) rn
  FROM public.traffic_data
  WHERE which_channel=1 AND market_place='UK' AND user_name IS NOT NULL AND date IN (SELECT d FROM cur_weeks)
  GROUP BY 1,2,3,4),
cur_asins AS (
  SELECT s.user_name,s.ref_id,c.category_name,s.sub_source_name,s.imp,s.clk,s.conv,s.cvr
  FROM cur_sig s JOIN cur_cat c ON c.user_name=s.user_name AND c.ref_id=s.ref_id AND c.sub_source_name=s.sub_source_name AND c.rn=1),
cur_units AS (
  SELECT o.asin, SUM(COALESCE(o.quantity,0)) u
  FROM public.order_transaction o
  WHERE o.source_name='AMAZON' AND o.market_place='UK' AND o.order_status='Completed' AND o.fba_sales=false
    AND o.order_date>=(SELECT MIN(d)-6 FROM cur_weeks) AND o.order_date<(SELECT MAX(d)+1 FROM cur_weeks)
  GROUP BY o.asin),
cur_sellers AS (
  SELECT a.user_name,a.category_name,a.ref_id,a.imp,a.clk,a.conv,a.cvr,
    ROW_NUMBER() OVER (PARTITION BY a.user_name,a.category_name ORDER BY u.u DESC,a.imp DESC) rnk,
    COUNT(*) OVER (PARTITION BY a.user_name,a.category_name) scnt
  FROM cur_asins a JOIN cur_units u ON a.ref_id=u.asin AND u.u>0),
cur_bm AS (
  SELECT user_name,category_name,
    AVG(imp) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bi,
    AVG(clk) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bc,
    AVG(conv) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bcv,
    AVG(cvr) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bv
  FROM cur_sellers GROUP BY user_name,category_name),
cur_seg AS (
  SELECT a.user_name,
    CASE
      WHEN (CASE WHEN a.imp>=b.bi THEN 'H' ELSE 'L' END)||(CASE WHEN a.clk>=b.bc THEN 'H' ELSE 'L' END)||(CASE WHEN a.conv>=b.bcv THEN 'H' ELSE 'L' END) = 'HLL' THEN 'HLH'
      WHEN (CASE WHEN a.imp>=b.bi THEN 'H' ELSE 'L' END)||(CASE WHEN a.clk>=b.bc THEN 'H' ELSE 'L' END)||(CASE WHEN a.conv>=b.bcv THEN 'H' ELSE 'L' END) = 'LHL' THEN 'HHL'
      ELSE (CASE WHEN a.imp>=b.bi THEN 'H' ELSE 'L' END)||(CASE WHEN a.clk>=b.bc THEN 'H' ELSE 'L' END)||(CASE WHEN a.conv>=b.bcv THEN 'H' ELSE 'L' END)
    END AS segment
  FROM cur_asins a LEFT JOIN cur_bm b ON a.user_name=b.user_name AND a.category_name=b.category_name)
SELECT segment, user_name, COUNT(*) n
FROM cur_seg
GROUP BY GROUPING SETS ((segment),(user_name),())
ORDER BY segment NULLS LAST, user_name NULLS LAST;
