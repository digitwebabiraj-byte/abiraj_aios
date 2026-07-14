# HANDOFF — FRRC: FBA Returns Root-Cause Report (REQ-10-D01)

**Read this file first.** It is the single source of truth for taking over this task. Everything below is either LOCKED (confirmed with the business, do not re-derive) or HELD (open, needs a decision). Nothing here should be re-guessed.

---

## 1. What this task is

Build a governed, repeatable report on the LEDsONE Postgres analytics platform that shows **which Amazon FBA products are being returned too often, why, and what to do about it** — one row per returning ASIN, routed to the person who owns it. The source specification is a hand-built Excel tracker (`_Amazon_FBA_Returns_Tracker_-_Rebecca.xlsx`); this task turns it into a live, data-backed report plus a user-facing view.

Deliverable ID: **REQ-10-D01** (first deliverable of the FRRC stream). Developer: abiraj. Report owner persona: Rebecca + the listing-optimisation / supplier-QC / packaging teams.

---

## 2. Current status

**DONE and validated (live DB, 30-day window 2026-06-14 → 2026-07-13):**
- Excel workbook (3 tabs, threshold-driven formulas) — `FRRC_FBA_Returns_Tracker_REQ-10-D01_30day.xlsx`
- User-facing HTML dashboard with owner dropdown — `FRRC_FBA_Returns_Console_REQ-10-D01_30day.html`
- 91 ASINs, 105 returns, all reconciled to DB control totals; 0 formula errors; cross-checked against the source tracker.

**CONFIRMED with the user (LOCKED — see §4):** window = last 30 days; Units Sold = FBA-UK Completed; returns = `request_date`-based; join/SKU via `listing_data` bridge; one ASIN = one owner (verified).

**HELD (open — see §9):** correct bucket for 6 rare reason codes; whether to count all returns or only physically-returned units; whether to attribute the 18 "N/A / Unassigned" ASINs via `listing_data` instead of sales; reviewer sign-offs.

---

## 3. Environment & guardrails

- **DB access:** Postgres via the MCP tool `Postgresql:execute_sql` (same server the report was built on). All tables are in schema `public`.
- **READ-ONLY.** No INSERT/UPDATE/DELETE, no schema change, no seeding on any source table (`amazon_returns`, `order_transaction`, `listing_data`, …). The only outputs are the report files.
- **SQL must be executed** and real rows returned — never present SQL alone as the deliverable (platform rule, per the skills).
- **Never invent a business rule.** If unclear, flag it for **Satheesvaran** and park it. Reviewer gates: Queryability → **Tamil Selvan**, Technical → **Sajeesan**.

---

## 4. Confirmed business rules — LOCKED

### Reporting window
Last 30 days ending the day **before** the run; current-day excluded.
Run 2026-07-14 ⇒ **2026-06-14 → 2026-07-13 inclusive**. (Compute as `run_date - 30 days` … `run_date - 1 day`.)

### Population
ASINs with **≥ 1 FBA return** in the window. Zero-return ASINs are excluded. Report is **return-driven**: start from returns, then look up sales.

### Returns (numerator)
`public.amazon_returns` WHERE `fulfilment = 'fba'` (lowercase in data) AND `request_date` in window. Aggregate `SUM(qty)` per ASIN. Counts **all** returns regardless of `status` (see HELD item about status filtering).

### Units Sold (denominator) — CONFIRMED FBA-UK
`public.order_transaction` WHERE `source_name = 'AMAZON'` AND `fba_sales = TRUE` AND `market_place = 'UK'` AND `order_status = 'Completed'` AND `order_date` in window. Aggregate `SUM(quantity)` per ASIN.
> This exact definition was confirmed by the user and reproduces the source tracker's Units Sold on 4/5 spot-checked ASINs and 65/101 exactly on the full cross-check (the rest are 1–3 higher in live data = orders recorded after Rebecca's manual snapshot).

### Return Rate
`Total Returns / Units Sold`. If `Units Sold = 0` → **"N/A"** (Flag = "N/A - No Sales Data"). N/A rows are correct, not a bug: the ASIN was returned but had no in-window FBA-UK sale (sold earlier, or sold FBM/non-UK).

