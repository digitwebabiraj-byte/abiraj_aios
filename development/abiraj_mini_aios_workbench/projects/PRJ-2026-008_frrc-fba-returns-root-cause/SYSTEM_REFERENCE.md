# SYSTEM_REFERENCE — FRRC: FBA Returns Root-Cause (Rebecca)

Complete functional detail for the FRRC report. Derived from the canonical sources
(`_Amazon_FBA_Returns_Tracker_-_Rebecca.xlsx` / `REQ-10-D01` / `HANDOFF_FRRC_REQ-10-D01.md` /
`FRRC_REQ-10-D01_execution_prompt.md`) and validated against the live Postgres analytics DB by the
build session (run 2026-07-14, fixed window 2026-06-14 → 2026-07-13). This is the single reference a
leader or new engineer reads to understand what the system does.

## 1. What the report is
For every **Amazon FBA ASIN that had ≥ 1 return** in the reporting window, one row showing real Units
Sold, Total Returns, Return Rate %, the return split across five reason buckets, and a computed **Flag
Status / Root Cause / Recommended Action** — routed to the ASIN's **Responsible Person (PH)**. It tells
the team *which* products are returned too often, *why* (listing vs quality vs buyer preference vs
shipping), and *what to do*. It is **read-only** — no source table is written. Zero-return ASINs are
excluded (nothing to flag); the report is **return-driven** (start from returns, look up sales).

## 2. Population (scope) — LOCKED
- **Amazon FBA only.** Returns: `amazon_returns.fulfilment = 'fba'` (lowercase in the data). Sales:
  `order_transaction.source_name = 'AMAZON'` AND `fba_sales = TRUE`.
- **Units Sold = FBA-UK Completed** (confirmed): `market_place = 'UK'` AND `order_status = 'Completed'`.
- ASINs with **≥ 1 FBA return** in the window. LEFT JOIN to sales, so a returning ASIN with **zero
  in-window FBA-UK sales** still appears with Return Rate = "N/A".

## 3. Reporting window — LOCKED (length is HELD)
- **Last 30 days ending the day BEFORE the run**; current-day partial data **excluded**.
  Run 2026-07-14 ⇒ **2026-06-14 → 2026-07-13 inclusive** (`run_date − 30 days` … `run_date − 1 day`).
- Returns filtered on `amazon_returns.request_date`; Units Sold on `order_transaction.order_date`,
  both within the **same** window.
- The exact **length/cadence is not fixed in the source spec** (the workbook's own example used
  ~62 days, 2026-05-11 → 2026-07-12). 30 days is the stated working choice — **held for Satheesvaran**
  (open item C). Swap the hardcoded date for `CURRENT_DATE` to make the window roll automatically.

## 4. Reason → bucket map — LOCKED (rare codes HELD)
| Bucket | Reason codes |
|---|---|
| **Listing Mismatch** | `NOT_COMPATIBLE`, `NOT_AS_DESCRIBED` |
| **Quality Issue** | `QUALITY_UNACCEPTABLE`, `DEFECTIVE`, `DAMAGED_BY_FC`, `DAMAGED_BY_CARRIER` |
| **Buyer Preference** | `UNWANTED_ITEM`, `FOUND_BETTER_PRICE`, `ORDERED_WRONG_ITEM` |
| **Shipping Issue** | `UNDELIVERABLE_UNKNOWN`, `UNDELIVERABLE_REFUSED` |
| **Unknown** | `NO_REASON_GIVEN` **+ (HELD)** `MISSING_PARTS`, `SWITCHEROO`, `MISSED_ESTIMATED_DELIVERY`, `POOR_FIT`, `MISORDERED`, `UNAUTHORIZED_PURCHASE` |

The six **HELD** codes are **not** in the tracker's map; they are currently counted under Unknown so
the five buckets always sum to `total_returns`. In the fixed window only 3 appeared
(`MISSED_ESTIMATED_DELIVERY`×2, `MISSING_PARTS`×1, `UNAUTHORIZED_PURCHASE`×1). **Run
`reason_domain_check.sql` first every run** — any live code not in the map is flagged for Satheesvaran,
never silently dropped (open item E). `Top Reason (Amazon)` = the single most frequent raw `reason` for
the ASIN (reference only, not used in the logic).

