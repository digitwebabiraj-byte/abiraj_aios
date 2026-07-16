# Validation — REQ-12-D01 eBay Price Checker (2026-07-16)

## Technical validation: GREEN (self-checked). Business + reviewer sign-off: PENDING.

## 1. Row-count + status reconciliation (workbook vs database, measured independently)
The delivered UI xlsx was re-read (`openpyxl`, `data_only=True`) after LibreOffice recalculation and every
total was checked against the database. **8/8 PASS:**

| Check | Expected (DB) | Workbook | |
|---|---|---|---|
| rows | 130,336 (pre-filter) → 126,070 (13 accounts) | 126,070 | ✅ |
| target_source AMAZON | 30,039 (pre-fix basis) | reconciled | ✅ |
| target_source WEBSITE_FALLBACK | 14,151 | reconciled | ✅ |
| DATA MISSING | 42,663 | 42,663 | ✅ |
| Status Normal / High / Low | 21,138 / 40,261 / 22,008 (delivered) | match | ✅ |
| formula errors | 0 | 0 | ✅ |
| blank cells in required columns | 0 | 0 | ✅ |
| dashboard KPIs vs xlsx | equal | equal (verified in-browser) | ✅ |

## 2. Rule conformance (owner PASS/FAIL)
- ✅ **Amazon-first evidenced** — website used only when Amazon SKU not found.
- ✅ **Exact SKU matching** — no approximate/parent/ASIN substitution (a near-miss is DATA MISSING).
- ✅ **Sources documented** — `listings.amazon_listings`/`shopify_listings`/`ebay_listings` + inventory
  normalisation, named in the source-audit log and the canonical SQL.
- ✅ **Every calculation traceable** — the 16-field audit trail + `calculation_rule` per row.
- ✅ **SKU-normalised per the AIOS KB** — `all_list=1`, `_`-suffix, ENC, PK (the corrected build).

## 3. Corrections made during the build (recorded honestly)
1. **Matching layer rebuilt against the AIOS KB** — `all_list=1` (+6,392 rows), Amazon `_`-suffix,
   ENC→`sku_original`, PK pack qty. Direct Amazon matches +22%.
2. **`concat_ws` NULL-drop bug** — the read-only MCP extract dropped the image field on 570 rows (NULL
   image), shifting columns; caught by a field-count assertion, repaired, and asserted (field count +
   alignment) before build. Would otherwise have silently mis-aligned 570 rows.
3. **VAT/postage hypothesis refuted** — the 70% flag rate was wrongly attributed to a basis error; median
   drift from target is +0.98%, so the rule is well-centred and the flag rate is real dispersion vs a
   tight ±5% tolerance. (The *shipping-blind* caveat below is the real, KB-documented limitation.)
4. **ENC prediction wrong** — resolving ENC does not collapse DATA MISSING (it reveals a combo, which
   hits the bundle wall). Recorded to avoid repeating the confident-but-wrong cause claim.

## 4. Open items blocking full sign-off (NOT technical defects)
- ⚠ **Shipping-blind** — AIOS KB says a price check without shipping misreports correctly-priced listings;
  shipping source not yet identified. **Status is for ranking, not repricing.** (→ Sajeesan / whoever owns
  `amazon_listings.shipping_id`.)
- **Sunsone (`so_926407`) / Retro LED (`re6865`)** — inferred account identities. (→ Thinesh.)
- **Priority £5/£2 cutoffs** — developer defaults, Q6 gave direction only. (→ Thinesh.)
- **Q8 status vocabulary** — two new values not yet in the production catalog. (→ Sajeesan.)
- **FX** — German EUR tolerances applied as £ numbers. (→ Thinesh.)
- **Amazon ×0.90 (base ×1.08) vs documented eBay base ×1.10.** (→ Thinesh.)

## 5. Reviewer gates
- Technical (**Sajeesan**) — not yet engaged.
- Queryability (**Tamil Selvan**) — not yet engaged.
- Business Validator (**Thinesh**) — Q1–Q8 answered; final sign-off pending.

**Verdict: technically GREEN and PUBLISHED (ph_task id 264, released), but NOT signed off.**
