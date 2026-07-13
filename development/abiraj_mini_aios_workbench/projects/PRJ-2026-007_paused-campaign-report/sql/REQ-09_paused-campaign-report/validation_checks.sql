-- ============================================================================
-- Paused Campaign Report — validation checks (PRJ-2026-007 / REQ-09-D01)
-- READ-ONLY. Run every build; require agreement with the rendered outputs.
-- 2026-07-13 expected: 33 targets / 32 ASINs; 41 total pauses / 33 still / 8 re-activated.
-- ============================================================================

-- Check 1 — count check (targets / distinct ASINs)
SELECT COUNT(*) AS targets, COUNT(DISTINCT "ASIN") AS asins
FROM (
  WITH util_camp AS (
      SELECT DISTINCT p.parent_id, p.source, p.record_name AS campaign_name
      FROM public.ppc p
      WHERE p.record_main_type = 'campaign' AND p.record_name ILIKE '%utharsika%'
  ),
  pauses AS (
      SELECT DISTINCT ON (al.record_id, al.source)
             al.parent_id, al.child_id, al.record_id, al.source, al.reason, al.action_datetime
      FROM public.ppc_etl_automation_log al
      JOIN util_camp uc ON al.parent_id = uc.parent_id AND al.source = uc.source
      WHERE al.action_type='ad_pause_logs' AND al.status='success' AND al.applied_by='0'
      ORDER BY al.record_id, al.source, al.action_datetime DESC
  )
  SELECT string_agg(DISTINCT pp.ref_id, ',') AS "ASIN"
  FROM pauses ps
  JOIN util_camp uc ON ps.parent_id = uc.parent_id AND ps.source = uc.source
  JOIN public.ppc st ON st.record_main_type='ad' AND st.child_id = ps.record_id
                    AND st.source = ps.source AND st.record_status='paused'
  LEFT JOIN public.ppc ag ON ag.record_main_type='ad_group' AND ag.parent_id = ps.parent_id
                    AND ag.child_id = ps.child_id AND ag.source = ps.source
  LEFT JOIN public.ppc_performance pp ON pp.record_id = ps.record_id
                    AND pp.source = ps.source AND pp.record_type='ad'
  GROUP BY uc.campaign_name, ag.record_name, ps.reason, ps.action_datetime
) q;

-- Check 2 — still-paused vs all-pauses (expect total 41, still_paused 33, reactivated 8)
WITH util_camp AS (
  SELECT DISTINCT parent_id, source FROM public.ppc
  WHERE record_main_type='campaign' AND record_name ILIKE '%utharsika%'),
pauses AS (
  SELECT DISTINCT ON (al.record_id, al.source) al.record_id, al.source
  FROM public.ppc_etl_automation_log al
  JOIN util_camp uc ON al.parent_id=uc.parent_id AND al.source=uc.source
  WHERE al.action_type='ad_pause_logs' AND al.status='success' AND al.applied_by='0'
  ORDER BY al.record_id, al.source, al.action_datetime DESC)
SELECT COUNT(*) total,
       COUNT(*) FILTER (WHERE st.record_status='paused') still_paused,
       COUNT(*) FILTER (WHERE st.record_status<>'paused' OR st.record_status IS NULL) reactivated
FROM pauses ps
LEFT JOIN public.ppc st ON st.record_main_type='ad'
      AND st.child_id=ps.record_id AND st.source=ps.source;

-- Check 3 — spot check: for any record_id, confirm ppc_performance ASIN/SKU match.
-- (Replace :rid with a real record_id from the report.)
-- SELECT record_id, ref_id AS asin, sku
-- FROM public.ppc_performance
-- WHERE record_type='ad' AND source=1 AND record_id = :rid;
