-- =============================================================================
-- REQ-11-D01 · Step-2 Existing-Asset Audit — eBay Feedback AI Triage (EBFT)
-- Project : PRJ-2026-009_ebay-feedback-ai-triage
-- Ran     : 2026-07-15 (read-only, via Postgres MCP execute_sql)
-- Results : evidence/logs_or_screenshots/REQ-11_.../2026-07-15_step2_existing_asset_audit.md
--
-- READ-ONLY. No DDL, no DML, no seed. Re-runnable at any time.
-- Answers the prompt's Step 2: "Inspect the database. Do not assume; query it."
-- =============================================================================


-- -----------------------------------------------------------------------------
-- CHECK 1a — Does any feedback table already exist? (Existing-Asset-First rule)
-- Result 2026-07-15: 5 rows, ALL staging_ai PPC/governance artifacts.
--                    NO eBay customer feedback table. => build from scratch.
-- -----------------------------------------------------------------------------
SELECT table_schema, table_name, table_type
FROM information_schema.tables
WHERE table_name ILIKE '%feedback%'
ORDER BY table_schema, table_name;


-- -----------------------------------------------------------------------------
-- CHECK 1b — Column-level sweep across ALL schemas (name search can miss).
-- Result 2026-07-15: only internal fields — developer_feedback (AIOS governance),
--                    manager_feedback (warehouse rota), feedback_rule (PMax).
--                    No comment_type / comment_text column exists anywhere.
-- -----------------------------------------------------------------------------
SELECT table_schema, table_name, column_name, data_type
FROM information_schema.columns
WHERE column_name ILIKE '%feedback%'
   OR column_name ILIKE '%comment_type%'
   OR column_name ILIKE '%commenttype%'
   OR column_name ILIKE '%comment_text%'
ORDER BY table_schema, table_name, column_name;


-- -----------------------------------------------------------------------------
-- CHECK 1c — Confirm the message schema's real contents + prove ebay_msg is NOT
--            feedback (it is support-message traffic — a different eBay API).
-- Result 2026-07-15: ResponseToASQQuestion 40,215 · ContactTransactionPartner
--                    17,391 · AskSellerQuestion 10,103 · ...  => NOT feedback.
-- -----------------------------------------------------------------------------
SELECT table_schema, table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'message'
ORDER BY table_name;

SELECT message_type, COUNT(*) AS rows
FROM message.ebay_msg
GROUP BY message_type
ORDER BY rows DESC;


-- -----------------------------------------------------------------------------
-- CHECK 2 — Which table holds Listing SKU -> Parent SKU?
-- The prompt names `listing_data_1` and `inv_final_stock`. Verify, do not assume.
-- Result 2026-07-15: `listing_data_1` DOES NOT EXIST (real table: listing_data).
--                    inv_final_stock has only `sku` — no parent column.
--                    => Parent SKU = public.listing_data.parent_sku
-- -----------------------------------------------------------------------------
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_name IN ('listing_data','listing_data_1','inv_final_stock','order_transaction')
ORDER BY table_schema, table_name;

SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN ('listing_data','listing_data_1','inv_final_stock')
  AND (column_name ILIKE '%parent%' OR column_name ILIKE '%sku%' OR column_name ILIKE '%ref_id%'
       OR column_name ILIKE '%channel%' OR column_name ILIKE '%family%')
ORDER BY table_name, column_name;

-- Parent-SKU coverage on eBay (open item M).
-- Result 2026-07-15: 139,171 rows · 118,739 with parent (85.32%) · 5,464 parents
--                    · mapped_sku populated on just 31 rows (dead on eBay).
SELECT COUNT(*)                                                          AS ebay_child_listing_rows,
       COUNT(*) FILTER (WHERE parent_sku IS NOT NULL AND parent_sku<>'') AS rows_with_parent_sku,
       ROUND(100.0*COUNT(*) FILTER (WHERE parent_sku IS NOT NULL AND parent_sku<>'')
             /NULLIF(COUNT(*),0),2)                                      AS pct_parent_sku_populated,
       COUNT(DISTINCT parent_sku) FILTER (WHERE parent_sku IS NOT NULL AND parent_sku<>'')
                                                                         AS distinct_parent_skus,
       COUNT(*) FILTER (WHERE mapped_sku IS NOT NULL AND mapped_sku<>'') AS rows_with_mapped_sku
