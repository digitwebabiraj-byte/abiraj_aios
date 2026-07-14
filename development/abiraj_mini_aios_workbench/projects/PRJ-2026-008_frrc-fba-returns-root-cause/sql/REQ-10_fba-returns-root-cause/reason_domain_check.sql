-- FRRC — REQ-10-D01 — live reason-domain check (RUN THIS FIRST, before the report)
-- Purpose: confirm every live FBA `reason` value is covered by the Step-4 bucket map.
-- Any code NOT in the map must be FLAGGED in the held-items note (route to Satheesvaran),
-- never silently pushed into "Unknown". READ-ONLY.

SELECT reason, COUNT(*) AS n
FROM public.amazon_returns
WHERE fulfilment = 'fba'
GROUP BY reason
ORDER BY n DESC;

-- Bucket map (SYSTEM_REFERENCE.md §4):
--   Listing Mismatch : NOT_COMPATIBLE, NOT_AS_DESCRIBED
--   Quality Issue    : QUALITY_UNACCEPTABLE, DEFECTIVE, DAMAGED_BY_FC, DAMAGED_BY_CARRIER
--   Buyer Preference : UNWANTED_ITEM, FOUND_BETTER_PRICE, ORDERED_WRONG_ITEM
--   Shipping Issue   : UNDELIVERABLE_UNKNOWN, UNDELIVERABLE_REFUSED
--   Unknown          : NO_REASON_GIVEN
-- HELD (not in the tracker's map; currently counted under Unknown so buckets reconcile — Satheesvaran to confirm):
--   MISSING_PARTS, SWITCHEROO, MISSED_ESTIMATED_DELIVERY, POOR_FIT, MISORDERED, UNAUTHORIZED_PURCHASE
-- In the 2026-06-14..2026-07-13 window only 3 held codes appeared:
--   MISSED_ESTIMATED_DELIVERY x2, MISSING_PARTS x1, UNAUTHORIZED_PURCHASE x1.