### Join & grain — SKU via `listing_data` bridge
Returns carry **listing/variant SKUs** (`PHSF1GDRFG_AML`, `CL3RBM5PK FBA`); sales carry **base SKUs** (`PHSF1GDRFG`). They do **not** join on `sku`. Anchor on **ASIN** (reliable on both sides; Amazon ≈ 1 SKU/ASIN), and resolve the display SKU through the bridge:
`public.listing_data` WHERE `which_channel = 1` AND `wrong_sku = 0` AND `COALESCE(is_parent,0) <> 1` AND `market_place = 'UK'`, resolved SKU = `COALESCE(NULLIF(mapped_sku,''), sku)`. 89/91 ASINs resolve; the 2 not in `listing_data` fall back to the return SKU. Keep the original **return SKU** beside the resolved SKU for traceability. (Bridge mechanics: `SKILL_ppc_stock_lookup.md` + `TABLE_listing_data_1.md`.)

### Reason → bucket map
- **Listing Mismatch:** NOT_COMPATIBLE, NOT_AS_DESCRIBED
- **Quality Issue:** QUALITY_UNACCEPTABLE, DEFECTIVE, DAMAGED_BY_FC, DAMAGED_BY_CARRIER
- **Buyer Preference:** UNWANTED_ITEM, FOUND_BETTER_PRICE, ORDERED_WRONG_ITEM
- **Shipping Issue:** UNDELIVERABLE_UNKNOWN, UNDELIVERABLE_REFUSED
- **Unknown:** NO_REASON_GIVEN **+ (HELD)** MISSING_PARTS, SWITCHEROO, MISSED_ESTIMATED_DELIVERY, POOR_FIT, MISORDERED, UNAUTHORIZED_PURCHASE — these are **not** in the tracker's map and are currently counted under Unknown so buckets reconcile. (In the 30-day window only 3 of these appear: MISSED_ESTIMATED_DELIVERY×2, MISSING_PARTS×1, UNAUTHORIZED_PURCHASE×1.)

### Thresholds (from the tracker's editable Thresholds tab — never hardcode in row logic)
Critical rate `> 0.20` · High rate `> 0.10` · Min returns to evaluate `>= 2` · Listing share `>= 0.40` · Quality share `>= 0.40` · Buyer share `>= 0.50`.

### Flag / Root Cause / Recommended Action
- **Flag:** rate N/A → "N/A - No Sales Data"; rate > 0.20 → "CRITICAL - URGENT REVIEW"; rate > 0.10 → "HIGH RETURN - REVIEW"; else "OK".
- **Root Cause (independent of Flag):** returns < 2 → "Too few returns to evaluate"; else Listing share ≥ 0.40 → "Listing/Expectation Mismatch"; else Quality share ≥ 0.40 → "Quality/Defect Issue"; else Buyer share ≥ 0.50 → "Buyer Preference - not a product issue"; else "Mixed reasons - no single dominant cause".
- **Recommended Action:** derived from Flag + Root Cause (OK → monitor; Listing → fix title/images/A+; Quality → supplier/QC + inspect inbound; Buyer → monitor only; Too few → monitor insufficient data; Mixed → review manually).
- **Reproduce the quirk faithfully:** Flag (rate-based) and Root Cause (count-based, min 2) are **independent** — a 1-return SKU can read CRITICAL yet resolve to "Too few returns to evaluate". Do not "fix" this.

### Responsible Person
`order_transaction.user_name` (portfolio holder) for the ASIN. **Verified: one ASIN = one owner** in this data (73/73 sold ASINs have exactly one owner). ASINs with no in-window FBA-UK sale have no sales-derived owner → shown as "Unassigned" (candidate to resolve via `listing_data` — HELD).

---

## 5. The exact SQL (final, executed)