FROM public.listing_data
WHERE which_channel = 2 AND wrong_sku = 0 AND is_parent = 0;


-- -----------------------------------------------------------------------------
-- CHECK 3 — THE STOP-GATE. Does item_id resolve to exactly one SKU?
-- Gate: >10% unattributable => rethink the SKU analytics BEFORE building them.
-- -----------------------------------------------------------------------------

-- 3a via the listing bridge.
-- Result 2026-07-15: 12,699 item_ids · only 312 single-SKU (2.46%) ·
--                    97.54% multi-SKU · worst listing carries 245 SKUs. FAILS.
WITH ebay_listings AS (
  SELECT ref_id,
         COUNT(DISTINCT COALESCE(NULLIF(mapped_sku,''), sku)) AS distinct_skus
  FROM public.listing_data
  WHERE which_channel = 2
    AND wrong_sku = 0
    AND is_parent = 0
    AND COALESCE(NULLIF(mapped_sku,''), sku) IS NOT NULL
    AND COALESCE(NULLIF(mapped_sku,''), sku) <> ''
  GROUP BY ref_id
)
SELECT COUNT(*)                                                   AS total_ebay_item_ids,
       COUNT(*) FILTER (WHERE distinct_skus = 1)                  AS resolve_to_exactly_one_sku,
       COUNT(*) FILTER (WHERE distinct_skus > 1)                  AS multi_sku,
       ROUND(100.0 * COUNT(*) FILTER (WHERE distinct_skus = 1) / NULLIF(COUNT(*),0), 2) AS pct_single_sku,
       ROUND(100.0 * COUNT(*) FILTER (WHERE distinct_skus > 1) / NULLIF(COUNT(*),0), 2) AS pct_multi_sku,
       MAX(distinct_skus)                                         AS worst_case_skus_on_one_listing
FROM ebay_listings;

-- =============================================================================
-- ADDENDUM (owner-prompted: "check customer service schema") — 2026-07-15
-- There is NO schema literally named customer-service; the ~60-object estate
-- lives in staging_ai under the cs_ / v_cs_ prefix. Findings: items N and O.
-- =============================================================================

-- N1 — The CANONICAL root-cause taxonomy that already exists for eBay.
-- Result 2026-07-15: 17 categories — Charge Back, CUSTOMER_MISUSE, Delivery Issue,
--   DISCOUNT, EBAY_RECALL, FULFILMENT_CARRIER, FULFILMENT_WAREHOUSE, INVOICE,
--   LISTING_CONTENT, MARKETPLACE_ADMIN, OTHER, OUT OF STOCK, PRE_SALES_QUERY,
--   PRODUCT_QUALITY, RETURN, TRANSFORMER_ISSUE, Wrong Address.
-- => Thinesh's 6-value enum DUPLICATES this on the same channel. Item N.
SELECT phrase FROM message.phrases WHERE send_type = 4 ORDER BY phrase;

-- N2 — Proof the taxonomy is live, not theoretical: 969 human-confirmed eBay rows.
-- Result 2026-07-15: LISTING_CONTENT 145 · OTHER 132 · PRODUCT_QUALITY 87 ·
--   MARKETPLACE_ADMIN 84 · OUT OF STOCK 82 · FULFILMENT_WAREHOUSE 80 · ...
--   NB LISTING_CONTENT (the largest) has NO equivalent in Thinesh's enum.
--   NB dirty values exist (casing variants, free-text leakage) — mapping must handle them.
SELECT root_cause, COUNT(*) AS confirmed_rows
FROM staging_ai.cs_confirmed_root_cause_register
WHERE platform = 'ebay'
GROUP BY root_cause ORDER BY confirmed_rows DESC;

