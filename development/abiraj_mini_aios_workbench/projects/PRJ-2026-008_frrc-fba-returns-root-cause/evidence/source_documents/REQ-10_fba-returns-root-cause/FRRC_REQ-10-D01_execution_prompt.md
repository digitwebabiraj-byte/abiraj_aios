# Execution Prompt — FRRC Returns Root-Cause Report (REQ-10-D01)

You are building and **executing** a governed multi-table report on the LEDsONE Postgres analytics platform. Follow this prompt exactly. All source data is **READ-ONLY**. SQL is never the final answer — every query must be run via `postgres:execute_sql` and the real rows returned.

---

## Objective

Reproduce the **Amazon FBA Returns Tracker & Root-Cause Analysis** (source spec: `_Amazon_FBA_Returns_Tracker_-_Rebecca.xlsx`) as a live, data-governed report. Produce **one row per Amazon FBA SKU that had at least one return** in the reporting window, with real Units Sold, Total Returns, Return Rate %, the return split by reason bucket, and a computed **Flag Status / Root Cause / Recommended Action** — driven by the thresholds below, nothing hardcoded differently.

Zero-return SKUs are excluded (nothing to flag). The tracker's existing sample rows are **illustrative only** — do not reproduce them; return real data.

---

## Step 0 — Read first (READ-ONLY)

Load and follow these before writing any SQL:
- `SKILL_multi_table.md` — routing, join path, aggregate-first rule, mandatory execution
- `TABLE_amazon_returns.md` — returns detection, reason values, fulfilment filter
- `TABLE_order_transaction.md` — Units Sold, order_status, source/fba flags, `user_name` (responsible PH)

Join path: `amazon_returns.sku = order_transaction.sku` is a **direct join** → use the **chained-CTE** approach. Do **not** use the `listing_data` bridge / supervised flow — that is only for stock/traffic paths, and no stock or traffic is used here.

---

## Step 1 — Verify the live reason domain (run this first)

Execute:
```sql
SELECT reason, COUNT(*) FROM public.amazon_returns
WHERE fulfilment = 'FBA'
GROUP BY reason ORDER BY 2 DESC;
```
Confirm every returned `reason` is covered by the bucket map in Step 4. Any live code not in the map must be **flagged in the held-items note**, never silently pushed into "Unknown".

---

## Step 2 — Scope & filters

- **Returns** (`amazon_returns`): `fulfilment = 'FBA'`, `request_date` within the window.
- **Sales / Units Sold** (`order_transaction`): `source_name = 'AMAZON'` AND `fba_sales = TRUE`, `order_date` within the **same** window.
- **Population:** SKUs with ≥ 1 FBA return in the window (driven from the returns side); LEFT JOIN to sales so a SKU with returns but zero in-window sales still appears (Return Rate = "N/A").
- **Responsible Person:** `order_transaction.user_name` (portfolio holder) for that SKU.

---

## Step 3 — Reporting window

- The window is the **last completed period ending on the day *before* the run date**. **Exclude current-day partial data.**
- Print the exact window dates used, and reconcile the workbook's built example (**2026-05-11 → 2026-07-12**), showing current-day exclusion.
- **Working assumption to STATE and PARK for Satheesvaran:** the exact window length/cadence is not fixed in the source spec (the workbook used ~62 days). State the length you used and flag it — do not silently lock it.

---

## Step 4 — Reason → bucket map (apply exactly)

| Bucket | Reason codes |
|---|---|
| Listing Mismatch | `NOT_COMPATIBLE`, `NOT_AS_DESCRIBED` |
| Quality Issue | `QUALITY_UNACCEPTABLE`, `DEFECTIVE`, `DAMAGED_BY_FC`, `DAMAGED_BY_CARRIER` |
| Buyer Preference | `UNWANTED_ITEM`, `FOUND_BETTER_PRICE`, `ORDERED_WRONG_ITEM` |
| Shipping Issue | `UNDELIVERABLE_UNKNOWN`, `UNDELIVERABLE_REFUSED` |
| Unknown | `NO_REASON_GIVEN` |

`Top Reason (Amazon)` = the single most frequent raw `reason` for the SKU (reference only, not used in the logic).

---

## Step 5 — Thresholds (editable inputs — treat as constants, do not hardcode differently)

| Threshold | Value | Rule |
|---|---|---|
| Critical Return Rate | `> 0.20` | Flag = "CRITICAL - URGENT REVIEW" |
| High Return Rate | `> 0.10` | Flag = "HIGH RETURN - REVIEW" (and ≤ 0.20) |
| Min Returns to Evaluate | `>= 2` | Root-cause logic runs only at/above this |
| Listing Mismatch share | `>= 0.40` | Root Cause = Listing/Expectation Mismatch |
| Quality share | `>= 0.40` | Root Cause = Quality/Defect Issue |
| Buyer Preference share | `>= 0.50` | Root Cause = Buyer Preference |

---

## Step 6 — Computation (mirror the tracker's formulas exactly)

**Return Rate %** = `Total Returns / Units Sold`; guard divide-by-zero with `NULLIF`; output **"N/A"** when Units Sold = 0 or NULL.

