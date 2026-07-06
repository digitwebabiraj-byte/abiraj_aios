-- =====================================================================
-- PH ASIN SEGMENTATION — OPTION A: MOVEMENT-WINDOW FIX (previous-window only)
-- Redefines the PREVIOUS window as the last 4 COMPLETE weeks (Saturday-ending),
-- leaving the CURRENT month's segments/signals/benchmarks EXACTLY as published.
-- Only prev_segment + movement are recomputed → dashboard segment counts unchanged.
--
-- STATUS: READY — DO NOT RUN until Bietrick approves Option A (sign-off gate).
-- SAFETY: backup-first; reversible; verify-after. Read the whole file before running.
-- SCOPE:  UK · which_channel=1 · FBM (fba_sales=false). Logic unchanged; only the
--         previous window's date boundaries move from "calendar May" to "4 weeks".
-- =====================================================================

-- ---------------------------------------------------------------------
-- STEP 0 — BACKUP FIRST (run before any change)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS analytics.ph_segment_report_backup_optA;
CREATE TABLE analytics.ph_segment_report_backup_optA AS
SELECT * FROM analytics.ph_segment_report;   -- restore point for prev_segment/movement

-- ---------------------------------------------------------------------
-- STEP 1 — Compute the 4-complete-week PREVIOUS segment per ASIN
--          (weeks 5–8 back = the 4 weeks before the current 4)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS analytics._ph_prev4;
CREATE TABLE analytics._ph_prev4 AS
WITH sats AS (
  SELECT date, ROW_NUMBER() OVER (ORDER BY date DESC) rn
  FROM (SELECT DISTINCT date FROM public.traffic_data
        WHERE which_channel=1 AND market_place='UK') d),
prv_w   AS (SELECT date FROM sats WHERE rn BETWEEN 5 AND 8),          -- previous 4 complete weeks
prv_span AS (SELECT min(date)-6 d0, max(date) d1 FROM prv_w),         -- sales window aligned to those weeks
-- category/account map (stable across windows — verified 7,958/7,958 identical)
catmap AS (
  SELECT user_name, ref_id,
         CASE sub_source_name WHEN 'amazon Ledsone' THEN 'LEDSone UK'
              WHEN 'amazon Dcvoltage' THEN 'DCVoltage UK' ELSE sub_source_name END account,
         max(category_name) cat
  FROM analytics.ph_segment_30days_window
  WHERE period_end IN (DATE '2026-06-30', DATE '2026-05-30')
    AND which_channel=1 AND market_place='UK'
  GROUP BY 1,2,3),
acct AS (SELECT DISTINCT sub_source_name,
         CASE sub_source_name WHEN 'amazon Ledsone' THEN 'LEDSone UK'
              WHEN 'amazon Dcvoltage' THEN 'DCVoltage UK' ELSE sub_source_name END account
         FROM public.traffic_data),
sig AS (  -- previous-window signals per ASIN (summed over the 4 previous weeks)
  SELECT t.user_name, t.ref_id, a.account,
         SUM(t.impression) imp, SUM(t.click) clk, SUM(t.conversion) conv,
         CASE WHEN SUM(t.click)>0 THEN SUM(t.conversion)::numeric/SUM(t.click) ELSE 0 END cvr
  FROM public.traffic_data t JOIN acct a ON a.sub_source_name=t.sub_source_name
  WHERE t.which_channel=1 AND t.market_place='UK' AND t.date IN (SELECT date FROM prv_w)
  GROUP BY 1,2,3),
sigc AS (SELECT sig.*, cm.cat FROM sig JOIN catmap cm
           ON cm.user_name=sig.user_name AND cm.ref_id=sig.ref_id AND cm.account=sig.account),
units AS (  -- FBM units per ASIN over the aligned previous sales window
  SELECT o.asin, SUM(COALESCE(o.quantity,0)) u
  FROM public.order_transaction o, prv_span
  WHERE o.source_name='AMAZON' AND o.market_place='UK' AND o.order_status='Completed'
    AND o.fba_sales=false AND o.order_date::date BETWEEN prv_span.d0 AND prv_span.d1
  GROUP BY o.asin),
sellers AS (
  SELECT sigc.*, ROW_NUMBER() OVER (PARTITION BY user_name,cat ORDER BY u.u DESC, sigc.imp DESC) rnk,
         COUNT(*) OVER (PARTITION BY user_name,cat) scnt
  FROM sigc JOIN units u ON u.asin=sigc.ref_id AND u.u>0),
bm AS (
  SELECT user_name,cat,
    AVG(imp) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bi,
    AVG(clk) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bc,
    AVG(cvr) FILTER (WHERE rnk<=CASE WHEN scnt>=30 THEN 30 ELSE 10 END) bv
  FROM sellers GROUP BY 1,2)
