-- REQ-11-D01 — eBay Negative & Neutral feedback triage pull
-- Run 2026-07-15 (read-only). Re-runnable: the window is relative to CURRENT_DATE.
--
-- ⚠ CONNECTOR MATTERS. This runs on the **`ledsone`** database (Ledsone-db-mcp connector),
--    NOT `order_management_copy`. The Step-2 audit (2026-07-15) swept `order_management_copy`'s
--    26 schemas and concluded "no eBay feedback data exists anywhere" — that conclusion was
--    correct for THAT database and wrong for the estate: the feedback lives here, in `ledsone`.
--    See 2026-07-15_d01_delivery_and_data_correction.md.
--
-- Source table: customer_service.ebay_orders_customer_feedbacks
--   311,042 rows · 2015-06-13 → 2026-07-15 · types Positive / Neutral / Negative
--   Documented origin: message_app.feedbacks (MySQL).

-- ---------------------------------------------------------------------------
-- 0. Existence / scale check — the evidence that contradicts the Step-2 conclusion
-- ---------------------------------------------------------------------------
SELECT
  count(*)                         AS total_feedback_rows,   -- 311042
  min(date)::date                  AS earliest,              -- 2015-06-13
  max(date)::date                  AS latest,                -- 2026-07-15
  count(DISTINCT type)             AS distinct_types,        -- 3
  current_database()               AS db                     -- ledsone
FROM customer_service.ebay_orders_customer_feedbacks;

-- ---------------------------------------------------------------------------
-- 1. Window scale — why the report is only 20 rows
--    Negatives run ~0.1% of all feedback; 30d Negative=6, Neutral=14, Positive=5,049.
-- ---------------------------------------------------------------------------
SELECT f.type, count(*) AS rows
FROM customer_service.ebay_orders_customer_feedbacks f
WHERE f.date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY f.type
ORDER BY rows DESC;

-- ---------------------------------------------------------------------------
-- 2. THE DELIVERABLE PULL — Negative + Neutral, last 30 days
--    (2026-07-15 run ⇒ window 2026-06-15 → 2026-07-15; 20 rows, all resolving to a real order)
-- ---------------------------------------------------------------------------
SELECT
  f.date,
  s.name        AS account,          -- seller sub-account (coventrylights, led_sone, …)
  f.item_id,
  oi.item_sku,                       -- order-line SKU; combo products give a +-joined string
  o.order_id    AS real_order_id,
  f.type,
  f.comment,
  (SELECT count(*) FROM customer_service.ebay_orders_customer_feedbacks f2
     WHERE f2.type = 'Negative' AND f2.item_id = f.item_id) AS repeat_item_count
FROM customer_service.ebay_orders_customer_feedbacks f
LEFT JOIN order_management.sub_source s
       ON s.id = f.sub_source
LEFT JOIN order_management.order_item_info oi
       ON oi.item_id = f.item_id::text
      AND oi.item_transaction_id = f.transaction_id
LEFT JOIN order_management.orders o
       ON o.id = oi.order_id
WHERE f.type IN ('Negative', 'Neutral')
  AND f.date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY f.date DESC;

-- NOTES ON THIS QUERY
--
-- * item_sku comes from order_management.order_item_info (the actual order line), NOT from
--   listings.ebay_listings — that table fans out to multiple rows per item_id (parent + child
--   variants) and is the wrong join for a one-row-per-feedback report.
--
-- * The 2024-onward join caveat (database/postgresql/schemas/customer_service/relationships.md):
--   feedback → order_item_info is ~0% match pre-2023, 82.2% in 2023, 100% from 2024 on. It does
--   NOT bite any recent-window pull — all 20 rows in the 2026 window resolved to a real order.
--   Only a historical/backfill pull needs the f.date >= '2024-01-01' guard.
--
-- * repeat_item_count deliberately counts NEGATIVE feedback only per item_id (the spec's
--   definition), so a Neutral row showing 0 means that item has never drawn a negative — it is
--   not a missing value. Decision item B (the repeat window) is still open: this is all-time.
--
-- * ⚠ Attribution: this pull is keyed on item_id + transaction_id, which is the ORDER-LINE key
--   (audit item K's PASS route, 96.07%), not the item_id-alone key that fails the 10% gate at
--   52.05%. Do not "simplify" this join to item_id alone.