```sql
WITH returns_agg AS (
  SELECT asin,
    mode() WITHIN GROUP (ORDER BY sku) AS return_sku,
    SUM(qty) AS total_returns,
    COALESCE(SUM(qty) FILTER (WHERE reason IN ('NOT_COMPATIBLE','NOT_AS_DESCRIBED')),0) AS listing_qty,
    COALESCE(SUM(qty) FILTER (WHERE reason IN ('QUALITY_UNACCEPTABLE','DEFECTIVE','DAMAGED_BY_FC','DAMAGED_BY_CARRIER')),0) AS quality_qty,
    COALESCE(SUM(qty) FILTER (WHERE reason IN ('UNWANTED_ITEM','FOUND_BETTER_PRICE','ORDERED_WRONG_ITEM')),0) AS buyer_qty,
    COALESCE(SUM(qty) FILTER (WHERE reason IN ('UNDELIVERABLE_UNKNOWN','UNDELIVERABLE_REFUSED')),0) AS shipping_qty,
    COALESCE(SUM(qty) FILTER (WHERE reason IN ('NO_REASON_GIVEN','MISSING_PARTS','SWITCHEROO','MISSED_ESTIMATED_DELIVERY','POOR_FIT','MISORDERED','UNAUTHORIZED_PURCHASE')),0) AS unknown_qty,
    mode() WITHIN GROUP (ORDER BY reason) AS top_reason
  FROM public.amazon_returns
  WHERE fulfilment='fba' AND request_date >= DATE '2026-07-14' - INTERVAL '30 days'
                        AND request_date <  DATE '2026-07-14'
  GROUP BY asin
),
sales_agg AS (
  SELECT asin, SUM(quantity) AS units_sold,
    mode() WITHIN GROUP (ORDER BY user_name) AS responsible_ph
  FROM public.order_transaction
  WHERE source_name='AMAZON' AND fba_sales=TRUE AND market_place='UK'
    AND order_status='Completed'
    AND order_date >= DATE '2026-07-14' - INTERVAL '30 days'
    AND order_date <  DATE '2026-07-14'
  GROUP BY asin
),
bridge AS (
  SELECT ref_id AS asin,
    mode() WITHIN GROUP (ORDER BY COALESCE(NULLIF(mapped_sku,''), sku)) AS inv_sku
  FROM public.listing_data
  WHERE which_channel=1 AND wrong_sku=0 AND COALESCE(is_parent,0)<>1 AND market_place='UK'
  GROUP BY ref_id
)
SELECT
  COALESCE(b.inv_sku, r.return_sku) AS sku,
  r.asin,
  COALESCE(s.units_sold,0)::int AS units_sold,
  r.total_returns::int, r.listing_qty::int, r.quality_qty::int, r.buyer_qty::int,
  r.shipping_qty::int, r.unknown_qty::int, r.top_reason, s.responsible_ph,
  r.return_sku, b.inv_sku
FROM returns_agg r
LEFT JOIN sales_agg s ON s.asin = r.asin
LEFT JOIN bridge    b ON b.asin = r.asin
ORDER BY r.total_returns DESC, COALESCE(s.units_sold,0) ASC, r.asin;
```

> Replace the hardcoded `DATE '2026-07-14'` with `CURRENT_DATE` to make it roll automatically. `mode()` picks the most common value where an ASIN has more than one candidate (display SKU / top reason / owner).

**Control totals to assert after running** (for the fixed 2026-06-14→07-13 window): 91 ASINs, 105 return units, each row's five reason buckets sum to `total_returns`.

---

## 6. Validation & cross-check (how correctness was proven)

