-- ============================================================================
-- 00 — CORRECT PH HOLDER NAMES (the "assigned_user standard")
-- Source of truth for who the Portfolio Holders are + their exact names.
-- Per Downloads/PH_assigned_user_Standard.docx: join user + ph_categories +
-- ph_cate_products, take the UNIQUE user names, and use each name EXACTLY
-- (character-for-character, no retyping, no capitalisation changes) wherever
-- assigned_user is written.
-- READ-ONLY.
-- ----------------------------------------------------------------------------
-- 2026-07-10 result: 30 holders (all with which_channel=1 Amazon products).
-- ============================================================================
SELECT u."user"      AS user_id,
       u.user_name   AS assigned_user,               -- use this EXACTLY
       COUNT(DISTINCT p.ref_id) FILTER (WHERE p.which_channel = 1) AS amazon_products,
       COUNT(DISTINCT p.ref_id)                               AS all_products
FROM   public.ph_categories    c
JOIN   public."user"           u ON u."user" = c.user_id
JOIN   public.ph_cate_products p ON p.ass_cate_id = c.id
GROUP  BY u."user", u.user_name
ORDER  BY u.user_name;