-- O — The existing SKU linkage: Amazon/Shopify use the ORDER LINE, eBay uses the LISTING.
-- Result 2026-07-15: EBAY / ITEM_ID_LISTING_MAP = 25,708 rows (the 2.46% key, Check 3a)
--                    AMAZON + SHOPIFY / VIA_ORDER_LINE = 12,423 rows (the correct key)
--                    ALL rows resolution_status='VALIDATION_REQUIRED' (never promoted).
-- => Independently reproduces fault K. Item K asks eBay to do what the others already do.
SELECT platform, link_type, resolution_method, resolution_status,
       COUNT(*) AS rows,
       COUNT(*) FILTER (WHERE resolved_sku IS NOT NULL AND resolved_sku<>'') AS with_sku
FROM staging_ai.cs_sku_message_linkage
GROUP BY platform, link_type, resolution_method, resolution_status
ORDER BY rows DESC;

-- O2 — Is the AI classification layer Thinesh wants already built? NO.
-- Result 2026-07-15: 12 rows total (6 Amazon + 6 Shopify, NO eBay); category-level
--   summary only; confidence_score='METADATA_ONLY'; recommended_action NULL;
--   everything VALIDATION_REQUIRED / STAGING. Nothing to reuse directly.
SELECT platform, issue_category, owner_team, recommended_action,
       confidence_score, validation_status, promotion_status, msgs_90d, share_pct
FROM staging_ai.cs_issue_classification_staging
ORDER BY msgs_90d DESC NULLS LAST;


-- -----------------------------------------------------------------------------
-- 3b on REAL recent eBay orders — item_id alone vs item_id + order_id.
-- Result 2026-07-15: 16,533 lines / 3,347 item_ids.
--   item_id alone        -> 52.05% single-SKU (max 42 SKUs)   = 47.95% unattributable  FAILS
--   item_id + order_id   -> 96.07% single-SKU                 =  3.93% unattributable  PASSES
-- => Attribute feedback by ORDER LINE (GetFeedback returns TransactionID /
--    OrderLineItemID), never by listing. This is open item K.
WITH recent_ebay AS (
  SELECT item_id, order_id, sku
  FROM public.order_transaction
  WHERE source_name = 'EBAY'
    AND order_date >= CURRENT_DATE - 90
    AND item_id IS NOT NULL AND item_id <> ''
    AND sku IS NOT NULL AND sku <> ''
),
by_item AS (
  SELECT item_id, COUNT(DISTINCT sku) AS n_sku
  FROM recent_ebay GROUP BY item_id
),
by_item_order AS (
  SELECT item_id, order_id, COUNT(DISTINCT sku) AS n_sku
  FROM recent_ebay GROUP BY item_id, order_id
)
SELECT
  (SELECT COUNT(*) FROM recent_ebay)                                              AS ebay_order_lines_90d,
  (SELECT COUNT(*) FROM by_item)                                                  AS distinct_item_ids,
  (SELECT COUNT(*) FROM by_item WHERE n_sku = 1)                                  AS item_id_single_sku,
  (SELECT ROUND(100.0*COUNT(*) FILTER (WHERE n_sku=1)/NULLIF(COUNT(*),0),2) FROM by_item)       AS pct_item_id_single_sku,
  (SELECT MAX(n_sku) FROM by_item)                                                AS max_skus_per_item_id,
  (SELECT COUNT(*) FROM by_item_order)                                            AS distinct_item_order_pairs,
  (SELECT ROUND(100.0*COUNT(*) FILTER (WHERE n_sku=1)/NULLIF(COUNT(*),0),2) FROM by_item_order) AS pct_item_plus_order_single_sku;
