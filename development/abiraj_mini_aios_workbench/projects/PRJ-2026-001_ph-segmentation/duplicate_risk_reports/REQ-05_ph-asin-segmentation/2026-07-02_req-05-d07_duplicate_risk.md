# REQ-05-D07 Duplicate-Risk Report — 2026-07-02

## Project / Requirement / Deliverable

PRJ-2026-001_ph-segmentation · REQ-05 · REQ-05-D07

| # | Check | Finding | Result |
|---|---|---|---|
| 1 | D07 knowledge file exists once | One copy in handover/REQ-05_… | GREEN |
| 2 | Dashboard previews not conflated as "the live build" | v2 restyle (884,658 B), v3 cards (888,305 B), catfilter (891,397 B) — distinct sizes/checksums; none labeled the canonical live build (that is MISSING_ARTIFACT) | GREEN |
| 3 | preview_v2 exists once | Re-homed from D06 via `git mv` (not copied) → one canonical copy at the D07 name | GREEN |
| 4 | 24 per-PH views exist once each | One folder `2026-07-02_ph_per_holder_views/`, 24 files + `.sha256` index; names match the authoritative PH spelling list | GREEN |
| 5 | Old vs new engine not both "current" | v1 (window-table, historical), v2 (returning-aware, D06), v3 (strict-rank, D07) — v3 is going-forward but is **MISSING_ARTIFACT**, so no engine file is mislabeled | GREEN |
| 6 | Chat transcript exists once | One copy in logs_or_screenshots/REQ-05_… | GREEN |
| 7 | No second REQ-05 / D07 row | Existing REQ-05 row updated in place; no REQ-06 / dated ID | GREEN |
| 8 | D06 mislabel resolved, no parallel truth | The mislabeled "1 Jul live" file re-homed to its true D07 identity; D06 records annotated; no duplicate left behind | GREEN |
| 9 | TASK_HOME / PROJECT_HOME scope kept | Task vs project context not cross-duplicated | GREEN |

## Note on movement-rule truth

The **strict-rank** movement rule (D07) supersedes the equal-weight h-count for future cycles. The
imported `preview_v3` reflects the redesigned cards; the exact strict-rank baked data lives in the
**MISSING** `live_v4_movrule.html`. This is flagged so no one treats preview_v3 as byte-identical to live.

## Decision

GREEN — no duplicate or parallel-truth risk. Two artifacts (final live HTML, engine v3) are absent and
recorded as MISSING_ARTIFACT rather than substituted.
