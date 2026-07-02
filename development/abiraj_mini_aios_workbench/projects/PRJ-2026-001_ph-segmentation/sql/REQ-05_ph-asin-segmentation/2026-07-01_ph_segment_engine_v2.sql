-- ============================================================================
-- PH ASIN SEGMENTATION — MONTHLY ENGINE  (v2: last 4 COMPLETE weeks)
-- ----------------------------------------------------------------------------
-- WINDOW (changed in v2): traffic_data is WEEKLY (each row = one week, dated on
-- the week-ending Saturday). A calendar month catches a VARIABLE number of weeks
-- (e.g. May=5, June=4), which made month-over-month movement unfair. v2 fixes
-- this: CURRENT = the last 4 complete weeks, PREVIOUS = the 4 weeks before that,
-- so both sides are always equal length. Self-contained on public.traffic_data
-- (+ public.order_transaction for units); does NOT depend on the monthly window
-- table. Category per ASIN = its max-impression category in the window (verified
-- 8,149/8,149 identical to the old window-table assignment).
--
-- LOCKED DECISIONS (unchanged): Method A CVR (avg of per-ASIN CVR over top-N sold);
-- zero-click -> LOW conversion ; conversions>clicks -> HIGH conversion ;
-- undefined combos mapped HLL->HLH , LHL->HHL ; scope = which_channel=1, UK,
-- FBM only (fba_sales=false) ; benchmark = avg Imp/Clk/CVR over top-30 sold
-- (top-10 if <30 ; needs_manual if <10) ; movement by h-count
-- (HHH=3, HHL/HLH/LHH=2, LLH=1, LLL=0) ; account from sub_source_name ;
-- ownership read from user_name (orphans, user_name NULL, are excluded here and
-- surfaced separately by analytics.v_orphan_asins).
--
-- MOVEMENT / NEW RULE (returning-aware, equal 4-week windows):
--   IMPROVED = current h-count > previous h-count ; DECLINED = < ; SAME = equal.
--   NEW      = ASIN present in the current 4 weeks but absent from the previous
--              8 weeks (both the previous 4 weeks AND the 4 weeks before that).
--   RETURNING (absent from the previous 4 weeks but active in the 4 before that)
--              is labelled SAME, NOT NEW -- a product that reappears after a gap
--              is not a new product. This generalises the one-time transition
--              patch applied to the 2026-07 live report into a permanent rule.
--
-- Re-run as-is every month (schedule: 3rd, after prior-month weeks have loaded).
-- No dates to edit. SAFE: ABORT-IF-EMPTY guards stop the script BEFORE dropping
-- ph_segment_report, so an empty/under-loaded source can never wipe it.
-- ============================================================================

-- ---- resolve the last 8 complete weeks (Saturdays) from the weekly source ----
DROP TABLE IF EXISTS analytics._ph_sats;
CREATE TABLE analytics._ph_sats AS
SELECT date, ROW_NUMBER() OVER (ORDER BY date DESC) AS rn
FROM (SELECT DISTINCT date FROM public.traffic_data
      WHERE which_channel=1 AND market_place='UK') d;

-- ---- ABORT-IF-EMPTY GUARD (1/2): need at least 8 complete weeks --------------
DO $ph_guard1$
BEGIN
  IF (SELECT count(*) FROM analytics._ph_sats WHERE rn<=8) < 8 THEN
    RAISE EXCEPTION 'PH ENGINE ABORT: fewer than 8 weekly snapshots in public.traffic_data (need last-4 + previous-4). Existing analytics.ph_segment_report left untouched.';
  END IF;
END
$ph_guard1$;

-- ============================================================================
-- CURRENT window  = weeks rn 1..4
-- ============================================================================
DROP TABLE IF EXISTS analytics._ph_cur;
CREATE TABLE analytics._ph_cur AS
WITH weeks AS (SELECT date FROM analytics._ph_sats WHERE rn BETWEEN 1 AND 4),
span AS (SELECT min(date)-6 AS d0, max(date) AS d1 FROM weeks),
sig AS (  -- summed weekly signals per owned ASIN (across categories)
  SELECT user_name, ref_id, sub_source_name,
         SUM(impression) imp, SUM(click) clk, SUM(conversion) conv,
         CASE WHEN SUM(click)>0 THEN SUM(conversion)::numeric/SUM(click) ELSE 0 END cvr
  FROM public.traffic_data
  WHERE which_channel=1 AND market_place='UK' AND user_name IS NOT NULL
    AND date IN (SELECT date FROM weeks)
  GROUP BY 1,2,3),
