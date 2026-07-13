# PROJECT_HOME — Zero Sales Full Optimization (ZSFO)

## Project ID
PRJ-2026-006_zero-sales-full-optimization

## Project Name
ZSFO — Zero Sales Full Optimization | Weekly zero-sale + diagnostics report, Amazon UK (Utharsika)

## Purpose
Automate the recurring **weekly (Monday)** report that lists Portfolio Holder **Utharsika's**
Amazon-UK ASINs which sold **zero units in the last completed 30 days** — across FBA+FBM
(`order_transaction`) **and** Vendor/1P (`vendor_sales`) — together with the traffic-funnel and
stock diagnostics needed to explain *why* each one is dead, so the listings can be optimised.
Every figure ties to a real `schema.table.column`; unproven fields are flagged, never invented.

## Business Question
Every Monday, which of Utharsika's Amazon-UK ASINs had **0 units sold in the last completed 30
days** (FBA+FBM and Vendor), and for each — what is its UK warehouse stock, Amazon FBM stock, and
30-day traffic funnel (impressions / clicks / conversion, week by week) — so the team can see the
likely root cause (out of stock · not surfacing · no clicks · no conversion) and act?

Status: **CONFIRMED** from `utharsika task.xlsx` (task `PH-2026-07-UTHAR04`, requirement
`REQ-08-D01`) and the `PROJECT_CONTEXT.md` handoff. **Business edge-case sign-off (Satheesvaran)
is still OPEN** — see Known Risks / One Next Action.

## Owner and Reviewers
- Owner / Developer: **Abiraj**
- End user (Portfolio Holder): **Utharsika** (DB spelling `utharsika`)
- Coordinator: Varmen
- Technical Reviewer: Sajeesan
- Queryability Reviewer: Tamil Selvan
- Business Validator: **Satheesvaran** (rule edge cases) — **sign-off pending**

## Original Requirement
- **REQ-08-D01 (2026-07-10)** — ZSFO weekly report for the first live Monday window
  **2026-06-10 → 2026-07-09**: governed read-only rebuild query (`generate_dataset.sql`) + a
  template-matching **.xlsx** and an interactive **HTML dashboard**, reconciled to the live DB,
  with an independent 6-check verification pack. Diagnostics added beyond the base spec:
  Last Vendor Sale / Last Amazon Sale (lifetime), Vendor Units (lifetime), week-by-week
  impressions/clicks (5 buckets) and a derived Root-cause hint.

## Approved Scope
- Maintain this project folder (`projects/PRJ-2026-006_zero-sales-full-optimization/`) only.
- **READ-ONLY** inspection of production PostgreSQL `order_management_copy` via the Postgres MCP,
  for discovery, the dataset pull and evidence.
