-- ============================================================================
-- 02 — CATEGORY-SPLIT recompute (for a PH too big to run whole)
-- Use this ONLY when 01_recompute_per_ph.sql TIMES OUT for one PH
-- (happened for utharsika = 1578 ASINs on 2026-07-10). A single PH's
-- classification is self-contained PER CATEGORY (benchmark is per PH+category),
-- and 0 ASINs span categories, so you can safely run one category at a time
-- and concatenate the rows. Full movement + sku, same engine logic. READ-ONLY.
--
-- HOW TO USE
--   1) Find the PH's categories + ASIN counts (traffic-only, cheap):
--        WITH cw AS (SELECT unnest(ARRAY[@@CUR_WEEKS@@]::date[]) d)
--        SELECT category_name, count(*) FROM (
--          SELECT ref_id,sub_source_name,category_name,
--                 ROW_NUMBER() OVER (PARTITION BY ref_id,sub_source_name ORDER BY SUM(impression) DESC) rn
--          FROM public.traffic_data
--          WHERE which_channel=1 AND market_place='UK' AND user_name='@@USER@@' AND date IN (SELECT d FROM cw)
--          GROUP BY 1,2,3) t WHERE rn=1 GROUP BY category_name ORDER BY 2 DESC;
--   2) Run THIS query once per category (set @@USER@@ and @@CATEGORY@@), append
--      a `,repeat('x',200000) AS pad` column to force large results to a file.
--   3) Merge the per-category rows in Python, prepend user_name, and recompute
--      the per-PH rank = ROW_NUMBER() by impression DESC across all categories.
--
-- FILL IN (dates = the Saturday week-ending dates in traffic_data):
--   @@CUR_WEEKS@@  last 4 complete weeks e.g. '2026-06-06','2026-06-13','2026-06-20','2026-06-27'
--   @@PREV_WEEKS@@ 4 weeks before that   e.g. '2026-05-09','2026-05-16','2026-05-23','2026-05-30'
--   @@PRIOR_WEEKS@@ 4 weeks before that  e.g. '2026-04-11','2026-04-18','2026-04-25','2026-05-02'
--   @@CUR_SPAN0@@ = min(CUR_WEEKS)-6, @@CUR_SPAN1@@ = max(CUR_WEEKS)+1  (order_date half-open)
--   @@PREV_SPAN0@@= min(PREV_WEEKS)-6, @@PREV_SPAN1@@= max(PREV_WEEKS)+1
-- ----------------------------------------------------------------------------
-- *** CONVERSION RULE = COUNT-BASED (Bietrick-approved 2026-07-10) *** — same change as 01.
-- Conversion = HIGH if a.conv >= b.bcv (category Avg-conv COUNT), else LOW. REPLACED the old CVR-
-- rate rule: (CASE WHEN a.clk=0 THEN 'L' WHEN a.conv>a.clk THEN 'H' WHEN a.cvr>=b.bv THEN 'H' ELSE 'L' END).
-- LIVE D10 dashboards used the OLD rate rule; re-running re-segments. bv kept for DISPLAY only.
-- ============================================================================
WITH
cw AS (SELECT unnest(ARRAY[@@CUR_WEEKS@@]::date[]) d),
pw AS (SELECT unnest(ARRAY[@@PREV_WEEKS@@]::date[]) d),
rw AS (SELECT unnest(ARRAY[@@PRIOR_WEEKS@@]::date[]) d),
csig AS (SELECT ref_id,sub_source_name,SUM(impression) imp,SUM(click) clk,SUM(conversion) conv,CASE WHEN SUM(click)>0 THEN SUM(conversion)::numeric/SUM(click) ELSE 0 END cvr FROM public.traffic_data WHERE which_channel=1 AND market_place='UK' AND user_name='@@USER@@' AND category_name='@@CATEGORY@@' AND date IN (SELECT d FROM cw) GROUP BY 1,2),
ca AS (SELECT ref_id,sub_source_name,imp,clk,conv,cvr FROM csig),
cu AS (SELECT o.asin,SUM(COALESCE(o.quantity,0)) u FROM public.order_transaction o WHERE o.source_name='AMAZON' AND o.market_place='UK' AND o.order_status='Completed' AND o.fba_sales=false AND o.order_date>=DATE '@@CUR_SPAN0@@' AND o.order_date<DATE '@@CUR_SPAN1@@' AND o.asin IN (SELECT ref_id FROM ca) GROUP BY o.asin),
cse AS (SELECT a.ref_id,a.imp,a.clk,a.conv,a.cvr,ROW_NUMBER() OVER (ORDER BY u.u DESC,a.imp DESC) rnk,COUNT(*) OVER () scnt FROM ca a JOIN cu u ON a.ref_id=u.asin AND u.u>0),
cbm AS (SELECT MAX(scnt) scnt,AVG(imp) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bi,AVG(clk) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bk,AVG(conv) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bcv,AVG(cvr) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bv FROM cse),
ccls AS (SELECT a.ref_id,a.sub_source_name,a.imp,a.clk,a.conv,a.cvr,b.bi,b.bk,b.bv,(CASE WHEN a.imp>=b.bi THEN 'H' ELSE 'L' END)||(CASE WHEN a.clk>=b.bk THEN 'H' ELSE 'L' END)||(CASE WHEN a.conv>=b.bcv THEN 'H' ELSE 'L' END) rawc FROM ca a CROSS JOIN cbm b),
cfin AS (SELECT ref_id,sub_source_name,imp,clk,conv,cvr,bi,bk,bv,CASE rawc WHEN 'HLL' THEN 'HLH' WHEN 'LHL' THEN 'HHL' ELSE rawc END seg,CASE CASE rawc WHEN 'HLL' THEN 'HLH' WHEN 'LHL' THEN 'HHL' ELSE rawc END WHEN 'HHH' THEN 1 WHEN 'HHL' THEN 2 WHEN 'HLH' THEN 3 WHEN 'LHH' THEN 4 WHEN 'LLH' THEN 5 ELSE 6 END srank FROM ccls),
psig AS (SELECT ref_id,sub_source_name,SUM(impression) imp,SUM(click) clk,SUM(conversion) conv,CASE WHEN SUM(click)>0 THEN SUM(conversion)::numeric/SUM(click) ELSE 0 END cvr FROM public.traffic_data WHERE which_channel=1 AND market_place='UK' AND user_name='@@USER@@' AND category_name='@@CATEGORY@@' AND date IN (SELECT d FROM pw) GROUP BY 1,2),
pu AS (SELECT o.asin,SUM(COALESCE(o.quantity,0)) u FROM public.order_transaction o WHERE o.source_name='AMAZON' AND o.market_place='UK' AND o.order_status='Completed' AND o.fba_sales=false AND o.order_date>=DATE '@@PREV_SPAN0@@' AND o.order_date<DATE '@@PREV_SPAN1@@' AND o.asin IN (SELECT ref_id FROM psig) GROUP BY o.asin),
pse AS (SELECT a.ref_id,a.imp,a.clk,a.conv,a.cvr,ROW_NUMBER() OVER (ORDER BY u.u DESC,a.imp DESC) rnk,COUNT(*) OVER () scnt FROM psig a JOIN pu u ON a.ref_id=u.asin AND u.u>0),
pbm AS (SELECT AVG(imp) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bi,AVG(clk) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bk,AVG(conv) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bcv,AVG(cvr) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bv FROM pse),
pcls AS (SELECT a.ref_id,a.sub_source_name,(CASE WHEN a.imp>=b.bi THEN 'H' ELSE 'L' END)||(CASE WHEN a.clk>=b.bk THEN 'H' ELSE 'L' END)||(CASE WHEN a.conv>=b.bcv THEN 'H' ELSE 'L' END) rawc FROM psig a CROSS JOIN pbm b),
pfin AS (SELECT ref_id,sub_source_name,CASE CASE rawc WHEN 'HLL' THEN 'HLH' WHEN 'LHL' THEN 'HHL' ELSE rawc END WHEN 'HHH' THEN 1 WHEN 'HHL' THEN 2 WHEN 'HLH' THEN 3 WHEN 'LHH' THEN 4 WHEN 'LLH' THEN 5 ELSE 6 END prev_srank FROM pcls),
prior AS (SELECT DISTINCT ref_id,sub_source_name FROM public.traffic_data WHERE which_channel=1 AND market_place='UK' AND user_name='@@USER@@' AND category_name='@@CATEGORY@@' AND date IN (SELECT d FROM rw)),
sku AS (SELECT asin,sku FROM (SELECT o.asin,o.sku,ROW_NUMBER() OVER (PARTITION BY o.asin ORDER BY SUM(COALESCE(o.quantity,0)) DESC) rn FROM public.order_transaction o WHERE o.source_name='AMAZON' AND o.market_place='UK' AND o.fba_sales=false AND o.sku IS NOT NULL AND o.asin IN (SELECT ref_id FROM ca) GROUP BY o.asin,o.sku) t WHERE rn=1),
rows_final AS (
  SELECT '@@CATEGORY@@'::text category_name,c.seg,
    CASE WHEN p.prev_srank IS NOT NULL THEN CASE WHEN c.srank<p.prev_srank THEN 'IMPROVED' WHEN c.srank>p.prev_srank THEN 'DECLINED' ELSE 'SAME' END WHEN pr.ref_id IS NOT NULL THEN 'SAME' ELSE 'NEW' END mov,
    c.ref_id,sk.sku,CASE WHEN c.sub_source_name='amazon Ledsone' THEN 1 ELSE 0 END acc,
    c.imp,c.clk,c.conv,round((c.cvr*100)::numeric,1) cvr,round(c.bi::numeric,0) bi,round(c.bk::numeric,1) bk,round((c.bv*100)::numeric,1) bcvr
  FROM cfin c LEFT JOIN pfin p ON c.ref_id=p.ref_id AND c.sub_source_name=p.sub_source_name LEFT JOIN prior pr ON c.ref_id=pr.ref_id AND c.sub_source_name=pr.sub_source_name LEFT JOIN sku sk ON sk.asin=c.ref_id),
cats_final AS (SELECT '@@CATEGORY@@'::text category_name,(SELECT count(*) FROM ca) listings,(SELECT COALESCE(MAX(scnt),0) FROM cbm) scnt,(SELECT round(bi::numeric,0) FROM cbm) bi,(SELECT round(bk::numeric,1) FROM cbm) bk,(SELECT round((bv*100)::numeric,1) FROM cbm) bcvr,(SELECT round(bcv::numeric,2) FROM cbm) bconv)
SELECT
 (SELECT json_agg(json_build_array(category_name,seg,mov,ref_id,sku,acc,imp,clk,conv,cvr,bi,bk,bcvr)) FROM rows_final) AS rows,
 (SELECT json_agg(json_build_array(category_name,listings,CASE WHEN scnt>=30 THEN 30 WHEN scnt>=10 THEN 10 ELSE scnt END,bi,bk,bcvr,CASE WHEN scnt>=30 THEN 'FULL_TOP_30' WHEN scnt>=10 THEN 'TOP_10' ELSE 'NEEDS_MANUAL' END,bconv)) FROM cats_final) AS cats;
