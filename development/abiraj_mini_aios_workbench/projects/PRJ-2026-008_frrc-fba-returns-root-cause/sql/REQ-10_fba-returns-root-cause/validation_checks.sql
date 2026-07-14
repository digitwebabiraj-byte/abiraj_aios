-- FRRC — REQ-10-D01 — validation / control-total checks (READ-ONLY)
-- Run after generate_report.sql; every check must agree with the rendered outputs before release.
-- Fixed window shown as 2026-06-14 .. 2026-07-13 (swap DATE '2026-07-14' for CURRENT_DATE to roll).

-- CHECK 1 — Completeness: report population vs DB control totals.
--   Expect (fixed window): 91 returning ASINs, 105 return units.
SELECT COUNT(DISTINCT asin) AS asins, COALESCE(SUM(qty),0) AS return_units
FROM public.amazon_returns
WHERE fulfilment = 'fba'
  AND request_date >= DATE '2026-07-14' - INTERVAL '30 days'
  AND request_date <  DATE '2026-07-14';

-- CHECK 2 — Bucket arithmetic: for every row, the five reason buckets must sum to total_returns.
--   Expect: 0 rows returned (0 failures). (Run the generate_report CTE and assert per-row
--   listing+quality+buyer+shipping+unknown = total_returns; 0 mismatches on the fixed window.)

-- CHECK 3 — One ASIN = one owner (grain/ownership assumption).
--   Expect: 0 rows (no ASIN maps to >1 in-window FBA-UK owner).
SELECT asin, COUNT(DISTINCT user_name) AS owners
FROM public.order_transaction
WHERE source_name = 'AMAZON' AND fba_sales = TRUE AND market_place = 'UK'
  AND order_status = 'Completed'
  AND order_date >= DATE '2026-07-14' - INTERVAL '30 days'
  AND order_date <  DATE '2026-07-14'
GROUP BY asin
HAVING COUNT(DISTINCT user_name) > 1;

-- CHECK 4 — Return-status breakdown (informational; feeds the OPEN status-filter decision).
--   Currently ALL returns count regardless of status. Pull the split before deciding whether to
--   count only physically-returned units (HELD — Satheesvaran).
SELECT status, COUNT(*) AS n, COALESCE(SUM(qty),0) AS units
FROM public.amazon_returns
WHERE fulfilment = 'fba'
  AND request_date >= DATE '2026-07-14' - INTERVAL '30 days'
  AND request_date <  DATE '2026-07-14'
GROUP BY status
ORDER BY units DESC;
