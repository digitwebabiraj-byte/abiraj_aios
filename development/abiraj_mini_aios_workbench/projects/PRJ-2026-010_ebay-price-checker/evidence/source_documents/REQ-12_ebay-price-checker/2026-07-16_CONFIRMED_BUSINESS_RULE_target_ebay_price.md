# CONFIRMED BUSINESS RULE — TARGET EBAY PRICE

**Captured verbatim from the business owner, 2026-07-16.** This rule **arrived as chat text**, not a
file — this document is its canonical record. It **supersedes the spreadsheet** (`Ebay System Task
-Thinesh.xlsx`) wherever the two disagree.

---

## SOURCE PRIORITY
1. Start with the eBay listing SKU.
2. Search for the matching SKU in the approved Amazon PostgreSQL source.
3. If the Amazon SKU exists and has a valid current Amazon price:
   `Target eBay Price = Amazon Price × 0.90`
4. If the Amazon SKU is not found, or its current price is missing or invalid, search for the matching
   SKU in the approved website PostgreSQL source.
5. If a valid website price exists:
   `Target eBay Price = Website Price × 1.10`
6. If neither source provides a valid price:
   `Target Source = NONE`, `Status = DATA MISSING`, `Action = Investigate SKU and source mapping`.

## SOURCE SELECTION RULE
Amazon is the first-priority source. Website price is a **fallback only** when: Amazon SKU not found ·
Amazon listing has no usable price · Amazon listing inactive (if the business-approved active-record rule
requires active listings) · Amazon price fails approved data-quality validation.
**Do not** average the two · **do not** compute both and pick lower/higher · **do not** let website
override a valid Amazon match · **do not** silently use an unrelated ASIN, parent SKU or similar SKU.

## FORMULAS
- Amazon selected: `target_price_raw = amazon_price * 0.90`
- Website selected: `target_price_raw = website_price * 1.10`
- Rounding: `target_price = ROUND(target_price_raw, 2)` — **2 decimal places, standard currency
  precision.** The owner's "£11 → about £10" example is **not** a whole-pound rule; whole-pound rounding
  is **parked pending separate formal approval**.
- Examples: Amazon £11.00 → £9.90 · Website £10.00 → £11.00.

## REQUIRED TARGET-SOURCE OUTPUT (16 fields)
`ebay_item_id · ebay_sku · amazon_match_status · amazon_sku · amazon_price · amazon_currency ·
website_match_status · website_sku · website_price · website_currency · target_source · target_price_raw ·
target_price · calculation_rule · source_updated_at · data_quality_note`

Allowed `target_source`: `AMAZON · WEBSITE_FALLBACK · NONE`.

## REQUIRED MATCH-STATUS VALUES (Amazon and Website each)
`MATCHED_VALID_PRICE · SKU_NOT_FOUND · PRICE_MISSING · PRICE_INVALID · INACTIVE · DUPLICATE_MATCH ·
CURRENCY_MISMATCH`

## DISCOVERY REQUIREMENT (10 points)
Identify: (1) canonical Amazon SKU field · (2) valid Amazon selling-price field · (3) website canonical
SKU field · (4) valid website selling-price field · (5) marketplace and currency fields · (6)
active/inactive fields · (7) price effective timestamps · (8) duplicate SKU conditions · (9) parent/child
SKU relationships · (10) existing target-price logic or objects.
**Do not implement the final system until exact source objects, joins, grain, active-record selection and
currency handling are validated.**

## READ-ONLY VALIDATION SAMPLE
Produce a sample: ≥5 Amazon-matched · ≥5 website-fallback · missing-source · duplicate/ambiguous (each
where available). For every row, show the source selected and why.

## PASS / FAIL (owner-stated)
- **PASS** if Amazon-first matching is evidenced · website used only as fallback · exact PostgreSQL
  sources documented · every calculation traceable.
- **FAIL** if website checked before Amazon · both prices blended · an approximate SKU selected · currency
  ignored · duplicate matches silently accepted · source evidence missing.

---

## How this was applied in REQ-12-D01 (and where it was clarified by Thinesh's Q1–Q8, 2026-07-16)
- **Approved Amazon source** = `listings.amazon_listings`, `site='UK'`/`'Germany'`, `sub_source=8`
  ('amazon Ledsone') — Thinesh Q3. On a duplicate match, the **lowest** Amazon price is taken — Thinesh Q1
  (this overrode a prior recommendation to nominate one account and refuse duplicates).
- **Approved website source** = `listings.shopify_listings`, `sub_source=104` ('ledsone', UK) and `108`
  ('ledsone-de', Germany). Confirmed by Thinesh as "the website".
- **Bundles** (`+` SKUs): sum the component prices, then apply the normal rule — Thinesh Q2. (Measured:
  works for only ~11% of bundles; the rest have unpriced components.)
- **Tolerance threshold** = £20 band (`±£0.50` below / `±£1.00` at-or-above) — Thinesh Q4/Q5. Resolves the
  spreadsheet's £15-vs-£20 self-contradiction.
- **DATA MISSING split** into `NO COMPARATOR` (eBay-only) vs `BUNDLE` for clarity — owner-approved refinement.
