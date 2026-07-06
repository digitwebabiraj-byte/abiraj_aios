# REQ-05-D09 AIOS Import Validation — 2026-07-06

## Project / Requirement / Deliverable

PRJ-2026-001_ph-segmentation · REQ-05 · REQ-05-D09

## Validation Table

| # | Check | Evidence | Result | Gap |
|---|---|---|---|---|
| 1 | D09 knowledge file preserved unchanged | sha `96591735…` recorded | PASS | — |
| 2 | Checksum recorded | manifest + update-evidence | PASS | — |
| 3 | Requirement ID remains REQ-05 | no change | PASS | — |
| 4 | Deliverable ID = REQ-05-D09 | used throughout | PASS | — |
| 5 | No REQ-06 / new task row | register row extended in place | PASS | — |
| 6 | Deliverables inventoried | knowledge file (imported) + local archives (LOCAL_NOT_IMPORTED) + drop script (documented) | PASS | — |
| 7 | Live DROP honestly documented, not re-run | DOCUMENTED_IN_D09; workbench did no DB action | PASS | — |
| 8 | Kept vs dropped sets clearly recorded | 9 dropped `ph_task_id5_backup_*` (≈1.8 MB) vs 3 kept `ph_segment_report_backup_*` | PASS | — |
| 9 | Fingerprint guard recorded | live id-5 md5 `1f657a1b` unchanged pre/post; 3 report backups intact | PASS | — |
| 10 | D08 correction applied (clarity pass live 3 Jul) | annotated in D08 records; D08 EOD source preserved | PASS | — |
| 11 | TASK_HOME / HANDOVER / PROJECT_HOME updated | D09 section + D08 note added | PASS | — |
| 12 | TASK_REGISTER updated without new row | REQ-05 row extended | PASS | — |
| 13 | Open gaps retained | v_orphan_asins backup, monthly-routine UI swap, Bietrick sign-offs | PASS | — |
| 14 | No workbench DB/automation action | update evidence: NONE | PASS | — |
| 15 | No commit/push in this record run | working tree only | PASS | — |
| 16 | Queryability / unknown-developer | knowledge file + records + D09 §2 manifest suffice | PASS | local archive md5s live on Abiraj's PC |

## Result Rules Applied

- **PASS/GREEN** — the D09 knowledge file is imported and checksummed; the live housekeeping DROP is
  honestly documented (archive-first, fingerprint-guarded); local archives recorded as LOCAL_NOT_IMPORTED
  (not fabricated). The D08 "clarity pass live" correction is applied.
- **AMBER** does not apply — nothing D09-specific is a missing *file the record needs*; the archives are
  local by nature and honestly labelled.
- **RED** does not apply — no checksum change, no second REQ-05/REQ-06, no overwrite, no workbench DB access.

## Validation Decision

**PASS (GREEN)** — faithful, read-only, checksum-verified documentation of the first project DROP; kept
vs dropped sets and the fingerprint guard are recorded; IDs consistent; another developer can continue.

> Delivery still ACTIVE: back up `v_orphan_asins.sql`, swap the monthly routine to the new UI before 3 Aug,
> and clear the three Bietrick sign-offs (NEW definition, edge-case protocol, 492 orphan assignments).

## One Next Step

Export `v_orphan_asins.sql` (the only live object not backed up as a file) and swap the monthly routine's
BLOCK-1 UI before the 3 Aug run.
