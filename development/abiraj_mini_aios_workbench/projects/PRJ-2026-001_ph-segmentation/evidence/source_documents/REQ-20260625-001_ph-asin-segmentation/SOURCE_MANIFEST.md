# PH Segmentation Source Manifest

## Project and Task

* Project ID: PRJ-2026-001_ph-segmentation
* Task ID: REQ-20260625-001_ph-asin-segmentation
* Import date: 2026-06-25
* Imported by: Claude Code for Abiraj (controlled execution layer)
* Intake source folder: C:\Users\digit\OneDrive\Desktop\PH_Segmentation_Intake

## Provenance Statement

The original PH Segmentation implementation was completed using **Claude Chat before the
GPT-controlled workflow was adopted**.

This manifest records a **retrospective preservation and validation import**.

It does **not** claim that GPT supervised the original work.

## Canonical Asset Register

| Asset ID | Original Filename | Classification | Source SHA-256 | Canonical Filename | Canonical Destination | Destination SHA-256 | Verification | Original Modified? |
|---|---|---|---|---|---|---|---|---|
| A1 | Traffic - 06 Segmentations - GPE (Growth Protection Engine).docx | ORIGINAL_INPUT_DOCUMENT | d8b7ff18a68305e39153e3328d2302d46f32289fe0406ef6887194cf12dca494 | 2026-06_ph-asin_segmentation_protocol_v1.0.docx | evidence/source_documents/REQ-20260625-001_ph-asin-segmentation/ | d8b7ff18a68305e39153e3328d2302d46f32289fe0406ef6887194cf12dca494 | MATCH | NO |
| A2 | PH_ASIN_Segmentation_Report_2026-07 (1).html | FINAL_HTML_OUTPUT | 25dd91034196fe95313f53f843bfa6508dd224d2b4b624effaa2580c29f7f74c | 2026-06-24_ph-asin_segmentation_report_2026-07.html | evidence/final_outputs/REQ-20260625-001_ph-asin-segmentation/ | 25dd91034196fe95313f53f843bfa6508dd224d2b4b624effaa2580c29f7f74c | MATCH | NO |
| A3 | 2026-06-23__abiraj__ph-asin__REQ-05-D01.md | HISTORICAL_WORK_SUMMARY | f25c7d700aed3b43ba3815b271b5b3ff7d1e6fe7856f9f4653bafa0d73dc702e | (original name preserved) | handover/REQ-20260625-001_ph-asin-segmentation/ | f25c7d700aed3b43ba3815b271b5b3ff7d1e6fe7856f9f4653bafa0d73dc702e | MATCH | NO |
| A4 | 2026-06-24__abiraj__ph-asin__REQ-05-D02.md | HISTORICAL_WORK_SUMMARY | b70b3a9ae0ffef728d284220af4668a333c88b7380871a3f4e1aeea96f12cf8a | (original name preserved) | handover/REQ-20260625-001_ph-asin-segmentation/ | b70b3a9ae0ffef728d284220af4668a333c88b7380871a3f4e1aeea96f12cf8a | MATCH | NO |
| A5 | claude_chat_link.txt | CLAUDE_CHAT_LINK — LIVE_LINK_ONLY | 89c7e1313767a4b0f3108e7aa7be278591ff88bde53cd809e5cd6cde6003a1f3 | 2026-06-25_claude_chat_share_link.txt | evidence/logs_or_screenshots/REQ-20260625-001_ph-asin-segmentation/ | 89c7e1313767a4b0f3108e7aa7be278591ff88bde53cd809e5cd6cde6003a1f3 | MATCH | NO |
| A6 | ph_segment_engine.sql | SQL_DELIVERABLE — HISTORICAL PROJECT ASSET | 0ca4818c07ae70c03226d4b8f771ed4a32ff957412f6b6594bb910fc1966239e | 2026-06-25_ph_segment_engine.sql | sql/REQ-20260625-001_ph-asin-segmentation/ | 0ca4818c07ae70c03226d4b8f771ed4a32ff957412f6b6594bb910fc1966239e | MATCH | NO |
| A7 | MONTHLY_RUN_PROMPT.md | MONTHLY_EXECUTION_PROMPT — PRESERVED AS HISTORICAL | 236f7a3e1041a80ad7919fc84ec05a6b006c965e4cf83bee6b57c53f5021f89f | 2026-06-25_monthly_run_prompt_historical.md | prompts/implementation/REQ-20260625-001_ph-asin-segmentation/ | 236f7a3e1041a80ad7919fc84ec05a6b006c965e4cf83bee6b57c53f5021f89f | MATCH | NO |

## Canonical HTML Confirmation

* Original filename: PH_ASIN_Segmentation_Report_2026-07 (1).html
* Canonical destination filename: 2026-06-24_ph-asin_segmentation_report_2026-07.html
* Full SHA-256: 25dd91034196fe95313f53f843bfa6508dd224d2b4b624effaa2580c29f7f74c
* Size: 440,506 bytes
* Confirmed by: Abiraj
* Confirmation date: 2026-06-25
* Status: CANONICAL_CONFIRMED

## Claude Provenance Limitation

LIVE_LINK_ONLY — ACCEPTED WITH LIMITATION. No export option was available to Abiraj; the link
may later expire or become inaccessible; the full conversation is not preserved locally; this
is partial provenance, not an import blocker. (The URL is stored in the evidence file and is
not reproduced here; it was not opened.)

## SQL Warning

STORED ONLY — NOT EXECUTED. The SQL contains write/DDL operations (drops/recreates
`analytics.ph_segment_report` and temp helpers). Execution requires Sajeesan's technical
approval and explicit database write authorisation.

## Monthly Prompt Status

PRESERVED AS HISTORICAL — NOT GOVERNED FOR REUSE.

## Files Excluded

ChatGPT_Brain_Setup.md — NOT REQUIRED.

## Known Evidence Gaps

* no saved SQL execution output;
* no independent 7,855-row validation;
* no immutable Claude transcript export;
* no business sign-off;
* no production-readiness approval.