## 5. Thresholds — from the editable Thresholds tab (never hardcode in row logic)
| Threshold | Value | Rule |
|---|---|---|
| Critical Return Rate | `> 0.20` | Flag = "CRITICAL - URGENT REVIEW" |
| High Return Rate | `> 0.10` (and ≤ 0.20) | Flag = "HIGH RETURN - REVIEW" |
| Min Returns to Evaluate | `>= 2` | Root-cause logic runs only at/above this |
| Listing Mismatch share | `>= 0.40` | Root Cause = Listing/Expectation Mismatch |
| Quality share | `>= 0.40` | Root Cause = Quality/Defect Issue |
| Buyer Preference share | `>= 0.50` | Root Cause = Buyer Preference |

These are applied in the **render layer** (`build_frrc30.py` / `build_console.py`), not baked into the
SQL row query, so the logic is re-tunable from the Thresholds tab alone.

## 6. Computed columns — LOCKED
**Return Rate %** = `Total Returns / Units Sold` (guard divide-by-zero with `NULLIF`). Units Sold = 0
or NULL → **"N/A"**.

**Flag Status** (rate-based): N/A → `N/A - No Sales Data`; rate > 0.20 → `CRITICAL - URGENT REVIEW`;
rate > 0.10 → `HIGH RETURN - REVIEW`; else `OK`.

**Root Cause** (count-based, then reason share): returns < 2 → `Too few returns to evaluate`; else
Listing share ≥ 0.40 → `Listing/Expectation Mismatch`; else Quality share ≥ 0.40 → `Quality/Defect
Issue`; else Buyer share ≥ 0.50 → `Buyer Preference - not a product issue`; else `Mixed reasons - no
single dominant cause`.

**Recommended Action** (from Flag + Root Cause): OK → `Monitor - no action needed`; Listing → `Update
title/images/description to match product; review A+ content`; Quality → `Raise with supplier/QC,
inspect next inbound shipment`; Buyer → `Monitor only - not a product/listing issue`; Too few →
`Monitor - insufficient data`; Mixed → `Review manually - mixed signal`.

> **Reproduce the quirk faithfully — do NOT "fix" it:** Flag (rate-based) and Root Cause (count-based,
> min 2) are **independent gates**. A 1-return ASIN can read `CRITICAL - URGENT REVIEW` yet resolve to
> `Too few returns to evaluate` / `Monitor - insufficient data`. This is intended behaviour.

## 7. Join & grain — LOCKED (ASIN anchor + listing_data bridge)
Returns carry **listing/variant SKUs** (`PHSF1GDRFG_AML`, `CL3RBM5PK FBA`); sales carry **base SKUs**
(`PHSF1GDRFG`). They do **not** join on `sku`. Anchor on **ASIN** (reliable on both sides; Amazon ≈ 1
SKU/ASIN) and resolve the display SKU through the bridge:
`public.listing_data` WHERE `which_channel = 1` AND `wrong_sku = 0` AND `COALESCE(is_parent,0) <> 1`
AND `market_place = 'UK'`; resolved SKU = `COALESCE(NULLIF(mapped_sku,''), sku)`. 89/91 ASINs resolve;
the 2 not in `listing_data` fall back to the **return SKU** (kept beside the resolved SKU for
traceability). Grain: **one row per returning ASIN.** (Bridge mechanics: `SKILL_ppc_stock_lookup.md` +
`TABLE_listing_data_1.md`.)

## 8. Responsible Person — LOCKED
`order_transaction.user_name` (portfolio holder) for the ASIN, via `mode()` where >1 candidate.
**Verified one ASIN = one owner** in this data. ASINs with no in-window FBA-UK sale have no
sales-derived owner → shown as **"Unassigned"** (candidate to resolve via `listing_data` — open item G).

## 9. Data model (read-only source objects)
| Table | Use | Key filters / columns |
|---|---|---|
| `public.amazon_returns` | returns (numerator) + reason split | `fulfilment='fba'`, `request_date` in window; `asin`, `sku`, `reason`, `qty`, `status`, `market_place`, `sub_source` |
| `public.order_transaction` | Units Sold (denominator) + Responsible PH | `source_name='AMAZON'`, `fba_sales=TRUE`, `market_place='UK'`, `order_status='Completed'`, `order_date` in window; `asin`, `sku`, `quantity`, `user_name` |
| `public.listing_data` | ASIN→SKU display bridge | `which_channel=1`, `wrong_sku=0`, `COALESCE(is_parent,0)<>1`, `market_place='UK'`; `ref_id`(ASIN), `sku`, `mapped_sku` |

