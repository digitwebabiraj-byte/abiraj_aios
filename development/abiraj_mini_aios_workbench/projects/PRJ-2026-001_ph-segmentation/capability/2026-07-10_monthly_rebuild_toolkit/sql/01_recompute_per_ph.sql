-- *** CONVERSION RULE = COUNT-BASED (Bietrick-approved 2026-07-10) ***
-- The 3rd signal (Conversion) is now scored the SAME way as Impressions & Clicks: HIGH if the
-- ASIN's conversion COUNT >= the category Avg-conv count (a.conv >= b.bcv), else LOW. This
-- REPLACED the old CVR-RATE rule, which was (kept here for audit / revert):
--   (CASE WHEN a.clk=0 THEN 'L' WHEN a.conv>a.clk THEN 'H' WHEN a.cvr>=b.bv THEN 'H' ELSE 'L' END)
-- NOTE: the LIVE 2026-07 (D10) dashboards were built with the OLD rate rule. Re-running this
-- count-based engine WILL re-segment some ASINs (HHL Leaky Buckets -> HHH Champions) and produce a
-- DIFFERENT distribution than the D10 build (42/580/173/10/626/8516). STORED, not executed here.
-- See capability/2026-07-10_proposed-rule-change-conversion-signal.md. Undefined-combo map
-- (HLL->HLH, LHL->HHL) UNCHANGED. bv (CVR benchmark) is still computed for DISPLAY only.
WITH
sats AS (SELECT date, ROW_NUMBER() OVER (ORDER BY date DESC) rn FROM (SELECT DISTINCT date FROM public.traffic_data WHERE which_channel=1 AND market_place='UK') d),
cw AS (SELECT date d FROM sats WHERE rn BETWEEN 2 AND 5),
pw AS (SELECT date d FROM sats WHERE rn BETWEEN 6 AND 9),
rw AS (SELECT date d FROM sats WHERE rn BETWEEN 10 AND 13),
pick AS (SELECT unnest(ARRAY['__PHNAME__']) AS un),
csig AS (SELECT user_name,ref_id,sub_source_name,SUM(impression) imp,SUM(click) clk,SUM(conversion) conv,CASE WHEN SUM(click)>0 THEN SUM(conversion)::numeric/SUM(click) ELSE 0 END cvr FROM public.traffic_data WHERE which_channel=1 AND market_place='UK' AND user_name IN (SELECT un FROM pick) AND date IN (SELECT d FROM cw) GROUP BY 1,2,3),
ccat AS (SELECT user_name,ref_id,sub_source_name,category_name,ROW_NUMBER() OVER (PARTITION BY user_name,ref_id,sub_source_name ORDER BY SUM(impression) DESC,category_name) rn FROM public.traffic_data WHERE which_channel=1 AND market_place='UK' AND user_name IN (SELECT un FROM pick) AND date IN (SELECT d FROM cw) GROUP BY 1,2,3,4),
ca AS (SELECT s.user_name,s.ref_id,c.category_name,s.sub_source_name,s.imp,s.clk,s.conv,s.cvr FROM csig s JOIN ccat c ON c.user_name=s.user_name AND c.ref_id=s.ref_id AND c.sub_source_name=s.sub_source_name AND c.rn=1),
cu AS (SELECT o.asin,SUM(COALESCE(o.quantity,0)) u FROM public.order_transaction o WHERE o.source_name='AMAZON' AND o.market_place='UK' AND o.order_status='Completed' AND o.fba_sales=false AND o.order_date>=(SELECT MIN(d)-6 FROM cw) AND o.order_date<(SELECT MAX(d)+1 FROM cw) AND o.asin IN (SELECT ref_id FROM ca) GROUP BY o.asin),
cse AS (SELECT a.user_name,a.category_name,a.ref_id,a.imp,a.clk,a.conv,a.cvr,ROW_NUMBER() OVER (PARTITION BY a.user_name,a.category_name ORDER BY u.u DESC,a.imp DESC) rnk,COUNT(*) OVER (PARTITION BY a.user_name,a.category_name) scnt FROM ca a JOIN cu u ON a.ref_id=u.asin AND u.u>0),
cbm AS (SELECT user_name,category_name,MAX(scnt) scnt,AVG(imp) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bi,AVG(clk) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bk,AVG(conv) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bcv,AVG(cvr) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bv FROM cse GROUP BY user_name,category_name),
ccls AS (SELECT a.user_name,a.ref_id,a.sub_source_name,a.category_name,a.imp,a.clk,a.conv,a.cvr,b.bi,b.bk,b.bv,(CASE WHEN a.imp>=b.bi THEN 'H' ELSE 'L' END)||(CASE WHEN a.clk>=b.bk THEN 'H' ELSE 'L' END)||(CASE WHEN a.conv>=b.bcv THEN 'H' ELSE 'L' END) rawc FROM ca a LEFT JOIN cbm b ON a.user_name=b.user_name AND a.category_name=b.category_name),
cfin AS (SELECT user_name,ref_id,sub_source_name,category_name,imp,clk,conv,cvr,bi,bk,bv,CASE rawc WHEN 'HLL' THEN 'HLH' WHEN 'LHL' THEN 'HHL' ELSE rawc END seg,CASE CASE rawc WHEN 'HLL' THEN 'HLH' WHEN 'LHL' THEN 'HHL' ELSE rawc END WHEN 'HHH' THEN 1 WHEN 'HHL' THEN 2 WHEN 'HLH' THEN 3 WHEN 'LHH' THEN 4 WHEN 'LLH' THEN 5 ELSE 6 END srank FROM ccls),
psig AS (SELECT user_name,ref_id,sub_source_name,SUM(impression) imp,SUM(click) clk,SUM(conversion) conv,CASE WHEN SUM(click)>0 THEN SUM(conversion)::numeric/SUM(click) ELSE 0 END cvr FROM public.traffic_data WHERE which_channel=1 AND market_place='UK' AND user_name IN (SELECT un FROM pick) AND date IN (SELECT d FROM pw) GROUP BY 1,2,3),
pcat AS (SELECT user_name,ref_id,sub_source_name,category_name,ROW_NUMBER() OVER (PARTITION BY user_name,ref_id,sub_source_name ORDER BY SUM(impression) DESC,category_name) rn FROM public.traffic_data WHERE which_channel=1 AND market_place='UK' AND user_name IN (SELECT un FROM pick) AND date IN (SELECT d FROM pw) GROUP BY 1,2,3,4),
pa AS (SELECT s.user_name,s.ref_id,c.category_name,s.sub_source_name,s.imp,s.clk,s.conv,s.cvr FROM psig s JOIN pcat c ON c.user_name=s.user_name AND c.ref_id=s.ref_id AND c.sub_source_name=s.sub_source_name AND c.rn=1),
pu AS (SELECT o.asin,SUM(COALESCE(o.quantity,0)) u FROM public.order_transaction o WHERE o.source_name='AMAZON' AND o.market_place='UK' AND o.order_status='Completed' AND o.fba_sales=false AND o.order_date>=(SELECT MIN(d)-6 FROM pw) AND o.order_date<(SELECT MAX(d)+1 FROM pw) AND o.asin IN (SELECT ref_id FROM pa) GROUP BY o.asin),
pse AS (SELECT a.user_name,a.category_name,a.ref_id,a.imp,a.clk,a.conv,a.cvr,ROW_NUMBER() OVER (PARTITION BY a.user_name,a.category_name ORDER BY u.u DESC,a.imp DESC) rnk,COUNT(*) OVER (PARTITION BY a.user_name,a.category_name) scnt FROM pa a JOIN pu u ON a.ref_id=u.asin AND u.u>0),
pbm AS (SELECT user_name,category_name,AVG(imp) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bi,AVG(clk) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bk,AVG(conv) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bcv,AVG(cvr) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bv FROM pse GROUP BY user_name,category_name),
pcls AS (SELECT a.ref_id,a.sub_source_name,(CASE WHEN a.imp>=b.bi THEN 'H' ELSE 'L' END)||(CASE WHEN a.clk>=b.bk THEN 'H' ELSE 'L' END)||(CASE WHEN a.conv>=b.bcv THEN 'H' ELSE 'L' END) rawc FROM pa a LEFT JOIN pbm b ON a.user_name=b.user_name AND a.category_name=b.category_name),
pfin AS (SELECT ref_id,sub_source_name,CASE CASE rawc WHEN 'HLL' THEN 'HLH' WHEN 'LHL' THEN 'HHL' ELSE rawc END WHEN 'HHH' THEN 1 WHEN 'HHL' THEN 2 WHEN 'HLH' THEN 3 WHEN 'LHH' THEN 4 WHEN 'LLH' THEN 5 ELSE 6 END prev_srank FROM pcls),
prior AS (SELECT DISTINCT ref_id,sub_source_name FROM public.traffic_data WHERE which_channel=1 AND market_place='UK' AND user_name IN (SELECT un FROM pick) AND date IN (SELECT d FROM rw)),
sku AS (SELECT asin,sku FROM (SELECT o.asin,o.sku,ROW_NUMBER() OVER (PARTITION BY o.asin ORDER BY SUM(COALESCE(o.quantity,0)) DESC) rn FROM public.order_transaction o WHERE o.source_name='AMAZON' AND o.market_place='UK' AND o.fba_sales=false AND o.sku IS NOT NULL AND o.asin IN (SELECT ref_id FROM ca) GROUP BY o.asin,o.sku) t WHERE rn=1),
rows_final AS (
  SELECT c.user_name,c.category_name,c.seg,
    CASE WHEN p.prev_srank IS NOT NULL THEN CASE WHEN c.srank<p.prev_srank THEN 'IMPROVED' WHEN c.srank>p.prev_srank THEN 'DECLINED' ELSE 'SAME' END WHEN pr.ref_id IS NOT NULL THEN 'SAME' ELSE 'NEW' END mov,
    c.ref_id,sk.sku,CASE WHEN c.sub_source_name='amazon Ledsone' THEN 1 ELSE 0 END acc,
    c.imp,c.clk,c.conv,round((c.cvr*100)::numeric,1) cvr,round(c.bi::numeric,0) bi,round(c.bk::numeric,1) bk,round((c.bv*100)::numeric,1) bcvr,
    ROW_NUMBER() OVER (PARTITION BY c.user_name ORDER BY c.imp DESC,c.ref_id) rank
  FROM cfin c LEFT JOIN pfin p ON c.ref_id=p.ref_id AND c.sub_source_name=p.sub_source_name LEFT JOIN prior pr ON c.ref_id=pr.ref_id AND c.sub_source_name=pr.sub_source_name LEFT JOIN sku sk ON sk.asin=c.ref_id),
cats_final AS (SELECT a.user_name,a.category_name,COUNT(*) listings,COALESCE(MAX(b.scnt),0) scnt,round(MAX(b.bi)::numeric,0) bi,round(MAX(b.bk)::numeric,1) bk,round((MAX(b.bv)*100)::numeric,1) bcvr,round(MAX(b.bcv)::numeric,2) bconv FROM ca a LEFT JOIN cbm b ON a.user_name=b.user_name AND a.category_name=b.category_name GROUP BY a.user_name,a.category_name)
SELECT
 (SELECT count(*) FROM rows_final) AS nrows,
 (SELECT json_agg(json_build_array(user_name,category_name,seg,mov,ref_id,sku,acc,imp,clk,conv,cvr,bi,bk,bcvr,rank)) FROM rows_final) AS rows,
 (SELECT json_agg(json_build_array(user_name,category_name,listings,CASE WHEN scnt>=30 THEN 30 WHEN scnt>=10 THEN 10 ELSE scnt END,bi,bk,bcvr,CASE WHEN scnt>=30 THEN 'FULL_TOP_30' WHEN scnt>=10 THEN 'TOP_10' ELSE 'NEEDS_MANUAL' END,bconv)) FROM cats_final) AS cats;