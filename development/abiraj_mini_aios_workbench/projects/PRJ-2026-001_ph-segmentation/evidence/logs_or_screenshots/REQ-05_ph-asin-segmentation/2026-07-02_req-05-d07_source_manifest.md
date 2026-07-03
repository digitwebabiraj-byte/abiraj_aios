# REQ-05-D07 Source Manifest

## Project ID

PRJ-2026-001_ph-segmentation

## Requirement ID

REQ-05

## Deliverable ID

REQ-05-D07

## Date

2026-07-02

## Recording Posture

The 2 July 2026 work (Phase-07) was executed by **Abiraj in a live Claude Chat session against the
live PostgreSQL database and dashboard**. This workbench record **documents and imports the saved
artifacts**; the executor did **not** query or modify the live DB, run SQL, or touch automation.
Evidence rule: **VERIFIED_FROM_FILE** = backed by a saved checksummed file here;
**DOCUMENTED_IN_D07** = stated in the D07 knowledge file (live session, not re-derived here);
**LIVE_STATE_NOT_RECHECKED** = live DB/dashboard state, not queried; **MISSING_ARTIFACT** = not on disk.

## What D07 delivered (from the knowledge file)

1. Full read-only verification of the live 2026-07 report (0 mismatches).
2. Live dashboard **restyle** (gold header + greeting over slate/teal body, bolder escalation banner,
   amber NEEDS_REVIEW rows) — pushed live (`preview_v2`, 884,616 B live).
3. **Card redesign** (per-card icons + colour-coding, Champions=green / Dead Horses=red) — pushed live (`preview_v3`).
4. **Strict segment-rank movement rule** (HHH=1…LLL=6, replacing the equal-weight h-count) — 65 rows
   moved SAME→IMPROVED/DECLINED; applied to the report table AND the baked dashboard data;
   final live = `live_v4_movrule.html` (888,511 B). **User-decided rule change (2 Jul), not a Bietrick sign-off.**
5. **Engine v3** (strict-rank) sandbox-validated (8,149 rows reproduced, 0 movement mismatches); not run live.
6. Plain-language walkthrough + source verification of the NEW mechanic (Saranya, paulr).

Also in the same day's chat thread: window-date meta strip, category-click filtering, dynamic
allocated card, jargon removal ("returning-aware"/"Method-A" gone), and **24 per-PH locked views**.

## Sources

