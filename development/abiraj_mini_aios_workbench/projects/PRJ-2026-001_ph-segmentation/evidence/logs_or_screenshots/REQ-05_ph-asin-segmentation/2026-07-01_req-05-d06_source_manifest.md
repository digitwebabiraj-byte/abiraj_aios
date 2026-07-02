# REQ-05-D06 Source Manifest

## Project ID

PRJ-2026-001_ph-segmentation

## Requirement ID

REQ-05

## Deliverable ID

REQ-05-D06

## Date

2026-07-01

## Recording Posture

The 1 July 2026 work was executed by **Abiraj in a separate Claude Chat session against the
live PostgreSQL database and dashboard**. This workbench record **documents and imports the
saved artifacts** from that session; the workbench executor did **not** query or modify the
live database, run SQL, or touch automation. Evidence rule: a claim is **VERIFIED_FROM_FILE**
only when backed by a saved, checksummed file inside this project; live-only outcomes are
**DOCUMENTED_IN_D06** or **LIVE_STATE_NOT_RECHECKED**; absent handoff files are **MISSING_ARTIFACT**.

## Sources

| Source File | Original Path | Canonical Destination | Size | SHA-256 | Classification | Status |
| ----------- | ------------- | --------------------- | ---: | ------- | -------------- | ------ |
| 2026-07-01__abiraj__ph-asin__REQ-05-D06.md | C:\Users\digit\OneDrive\Desktop\DigitWeb_Works_Abiraj\01_07_2026\2026-07-01__abiraj__ph-asin__REQ-05-D06.md | handover/REQ-05_ph-asin-segmentation/2026-07-01__abiraj__ph-asin__REQ-05-D06.md | 43951 | 5ebdcb0c238389c37d2b96cfe005b2da770fcaff64563887fc0e41951bb1739c | DAILY_KNOWLEDGE | IMPORTED (checksum matched) |
| ph_segment_engine.sql (v2) | C:\Users\digit\OneDrive\Desktop\Postgress_backup\files.zip → ph_segment_engine.sql | sql/REQ-05_ph-asin-segmentation/2026-07-01_ph_segment_engine_v2.sql | 12534 | 14a63bc4d24e114a6333b51367b360b7b65f48e2a8a6ce1b2bb2912040e529b0 | CANONICAL_ENGINE | IMPORTED (checksum matched) |
| PH_ASIN_Monthly_Routine.txt | C:\Users\digit\OneDrive\Desktop\Postgress_backup\files.zip → PH_ASIN_Monthly_Routine.txt | prompts/implementation/REQ-05_ph-asin-segmentation/2026-07-01_ph_asin_monthly_routine.txt | 38322 | 947879174d87d7f4632e1150a62b05784882e909e8224e85e8706d568c95d1ed | MONTHLY_ROUTINE | IMPORTED (checksum matched) |
| PH_ASIN_Protocol_v1.0_Clarifications.md | C:\Users\digit\OneDrive\Desktop\Postgress_backup\PH_ASIN_Protocol_v1.0_Clarifications.md | validation/REQ-05_ph-asin-segmentation/2026-07-01_ph_asin_protocol_v1_clarifications.md | 4963 | 1de131c25557462929f351dc37b4d4a94eb24fcd519e7772dfe5e4b0cc99f359 | PROTOCOL_CLARIFICATION | IMPORTED (checksum matched) |
| unowned_asins_for_assignment_2026-07.csv (Orphan-ASIN assignment output; file keeps older "unowned" term) | C:\Users\digit\Downloads\unowned_asins_for_assignment_2026-07.csv | evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-07-01_unowned_asins_for_assignment_2026-07.csv | 27447 | d4f288d0a47c729275a73f84ea1c4130ad0e4c1a5ca9a41a20e56214267af02c | ORPHAN_ASSIGNMENT_OUTPUT | IMPORTED 2026-07-02 (checksum matched; 492 data rows) |
| preview_v2.html (confirmed by Abiraj as the latest/live id-5 v2 dashboard) | C:\Users\digit\Downloads\preview_v2.html | evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-07-01_ph_asin_dashboard_id5_live_2026-07.html | 884658 | 951354efd8969d7d97762f9fc6a8d6e5172687524a418fe98f75179f321711b6 | LIVE_HTML_SNAPSHOT | IMPORTED 2026-07-02 (checksum matched) |
| PH_ASIN_Dashboard_PH_view_TEMPLATE.html | C:\Users\digit\Downloads\PH_ASIN_Dashboard_PH_view_TEMPLATE.html | evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-07-01_ph_asin_dashboard_ph_view_template.html | 752008 | 1bb90b8cca63a2457a27c76bdbf5879e3f0aa61fd62c2cf402c23ff4025319c0 | UI_TEMPLATE | IMPORTED 2026-07-02 (checksum matched) |

### Note on the historical engine

The **v1** monthly-window engine is already preserved in the project at
`sql/REQ-05_ph-asin-segmentation/2026-06-25_ph_segment_engine.sql` (reads
`analytics.ph_segment_30days_window`). The newly-imported **v2** engine is self-contained on
weekly `public.traffic_data` and does not depend on the monthly window table. Both are retained;
v1 is HISTORICAL_NOT_FOR_EXECUTION provenance, v2 is the going-forward engine (next live run 3 Aug).
A separate undated `ph_segment_engine.sql` copy exists in `DigitWeb_Works_Abiraj/PH_Segmentation_Intake/`
(a v1 variant, SHA-256 `0ca4818c…`) — **not imported** (duplicate of the v1 lineage, not the v2 delivered today).

## Claims Evidence Classification

