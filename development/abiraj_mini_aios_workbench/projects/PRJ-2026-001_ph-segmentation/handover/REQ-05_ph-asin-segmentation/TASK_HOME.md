# PH Segmentation Onboarding Task

## Task ID

REQ-05_ph-asin-segmentation

## Project ID

PRJ-2026-001_ph-segmentation

## Original Requirement Reference

REQ-05, as referenced in the Day-1 and Day-2 historical work summaries.

## Purpose

Preserve, classify, document and validate the previously completed PH Segmentation work
inside the approved Mini-AIOS project structure.

## Provenance

The implementation **preceded the GPT-controlled operating loop** — it was completed in
Claude Chat before the GPT → Claude → GPT model was adopted. This task is preservation and
validation only; GPT did not supervise the original implementation.

## Reconstructed Business Purpose

Classify every UK-Amazon FBM ASIN owned by each Portfolio Holder (PH) into one of six
performance segments each month (Impressions, Clicks, CVR vs per-PH per-category benchmark),
track month-over-month movement, and surface it as an interactive report with a fixed action
plan per segment. **Status: BUSINESS CONFIRMATION REQUIRED.**

## Candidate Business Question

Which of each PH's UK-Amazon FBM ASINs are underperforming each month based on impressions,
clicks and CVR against category benchmarks, how are they moving month over month, and what
action is due?

Status: **REQUIRES BUSINESS VALIDATOR** (not CONFIRMED).

## Inputs

* Protocol: `evidence/source_documents/REQ-…001/2026-06_ph-asin_segmentation_protocol_v1.0.docx`
* Day-1 summary: `handover/REQ-…001/2026-06-23__abiraj__ph-asin__REQ-05-D01.md`
* Day-2 summary: `handover/REQ-…001/2026-06-24__abiraj__ph-asin__REQ-05-D02.md`
* SQL engine: `sql/REQ-…001/2026-06-25_ph_segment_engine.sql`
* Monthly prompt (historical): `prompts/implementation/REQ-…001/2026-06-25_monthly_run_prompt_historical.md`
* Provenance link: `evidence/logs_or_screenshots/REQ-…001/2026-06-25_claude_chat_share_link.txt`

## Canonical Outputs

* Final HTML: `evidence/final_outputs/REQ-…001/2026-06-24_ph-asin_segmentation_report_2026-07.html`
* SQL engine: `sql/REQ-…001/2026-06-25_ph_segment_engine.sql` (stored, not executed)

## Historical Decisions (evidence-backed, from D02)

* D-0 scope ratified — writes to `analytics.*` + new source table authorised by Abiraj.
* D-1 re-derive per protocol; do not trust the pre-baked column.
* D-2 Method A CVR (per-ASIN CVR averaged across top-N).
* D-3 conversion edges: zero-click → LOW; conv > clicks → HIGH.
* D-4/Option B undefined-combo map: HLL → HLH, LHL → HHL.
* D-5 FBM-only inputs (`fba_sales=false`).
* D-6 single-cycle table (no history) accepted.

## Completion Claim Status

| Claim | Status | Evidence | Gap |
|---|---|---|---|
| Segmentation completed | PARTIAL | D02 summary + final HTML | No independent execution evidence |
| 7,855 ASINs processed | PARTIAL | D02 distribution table | No saved query output |
| Zero unclassified | PARTIAL | D02 (counts reconcile to 7,855) | Not independently re-run |
| FBM correction performed | PARTIAL | D02 §3B/§5 before-after counts | Self-reported only |
| HTML generated | VERIFIED | File present; parses; title/features match | Visual correctness pending |
| SQL engine produced | VERIFIED | File present; reviewed read-only | TECHNICAL REVIEW REQUIRED to run |
| Monthly prompt produced | VERIFIED | File present; reviewed read-only | Historical only |
| Output approved | BUSINESS CONFIRMATION REQUIRED | none | No sign-off artifact |
| Production-ready | UNPROVEN | none | No approval; visual + technical review pending |

## Technical Risks

* SQL is **write/DDL**; contains **DROP/CREATE** on `analytics.ph_segment_report` + temp helpers.
* No saved execution output (row count / distribution).
* D01 described an `order_transaction` SKU→ASIN join; the SQL reads `order_transaction."asin"` directly.
* Option B mapping (`LHL→HHL`) differs from the prior live-DB mapping (`LHL→LLH`).
* HTML visual review still required (JS-rendered).

## Evidence Paths

* Source manifest: `evidence/source_documents/REQ-…001/SOURCE_MANIFEST.md`
* Import evidence: `evidence/logs_or_screenshots/REQ-…001/2026-06-25_import_evidence.md`
* Duplicate-risk: `duplicate_risk_reports/REQ-…001/2026-06-25_import_duplicate_risk.md`

## Validation Path

`validation/REQ-05_ph-asin-segmentation/2026-06-25_import_validation.md`

## Review Results

* Technical Validation: PASS — Sajeesan
* Queryability Validation: PASS — Tamil Selvan
* Business Validation: PASS — Bietrick
* Coordinator Validation: PASS — Varmen

(All confirmed by Abiraj on 2026-06-25; no separate signed reviewer artifact was supplied.)

## Daily Increment — REQ-05-D06 — 2026-07-01

