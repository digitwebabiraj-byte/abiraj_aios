# REQ-05-D06 Duplicate-Risk Report — 2026-07-01

## Project / Requirement / Deliverable

PRJ-2026-001_ph-segmentation · REQ-05 · REQ-05-D06

| # | Check | Finding | Result |
|---|---|---|---|
| 1 | D06 daily file exists once | One copy at handover/REQ-05_ph-asin-segmentation/2026-07-01__abiraj__ph-asin__REQ-05-D06.md | GREEN |
| 2 | Engine v2 exists once | One copy at sql/REQ-05_.../2026-07-01_ph_segment_engine_v2.sql; distinct from v1 (2026-06-25, window-table) | GREEN |
| 3 | Live HTML snapshot exists once | Imported once (2 Jul) as `2026-07-01_ph_asin_dashboard_id5_live_2026-07.html` (884,658 B, sha `951354ef…`) | GREEN |
| 4 | UI template vs live HTML differentiated | Both imported and distinct: template `..._ph_view_template.html` (752,008 B, 0 dropdown/status markers = review mockup) vs live `..._id5_live_2026-07.html` (884,658 B, 20 markers = shipped UI). Different sizes + checksums | GREEN |
| 5 | Old and new engines not both labelled current | v1 = HISTORICAL provenance; v2 = going-forward (next live run 3 Aug). Labelled explicitly in the manifest and TASK_HOME | GREEN |
| 6 | Orphan CSV exists once | Imported once (2 Jul) as `2026-07-01_unowned_asins_for_assignment_2026-07.csv` (492 rows). File keeps older "unowned" name; concept = Orphan ASIN (noted in manifest) | GREEN |
| 7 | DB view vs CSV not competing truth | `analytics.v_orphan_asins` = live monitor (current); CSV = 2026-07 assignment snapshot (point-in-time). Roles documented; not competing | GREEN |
| 8 | TASK_HOME.md remains task context | Updated in place with a dated increment section; no project-level content moved in | GREEN |
| 9 | PROJECT_HOME.md remains project context | Updated project-level fields only; no task detail duplicated in | GREEN |
| 10 | No second REQ-05 or D06 row | No new task row; existing REQ-05 row updated; no REQ-06 / dated ID minted | GREEN |

## Additional checks

- Undated `PH_Segmentation_Intake/ph_segment_engine.sql` (v1 variant) deliberately NOT imported — avoids a third engine copy.
- No canonical file was overwritten (all destinations were empty before copy).
- SYSTEM_REFERENCE.md not edited (its §1/§7 8,149-build update remains a separate governed step).

## Decision

GREEN — no duplicate or parallel-truth risk introduced by the D06 import.