cat AS (  -- one category per ASIN = the max-impression category in this window
  SELECT user_name, ref_id, sub_source_name, category_name,
         ROW_NUMBER() OVER (PARTITION BY user_name,ref_id,sub_source_name
                            ORDER BY SUM(impression) DESC, category_name) rn
  FROM public.traffic_data
  WHERE which_channel=1 AND market_place='UK' AND user_name IS NOT NULL
    AND date IN (SELECT date FROM weeks)
  GROUP BY 1,2,3,4),
ph_asins AS (
  SELECT sig.user_name, sig.ref_id, c.category_name, sig.sub_source_name,
         sig.imp, sig.clk, sig.conv, sig.cvr
  FROM sig JOIN cat c
    ON c.user_name=sig.user_name AND c.ref_id=sig.ref_id
   AND c.sub_source_name=sig.sub_source_name AND c.rn=1),
units AS (  -- FBM units over the window-aligned sales span
  SELECT o."asin", SUM(COALESCE(o."quantity",0)) AS u
  FROM public.order_transaction o, span
  WHERE o."source_name"='AMAZON' AND o."market_place"='UK' AND o."order_status"='Completed' AND o."fba_sales"=false
    AND o."order_date"::date >= span.d0 AND o."order_date"::date <= span.d1
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
    WHEN 'HHH' THEN 3 WHEN 'HHL' THEN 2 WHEN 'HLH' THEN 2 WHEN 'LHH' THEN 2 WHEN 'LLH' THEN 1 ELSE 0 END hcount,
  (SELECT max(date) FROM weeks) AS window_end,
  (SELECT min(date)-6 FROM weeks) AS window_start
FROM raw;

-- ============================================================================
-- PREVIOUS window = weeks rn 5..8  (same logic; only ref_id/segment/hcount kept)
-- ============================================================================
DROP TABLE IF EXISTS analytics._ph_prev;
CREATE TABLE analytics._ph_prev AS
WITH weeks AS (SELECT date FROM analytics._ph_sats WHERE rn BETWEEN 5 AND 8),
span AS (SELECT min(date)-6 AS d0, max(date) AS d1 FROM weeks),
sig AS (
  SELECT user_name, ref_id, sub_source_name,
         SUM(impression) imp, SUM(click) clk, SUM(conversion) conv,
         CASE WHEN SUM(click)>0 THEN SUM(conversion)::numeric/SUM(click) ELSE 0 END cvr
  FROM public.traffic_data
  WHERE which_channel=1 AND market_place='UK' AND user_name IS NOT NULL
    AND date IN (SELECT date FROM weeks)
  GROUP BY 1,2,3),
cat AS (
  SELECT user_name, ref_id, sub_source_name, category_name,
         ROW_NUMBER() OVER (PARTITION BY user_name,ref_id,sub_source_name
                            ORDER BY SUM(impression) DESC, category_name) rn
  FROM public.traffic_data
  WHERE which_channel=1 AND market_place='UK' AND user_name IS NOT NULL
    AND date IN (SELECT date FROM weeks)
  GROUP BY 1,2,3,4),
ph_asins AS (
  SELECT sig.user_name, sig.ref_id, c.category_name, sig.sub_source_name,
         sig.imp, sig.clk, sig.conv, sig.cvr
  FROM sig JOIN cat c
    ON c.user_name=sig.user_name AND c.ref_id=sig.ref_id
   AND c.sub_source_name=sig.sub_source_name AND c.rn=1),
units AS (
  SELECT o."asin", SUM(COALESCE(o."quantity",0)) AS u
  FROM public.order_transaction o, span
  WHERE o."source_name"='AMAZON' AND o."market_place"='UK' AND o."order_status"='Completed' AND o."fba_sales"=false
    AND o."order_date"::date >= span.d0 AND o."order_date"::date <= span.d1
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
  SELECT a.user_name,a.ref_id,a.category_name,a.sub_source_name,a.imp,a.clk,a.conv,a.cvr,
    (CASE WHEN a.imp>=b.bi THEN 'H' ELSE 'L' END)
    ||(CASE WHEN a.clk>=b.bc THEN 'H' ELSE 'L' END)
    ||(CASE WHEN a.clk=0 THEN 'L' WHEN a.conv>a.clk THEN 'H' WHEN a.cvr>=b.bv THEN 'H' ELSE 'L' END) rawc
  FROM ph_asins a LEFT JOIN bm b ON a.user_name=b.user_name AND a.category_name=b.category_name)
SELECT ref_id,sub_source_name,
  CASE rawc WHEN 'HLL' THEN 'HLH' WHEN 'LHL' THEN 'HHL' ELSE rawc END prev_segment,
  CASE CASE rawc WHEN 'HLL' THEN 'HLH' WHEN 'LHL' THEN 'HHL' ELSE rawc END
    WHEN 'HHH' THEN 3 WHEN 'HHL' THEN 2 WHEN 'HLH' THEN 2 WHEN 'LHH' THEN 2 WHEN 'LLH' THEN 1 ELSE 0 END prev_hcount
FROM raw;

-- ---- prior presence (weeks 9-12) for the returning-aware NEW rule -----------
-- An ASIN absent from the previous 4 weeks (5-8) but active in the 4 weeks
-- before that (9-12) is RETURNING, not NEW. We only need its presence here
-- (not a full re-classification), so this stays cheap.
DROP TABLE IF EXISTS analytics._ph_prior;
CREATE TABLE analytics._ph_prior AS
SELECT DISTINCT ref_id, sub_source_name
FROM public.traffic_data
WHERE which_channel=1 AND market_place='UK' AND user_name IS NOT NULL
  AND date IN (SELECT date FROM analytics._ph_sats WHERE rn BETWEEN 9 AND 12);

-- ---- ABORT-IF-EMPTY GUARD (2/2) ------------------------------------------
DO $ph_guard2$
BEGIN
  IF (SELECT count(*) FROM analytics._ph_cur) = 0 THEN
    RAISE EXCEPTION 'PH ENGINE ABORT: current window produced 0 classified rows. Existing analytics.ph_segment_report left untouched.';
  END IF;
END
$ph_guard2$;

-- ---- final report table (movement + SKU + report_period label + window cols) --
DROP TABLE IF EXISTS analytics.ph_segment_report;
CREATE TABLE analytics.ph_segment_report AS
WITH cur_end AS (SELECT max(window_end) pe FROM analytics._ph_cur),
sku_pick AS (
  SELECT asin,sku,ROW_NUMBER() OVER (PARTITION BY asin ORDER BY SUM(COALESCE(quantity,0)) DESC) rn
  FROM public.order_transaction
  WHERE "source_name"='AMAZON' AND "market_place"='UK' AND "fba_sales"=false AND sku IS NOT NULL
  GROUP BY asin,sku)
SELECT TO_CHAR(date_trunc('month',(SELECT pe FROM cur_end)) + INTERVAL '1 month','YYYY-MM') AS report_period,
  c.user_name,c.ref_id AS asin,s.sku,c.account,c.category_name,
  c.imp AS impression,c.clk AS click,c.conv AS conversion,(c.cvr*100)::numeric(10,2) cvr_pct,
  c.bi::numeric(10,0) bm_impression,c.bc::numeric(10,1) bm_click,(c.bv*100)::numeric(10,2) bm_cvr_pct,
  c.sellers benchmark_sellers,c.needs_manual,c.segment,p.prev_segment,
  CASE
    WHEN p.prev_segment IS NOT NULL THEN
      CASE WHEN c.hcount>p.prev_hcount THEN 'IMPROVED'
           WHEN c.hcount<p.prev_hcount THEN 'DECLINED' ELSE 'SAME' END
    WHEN pr.ref_id IS NOT NULL THEN 'SAME'   -- returning (active in weeks 9-12), not NEW
    ELSE 'NEW' END movement,
  c.window_start, c.window_end
FROM analytics._ph_cur c
LEFT JOIN analytics._ph_prev p ON c.ref_id=p.ref_id AND c.sub_source_name=p.sub_source_name
LEFT JOIN analytics._ph_prior pr ON c.ref_id=pr.ref_id AND c.sub_source_name=pr.sub_source_name
LEFT JOIN sku_pick s ON c.ref_id=s.asin AND s.rn=1;

DROP TABLE IF EXISTS analytics._ph_cur;
DROP TABLE IF EXISTS analytics._ph_prev;
DROP TABLE IF EXISTS analytics._ph_prior;
DROP TABLE IF EXISTS analytics._ph_sats;