Third recorded delivery increment of REQ-05 (after 26 Jun and 30 Jun). **Not a new Task ID.**
Executed by Abiraj in a live Claude Chat session; imported here read-only. Import result **AMBER**
(4 of the day's artifacts imported + checksummed; 3 named artifacts absent — see the source manifest).

### Work Completed (from the D06 knowledge file)

- **Option A movement correction** — Bietrick approved; previous comparison window recomputed to
  4 complete weeks (3–30 May) while **current segments were left unchanged** (51/426/139/5/440/7,088).
  Declines corrected 628 → 574.
- **Returning-aware NEW correction** — a 46-row false-NEW artifact was caught and fixed with an
  8-week lookback rule (NEW back to the true 191) before go-live. Escalation moved 21 → 22 PHs,
  investigated and confirmed as accurate redistribution, not inflation.
- **Orphan ASIN monitor + assignment output** — term formalised; ownership confirmed absent across
  4 systems; permanent view `analytics.v_orphan_asins` created; live dashboard warning added;
  492-row assignment CSV produced (CSV not exported to repo — MISSING_ARTIFACT).
- **Engine v2** — `2026-07-01_ph_segment_engine_v2.sql`: self-contained on weekly `traffic_data`,
  equal 4-week windows, returning-aware, orphans excluded. Validated in scratch tables only;
  **deliberately not run against the live 2026-07 report** (next real run 3 Aug).
- **Monthly routine update** — `2026-07-01_ph_asin_monthly_routine.txt`: engine v2 embedded, orphan
  count pulls live from the view. **HTML shell BLOCK 1 still builds the old tabs UI** (open gap).
- **Protocol clarification** — `2026-07-01_ph_asin_protocol_v1_clarifications.md`: lateral→SAME,
  zero-click→LOW conversion, conv>clicks→HIGH conversion, HLL→HLH, LHL→HHL (Bietrick sign-off line).
- **Full verification** — 8,146/8,149 rows reconciled exactly to source (3 differ ±1 conversion);
  orphan/owned sets 0 overlap; dashboard vs report counts reconciled; **backups deliberately KEPT**.
- **Dropdown/table UI redesign** — dashboard rebuilt to a PH-dropdown + one-view flat-table layout
  (Rank, Avg Conv, Δ Conv, Status columns) matching a reference board, with classification logic
  proven 100% unchanged (Method-A CVR shown, not the reference's weighted CVR). Pushed live twice.

### Canonical Assets (imported this increment)

- Daily knowledge: `handover/REQ-05_ph-asin-segmentation/2026-07-01__abiraj__ph-asin__REQ-05-D06.md`
- Engine v2: `sql/REQ-05_ph-asin-segmentation/2026-07-01_ph_segment_engine_v2.sql`
- Monthly routine: `prompts/implementation/REQ-05_ph-asin-segmentation/2026-07-01_ph_asin_monthly_routine.txt`
- Protocol clarifications: `validation/REQ-05_ph-asin-segmentation/2026-07-01_ph_asin_protocol_v1_clarifications.md`
- Live dashboard HTML (id-5 v2): `evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-07-01_ph_asin_dashboard_id5_live_2026-07.html` *(imported 2 Jul)*
- UI review template: `evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-07-01_ph_asin_dashboard_ph_view_template.html` *(imported 2 Jul)*
- Orphan/unowned assignment CSV (492 rows): `evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-07-01_unowned_asins_for_assignment_2026-07.csv` *(imported 2 Jul)*
- Manifest: `evidence/logs_or_screenshots/REQ-05_ph-asin-segmentation/2026-07-01_req-05-d06_source_manifest.md`
- Update evidence / duplicate-risk / validation: matching `2026-07-01_req-05-d06_*` records.

### Current Live State (DOCUMENTED_IN_D06 — NOT RECHECKED DURING AIOS IMPORT)

- Live dashboard row: `tech_team_outputs.ph_task` id 5 (new dropdown UI, ~879,907 bytes).
- Live 2026-07 report uses the approved Option-A movement; current segments unchanged.
- Engine v2 is for the next fresh cycle (3 Aug); orphan monitor view exists.
- Live dashboard HTML, UI template, and orphan/unowned CSV are **now imported** (2 Jul) as saved,
  checksummed evidence in `evidence/final_outputs/`. The live DB row itself was not re-queried
  (LIVE_STATE_NOT_RECHECKED), but every work-product exists as a file.

### Open Gaps

- Cloud Routine creation still pending (Windows feature).
- Routine HTML BLOCK 1 still builds the **old** UI — must be swapped before the 3 Aug run.
- Backup tables retained (housekeeping deferred).
- Engine v2 has not completed its first live monthly run (by design, 3 Aug).
- Live values may drift after the recorded verification time.

### Status

- Daily Increment REQ-05-D06: **COMPLETE** (import **PASS** as of 2 Jul — all 7 work-products
  imported + checksummed; was AMBER on 1 Jul when 3 artifacts were absent).
- Requirement REQ-05: **ACTIVE — FOLLOW-UP WORK REMAINS** (delivery gaps below, not import defects).

### Next Step

Replace the monthly routine's HTML BLOCK 1 with the approved dropdown/table UI before the next
monthly run. (All 7 D06 work-products are now imported — the artifact-import step is closed.)

## Current Status

CLOSED for the onboarding/preservation scope (PASS) — **in a DELIVERY phase since 2026-06-26**,
with three recorded delivery increments of this same requirement: 26 Jun (dashboard UI fix + live
release), 30 Jun (final-June refresh + validation), and **1 Jul (REQ-05-D06 — Option-A movement
fix, Orphan ASIN routing, engine v2, protocol clarifications, dropdown UI redesign)**. None are
new Task IDs.

## Final Task Result

PASS (onboarding scope). Delivery increments: AMBER — see each delivery/increment record.

## One Next Step

Swap the monthly routine's HTML BLOCK 1 to the new dropdown UI before the 3 Aug run. (The D06
artifact import is complete — all 7 work-products are saved and checksummed; live-UI and orphan
claims are now VERIFIED_FROM_FILE.)

## Pass / Fail Rule

PASS if all approved files are preserved with matching checksums, documented provenance and
no unsupported claim marked as verified. FAIL otherwise.
