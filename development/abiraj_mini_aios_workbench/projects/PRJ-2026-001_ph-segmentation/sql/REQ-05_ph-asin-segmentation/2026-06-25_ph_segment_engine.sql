-- ============================================================================
-- PH ASIN SEGMENTATION — MONTHLY ENGINE (auto-detects latest 2 windows)
-- Locked decisions: Method A CVR (avg of per-ASIN CVR over top-N sold) ;
-- zero-click -> LOW conversion ; conversions>clicks -> HIGH conversion ;
-- undefined combos mapped HLL->HLH , LHL->HHL ; scope = which_channel=1, UK, FBM only (fba_sales=false).
-- Re-run as-is every month. No dates to edit.
-- ============================================================================

-- ---- resolve current + previous windows from the source table -------------
DROP TABLE IF EXISTS analytics._ph_windows;
CREATE TABLE analytics._ph_windows AS
SELECT period_start, period_end,
       ROW_NUMBER() OVER (ORDER BY period_end DESC) AS rn
FROM (SELECT DISTINCT period_start, period_end
      FROM analytics.ph_segment_30days_window
      WHERE which_channel=1 AND market_place='UK') w;

-- ---- helper: classify one window into a temp table ------------------------
-- CURRENT window = rn 1
DROP TABLE IF EXISTS analytics._ph_cur;
CREATE TABLE analytics._ph_cur AS
WITH win AS (SELECT period_start, period_end FROM analytics._ph_windows WHERE rn=1),
ph_asins AS (
  SELECT s.user_name, s.ref_id, s.category_name, s.sub_source_name,
         s.impression_count AS imp, s.click_count AS clk, s.conversion_count AS conv,
         CASE WHEN s.click_count>0 THEN s.conversion_count::numeric/s.click_count ELSE 0 END AS cvr
  FROM analytics.ph_segment_30days_window s, win
  WHERE s.period_end=win.period_end AND s.which_channel=1 AND s.market_place='UK'),
units AS (
  SELECT o."asin", SUM(COALESCE(o."quantity",0)) AS u
  FROM public.order_transaction o, win
  WHERE o."source_name"='AMAZON' AND o."market_place"='UK' AND o."order_status"='Completed' AND o."fba_sales"=false  -- FBM only (protocol scope)
    AND o."order_date"::date >= win.period_start AND o."order_date"::date <= win.period_end
  GROUP BY o."asin"),
sellers AS (
  SELECT a.user_name,a.category_name,a.ref_id,a.imp,a.clk,a.cvr,
         ROW_NUMBER() OVER (PARTITION BY a.user_name,a.category_name ORDER BY u.u DESC,a.imp DESC) rnk,
         COUNT(*) OVER (PARTITION BY a.user_name,a.category_name) scnt
  FROM ph_asins a JOIN units u ON a.ref_id=u.asin AND u.u>0),
bm AS (
  SELECT user_name,category_name,MAX(scnt) sellers,
    AVG(imp) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bi,
    AVG(clk) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bc,
    AVG(cvr) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bv
  FROM sellers GROUP BY user_name,category_name),
raw AS (
  SELECT a.user_name,a.ref_id,a.category_name,a.sub_source_name,a.imp,a.clk,a.conv,a.cvr,
    b.bi,b.bc,b.bv,b.sellers,(b.bi IS NULL OR b.sellers<10) needs_manual,
    (CASE WHEN a.imp>=b.bi THEN 'H' ELSE 'L' END)
    ||(CASE WHEN a.clk>=b.bc THEN 'H' ELSE 'L' END)
    ||(CASE WHEN a.clk=0 THEN 'L' WHEN a.conv>a.clk THEN 'H' WHEN a.cvr>=b.bv THEN 'H' ELSE 'L' END) rawc
  FROM ph_asins a LEFT JOIN bm b ON a.user_name=b.user_name AND a.category_name=b.category_name)
SELECT user_name,ref_id,category_name,
  CASE sub_source_name WHEN 'amazon Ledsone' THEN 'LEDSone UK' WHEN 'amazon Dcvoltage' THEN 'DCVoltage UK' ELSE sub_source_name END account,
  sub_source_name,imp,clk,conv,cvr,bi,bc,bv,sellers,needs_manual,rawc,
  CASE rawc WHEN 'HLL' THEN 'HLH' WHEN 'LHL' THEN 'HHL' ELSE rawc END segment,
  CASE CASE rawc WHEN 'HLL' THEN 'HLH' WHEN 'LHL' THEN 'HHL' ELSE rawc END
    WHEN 'HHH' THEN 3 WHEN 'HHL' THEN 2 WHEN 'HLH' THEN 2 WHEN 'LHH' THEN 2 WHEN 'LLH' THEN 1 ELSE 0 END hcount
FROM raw;