**Flag Status** (rate-based):
- Return Rate = N/A → `N/A - No Sales Data`
- rate > 0.20 → `CRITICAL - URGENT REVIEW`
- rate > 0.10 → `HIGH RETURN - REVIEW`
- else → `OK`

**Root Cause** (count-based, then reason share):
- Total Returns < 2 → `Too few returns to evaluate`
- else Listing Mismatch Qty / Total Returns ≥ 0.40 → `Listing/Expectation Mismatch`
- else Quality Qty / Total Returns ≥ 0.40 → `Quality/Defect Issue`
- else Buyer Preference Qty / Total Returns ≥ 0.50 → `Buyer Preference - not a product issue`
- else → `Mixed reasons - no single dominant cause`

**Recommended Action** (from Flag Status + Root Cause):
- Flag = OK → `Monitor - no action needed`
- Root Cause = Listing/Expectation Mismatch → `Update title/images/description to match product; review A+ content`
- Root Cause = Quality/Defect Issue → `Raise with supplier/QC, inspect next inbound shipment`
- Root Cause = Buyer Preference → `Monitor only - not a product/listing issue`
- Root Cause = Too few returns → `Monitor - insufficient data`
- else → `Review manually - mixed signal`

> **Reproduce faithfully, do not "fix":** Flag Status (rate-based) and Root Cause (count-based, min 2) are **independent gates**. A 1-return SKU can read `CRITICAL - URGENT REVIEW` yet resolve to `Monitor - insufficient data`. Keep this behaviour.

---

## Step 7 — Build the chained CTE (aggregate first, then join)

```
CTE returns_agg:   FROM amazon_returns, fulfilment='FBA' + window
                   GROUP BY sku, asin
                   → total_returns = SUM(qty)
                   → listing_mismatch_qty / quality_qty / buyer_pref_qty / shipping_qty / unknown_qty
                     via SUM(CASE WHEN reason IN (...) THEN qty ELSE 0 END)
                   → top_reason via MODE()/count-rank per sku

CTE sales_agg:     FROM order_transaction, source_name='AMAZON' AND fba_sales=TRUE + window
                   + order_status filter (see held items)
                   GROUP BY sku
                   → units_sold = SUM(quantity)
                   → responsible_ph = any/most-frequent user_name

FINAL SELECT:      returns_agg LEFT JOIN sales_agg ON sku
                   → return_rate (NULLIF guard, 'N/A' when units_sold is 0/NULL)
                   → flag_status / root_cause / recommended_action via CASE ladders (Step 6)
                   ORDER BY total_returns DESC, return_rate DESC
```

Never join raw tables before aggregating (row explosion).

---

## Step 8 — Output shape (exact columns, one row per SKU)

`SKU` · `ASIN` · `Units Sold (Period)` · `Total Returns` · `Return Rate %` · `Listing Mismatch Qty` · `Quality Issue Qty` · `Buyer Preference Qty` · `Shipping Issue Qty` · `Unknown Qty` · `Top Reason (Amazon)` · `Flag Status` · `Root Cause` · `Recommended Action` · `Responsible Person (PH)`

---

## Step 9 — Execute and deliver

1. Run the reason-domain check (Step 1) via `postgres:execute_sql`.
2. Run the full report query via `postgres:execute_sql` and return the **real rows** (not the query alone).
3. Print the **exact window** used + the 2026-05-11→07-12 reconciliation.
4. Attach the **held-items note** (Step 10).
5. Add a short **schedule / re-run note** (how it runs on cadence, how to trigger an ad-hoc window).

---

## Step 10 — Working assumptions to STATE and PARK for Satheesvaran (never invent)

Record the assumption you used **and** flag it for confirmation:
- **Order-status set** counting as a "sale" for Units Sold — working assumption: exclude `Cancelled` and `Pending` (per the workbook's "Cancelled/Pending excluded" note); confirm whether `Deleted`/`Hold`/`Refunded` are also excluded.
- **Marketplace scope** — UK-only vs all Amazon marketplaces.
- **Window length / cadence** — the source spec does not fix it.
- **Returns↔sales window alignment** — keep `request_date`-based, or align returns to their order's `order_date` via `order_id`.
- **Full reason-code domain** — any live `reason` not in the Step 4 map.
- **Multi-PH SKUs** — resolution rule if a SKU maps to more than one `user_name` in the window.

---

## Safety & stop conditions (hard rules)

- **READ-ONLY.** No INSERT/UPDATE/DELETE, no schema change, no seed on `amazon_returns`, `order_transaction`, `listing_data`, or any table.
- **Do not invent business rules.** Unclear rule → flag and park (Step 10), do not decide.
- **SQL alone is never the deliverable** — it must be executed and real rows returned (per the multi-table skill).
- **Stop** if: a write would land on any source table · order-status/marketplace/window rule is required but unconfirmable · a live reason code cannot be safely bucketed.
- Reviewer gates after build: Queryability (Tamil Selvan) · Technical (Sajeesan) · Business-logic clarifications (Satheesvaran).
