# REQ-05-D06 AIOS Import Validation — 2026-07-01

## Project / Requirement / Deliverable

PRJ-2026-001_ph-segmentation · REQ-05 · REQ-05-D06

## Validation Table

| # | Check | Evidence | Result | Gap |
|---|---|---|---|---|
| 1 | D06 source file preserved unchanged | Post-copy SHA-256 `5ebdcb0c…` = source | PASS | — |
| 2 | D06 checksum recorded | Source manifest + update evidence | PASS | — |
| 3 | Requirement ID remains REQ-05 | No change made | PASS | — |
| 4 | Deliverable ID remains REQ-05-D06 | Records use REQ-05-D06 throughout | PASS | — |
| 5 | No REQ-06 created | Task register unchanged in ID; no new row | PASS | — |
| 6 | Supporting artifacts inventoried | knowledge file + 6 supporting + Option-A bonus, all found (4 on 1 Jul, CSV+template 2 Jul, navy build 6 Jul) in manifest | PASS | — |
| 7 | Available artifacts copied once | all copies checksum-verified, no overwrite | PASS | — |
| 8 | Missing artifacts resolved | 1 Jul navy live dashboard imported 6 Jul from `Downloads\files (2)\` (md5 `9b65e429`); nothing missing | PASS | none remaining |
| 9 | TASK_HOME updated | Daily-increment section added | PASS | — |
| 10 | HANDOVER updated | 1 July section + Do-Not-Repeat added | PASS | — |
| 11 | PROJECT_HOME updated | Latest date/deliverable/state fields updated | PASS | — |
| 12 | TASK_REGISTER updated without another row | Existing REQ-05 row updated in place | PASS | — |
| 13 | Open gaps retained | Routine BLOCK-1 UI, automation, backups, engine-v2-first-run all recorded | PASS | — |
| 14 | No database action performed | Update evidence: DB = NONE | PASS | — |
| 15 | No automation action performed | Update evidence: automation = NONE | PASS | — |
| 16 | No backup table dropped | Update evidence: backups dropped = NONE | PASS | — |
| 17 | No live HTML executed | HTML stored only, not run; the navy live HTML is now imported (md5 `9b65e429`) | PASS | — |
| 18 | No commit or push performed | Git: NOT CREATED / NOT PERFORMED | PASS | — |
| 19 | Queryability test passes | See queryability section below | PASS | — |
| 20 | Unknown-developer test passes | D06 file + all 7 artifacts + records let a new dev continue | PASS | — |

## Queryability (answerable from repo files only)

A clean LLM reading the imported D06 file + records can explain: what changed on 1 July; why
the 4-complete-weeks window was needed; what Option A means; what an Orphan ASIN is; where
engine v2 is; why v2 was not run against the live July report; which UI is documented as live;
which reference methodology (weighted CVR) was rejected; what the routine still needs (BLOCK-1
swap); what automation remains pending; why backups remain; who reviews the work; and what
happens next. As of the 2 Jul second pass, the orphan CSV and both dashboard HTML files are also imported, so
those claims are now VERIFIED_FROM_FILE. PASS.

## Result Rules Applied

- **PASS** requires all named artifacts present and recorded — **now met** (knowledge file + all 6
  supporting artifacts imported and checksummed; the last one, the 1 Jul navy live dashboard, was
  imported 6 Jul; live-state claims honestly labelled).
- **AMBER** no longer applies now that the navy build is imported.
- **RED** does not apply: no checksum change, no second REQ-05, no REQ-06, no overwrite, no
  DB access required.

## Validation Decision

**PASS (updated 2026-07-06)** — faithful, read-only, checksum-verified import of the D06 knowledge
file and all 6 supporting artifacts; nothing missing; IDs consistent; another developer can continue.
_History: AMBER (1 Jul) → wrongly PASS (2 Jul) → AMBER (3 Jul, navy flagged missing) → PASS (6 Jul,
navy build found in `Downloads\files (2)\` and imported, md5 `9b65e429`)._

> Note: the **AIOS import/documentation** is PASS. The **REQ-05 delivery** remains ACTIVE — the
> engine-v2 first live run (3 Aug) and the routine BLOCK-1 UI swap are still open (see TASK_HOME);
> those are delivery gaps, not import defects.

## One Next Step

Swap the monthly routine's HTML shell (BLOCK 1) to the new dropdown UI before the 3 Aug run so an
automated run cannot regenerate the old layout over the now-live v2 dashboard.