| Claim | Source | Evidence Status | Limitation |
| ----- | ------ | --------------- | ---------- |
| Option A movement-window fix approved by Bietrick and applied live to `ph_task` id 5 | D06 §2 Change 1-2, §7 D-26/D-27 | DOCUMENTED_IN_D06 | Live DB write; not re-queried in workbench |
| Current segment counts unchanged (51/426/139/5/440/7,088) | D06 §2 Change 2 | DOCUMENTED_IN_D06 (consistent with repo 8,149 build) | Live DB; matches 30 Jun REPORTED_BY_ABIRAJ distribution |
| Declines 628 → 574; escalation 21 → 22 PHs (accurate redistribution) | D06 §2 Change 3/5, §3 Finding A/C | DOCUMENTED_IN_D06 | Live re-derivation; no saved query output |
| 46-row false-NEW artifact caught and corrected (returning-aware 8-week lookback) | D06 §2 Change 4, §3 Finding B, §6 | DOCUMENTED_IN_D06 | Logic now in engine v2 (VERIFIED_FROM_FILE for the rule) |
| Orphan ASIN defined; ownership absent across 4 systems; 492 converting orphans | D06 §2 Change 7-11, §3 Finding D + imported `2026-07-01_unowned_asins_for_assignment_2026-07.csv` | VERIFIED_FROM_FILE (492 rows in the imported CSV) | Ownership checks themselves ran live; not re-queried |
| `analytics.v_orphan_asins` permanent monitor created + live dashboard flag added | D06 §2 Change 9-10 | DOCUMENTED_IN_D06 | Live DB object + live dashboard edit; not queried here |
| Engine v2 self-contained on weekly `traffic_data`, returning-aware, orphan-excluding | Imported `2026-07-01_ph_segment_engine_v2.sql` | VERIFIED_FROM_FILE | Validated in scratch tables only; NOT run against live 2026-07 (by design) |
| Monthly routine updated to v2 engine + live orphan wiring; HTML shell BLOCK 1 still old UI | Imported `2026-07-01_ph_asin_monthly_routine.txt` | VERIFIED_FROM_FILE (file present) | BLOCK 1 old-UI gap confirmed in file (see Gap B) |
| Protocol v1.0 clarifications (lateral-SAME, zero-click→LOW, conv>clicks→HIGH, HLL→HLH, LHL→HHL) | Imported `2026-07-01_ph_asin_protocol_v1_clarifications.md` | VERIFIED_FROM_FILE | Sign-off line present for Bietrick |
| Full pre-drop verification: 8,146/8,149 rows reconcile exactly (3 differ ±1 conv) | D06 §2 Change 16, §3 Finding G | DOCUMENTED_IN_D06 | Live reconciliation; no saved output; backups deliberately KEPT |
| UI redesigned to dropdown/one-view table, classification logic unchanged, pushed live twice | D06 §2 Change 17-19, §3 Finding H/I + imported `2026-07-01_ph_asin_dashboard_id5_live_2026-07.html` (884,658 B) + `..._ph_view_template.html` | VERIFIED_FROM_FILE (saved dashboard HTML proves the dropdown/status-column UI) | Saved copy = 884,658 B vs D06-cited ~879,907 B (minor); live DB row not queried, so byte-identity to id 5 is LIVE_STATE_NOT_RECHECKED |
| Live output row `tech_team_outputs.ph_task` id 5 is the current dashboard | D06 §2 Change 19 metadata | LIVE_STATE_NOT_RECHECKED | DB not queried during this import; the imported HTML is the confirmed latest v2 build (Abiraj) |

## Missing Artifacts

**NONE — resolved 2026-07-02.** The three artifacts initially absent were supplied by Abiraj from
`C:\Users\digit\Downloads\` and imported with matching checksums:

1. `unowned_asins_for_assignment_2026-07.csv` (492 rows) → `evidence/final_outputs/…/2026-07-01_unowned_asins_for_assignment_2026-07.csv`.
2. `preview_v2.html` (latest/live id-5 v2 dashboard) → `…/2026-07-01_ph_asin_dashboard_id5_live_2026-07.html`.
3. `PH_ASIN_Dashboard_PH_view_TEMPLATE.html` → `…/2026-07-01_ph_asin_dashboard_ph_view_template.html`.

Original discovery (1 Jul) searched the entire `DigitWeb_Works_Abiraj` tree, `Desktop/Postgress_backup/`
(incl. `files.zip`), and a depth-4 `Desktop` sweep. No replacements were ever invented.

## Duplicate Check

- D06 daily file imported once (no prior copy in the project). GREEN.
- Engine v2 imported once; distinct from the existing v1 (`2026-06-25_ph_segment_engine.sql`) by content and window logic. GREEN.
- Monthly routine imported once; supersedes nothing already in the repo (the 2026-06-25 file is the *historical run prompt*, a different artifact). GREEN.
- Protocol clarifications imported once. GREEN.
- No missing artifact was fabricated. GREEN.

## Known Limits

- All live-DB and live-dashboard outcomes are DOCUMENTED_IN_D06, not independently re-verified (DB must not be queried here).
- The 8,149 build remains without an imported HTML artifact — the source-of-truth note carried since 30 Jun still stands (see PROJECT_HOME.md), though the numbers are now further corroborated by D06's full reconciliation.

## Result

**PASS (updated 2026-07-02)** — the D06 daily knowledge file and **all 6 named supporting
artifacts** are now imported with matching checksums (4 on 1 Jul, 3 on 2 Jul). No artifact is
missing. REQ-05 mapping is confirmed and unambiguous. Live-DB and live-dashboard *state* claims
remain honestly labelled LIVE_STATE_NOT_RECHECKED (the DB was not queried), but every named
work-product now exists as a checksummed file in the repo.

_(Superseded status: this manifest was AMBER at first creation on 1 Jul, when 3 artifacts were absent.)_
