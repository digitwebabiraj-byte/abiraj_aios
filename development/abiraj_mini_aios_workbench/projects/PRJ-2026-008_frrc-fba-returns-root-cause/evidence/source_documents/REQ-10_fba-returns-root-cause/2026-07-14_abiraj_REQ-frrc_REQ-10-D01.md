# **Daily Requirement Document**

## **1. Metadata Block**

| Field | Value |
| ----- | ----- |
| daily_requirement_submitted_date | 2026-07-14 |
| expected_deadline_date | 2026-07-14 |
| end_user | Rebecca (report owner/persona for the FBA Returns Tracker), the listing-optimization & supplier-QC teams, packaging/ops, department leaders, developers or MD — anyone who must act on high-return-rate Amazon FBA SKUs |
| expected_roi | Replaces the manual ~1.5-hour-per-cycle hunt (pull the FBA Customer Returns report + All Orders reports, match SKUs, compute return rate, categorise every return reason, then decide root cause + action per SKU) with **one automated, root-cause report**. It surfaces exactly which Amazon FBA SKUs have an **abnormally high return rate** and attaches the diagnostics needed to decide *why* — the return split by reason bucket (Listing Mismatch / Quality / Buyer Preference / Shipping / Unknown) beside real Units Sold. This lets the team separate a **listing-mismatch problem** (wrong expectations set → fix title/images/A+) from a **quality/defect problem** (→ raise with supplier/QC, inspect next inbound) from **ordinary buyer preference** (→ monitor only), instead of guessing — shortening the time from "returning too often" to "fixed" before repeat returns damage account health and margin |
| developer | abiraj |
| project | FRRC — FBA Returns Root-Cause (weekly Amazon FBA returns tracker & root-cause action report) — LEDsONE analytics platform |
| project_code | frrc |
| phase | Phase — Report build & scheduling (FRRC Stage 1 — canonical returns root-cause report, first deliverable) |
| requirement_id | REQ-10 |
| deliverable_id | REQ-10-D01 |
| blos_keys | Flagging & root-cause thresholds (from the tracker's editable **Thresholds** tab, not hardcoded): **Critical** Return Rate % > **0.20** · **High** > **0.10** · **Minimum 2 returns** before root-cause logic runs · reason-share cutoffs — Listing Mismatch ≥ **0.40**, Quality ≥ **0.40**, Buyer Preference ≥ **0.50**. Return Rate % = **Total Returns ÷ Units Sold** in the same window. Reporting-only — no source table is mutated |
| domain | Analytics — Amazon Marketplace — FBA Returns — Root-Cause Reporting — Text-to-SQL |
| daily_planned_benefits | (1) One canonical **FBA Returns Root-Cause report** any user can run — every FBA SKU that had at least one return in the window, with Units Sold, Total Returns, Return Rate %, the reason-bucket split, and a computed **Flag Status / Root Cause / Recommended Action** beside each row · (2) Correct, defensible **reporting-window logic** (returns matched to real Units Sold over the same window; N/A shown where a SKU had returns but no in-window sales) proven with a worked example · (3) Correct **multi-domain join** — returns → sales (units sold) → responsible PH — with the reason-code → bucket mapping applied exactly as the Thresholds tab defines · (4) All flagging/root-cause logic driven by the **editable threshold table**, nothing hardcoded in the row formulas · (5) Any unclear business rule **flagged to Satheesvaran and parked**, never invented — read-only against all source tables |

---

# **2. Today Requirement Block**

### **Purpose**

Defines which part of the complete FRRC requirement is to be executed today. The source specification is the Excel workbook `_Amazon_FBA_Returns_Tracker_-_Rebecca.xlsx` (sheets **Objective & Guide**, **Thresholds**, **Tracker**), which defines a recurring **FBA Returns Tracker & Root-Cause Analysis** but is a **hand-built illustrative artifact** — it holds the rule set, the editable thresholds and a worked tracker built from a one-off report drop, but **no runnable, data-governed report exists yet**. Today's scope: turn that specification into a **working, executed multi-table report** for Amazon FBA SKUs — every SKU with at least one return in the window, enriched with real Units Sold and the return-reason split needed to compute Flag Status, Root Cause and Recommended Action — and confirm the reporting-window and threshold rules against a worked example before locking them. The source tables, application data and database are **read-only** — nothing is written back to any source table; the only output is the report/dataset and this planning record.

## **2.1 Today Requirement**

### **Task Name:**

Build and execute the FRRC returns root-cause report — Amazon FBA SKUs that had returns in the window, with real Units Sold, Total Returns, Return Rate %, the return split by reason bucket, and a computed Flag Status / Root Cause / Recommended Action driven by the editable thresholds.

### **Business Purpose:**

The optimisation, supplier-QC and packaging teams currently have no automated way to know which FBA SKUs are being returned abnormally often, or *why*. Today's work is to produce **one canonical report** that answers, from the governed data alone: which FBA SKUs had returns in the last completed window, and for each one — how many **Units Sold**, how many **Total Returns**, the resulting **Return Rate %**, and the return count split across **Listing Mismatch / Quality / Buyer Preference / Shipping / Unknown** buckets — then applies the Thresholds tab to compute **Flag Status** (CRITICAL / HIGH / OK / N/A), **Root Cause** and **Recommended Action** for each row. This lets a reviewer immediately classify each high-return SKU as a listing problem, a quality/supplier problem, or ordinary buyer preference, and act. Where the source spec's logic is unclear (exact order-status set that counts as a "sale", marketplace scope, the full live reason-code domain, and how the returns window aligns to the sales window), the ambiguity is to be **recorded and escalated to Satheesvaran** — never silently decided. The tracker's existing rows and any sample values are **illustrative only** and must not be reproduced as the answer.

---

### **Source Information**

Source System:

Postgres analytics database (READ-ONLY for this task)

Requirement source (READ-ONLY):
`_Amazon_FBA_Returns_Tracker_-_Rebecca.xlsx` — sheets `Objective & Guide`, `Thresholds`, `Tracker` (rule set + editable thresholds + illustrative output shape)

Governing skills (READ-ONLY):
`SKILL_multi_table.md` (routing, join path, aggregation-before-join, mandatory postgres execution)
`SKILL_single_table.md` (intent routing reference)
`SKILL_ppc_stock_lookup.md` (ASIN ↔ SKU bridge / clean-SKU step — reference only, used if ASIN-level resolution is needed)

Tables to be read (READ-ONLY):

`public.amazon_returns` — return detection (`asin`, `sku`, `fulfilment`, `reason`, `qty`, `request_date`, `market_place`, `sub_source`)
`public.order_transaction` — real Units Sold per SKU (`sku`, `asin`, `quantity`, `order_status`, `order_date`, `source_name`, `fba_sales`, `market_place`, `user_name` = responsible PH)
`public.listing_data` — ASIN (`ref_id`) → SKU / `mapped_sku` bridge (`wrong_sku`, `market_place`, `which_channel`) — only if ASIN-keyed reconciliation is required

---

### **Filter Conditions**

Write scope: **report/dataset output ONLY** — no write to any source table, no schema change, no seed
Task ID: `REQ-frrc_ledsone-fba-returns-root-cause` — deliverable **REQ-10-D01** (first deliverable of the REQ-10 / FRRC stream)
Channel / fulfilment scope: **Amazon FBA only** — returns `amazon_returns.fulfilment = 'FBA'`; sales `order_transaction.source_name = 'AMAZON'` AND `fba_sales = TRUE`
Population: SKUs with **at least one return** in the window (zero-return SKUs are excluded — there is nothing to flag), matching the workbook's stated population
Return Rate definition: **Total Returns ÷ Units Sold** over the same window; show **"N/A"** where the SKU had returns but **no in-window sales** (`Units Sold = 0`)
Reporting period: the last completed window, ending on the day *before* the report is generated — **current-day partial data excluded** (the workbook's built example used **2026-05-11 → 2026-07-12**; the exact cadence/length is a held item, see Stop conditions)
Worked example (to be validated): report generated **2026-07-14** ⇒ window computed the same way and printed alongside the results
Threshold source: all flagging/root-cause cutoffs are read from the **Thresholds** tab values (Critical > 0.20, High > 0.10, min 2 returns, reason-share 0.40 / 0.40 / 0.50) — treated as editable inputs, **never hardcoded** into the row logic
Execution rule: SQL is never the final answer — it **must be executed via `postgres:execute_sql`** and the real rows returned
Stop conditions: order-status set that counts as a "sale" unconfirmed by Satheesvaran · marketplace scope (UK-only vs all Amazon) unconfirmed · returns-window ↔ sales-window alignment rule unconfirmed · live `reason` domain not all mapped to a bucket · a write would land on any source table

---

### **Required Data Output**

| Field | Purpose |
| ----- | ----- |
| FRRC report dataset (main deliverable) | One row per qualifying FBA SKU: `SKU` · `ASIN` · `Units Sold (Period)` · `Total Returns` · `Return Rate %` · `Listing Mismatch Qty` · `Quality Issue Qty` · `Buyer Preference Qty` · `Shipping Issue Qty` · `Unknown Qty` · `Top Reason (Amazon)` · `Flag Status` · `Root Cause` · `Recommended Action` · `Responsible Person (PH)` — matching the Tracker sheet's required shape |
| Executed SQL + real results | The multi-table CTE query, **run** against postgres, with the actual returned rows (not a query shown alone) |
| Reporting-window proof | The exact window used for the 2026-07-14 run, plus the workbook's 2026-05-11 → 2026-07-12 example reconciled, showing current-day exclusion and how returns are matched to Units Sold |
| Threshold-application note | How each row's Flag Status / Root Cause / Recommended Action was derived from the Thresholds tab values (nothing hardcoded), so the logic is re-traceable and re-tunable |
| Reason-bucket mapping note | The `reason` → bucket assignment applied (Listing Mismatch / Quality / Buyer Preference / Shipping / Unknown) exactly as the Thresholds tab defines, with any live reason code not covered by the map called out |
| Open-logic / held-items note | Every unclear rule (order-status filter, marketplace scope, window alignment, full reason-code domain) parked for Satheesvaran — flagged, not invented |
| Schedule note | How the report is set to run on cadence and how to re-run it manually for an ad-hoc window |
| report_period | 2026-07 |

---

# **Business Logic Block**

Purpose:
Defines how today's report is to be built and evaluated. Only a report/dataset is to be produced — nothing in any source table is to be changed. All flagging/root-cause logic is driven by the editable Thresholds tab, never hardcoded into the row logic.

## **Return-Rate Qualification & Flagging**

Rule:

- A SKU enters the report only if it has **≥ 1 return** (FBA) in the window; zero-return SKUs are excluded.
- `Return Rate % = Total Returns ÷ Units Sold` over the same window. If `Units Sold = 0`, Return Rate % is **"N/A"** and Flag Status = **"N/A - No Sales Data"**.
- Flag Status keys off the **rate** (Thresholds tab): rate > **0.20** → `CRITICAL - URGENT REVIEW`; rate > **0.10** (and ≤ 0.20) → `HIGH RETURN - REVIEW`; else → `OK`.
- The order-status set that counts as a "sale" for Units Sold (e.g. Completed only, vs also New/Inprogress; and whether Refunded rows are included) is to be **confirmed with Satheesvaran** before locking; the working assumption is to be stated explicitly in the held-items note.

## **Reporting-Period (last completed window, current-day excluded)**

Rule:

- The window ends on the day *before* the report is generated. Current-day partial data is **never** included.
- Returns are filtered on `amazon_returns.request_date` within the window; Units Sold on `order_transaction.order_date` within the **same** window. The workbook itself notes a SKU can show "N/A" when it "sold just before the window started" — so the **returns-window ↔ sales-window alignment** (keep request_date-based, or align returns to their order's `order_date` via `order_id`) is a held item to confirm, not to decide today.
- Worked example to reconcile: the workbook's built window **2026-05-11 → 2026-07-12**. For the 2026-07-14 build run, the window is computed the same way and printed alongside the results. The exact cadence/length (weekly vs rolling-60) is unfixed in the source and is parked for Satheesvaran.

## **Root-Cause Enrichment (reason buckets)**

Rule:

- Root Cause runs only if `Total Returns ≥ 2` (Thresholds tab **Minimum Returns to Evaluate**); otherwise Root Cause = **"Too few returns to evaluate"** and Recommended Action = "Monitor - insufficient data".
- Each return's `reason` is mapped to one bucket, exactly as the Thresholds tab defines:
  - **Listing Mismatch** — `NOT_COMPATIBLE`, `NOT_AS_DESCRIBED`
  - **Quality Issue** — `QUALITY_UNACCEPTABLE`, `DEFECTIVE`, `DAMAGED_BY_FC`, `DAMAGED_BY_CARRIER`
  - **Buyer Preference** — `UNWANTED_ITEM`, `FOUND_BETTER_PRICE`, `ORDERED_WRONG_ITEM`
  - **Shipping Issue** — `UNDELIVERABLE_UNKNOWN`, `UNDELIVERABLE_REFUSED`
  - **Unknown** — `NO_REASON_GIVEN`
- Root Cause is then the first bucket whose share clears its cutoff (Thresholds tab): Listing Mismatch Qty ÷ Total Returns ≥ **0.40** → "Listing/Expectation Mismatch"; else Quality Qty ÷ Total ≥ **0.40** → "Quality/Defect Issue"; else Buyer Preference Qty ÷ Total ≥ **0.50** → "Buyer Preference - not a product issue"; else "Mixed reasons - no single dominant cause".
- `Top Reason (Amazon)` = the single most common raw `reason` for the SKU (quick reference only, not used in the logic).
- **Full reason-code domain must be confirmed:** `DAMAGED_BY_FC`, `DAMAGED_BY_CARRIER`, `FOUND_BETTER_PRICE`, `ORDERED_WRONG_ITEM`, `UNDELIVERABLE_REFUSED` are used in the bucket map but are **not** in the documented `amazon_returns.reason` reference. Run a `DISTINCT reason` check first; any live code not covered by the map is flagged (not silently dropped) so no return is mis-bucketed.

## **Recommended Action**

Rule:

- Derived from Flag Status + Root Cause exactly as the Tracker sheet defines: `OK` → "Monitor - no action needed"; Listing/Expectation Mismatch → "Update title/images/description to match product; review A+ content"; Quality/Defect Issue → "Raise with supplier/QC, inspect next inbound shipment"; Buyer Preference → "Monitor only - not a product/listing issue"; Too few returns → "Monitor - insufficient data"; Mixed → "Review manually - mixed signal".
- Note the source's intended behaviour: Flag Status (rate-based) and Root Cause (count-based, min 2) are **independent gates**, so a SKU can read `CRITICAL` yet still resolve to "Too few returns to evaluate" / "Monitor - insufficient data". This is reproduced faithfully, not corrected.

## **Responsible Person**

Rule:

- `Responsible Person (PH)` is resolved from `order_transaction.user_name` (portfolio holder) for that SKU. Where a SKU maps to more than one PH in the window, the resolution rule (most-recent vs most-units) is stated in the held-items note.

## **Safety**

Rule:

- **Read-only against all source data.** No INSERT/UPDATE/DELETE on `amazon_returns`, `order_transaction`, `listing_data` or any other table; no schema change; no seeding; no application/config/deployment change.
- The report documents behaviour **from the data as it stands** — no invented rules and no business-rule decisions. If a rule is unclear it is **flagged and parked**, not decided.
- SQL alone is never the deliverable — the query **must be executed** and real rows returned (per the multi-table and single-table skills).
- Reviewer gates: Queryability (Tamil Selvan) and Technical (Sajeesan) sign-off to follow; business-logic clarifications routed to **Satheesvaran** per the source spec.

---

# **Data Enrichment Block**

Purpose:
Record the join path and the resolution trail so a reviewer can re-trace every column in the report.

Source:

`public.amazon_returns`  — return detection (FBA), reason split, `qty`, filtered `fulfilment = 'FBA'`
`public.order_transaction`  — real Units Sold per SKU (`source_name = 'AMAZON'`, `fba_sales = TRUE`), and Responsible PH (`user_name`)
`public.listing_data`  — ASIN (`ref_id`) → SKU / `mapped_sku` bridge, `wrong_sku = 0` — only if ASIN-keyed reconciliation is required

Required Data:

| Field | Reason |
| ----- | ----- |
| Multi-table CTE query (executed) | Returns aggregated by SKU + reason bucket → Units Sold aggregated by SKU over the same window → Return Rate % → Flag Status / Root Cause / Recommended Action from Thresholds → Responsible PH, run via `postgres:execute_sql` |
| Reporting-window record | The exact window used for the run + the workbook's 2026-05-11 → 2026-07-12 example reconciled, proving current-day exclusion and returns↔sales alignment |
| Reason-bucket resolution trail | The `reason` → bucket map applied, plus the live `DISTINCT reason` check and any code not covered by the map |
| Threshold-application trail | Per-row: which threshold each Flag Status / Root Cause / Action came from, so the logic is re-tunable from the Thresholds tab alone |
| SKU / ASIN reconciliation note | Whether returns and sales joined cleanly on `sku`; where ASIN-level reconciliation was needed, the `listing_data` (`wrong_sku = 0`, `mapped_sku` fallback, clean-SKU step) trail per `SKILL_ppc_stock_lookup.md` |
| Assumptions / held-items note | Order-status filter, marketplace scope, window alignment, full reason-code domain, multi-PH resolution — each parked for Satheesvaran, not fixed today |
| Schedule / re-run note | How the report runs on cadence and how to trigger it manually for an ad-hoc window |
| report_period | 2026-07 |