SELECT sigc.user_name, sigc.ref_id, sigc.account,
  CASE rawc WHEN 'HLL' THEN 'HLH' WHEN 'LHL' THEN 'HHL' ELSE rawc END AS prev_segment,
  CASE CASE rawc WHEN 'HLL' THEN 'HLH' WHEN 'LHL' THEN 'HHL' ELSE rawc END
    WHEN 'HHH' THEN 3 WHEN 'HHL' THEN 2 WHEN 'HLH' THEN 2 WHEN 'LHH' THEN 2 WHEN 'LLH' THEN 1 ELSE 0 END AS prev_h
FROM (SELECT sigc.*,
        (CASE WHEN sigc.imp>=b.bi THEN 'H' ELSE 'L' END)
      ||(CASE WHEN sigc.clk>=b.bc THEN 'H' ELSE 'L' END)
      ||(CASE WHEN sigc.clk=0 THEN 'L' WHEN sigc.conv>sigc.clk THEN 'H'
              WHEN sigc.cvr>=b.bv THEN 'H' ELSE 'L' END) rawc
      FROM sigc LEFT JOIN bm b ON b.user_name=sigc.user_name AND b.cat=sigc.cat) sigc;

-- ---------------------------------------------------------------------
-- STEP 2 — Recompute prev_segment + movement on the live report
--          (current segment/signals/benchmarks are LEFT UNTOUCHED)
-- ---------------------------------------------------------------------
UPDATE analytics.ph_segment_report r
SET prev_segment = p.prev_segment,
    movement = CASE
        WHEN p.prev_h IS NULL THEN 'NEW'
        WHEN (CASE r.segment WHEN 'HHH' THEN 3 WHEN 'HHL' THEN 2 WHEN 'HLH' THEN 2
                             WHEN 'LHH' THEN 2 WHEN 'LLH' THEN 1 ELSE 0 END) > p.prev_h THEN 'IMPROVED'
        WHEN (CASE r.segment WHEN 'HHH' THEN 3 WHEN 'HHL' THEN 2 WHEN 'HLH' THEN 2
                             WHEN 'LHH' THEN 2 WHEN 'LLH' THEN 1 ELSE 0 END) < p.prev_h THEN 'DECLINED'
        ELSE 'SAME' END
FROM analytics._ph_prev4 p
WHERE r.report_period='2026-07'
  AND p.user_name=r.user_name AND p.ref_id=r.asin AND p.account=r.account;

-- ASINs with no previous-window row at all → NEW
UPDATE analytics.ph_segment_report r
SET movement='NEW', prev_segment=NULL
WHERE r.report_period='2026-07'
  AND NOT EXISTS (SELECT 1 FROM analytics._ph_prev4 p
                  WHERE p.user_name=r.user_name AND p.ref_id=r.asin AND p.account=r.account);

DROP TABLE IF EXISTS analytics._ph_prev4;

-- ---------------------------------------------------------------------
-- STEP 3 — VERIFY (expected: current segments unchanged; movement fairer)
-- ---------------------------------------------------------------------
SELECT
  (SELECT count(*) FROM analytics.ph_segment_report WHERE report_period='2026-07') AS rows,
  -- current segment counts MUST match the published dashboard (unchanged):
  (SELECT jsonb_object_agg(segment,c)::text FROM
     (SELECT segment,count(*) c FROM analytics.ph_segment_report
      WHERE report_period='2026-07' GROUP BY segment) x) AS segment_counts_should_be_unchanged,
  -- movement after the fair window:
  (SELECT jsonb_object_agg(movement,c)::text FROM
     (SELECT movement,count(*) c FROM analytics.ph_segment_report
      WHERE report_period='2026-07' GROUP BY movement) y) AS movement_after_fix,
  -- escalation after fix (declined PHs):
  (SELECT count(*) FROM (SELECT user_name FROM analytics.ph_segment_report
     WHERE report_period='2026-07' GROUP BY user_name
     HAVING count(*) FILTER(WHERE movement='DECLINED')>5) z) AS declined_PHs_after_fix;

-- ---------------------------------------------------------------------
-- STEP 4 — (after verify OK) rebuild id 5 HTML so movement chips update.
--   Reuse the existing server-side build: reset shell via
--   regexp_replace(html_content,'const D=[^\n]*;','const D=__DATA__;')
--   then the standard replace(__DATA__, <jsonb from ph_segment_report>).
--   (Segment counts unchanged; only movement chips + escalation banner change.)
-- ---------------------------------------------------------------------

-- ROLLBACK (if needed): restore prev_segment/movement from the backup
--   UPDATE analytics.ph_segment_report r
--   SET prev_segment=b.prev_segment, movement=b.movement
--   FROM analytics.ph_segment_report_backup_optA b
--   WHERE r.report_period=b.report_period AND r.asin=b.asin AND r.account=b.account;