**Aggregate-first, then join** (never join raw tables — row explosion). Chained-CTE:
`returns_agg` (by asin) LEFT JOIN `sales_agg` (by asin) LEFT JOIN `bridge` (by asin). Full query:
`sql/REQ-10_.../generate_report.sql` (= HANDOFF §5).

## 10. Report columns (exact, one row per ASIN)
`SKU · ASIN · Units Sold (Period) · Total Returns · Return Rate % · Listing Mismatch Qty · Quality
Issue Qty · Buyer Preference Qty · Shipping Issue Qty · Unknown Qty · Top Reason (Amazon) · Flag Status
· Root Cause · Recommended Action · Responsible Person (PH)`.

**Deliverables:**
- **`frrc30.json`** — the governed 91-row pull (system of record); the raw keys are `sku, asin,
  units_sold, total_returns, listing_qty, quality_qty, buyer_qty, shipping_qty, unknown_qty, top_reason,
  responsible_ph, return_sku, inv_sku`.
- **3-tab Excel** (`build_frrc30.py`) — threshold-driven formulas (Objective/Thresholds/Tracker shape).
- **Full-screen HTML console** (`build_console.py`) — dark sidebar with a **Portfolio-holder dropdown**
  + owner list (return counts, critical/high dots), KPI tiles, search, Flag chips, sort, and per-ASIN
  cards (reason-mix bar, likely cause, recommended action, rare-reason note). The owner dropdown drives
  the whole view — the report's headline "route each returning product to its owner" feature.

## 11. Reconciliation (run 2026-07-14, fixed window)
- **91** returning ASINs · **105** return units · per-row bucket sum = total_returns (**0 failures**).
- Flag distribution **CRITICAL 44 · HIGH 20 · OK 9 · N/A 18**; **19** named owners + **18** unassigned
  (= the 18 N/A rows).
- Cross-check vs source tracker (Rebecca's 2026-05-11 → 2026-07-12 window): Returns 95/101 exact; Units
  65/101 exact, all misses 1–3 higher in live (post-snapshot orders) — confirmed the Units-Sold and
  returns rules and settled the returns-window question (`request_date`-based, no `order_date`
  re-alignment). Excel recalc: **0 formula errors**.
- Data quirks confirmed live: `fulfilment` lowercase `fba`; `order_status` uses American spelling
  `Canceled`; return SKUs are listing-variants, sales SKUs are base (hence ASIN anchor + bridge).

## 12. Regeneration / re-run
1. Run `sql/REQ-10_.../reason_domain_check.sql` (Step 1) via the Postgres MCP; confirm every live
   `reason` is covered by §4 (flag any that isn't).
2. Run `sql/REQ-10_.../generate_report.sql` (the `json_agg` form) read-only; save as `frrc30.json`.
   Assert control totals via `validation_checks.sql` (91 ASINs / 105 returns / 0 bucket failures on the
   fixed window; recompute on a rolling window). Stop if they don't match.
3. `python3 build_frrc30.py` → the 3-tab Excel; recalc with the xlsx recalc script → expect 0 errors.
4. `python3 build_console.py` → the HTML console.
5. To roll daily: replace `DATE '2026-07-14'` with `CURRENT_DATE` in the SQL, and update the
   `WIN_START / WIN_END / RUN` constants at the top of both build scripts.

## 13. Known limits & held items
- Business edge cases (order-status set, marketplace scope, window length, returns↔sales alignment,
  rare reason codes, return-status filter, unassigned owners — items A–G in `PROJECT_HOME.md`) **await
  Satheesvaran sign-off**. Only the **return-status filter (F)** changes the numbers.
- `order_transaction`/`amazon_returns` reflect **current** live data — figures move as post-window
  orders land (the 1–3 unit drift seen in cross-check).
- The ultimate external cross-check is the **Amazon Seller Central FBA Customer Returns + All Orders
  reports** for the same window; a mismatch there is an upstream data issue, not a report bug.
- Scheduling not wired — the query is `CURRENT_DATE`-ready but no recurring trigger exists (REQ-10-D02).
- The prior session's **rendered outputs** (`FRRC_FBA_Returns_Console_*.html`,
  `FRRC_FBA_Returns_Tracker_*.xlsx`) are not in the import bundle — regenerate from `frrc30.json`.
