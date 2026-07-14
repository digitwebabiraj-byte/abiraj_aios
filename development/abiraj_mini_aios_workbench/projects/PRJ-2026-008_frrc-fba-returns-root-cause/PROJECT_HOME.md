# PROJECT_HOME — FRRC: FBA Returns Root-Cause (Rebecca)

## Project ID
PRJ-2026-008_frrc-fba-returns-root-cause

## Project Name
FRRC — FBA Returns Root-Cause | weekly Amazon FBA returns tracker & root-cause action report
(LEDsONE analytics platform)

## Purpose
Turn the hand-built Excel tracker `_Amazon_FBA_Returns_Tracker_-_Rebecca.xlsx` into a **live,
governed, repeatable report** that shows **which Amazon FBA products are being returned too often,
*why*, and what to do about it** — one row per returning ASIN, routed to the person who owns it. For
every Amazon FBA ASIN with ≥ 1 return in the window it reports real Units Sold, Total Returns, Return
Rate %, the return split across five reason buckets, and a threshold-driven **Flag Status / Root Cause
/ Recommended Action**. It is a **read-only reporting task** — no source table is ever written. Every
value ties to a real `schema.table.column`; all flagging/root-cause logic is driven by the editable
**Thresholds** tab, nothing hardcoded; unclear business rules are flagged for **Satheesvaran**, never
invented.

## Business Question
Which Amazon FBA SKUs/ASINs had returns in the last completed window, and for each — how many Units
Sold, how many Total Returns, the resulting Return Rate %, the return count split across Listing
Mismatch / Quality / Buyer Preference / Shipping / Unknown, and the computed Flag Status, Root Cause
and Recommended Action — so the optimisation, supplier-QC and packaging teams can classify each
high-return product as a **listing** problem, a **quality/supplier** problem, or ordinary **buyer
preference**, and act before repeat returns damage account health and margin?

Status: **CONFIRMED** from `_Amazon_FBA_Returns_Tracker_-_Rebecca.xlsx` (tabs Objective & Guide /
Thresholds / Tracker), requirement `REQ-10-D01`, and the `HANDOFF_FRRC_REQ-10-D01.md` handoff.
**Business edge-case sign-off (Satheesvaran) is OPEN** — see Known Risks / One Next Action.

## Owner and Reviewers
- Owner / Developer: **Abiraj**
- Report owner persona / end user: **Rebecca** + the listing-optimisation / supplier-QC / packaging
  teams, department leaders, MD
- Coordinator: Varmen
- Technical Reviewer: **Sajeesan** — sign-off pending
- Queryability Reviewer: **Tamil Selvan** — sign-off pending
- Business Validator: **Satheesvaran** (rule edge cases) — **sign-off pending**

## Original Requirement
- **REQ-10-D01 (2026-07-14)** — Build and **execute** the FRRC returns root-cause report: a governed
  read-only multi-table CTE query returning the 15 required columns, plus a threshold-driven **.xlsx**
  (3 tabs) and a full-screen **HTML console** with an owner dropdown, reconciled to the live DB, with
  control-total validation. The tracker's existing sample rows are **illustrative only** and are not
  reproduced as the answer.

## Approved Scope
- Maintain this project folder (`projects/PRJ-2026-008_frrc-fba-returns-root-cause/`) only.
- **READ-ONLY** inspection of the production Postgres analytics DB via the Postgres MCP, for discovery,
  the report pull and evidence. All source tables (`amazon_returns`, `order_transaction`,
  `listing_data`) are read-only.
- COPY-only import of the handoff bundle from `C:\Users\digit\Downloads\files (5).zip` (originals kept).
- Generate the report query + the xlsx/HTML renderers and their outputs. **No DB object created,
  dropped or altered** — this report is a per-run extract, not a view.

## Prohibited Scope
- No `INSERT`/`UPDATE`/`DELETE`, no DDL, no schema change, no seed anywhere in the DB.
- Do not invent business rules (order-status set, marketplace scope, window length, reason-code
  bucketing) — flag them for Satheesvaran.
- Do not reproduce the tracker's illustrative sample rows as the answer.
- Do not modify anything outside this project folder without written approval.
- Do not commit or push without explicit instruction.

