-- ============================================================================
-- 04 — ALLOCATED / ROSTER counts per PH (the dashboard "Allocated" card)
-- Distinct Amazon products allocated to each holder via the roster tables.
-- This is the "Allocated/roster" number (differs from "Active this window"
-- which comes from the segmentation). READ-ONLY.
-- Feed the result into build (D.alloc / the per-PH "Allocated" card).
-- 2026-07-10 sample: paulr 634, thuwaraga 776, utharsika 1723, Jasmini 1264 ...
-- ============================================================================
SELECT u.user_name,
       COUNT(DISTINCT p.ref_id) AS allocated   -- which_channel=1 = Amazon
FROM   public.ph_categories    c
JOIN   public."user"           u ON u."user" = c.user_id
JOIN   public.ph_cate_products p ON p.ass_cate_id = c.id
WHERE  p.which_channel = 1
GROUP  BY u.user_name
ORDER  BY u.user_name;
