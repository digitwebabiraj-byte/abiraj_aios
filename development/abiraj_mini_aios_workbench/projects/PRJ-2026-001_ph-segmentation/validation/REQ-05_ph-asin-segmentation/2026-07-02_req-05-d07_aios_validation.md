# REQ-05-D07 AIOS Import Validation — 2026-07-02

## Project / Requirement / Deliverable

PRJ-2026-001_ph-segmentation · REQ-05 · REQ-05-D07

## Validation Table

| # | Check | Evidence | Result | Gap |
|---|---|---|---|---|
| 1 | D07 knowledge file preserved unchanged | sha `65c1a010…` recorded | PASS | — |
| 2 | Checksums recorded for all imports | manifest + `.sha256` index | PASS | — |
| 3 | Requirement ID remains REQ-05 | no change | PASS | — |
| 4 | Deliverable ID = REQ-05-D07 | used throughout | PASS | — |
| 5 | No REQ-06 / new task row | register row updated in place | PASS | — |
| 6 | Artifacts inventoried | manifest tables all items (present + missing) | PASS | — |
| 7 | Available artifacts copied once | 3 previews + 24 views + knowledge + transcript | PASS | — |
| 8 | Missing artifacts identified | live_v4_movrule + engine v3 flagged MISSING_ARTIFACT | PASS | drives AMBER |
| 9 | 24 per-PH views verified | folder + 24-entry checksum index; names match authoritative list | PASS | — |
| 10 | D06 mislabel corrected | preview_v2 re-homed; D06 records annotated | PASS | — |
| 11 | TASK_HOME / HANDOVER / PROJECT_HOME updated | D07 sections added | PASS | — |
| 12 | TASK_REGISTER updated without new row | REQ-05 row extended | PASS | — |
| 13 | Open gaps retained | routine BLOCK-1 UI swap, automation, engine-v3 first run, 3 Bietrick sign-offs | PASS | — |
| 14 | No DB action | update evidence: NONE | PASS | — |
| 15 | No automation action | NONE | PASS | — |
| 16 | No backup dropped | NONE | PASS | — |
| 17 | No live HTML executed | previews stored only | PASS | — |
| 18 | No commit/push in this run | working tree only | PASS | — |
| 19 | Queryability | see below | PASS | — |
| 20 | Unknown-developer test | knowledge file + previews + views + records suffice | PASS | exact live build not in repo |

## Queryability

From the repo alone a clean LLM can explain: the restyle, card redesign, and strict-rank movement
rule; why strict-rank changed 65 lateral moves; that engine v3 was sandbox-only; where the previews
and 24 per-PH views are; which artifacts (final live HTML, engine v3) are missing and why; and the
D06 mislabel correction. PASS.

## Result Rules Applied

- **PASS** would require all named artifacts present. Two (final live HTML, engine v3) are absent.
- **AMBER** applies: knowledge file + previews + 24 views + transcript imported and checksummed;
  final live build and engine v3 are MISSING_ARTIFACT.
- **RED** does not apply: no checksum change, no second REQ-05/REQ-06, no overwrite (preview_v2 re-homed,
  content identical), no DB access.

## Validation Decision

**AMBER** — faithful, read-only, checksum-verified import; two artifacts absent and honestly recorded;
D06 mislabel corrected. IDs consistent; another developer can continue.

> The AIOS import is AMBER only for the two missing files. The **REQ-05 delivery** remains ACTIVE:
> routine BLOCK-1 UI swap before 3 Aug, engine-v3 first live run, and three Bietrick sign-offs
> (NEW definition, edge-case protocol, 492 orphan assignments) are open — delivery items, not import defects.

## One Next Step

Export + import `live_v4_movrule.html` (exact final live dashboard) and `ph_segment_engine.sql` v3 so
those claims move from DOCUMENTED_IN_D07 to VERIFIED_FROM_FILE; then swap the monthly routine's HTML
BLOCK 1 to the new UI before the 3 Aug run.