- COPY-only import of the delivery handoff / spec from `C:\Users\digit\Downloads\` (originals kept).
- Generate the dataset query + the xlsx/HTML renderers and their outputs. **No DB object created,
  dropped or altered** — this report is a per-run extract, not a view.

## Prohibited Scope
- No `INSERT`/`UPDATE`/`DELETE`, no DDL, no schema change anywhere in the DB.
- Do not invent sales, SKU→SKU mappings, product names or user attributions not present in the DB.
- Do not modify anything outside this project folder without written approval.
- Do not commit or push without explicit instruction.

## Systems and Sources (read-only)
- **PostgreSQL `order_management_copy`** (production), via the Postgres MCP (connector GUIDs rotate
  per session — rely on the DB name, not the id).
- Key objects: `traffic_data` (universe + funnel), `order_transaction` (FBA+FBM sales),
  `vendor_sales` (1P sales), `listing_data` (SKU bridge + FBM qty), `location_wise_inv_stock`
  (UK warehouse stock). Full per-table rules in `SYSTEM_REFERENCE.md`.
- Spec / acceptance source: `utharsika task.xlsx` (`PH-2026-07-UTHAR04`) + `PROJECT_CONTEXT.md`.

## Imported / Generated Assets
Under Task `REQ-08_zero-sales-full-optimization` (COPY-only import; Downloads originals preserved):
- `evidence/source_documents/REQ-08_.../PROJECT_CONTEXT.md` — approved handoff.
- `evidence/source_documents/REQ-08_.../utharsika_task.xlsx` — the task spec sheet.
- `evidence/source_documents/REQ-08_.../ORIGINAL_ZSFO_VERIFICATION_PACK_full-catalogue_superseded.md`
  — the first (full-catalogue) verification draft, preserved for audit.
- `sql/REQ-08_.../generate_dataset.sql` — canonical read-only rebuild query.
- `evidence/final_outputs/REQ-08_.../`:
  - `data.json` — governed pull (1,250 rows + run metadata).
  - `build_report.py` → `ZSFO_Zero_Sales_Full_Optimization_Utharsika.xlsx`.
  - `build_html.py`   → `ZSFO_Utharsika_dashboard.html`.
  - `ZSFO_VERIFICATION_PACK.md` — corrected independent 6-check pack (Utharsika population).
- `validation/REQ-08_.../2026-07-10_validation.md` — live reconciliation evidence.
- `closure/REQ-08_.../2026-07-10_final_closure.md` — closure record.

## Source-of-Truth Locations
- **Dashboard (key deliverable):** `evidence/final_outputs/REQ-08_.../ZSFO_Utharsika_dashboard.html`
  (rebuild via `build_html.py`; spine `data.json`; query `generate_dataset.sql`).
- **Spreadsheet:** `…/ZSFO_Zero_Sales_Full_Optimization_Utharsika.xlsx` (rebuild via `build_report.py`).
- **Locked rules / functional detail:** `SYSTEM_REFERENCE.md`.
- **Approved handoff/spec:** `evidence/source_documents/REQ-08_.../`.

## Run Snapshot (2026-07-10, window 2026-06-10 → 2026-07-09)
- **Universe 1,719** Amazon-UK ASINs → **1,250 zero-sale** (report). Sold FBA/FBM 469; vendor
  in-window 34 (all inside the 469). 0 vendor-only false exclusions.
- Root cause: 680 impressions-but-0-clicks · 323 clicks-but-0-sales · **214 out of stock** ·
  33 zero-impressions.
- 1,035 of the 1,250 still hold UK warehouse stock (dead but stocked — prime optimisation targets).
- **Live-DB note:** `location_wise_inv_stock` is *current* stock (no history) — the 30-day window
  is historical but stock is as-of-today; stated on the dashboard footer + xlsx subtitle.

## Known Risks / Open Items
- **Business edge-case sign-off (Satheesvaran) OPEN:** exact `order_status` set counted as a sale,
  and the authoritative universe definition (traffic-derived vs listing-derived) still need a
  business confirmation. Current build uses `order_status='Completed'` and the traffic-derived
  universe (1,719), per the handoff.
- **Scheduling not yet wired.** `run_date` and the five week-bucket ranges are set in
  `generate_dataset.sql`; a Monday trigger with a dynamic `CURRENT_DATE` window is an open task.
- **Stock is live-as-of-today**, not a window snapshot (documented, not a defect).

## D02 — Amazon `AMZ_2026` cross-check (added 2026-07-10)
A revised handoff cross-checked D01 against Amazon's own `AMZ_2026` "Ordered Product Sales" report
and produced a "corrected" report of **1,065** ASINs (zero in both postgres and Amazon) with a
189-ASIN "Removed (sold per Amazon)" tab. **Onboarded as D02** (imported files +
`removed_191_amz_reconciliation.csv`).

**Independent verification correction (see D02 validation):**
- Directionally sound: reproduced **191 removed → 1,059** (planner 1,065 within 6 ASINs).
- **Handoff diagnosis REFUTED:** it blamed a **vendor (1P) `vendor_sales` gap** and prescribed a
  re-sync. Verified: **0 of 191** are vendor; **87% are seller (3P) sibling-ASIN sales already in our
  DB** — this is **per-ASIN vs per-product attribution (listing sprawl)**, the same finding surfaced
  earlier. `vendor_sales` is not missing for 2026 (rows through 2026-07-08).
- Handoff £12,394.76 → verified `AMZ_2026` **£5,101.24**; flagship "B093T3TR2Y £2,659" is wrong
  (AMZ shows June £0/332 items + July £730.64/88 — the £2,659 came from the stale IMPORTRANGE tab).
- **No DB re-sync performed** — read-only project, and the fix is unwarranted.

## Live Publish
Published to the shared ops store `tech_team_outputs.ph_task` (DB `order_management_copy`) —
**row id 167**: `project_code=ZSFO` · `task_id=ZSFO_utharsika_zero_sales_dashboard-V1` ·
`task_name=ZSFO · Zero Sales Full Optimization — Utharsika (Amazon UK)` · `team=Development` ·
`developer=Abiraj` · `assigned_user=utharsika` · `assigned_user_team=ph_priors` ·
`version_status=released`. Written via guarded single-row INSERT/UPDATE (owner-authorised, via the
`temp_user` write connection); no other row touched, no schema/DDL, no application/`public` data
changed. Canonical copy in-repo:
`evidence/final_outputs/REQ-08_.../D02_amz_crosscheck/ZSFO_Utharsika_dashboard_PUBLISHED_id167_v1.html`.

**Current live version (2026-07-13): period switched to LAST MONTH = June 2026** (per end-user
request — reverses the original spec's "do not use previous calendar month"; the 30-day rolling
window is retired for now). Basis: **1,237 DB June-zero − 122 sold-in-June-per-Amazon (KPI col N) =
1,115 true June zero-sale.** Root-cause: Low CTR 654 · Clicks-no-sale 225 · No stock 137 · Not
listed 66 · No visibility 33. Same design + the full-screen UI pass (compact header/hero, ~2→12
visible rows). Footer wording **corrected** to "122 removed — sold in June per Amazon (sibling-ASIN)"
(the earlier inaccurate "missing vendor data" line is gone). Window label = "June 2026 (last month)".

## Status
- **D01: COMPLETE (technical) — VALIDATION GREEN; BUSINESS SIGN-OFF PENDING.** Corrected query
  (vendor OVERLAP + NULL-channel bridge), 1,250-row governed pull, xlsx + HTML dashboard, 6/6
  verification pack. Not committed/pushed.
- **D02: ONBOARDED — VALIDATION AMBER.** Corrected report row-set sound (1,065 ≈ 1,059), but the
  handoff's vendor-gap diagnosis is refuted and the per-ASIN-vs-per-product definition is still an
  open owner decision.
- Not yet business-validated by Satheesvaran. Nothing committed/pushed.

## One Next Action
Take the **corrected mechanism** (sibling-ASIN attribution, not a vendor gap) to **Satheesvaran**
and decide the definition: **per-ASIN** (dead listings — keep 1,250, add a "sells under sibling
ASIN" flag) vs **per-product** (dead SKUs — exclude the ~191, the D02 view). Also fix the exclusion
rule (AMZ items vs £, swings ~120 ASINs) and the `AMZ_2026` June £0/items data anomaly. Do **not**
schedule a `vendor_sales` re-sync — it would not change the result.
