-- ============================================================================
-- Paused Campaign Report — Utharsika (PRJ-2026-007 / REQ-09-D01 / PH-2026-07-UTHAR10)
-- READ-ONLY. DB: order_management_copy (Postgres MCP execute_sql / temp_user psycopg2).
-- Returns: Campaign Name, Ad Group Name, ASIN, SKU, Pause Reason,
--          Campaign Pause Date, Days Paused — one row per still-paused ad target.
--
-- OPTIMIZED 2026-08-03 (output-identical, validated 341 rows / 0 ASIN / 0 SKU mismatches
-- vs the prior wholesale join). ppc_performance is 24.7M rows with NO index on record_id,
-- so the previous `LEFT JOIN ppc_performance ON record_id` full-scanned it every run and
-- the warehouse terminated the backend mid-query once Utharsika grew to 91 campaigns.
-- The perf CTE now reaches ASIN/SKU through the (parent_id, record_type, date) index
-- instead — every paused ad's perf rows carry its campaign parent_id, so this returns
-- exactly the same rows via an index seek (~4s instead of a timeout).
--
-- Rules (see SYSTEM_REFERENCE.md §4):
--   scope  : campaign record_name ILIKE '%utharsika%' (no owner column exists)
--   source : Amazon automation pauses only
--            (action_type='ad_pause_logs', status='success', applied_by='0')
--   latest : DISTINCT ON (record_id, source) ... ORDER BY action_datetime DESC
--   filter : still paused today (current ppc.record_status='paused' at ad grain)
--   reason : verbatim from ppc_etl_automation_log.reason
--   days   : CURRENT_DATE - action_datetime::date
-- ============================================================================

WITH util_camp AS (
    SELECT DISTINCT p.parent_id, p.source, p.record_name AS campaign_name
    FROM public.ppc p
    WHERE p.record_main_type = 'campaign'
      AND p.record_name ILIKE '%utharsika%'
),
pauses AS (   -- latest successful automation pause per ad target
    SELECT DISTINCT ON (al.record_id, al.source)
           al.parent_id, al.child_id, al.record_id, al.source, al.reason, al.action_datetime
    FROM public.ppc_etl_automation_log al
    JOIN util_camp uc ON al.parent_id = uc.parent_id AND al.source = uc.source
    WHERE al.action_type = 'ad_pause_logs'
      AND al.status      = 'success'
      AND al.applied_by  = '0'
    ORDER BY al.record_id, al.source, al.action_datetime DESC
),
perf AS (   -- ASIN/SKU limited via the (parent_id, record_type, date) index to Utharsika ads only.
            -- ppc_performance has NO record_id index (24.7M rows), so a record_id join = full scan.
            -- Every paused ad's perf rows carry its campaign parent_id, so parent_id IN util_camp
            -- reaches exactly the same rows through an index seek. DISTINCT collapses per-date dupes.
    SELECT DISTINCT pp.record_id, pp.source, pp.ref_id, pp.sku
    FROM public.ppc_performance pp
    WHERE pp.record_type = 'ad'
      AND pp.parent_id IN (SELECT parent_id FROM util_camp)
)
SELECT uc.campaign_name                          AS "Campaign Name",
       ag.record_name                            AS "Ad Group Name",
       string_agg(DISTINCT pp.ref_id, ',')       AS "ASIN",
       string_agg(DISTINCT pp.sku, ',')          AS "SKU",
       ps.reason                                 AS "Pause Reason",
       ps.action_datetime::date                  AS "Campaign Pause Date",
       (CURRENT_DATE - ps.action_datetime::date) AS "Days Paused"
FROM pauses ps
JOIN util_camp uc ON ps.parent_id = uc.parent_id AND ps.source = uc.source
JOIN public.ppc st  ON st.record_main_type = 'ad'
                   AND st.child_id = ps.record_id AND st.source = ps.source
                   AND st.record_status = 'paused'          -- still paused only
LEFT JOIN public.ppc ag ON ag.record_main_type = 'ad_group'
                   AND ag.parent_id = ps.parent_id AND ag.child_id = ps.child_id
                   AND ag.source = ps.source
LEFT JOIN perf pp ON pp.record_id = ps.record_id AND pp.source = ps.source
GROUP BY uc.campaign_name, ag.record_name, ps.reason, ps.action_datetime
ORDER BY "Days Paused" DESC, "Campaign Name";

-- ----------------------------------------------------------------------------
-- data.json pull: wrap the SELECT above in json_agg so the governed extract is
-- captured verbatim (used by build_report.py / build_html.py):
--
-- SELECT json_agg(row_to_json(q) ORDER BY q.days_paused DESC, q.campaign_name) AS data
-- FROM ( <the SELECT above, aliased lower_snake_case> ) q;
-- ----------------------------------------------------------------------------
