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
| live_v4_movrule.html (the 2 Jul intermediate strict-rank live build, 888,511 B) | — (no file matches its md5 `b7ae5e46` in any supplied folder) | evidence/final_outputs/REQ-05_ph-asin-segmentation/ (reserved) | — | — | LIVE_HTML_SNAPSHOT | MISSING_ARTIFACT — **but superseded** (the current live is the 3 Jul catfilter build, md5 `1f657a1b`, which IS imported). Not needed. |
| ph_segment_engine.sql (strict-rank; file header labels it "v2", adds the strict-rank movement rule — this is what D07 called "v3") + `..._prev-equalweight.sql.bak` | C:\Users\digit\Downloads\files (2)\ph_segment_engine.sql | sql/REQ-05_ph-asin-segmentation/2026-07-02_ph_segment_engine_strict_rank.sql | 13158 | 3164f4274b8e7855e882a20cfd0166b0a29063873fea70903e98ac9fa026536c | CANONICAL_ENGINE | **IMPORTED 2026-07-06** — distinct from the D06 returning-aware v2 (`14a63bc4`); adds strict-rank movement |

### D06 correction (recorded here for provenance)

On 1 Jul, `preview_v2.html` (md5 `c1a3555c…`, sha `951354ef…`) was imported into the **D06** record and
mislabeled as the "1 July navy live dashboard." It is in fact the **2 July restyle** (this D07 increment).
The true 1 July dashboard was the navy dropdown build (~879,907 B). It was **found 6 Jul** in
`Downloads\files (2)\` and imported into the D06 record (md5 `9b65e429`). The mislabeled restyle file has
been **re-homed** to `2026-07-02_ph_asin_dashboard_v2_restyle_preview.html`. See
`2026-07-01_req-05-d06_source_manifest.md` (D06-correction note, resolved 6 Jul).

## Claims Evidence Classification

| Claim | Evidence Status | Limitation |
| ----- | --------------- | ---------- |
| Read-only verification of live report: 0 mismatches, 8,146/8,149 source reconcile | DOCUMENTED_IN_D07 | Live session; not re-derived here |
| Restyle (gold/slate-teal) pushed live | VERIFIED_FROM_FILE (preview_v2) + DOCUMENTED_IN_D07 | Live DB row not queried |
| Card redesign pushed live | VERIFIED_FROM_FILE (preview_v3) + DOCUMENTED_IN_D07 | preview_v3 = 888,305 B vs live 888,511 B; live row not queried |
| Strict-rank movement rule: 65 rows SAME→IMPROVED/DECLINED, report + dashboard + engine | DOCUMENTED_IN_D07 + strict-rank engine imported 6 Jul | The rule is now VERIFIED_FROM_FILE in the imported engine; the exact 2 Jul intermediate live (`live_v4_movrule`) is absent but superseded by the current catfilter live |
| Engine (strict-rank) sandbox-validated, not run live | VERIFIED_FROM_FILE (imported 6 Jul, `3164f427…`) | Contains strict-rank + returning-aware; not run against live by design (first live run 3 Aug) |
| 24 per-PH locked views (only own data, dropdown hidden) | VERIFIED_FROM_FILE | 24 files + checksum index imported |
| Backups taken (`_css`, `_cards`, `_movdata`, `_movrule`), none dropped | DOCUMENTED_IN_D07 | Live DB state; not queried |
| Live output `ph_task` id 5 = 888,511 B | LIVE_STATE_NOT_RECHECKED | DB not queried; no exact-copy file imported |

## Missing Artifacts

**Update 2026-07-06:** the strict-rank **engine is now imported** (found in `Downloads\files (2)\`,
sha `3164f427`). One item remains absent but is **not needed**:

1. ~~`ph_segment_engine.sql` (strict-rank)~~ — **RESOLVED 6 Jul**, imported as
   `sql/…/2026-07-02_ph_segment_engine_strict_rank.sql`.
2. `live_v4_movrule.html` (888,511 B, md5 `b7ae5e46`) — the **2 Jul intermediate** strict-rank live build.
   No supplied file matches its md5. **Superseded** — the current live dashboard is the 3 Jul catfilter build
   (md5 `1f657a1b`), which IS imported. `preview_v3.html` (888,305 B) remains as the nearest 2 Jul proxy.
   Not needed for a complete record.

## Duplicate Check

- D07 knowledge file imported once. GREEN.
- Three dashboard previews (v2 restyle / v3 cards / catfilter) are distinct builds by size + checksum;
  none duplicates another, and none is labeled the canonical live build (that is MISSING). GREEN.
- 24 per-PH views imported once each with a checksum index. GREEN.
- preview_v2 exists once (re-homed from D06, not duplicated). GREEN.

## Known Limits

- The strict-rank **engine is now imported** (6 Jul). The only absent item is the 2 Jul *intermediate*
  live build (`live_v4_movrule.html`), which is **superseded** by the imported 3 Jul catfilter live —
  so it is not needed. `preview_v3` remains the nearest 2 Jul proxy.
- All live-DB / dashboard state remains LIVE_STATE_NOT_RECHECKED (DB not queried here).

## Result

**PASS (updated 2026-07-06)** — the D07 knowledge file, all three dashboard previews, the 24 per-PH
views, the chat transcript, **and the strict-rank engine** (imported 6 Jul, `3164f427`) are imported and
checksummed. The only absent item is the superseded 2 Jul intermediate live build, which the current
imported catfilter live replaces — nothing needed is missing. REQ-05 mapping confirmed; no new Task ID;
no DB/automation/commit action.

_Was AMBER (2 Jul) while the engine + live build were off-disk; upgraded to PASS on 6 Jul once the engine
was found in `Downloads\files (2)\`._