- **Completeness:** report rows/returns == DB control totals (`SELECT COUNT(DISTINCT asin), SUM(qty) FROM amazon_returns WHERE fulfilment='fba' AND request_date in window`).
- **Bucket arithmetic:** for every row, `listing+quality+buyer+shipping+unknown == total_returns` (0 failures).
- **Cross-check vs source tracker** (run the method on Rebecca's window 2026-05-11→07-12, compare per ASIN): Returns 95/101 exact; Units 65/101 exact, all misses 1–3 higher in live (post-snapshot orders). This confirmed the Units-Sold and returns rules and settled the returns-window question (request_date-based, no order_date re-alignment).
- **Formulas:** Excel recalculated via `/mnt/skills/public/xlsx/scripts/recalc.py` → 0 errors.
- **Data quirks confirmed on live DB:** `fulfilment` is lowercase `fba`; `order_status` uses American `Canceled`; returns SKUs are listing-variants, sales SKUs are base (hence the ASIN anchor + bridge).

---

## 7. Files to give Claude Code (manifest)

**Read to understand the task (in this order):**
1. `HANDOFF_FRRC_REQ-10-D01.md` — this file.
2. `2026-07-14_abiraj_REQ-frrc_REQ-10-D01.md` — the full requirement/spec document.
3. `_Amazon_FBA_Returns_Tracker_-_Rebecca.xlsx` — the source spec + ground-truth data (tabs: Objective & Guide, Thresholds, Tracker).
4. `project_knowledge/SKILL_multi_table.md` — join path, aggregate-first, mandatory execution.
5. `project_knowledge/SKILL_ppc_stock_lookup.md` — the `listing_data` bridge + clean-SKU logic.
6. `project_knowledge/TABLE_amazon_returns.md`, `TABLE_order_transaction.md`, `TABLE_listing_data_1.md` — column defs for the three tables used.
7. `project_knowledge/SKILL_single_table.md` — intent-routing reference.

**Use to reproduce / regenerate deliverables:**
8. `frrc30.json` — the exact 30-day dataset pulled from the DB (input to both builders).
9. `build_frrc30.py` — builds the 3-tab Excel with threshold formulas from `frrc30.json`.
10. `build_console.py` — builds the full-screen HTML dashboard (owner dropdown) from `frrc30.json`.
11. `FRRC_REQ-10-D01_execution_prompt.md` — a self-contained prompt describing the whole method.

**Current outputs (reference / what "done" looks like):**
12. `FRRC_FBA_Returns_Tracker_REQ-10-D01_30day.xlsx`
13. `FRRC_FBA_Returns_Console_REQ-10-D01_30day.html`
14. `FRRC_FBA_Returns_Report_REQ-10-D01_30day.html` (simpler grouped HTML)

> Note: `build_*.py` need Python with `openpyxl` (`pip install openpyxl`). The full project (all `TABLE_*.md` / `SKILL_*.md`) lives in the user's platform project knowledge — hand Claude Code the whole project if it needs tables beyond the three above.

---

## 8. How to regenerate (end to end)

1. Run the SQL in §5 via `Postgresql:execute_sql` (wrap in `SELECT json_agg(t)::text FROM ( … ) t` to capture as JSON). Save as `frrc30.json` (array of row objects with keys: `sku, asin, units_sold, total_returns, listing_qty, quality_qty, buyer_qty, shipping_qty, unknown_qty, top_reason, responsible_ph, return_sku, inv_sku`).
2. Assert control totals (§6). Stop if they don't match.
3. `python3 build_frrc30.py` → Excel. Recalc with `/mnt/skills/public/xlsx/scripts/recalc.py <file> 90`; expect 0 errors.
4. `python3 build_console.py` → HTML dashboard.
5. To make it roll daily: swap `DATE '2026-07-14'` for `CURRENT_DATE` in the SQL, and update the window constants at the top of both build scripts (`WIN_START/WIN_END/RUN`).

---

## 9. Open items / next steps

**For Satheesvaran (business decisions — do NOT decide unilaterally):**
- **Rare reason codes:** confirm the bucket for MISSING_PARTS, SWITCHEROO, MISSED_ESTIMATED_DELIVERY, POOR_FIT, MISORDERED, UNAUTHORIZED_PURCHASE (currently → Unknown). Suggested (unconfirmed): MISSED_ESTIMATED_DELIVERY→Shipping, MISSING_PARTS→Quality, UNAUTHORIZED_PURCHASE→Buyer Preference.
- **Return status filter:** currently every return counts regardless of `amazon_returns.status`. Decide whether to count only physically-returned units (exclude e.g. undeliverable/refused/reimbursed). This is the only open item that changes the numbers — pull the `status` breakdown first.

**Engineering next steps:**
- **"Unassigned" owners (18 N/A ASINs):** owner currently comes from sales; N/A rows have none. Optionally attribute them via `listing_data` (by ASIN) so all 91 rows show a named owner.
- **Scheduling:** parameterise the window (`CURRENT_DATE`) and wire a cadence + manual ad-hoc run.
- **Review gates:** submit for Queryability (Tamil Selvan) and Technical (Sajeesan) sign-off before locking.

**Nice-to-have (requested/considered):** print/PDF export per owner; a severity trend chart on the dashboard.

---

## 10. One-paragraph summary for a cold start

FRRC is a return-driven, read-only Postgres report: for every Amazon FBA ASIN returned in the last 30 days, show real FBA-UK units sold, total returns, return rate, the return split across five reason buckets, and a threshold-driven Flag / Root Cause / Recommended Action, routed to the ASIN's owner. The SQL in §5 is final and validated against the source tracker; the two build scripts turn its JSON output into the Excel and the HTML dashboard. All rules in §4 are confirmed and locked; only the items in §9 remain, and only the return-status decision can change the numbers.