-- PREVIOUS window = rn 2  (same logic, only ref_id/segment/hcount kept)
DROP TABLE IF EXISTS analytics._ph_prev;
CREATE TABLE analytics._ph_prev AS
WITH win AS (SELECT period_start, period_end FROM analytics._ph_windows WHERE rn=2),
ph_asins AS (
  SELECT s.user_name,s.ref_id,s.category_name,s.sub_source_name,
         s.impression_count imp,s.click_count clk,s.conversion_count conv,
         CASE WHEN s.click_count>0 THEN s.conversion_count::numeric/s.click_count ELSE 0 END cvr
  FROM analytics.ph_segment_30days_window s, win
  WHERE s.period_end=win.period_end AND s.which_channel=1 AND s.market_place='UK'),
units AS (
  SELECT o."asin", SUM(COALESCE(o."quantity",0)) u
  FROM public.order_transaction o, win
  WHERE o."source_name"='AMAZON' AND o."market_place"='UK' AND o."order_status"='Completed' AND o."fba_sales"=false  -- FBM only (protocol scope)
    AND o."order_date"::date >= win.period_start AND o."order_date"::date <= win.period_end
  GROUP BY o."asin"),
sellers AS (
  SELECT a.user_name,a.category_name,a.ref_id,a.imp,a.clk,a.cvr,
    ROW_NUMBER() OVER (PARTITION BY a.user_name,a.category_name ORDER BY u.u DESC,a.imp DESC) rnk,
    COUNT(*) OVER (PARTITION BY a.user_name,a.category_name) scnt
  FROM ph_asins a JOIN units u ON a.ref_id=u.asin AND u.u>0),
bm AS (
  SELECT user_name,category_name,
    AVG(imp) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bi,
    AVG(clk) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bc,
    AVG(cvr) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bv
  FROM sellers GROUP BY user_name,category_name),
raw AS (
  SELECT a.ref_id,a.sub_source_name,
    (CASE WHEN a.imp>=b.bi THEN 'H' ELSE 'L' END)
    ||(CASE WHEN a.clk>=b.bc THEN 'H' ELSE 'L' END)
    ||(CASE WHEN a.clk=0 THEN 'L' WHEN a.conv>a.clk THEN 'H' WHEN a.cvr>=b.bv THEN 'H' ELSE 'L' END) rawc
  FROM ph_asins a LEFT JOIN bm b ON a.user_name=b.user_name AND a.category_name=b.category_name)
SELECT ref_id,sub_source_name,
  CASE rawc WHEN 'HLL' THEN 'HLH' WHEN 'LHL' THEN 'HHL' ELSE rawc END prev_segment,
  CASE CASE rawc WHEN 'HLL' THEN 'HLH' WHEN 'LHL' THEN 'HHL' ELSE rawc END
    WHEN 'HHH' THEN 3 WHEN 'HHL' THEN 2 WHEN 'HLH' THEN 2 WHEN 'LHH' THEN 2 WHEN 'LLH' THEN 1 ELSE 0 END prev_hcount
FROM raw;

-- ---- final report table (movement + SKU + report_period label) ------------
DROP TABLE IF EXISTS analytics.ph_segment_report;
CREATE TABLE analytics.ph_segment_report AS
WITH cur_end AS (SELECT period_end FROM analytics._ph_windows WHERE rn=1),
sku_pick AS (
  SELECT asin,sku,ROW_NUMBER() OVER (PARTITION BY asin ORDER BY SUM(COALESCE(quantity,0)) DESC) rn
  FROM public.order_transaction
  WHERE "source_name"='AMAZON' AND "market_place"='UK' AND "fba_sales"=false AND sku IS NOT NULL
  GROUP BY asin,sku)
SELECT TO_CHAR((SELECT period_end FROM cur_end)+1,'YYYY-MM') AS report_period,
  c.user_name,c.ref_id AS asin,s.sku,c.account,c.category_name,
  c.imp AS impression,c.clk AS click,c.conv AS conversion,(c.cvr*100)::numeric(10,2) cvr_pct,
  c.bi::numeric(10,0) bm_impression,c.bc::numeric(10,1) bm_click,(c.bv*100)::numeric(10,2) bm_cvr_pct,
  c.sellers benchmark_sellers,c.needs_manual,c.segment,p.prev_segment,
  CASE WHEN p.prev_segment IS NULL THEN 'NEW'
       WHEN c.hcount>p.prev_hcount THEN 'IMPROVED'
       WHEN c.hcount<p.prev_hcount THEN 'DECLINED' ELSE 'SAME' END movement
FROM analytics._ph_cur c
LEFT JOIN analytics._ph_prev p ON c.ref_id=p.ref_id AND c.sub_source_name=p.sub_source_name
LEFT JOIN sku_pick s ON c.ref_id=s.asin AND s.rn=1;

DROP TABLE IF EXISTS analytics._ph_cur;
DROP TABLE IF EXISTS analytics._ph_prev;
DROP TABLE IF EXISTS analytics._ph_windows;