| Source File | Original Path | Canonical Destination | Size | SHA-256 | Classification | Status |
| ----------- | ------------- | --------------------- | ---: | ------- | -------------- | ------ |
| 2026-07-02__abiraj__ph-asin__REQ-05-D07.md | DigitWeb_Works_Abiraj\02_07_2026\ | handover/REQ-05_ph-asin-segmentation/2026-07-02__abiraj__ph-asin__REQ-05-D07.md | 37642 | 65c1a010988e2946643d492dcdd5dee387931b4da69b65822829480a7f72e860 | DAILY_KNOWLEDGE | IMPORTED (checksum recorded) |
| preview_v2.html (restyle push #1) | Downloads (re-homed from the D06 import) | evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-07-02_ph_asin_dashboard_v2_restyle_preview.html | 884658 | 951354efd8969d7d97762f9fc6a8d6e5172687524a418fe98f75179f321711b6 | DASHBOARD_PREVIEW | IMPORTED (git mv from D06 — see correction below) |
| preview_v3.html (cards redesign; closest saved copy to the final live build) | Downloads | evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-07-02_ph_asin_dashboard_v3_cards_preview.html | 888305 | d4af079c8052b6b068f537e5d6e34a01972464b896f2ac77d8977f5b687539c7 | DASHBOARD_PREVIEW | IMPORTED (888,305 B vs D07-cited final 888,511 B — see limitation) |
| preview_catfilter.html (window dates + category filter + allocated card + jargon removed) | Downloads | evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-07-02_ph_asin_dashboard_catfilter_preview.html | 891397 | a72dc10e6d66b738a482d2a5db49b54b60feeefd0710285c93a7157a934fd332 | DASHBOARD_PREVIEW | IMPORTED |
| 24 per-PH locked views (Abinayaa…utharsika, exact spellings) | Desktop\files\ | evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-07-02_ph_per_holder_views/ | — | see `2026-07-02_per_holder_views.sha256` | PER_HOLDER_VIEWS | IMPORTED (24 files + checksum index) |
| claude_chat_link.txt (D07 chat transcript excerpt) | Downloads | evidence/logs_or_screenshots/REQ-05_ph-asin-segmentation/2026-07-02_claude_chat_transcript_d07.txt | 35862 | 400ac14be1c496bc7dab759012eed9125117e9bf1004a6f368ae0882e3f5d64a | PROVENANCE | IMPORTED |
| live_v4_movrule.html (final live id-5 dashboard, 888,511 B) | — (not on disk; Abiraj has only preview_v3) | evidence/final_outputs/REQ-05_ph-asin-segmentation/ (reserved) | — | — | LIVE_HTML_SNAPSHOT | MISSING_ARTIFACT |
| ph_segment_engine.sql v3 (strict-rank) + ph_segment_engine_prev-equalweight.sql.bak | — (not on disk) | sql/REQ-05_ph-asin-segmentation/ (reserved) | — | — | CANONICAL_ENGINE | MISSING_ARTIFACT |

### D06 correction (recorded here for provenance)

On 1 Jul, `preview_v2.html` (md5 `c1a3555c…`, sha `951354ef…`) was imported into the **D06** record and
mislabeled as the "1 July navy live dashboard." It is in fact the **2 July restyle** (this D07 increment).
The true 1 July dashboard was the navy dropdown build (879,907 B), which was **never exported to a file**
(it survives only in the DB backup `ph_task_id5_backup_20260702_css`). The file has been **re-homed** to
`2026-07-02_ph_asin_dashboard_v2_restyle_preview.html` and the D06 records annotated. See
`2026-07-01_req-05-d06_source_manifest.md` (D06-correction note).

## Claims Evidence Classification

| Claim | Evidence Status | Limitation |
| ----- | --------------- | ---------- |
| Read-only verification of live report: 0 mismatches, 8,146/8,149 source reconcile | DOCUMENTED_IN_D07 | Live session; not re-derived here |
| Restyle (gold/slate-teal) pushed live | VERIFIED_FROM_FILE (preview_v2) + DOCUMENTED_IN_D07 | Live DB row not queried |
| Card redesign pushed live | VERIFIED_FROM_FILE (preview_v3) + DOCUMENTED_IN_D07 | preview_v3 = 888,305 B vs live 888,511 B; live row not queried |
| Strict-rank movement rule: 65 rows SAME→IMPROVED/DECLINED, report + dashboard + engine | DOCUMENTED_IN_D07 | Final `live_v4_movrule.html` is MISSING_ARTIFACT; the imported preview_v3 predates the last 206-byte movement tweak |
| Engine v3 (strict-rank) sandbox-validated, not run live | DOCUMENTED_IN_D07 | Engine v3 SQL is MISSING_ARTIFACT — cannot verify from file |
| 24 per-PH locked views (only own data, dropdown hidden) | VERIFIED_FROM_FILE | 24 files + checksum index imported |
| Backups taken (`_css`, `_cards`, `_movdata`, `_movrule`), none dropped | DOCUMENTED_IN_D07 | Live DB state; not queried |
| Live output `ph_task` id 5 = 888,511 B | LIVE_STATE_NOT_RECHECKED | DB not queried; no exact-copy file imported |

## Missing Artifacts

1. `live_v4_movrule.html` (888,511 B) — the actual final live dashboard (restyle + cards + strict-rank movement).
   Abiraj has only `preview_v3.html` (888,305 B), imported as the closest proxy.
2. `ph_segment_engine.sql` v3 (strict-rank) + `ph_segment_engine_prev-equalweight.sql.bak` — not on disk.

## Duplicate Check

- D07 knowledge file imported once. GREEN.
- Three dashboard previews (v2 restyle / v3 cards / catfilter) are distinct builds by size + checksum;
  none duplicates another, and none is labeled the canonical live build (that is MISSING). GREEN.
- 24 per-PH views imported once each with a checksum index. GREEN.
- preview_v2 exists once (re-homed from D06, not duplicated). GREEN.

## Known Limits

- The repo does **not** hold the exact final live dashboard (`live_v4_movrule.html`) or engine v3; both
  are honestly flagged MISSING_ARTIFACT. `preview_v3` is the nearest saved representation.
- All live-DB / dashboard state remains LIVE_STATE_NOT_RECHECKED (DB not queried here).

## Result

**AMBER** — the D07 knowledge file, all three dashboard previews, the 24 per-PH views, and the chat
transcript are imported and checksummed; the exact final live dashboard and engine v3 are absent and
recorded as MISSING_ARTIFACT. REQ-05 mapping is confirmed; no new Task ID; no DB/automation/commit action.
