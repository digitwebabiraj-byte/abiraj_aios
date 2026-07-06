# REQ-05-D09 Source Manifest

## Project ID

PRJ-2026-001_ph-segmentation

## Requirement ID

REQ-05

## Deliverable ID

REQ-05-D09

## Date

2026-07-06

## Recording Posture

The 6 July 2026 work (Phase-09) was executed by **Abiraj in a live Claude Chat session** against the
live PostgreSQL DB. It was **the project's first destructive action** — a scoped `DROP TABLE` on 9
disposable dashboard backups, **archive-first and fingerprint-guarded**. This workbench record documents
and imports the knowledge file **read-only**; the executor did not query or modify the live DB. Evidence
rule: **VERIFIED_FROM_FILE** = saved checksummed file here; **DOCUMENTED_IN_D09** = stated in the D09
knowledge file (live session, not re-derived here); **LOCAL_NOT_IMPORTED** = exists on Abiraj's PC only.

## What D09 delivered (from the knowledge file)

- Archived the **9 `tech_team_outputs.ph_task_id5_backup_*`** dashboard backups to local byte-verified
  files (+ manifest), then **dropped them in a single transaction** (≈1.8 MB reclaimed).
- **Pre-check:** live `ph_task` id 5 present · 9 targets · 3 report backups. **Post-check:** 0 id-5 backups
  remain · **live id-5 `md5(html_content)` = `1f657a1b` unchanged** · 3 report backups intact.
- **Kept:** live `ph_task` (all rows) + the 3 `analytics.ph_segment_report_backup_{20260630, 20260702_movrule, opta}`
  (rollback net) + the 492 orphan assignments — held for Bietrick sign-off.

## Sources

| Source File | Original Path | Canonical Destination | Size | SHA-256 | Classification | Status |
| ----------- | ------------- | --------------------- | ---: | ------- | -------------- | ------ |
| 2026-07-06__abiraj__ph-asin__REQ-05-D09.md | DigitWeb_Works_Abiraj\06_07_2026\ | handover/REQ-05_ph-asin-segmentation/2026-07-06__abiraj__ph-asin__REQ-05-D09.md | 22751 | 96591735b98756505c36b9ba8fc2be9fc3ea773dccbbf50faf3b7056ea499712 | DAILY_KNOWLEDGE | IMPORTED (checksum recorded) |
| Archive folder + zip of the 9 dropped tables | Abiraj's PC (local) | — | — | — | ARCHIVE_BACKUP | LOCAL_NOT_IMPORTED (byte-verified locally; sizes in the D09 §2 manifest) |
| Archive manifest (table → file → rows → md5) | Abiraj's PC (local) | — | — | — | ARCHIVE_MANIFEST | LOCAL_NOT_IMPORTED (per-table sizes recorded in D09 §2; per-file md5s in the local manifest) |
| Executed drop script (single transaction) | live session | — | — | — | LIVE_DDL | DOCUMENTED_IN_D09 (not exported) |
| 2026-07-06_abiraj_REQ-ph-asin_REQ-05-D09.md (morning requirement) | DigitWeb_Works_Abiraj\06_07_2026\ | — | — | — | REQUIREMENT | NOT IMPORTED (matches D06–D08 precedent — knowledge file only) |

## Claims Evidence Classification

| Claim | Evidence Status | Limitation |
| ----- | --------------- | ---------- |
| 9 `ph_task_id5_backup_*` archived (byte-verified) + dropped in one transaction | DOCUMENTED_IN_D09 | Archives are local files (LOCAL_NOT_IMPORTED); per-table sizes in D09 §2 |
| Pre-check 9 targets / live id-5 / 3 report backups | DOCUMENTED_IN_D09 | Live read-only; not re-run here |
| Post-check 0 remain · live id-5 md5 `1f657a1b` unchanged · 3 report backups intact | DOCUMENTED_IN_D09 | DB not queried here; `1f657a1b` matches the imported catfilter/current-live dashboard |
| 3 report backups + 492 orphan assignments kept (held for Bietrick) | DOCUMENTED_IN_D09 | Live DB state; not queried |
| First DROP in the project; scope limited to the 9 named backups | DOCUMENTED_IN_D09 | — |

## Missing / not-imported artifacts

- The **9 archive files + local manifest + drop script** are on Abiraj's PC (LOCAL_NOT_IMPORTED) — not
  provided to the workbench. Their existence + per-table sizes are recorded in the D09 knowledge file (§2).
  The drop itself is DOCUMENTED_IN_D09. No fabricated hashes.

## Duplicate Check

- D09 knowledge file imported once. GREEN.
- No overlap with earlier increments (D09 is the housekeeping/DROP day; no dashboard/report/engine change). GREEN.
- The `(old)` D08 requirement variant and the morning requirement are not imported. GREEN.

## Result

**GREEN / PASS** — the D09 knowledge file is imported and checksummed. D09 is a live-DB housekeeping action
(first DROP), archive-first + fingerprint-guarded, honestly documented; the local archives are recorded as
LOCAL_NOT_IMPORTED (not fabricated). No new missing artifact needed for the record. No workbench DB/commit action.