## Systems and Sources (read-only)
- **Production Postgres analytics DB**, via the Postgres MCP (connector GUIDs rotate per session — rely
  on the `execute_sql` tool, not the id). All source objects in schema `public`.
- Key objects: `public.amazon_returns` (return detection, FBA, reason, qty), `public.order_transaction`
  (real Units Sold, `user_name` = responsible PH), `public.listing_data` (ASIN→SKU bridge). Full
  per-table rules in `SYSTEM_REFERENCE.md` §6 and the platform's `TABLE_*.md` references.
- Spec / acceptance source: `_Amazon_FBA_Returns_Tracker_-_Rebecca.xlsx` (`REQ-10-D01`) +
  `HANDOFF_FRRC_REQ-10-D01.md` + `FRRC_REQ-10-D01_execution_prompt.md`.

## Imported / Generated Assets
Under Task `REQ-10_fba-returns-root-cause` (COPY-only import; Downloads originals preserved):
- `evidence/source_documents/REQ-10_.../HANDOFF_FRRC_REQ-10-D01.md` — **single source of truth** (locked rules, final SQL, validation, open items).
- `evidence/source_documents/REQ-10_.../2026-07-14_abiraj_REQ-frrc_REQ-10-D01.md` — full daily requirement / spec.
- `evidence/source_documents/REQ-10_.../FRRC_REQ-10-D01_execution_prompt.md` — self-contained execution prompt.
- `evidence/source_documents/REQ-10_.../SOURCE_MANIFEST.md` — provenance + SHA-256.
- `sql/REQ-10_.../generate_report.sql` — canonical read-only report query (from HANDOFF §5).
- `sql/REQ-10_.../reason_domain_check.sql` — Step-1 live reason-domain check (run first).
- `sql/REQ-10_.../validation_checks.sql` — control-total / arithmetic / ownership / status-split checks.
- `evidence/final_outputs/REQ-10_.../frrc30.json` — governed 91-row pull — **system of record**.
- `evidence/final_outputs/REQ-10_.../build_frrc30.py` → the 3-tab threshold-driven `.xlsx`.
- `evidence/final_outputs/REQ-10_.../build_console.py` → the full-screen HTML console (owner dropdown).
- `evidence/final_outputs/REQ-10_.../FRRC_FBA_Returns_Console_REQ-10-D01_30day.html` — **rendered console output** (md5 `fb00ff20`, 35,625 bytes); data parity with `frrc30.json` verified exact.
- `evidence/logs_or_screenshots/REQ-10_.../2026-07-14_import_checksum_evidence.md` — import + dataset-integrity evidence.

## Source-of-Truth Locations
- **Data (system of record):** `evidence/final_outputs/REQ-10_.../frrc30.json` — the governed,
  validated pull for the fixed window. The rendered `.xlsx`/HTML are **derived** from it.
- **Locked rules / functional detail:** `SYSTEM_REFERENCE.md` (+ `HANDOFF_FRRC_REQ-10-D01.md` §4).
- **Canonical query:** `sql/REQ-10_.../generate_report.sql`.
- **Approved handoff/spec:** `evidence/source_documents/REQ-10_.../`.
- **Note:** the rendered **HTML console** is now imported (`FRRC_FBA_Returns_Console_REQ-10-D01_30day.html`,
  data-parity-exact with `frrc30.json`). The `FRRC_FBA_Returns_Tracker_*.xlsx` and the simpler grouped
  `FRRC_FBA_Returns_Report_*.html` are still to import — regenerable from `frrc30.json` via the build
  scripts. `build_console.py` / the console load Google Fonts (CDN) but embed all report data — no
  network call fetches data.

## Run Snapshot (fixed window 2026-06-14 → 2026-07-13, run 2026-07-14)
- **91** returning Amazon FBA ASINs · **105** return units · bucket-sum = total_returns on every row
  (0 arithmetic failures).
- Flag distribution: **CRITICAL 44 · HIGH 20 · OK 9 · N/A 18**. The 18 N/A rows had a return but no
  in-window FBA-UK Completed sale (sold earlier, or sold FBM/non-UK) — correct, not a bug.
