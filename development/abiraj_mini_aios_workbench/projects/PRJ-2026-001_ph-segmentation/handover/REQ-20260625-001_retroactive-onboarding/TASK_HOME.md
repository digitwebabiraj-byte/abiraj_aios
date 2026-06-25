# PH Segmentation Retrospective Onboarding Task

## Task ID

REQ-20260625-001_retroactive-onboarding

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
* Import evidence: `evidence/logs_or_screenshots/REQ-…001/2026-06-25_retrospective_import_evidence.md`
* Duplicate-risk: `duplicate_risk_reports/REQ-…001/2026-06-25_retrospective_import_duplicate_risk.md`

## Validation Path

`validation/REQ-20260625-001_retroactive-onboarding/2026-06-25_retrospective_import_validation.md`

## Review Results

* Technical Validation: PASS — Sajeesan
* Queryability Validation: PASS — Tamil Selvan
* Business Validation: PASS — Bietrick
* Coordinator Validation: PASS — Varmen

(All confirmed by Abiraj on 2026-06-25; no separate signed reviewer artifact was supplied.)

## Current Status

CLOSED

## Final Task Result

PASS

## One Next Step

Create a new Task ID before future monthly execution.

## Pass / Fail Rule

PASS if all approved files are preserved with matching checksums, documented provenance and
no unsupported claim marked as verified. FAIL otherwise.