- **19** named responsible PHs + **18** unassigned (the N/A rows, no sales-derived owner).
- Reproduces the source tracker on cross-check (Returns 95/101 exact, Units 65/101 exact, all misses
  1–3 higher in live = post-snapshot orders). Excel recalc: 0 formula errors.

## Known Risks / Open Items (flag to Satheesvaran — do NOT decide)
- **A. Order-status set** counting as a "sale" for Units Sold — working assumption **FBA-UK Completed
  only** (Cancelled/Pending excluded). Confirm whether Deleted/Hold/Refunded are also excluded.
- **B. Marketplace scope** — UK-only (current) vs all Amazon marketplaces.
- **C. Window length / cadence** — the source spec does not fix it; **last 30 days** is the working
  choice (the workbook's own example was ~62 days).
- **D. Returns ↔ sales window alignment** — `request_date`-based (current) vs align returns to their
  order's `order_date` via `order_id`.
- **E. Rare reason codes** — bucket for `MISSING_PARTS`, `SWITCHEROO`, `MISSED_ESTIMATED_DELIVERY`,
  `POOR_FIT`, `MISORDERED`, `UNAUTHORIZED_PURCHASE` (currently → Unknown so buckets reconcile).
- **F. Return-status filter** — currently every return counts regardless of `amazon_returns.status`;
  decide whether to count only physically-returned units. **This is the only open item that changes
  the numbers** — pull the status breakdown (validation CHECK 4) first.
- **G. Unassigned owners (18 N/A ASINs)** — engineering option to attribute via `listing_data` (by
  ASIN) so all 91 rows show a named owner.

## Live Publish
**PUBLISHED LIVE per-PH 2026-07-14** to `tech_team_outputs.ph_task` (DB `order_management_copy`) —
**19 rows, ids 216–234**, `project_code=frrc`, `assigned_user_team=ph_priors`, `version_status=released`,
one row per named portfolio holder (each holder sees **only their own** returning ASINs). Identifiers
from `2026-07-14_abiraj_REQ-frrc_REQ-10-D01.md`; `task_id=frrc_<PH-slug>_fba_returns_root_cause-V1`.
Covers **73 of 91 ASINs**; the **18 unassigned** N/A ASINs route to nobody (open item G). Done via an
owner-directed guarded write as `temp_user` (INSERT-only, one txn, md5-verified pre-commit, `frrc`
confirmed unused first; ph-asin/PC/ZSFO precedent); independently re-verified via the read-only MCP.
Rollback = `DELETE … WHERE project_code='frrc'` (new rows only). Full record:
`evidence/logs_or_screenshots/REQ-10_.../2026-07-14_per_ph_publish_record.md`. The credential-bearing
publish script stays in the session scratchpad — never committed.
**V2 UI (same day):** the per-PH dashboards were rebuilt with an embed-friendly document-flow layout
(sticky sidebar + sticky filter bar, cards fill full height — fixes the cramped internal-scroll box in
the portal) and a polished sidebar (avatar, mini stats, severity-split bar); published as a guarded
in-place UPDATE of the same 19 rows, `version_level` 1→2, identity fields unchanged, md5-verified.

## Status
- **D01: COMPLETE (technical) — PUBLISHED per-PH (rows 216–234); VALIDATION GREEN (self-checked);
  REVIEWER + BUSINESS SIGN-OFF PENDING.** Validated multi-table query, 91-row governed pull,
  threshold-driven xlsx + HTML console + 19 per-PH dashboards, control totals reconciled (91 ASINs /
  105 returns / 0 bucket failures) and cross-checked vs the source tracker.
- Not yet signed off by Tamil Selvan (queryability), Sajeesan (technical), or Satheesvaran (items A–G).

## One Next Action
Route the open items to **Satheesvaran** for a business decision — prioritise **F (return-status
filter)**, since it is the only one that changes the numbers; then **C (window length)** and **E (rare
reason codes)**. In parallel, submit for Tamil Selvan (queryability) and Sajeesan (technical) sign-off.
Once locked, optionally open **REQ-10-D02** to schedule the run with a dynamic `CURRENT_DATE`. Do not
change any locked rule without Satheesvaran sign-off.
