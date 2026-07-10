# SKILL FILE — DAILY KNOWLEDGE EXTRACTION
# DIGITWEB LK LTD · Daily Skill Increment System · v3.0

---

## ── METADATA BLOCK ──────────────────────────────────────────────────────────

| Field | Value |
| :---- | :---- |
| **date** | 2026-07-10 |
| **developer** | abiraj |
| **project** | PH ASIN Segmentation — Growth Protection Engine (GPE) |
| **project_code** | ph-asin |
| **phase** | Phase-10 — Corrected 2026-07 rebuild + full leader & per-PH dashboard push |
| **requirement_id** | REQ-05 |
| **deliverable_id** | REQ-05-D10 |
| **status** | **COMPLETE.** DB was updated since the published 2026-07 report, so the report was regenerated **read-only** for the SAME July window (6–27 Jun) with corrected data and **all dashboards were pushed live** to `tech_team_outputs.ph_task`. Result: **9,947 ASINs / 30 PHs** (was 8,149 / 24 — the +1,798 is an ownership/orphan-assignment restructure, NOT a method change). Pushed: **leader id 5** (md5 `1f657a1b` → `35fa7b66`) + **30 per-PH** rows (22 UPDATE + 8 INSERT incl. new hire **thanusha**); **deleted** 2 departed holders (Poovitha #65, thanucha #79) so the dashboard shows **31 rows** not 33; fixed `assigned_user_team='ph_priors'` on the 8 inserts. Every write backup-first + md5-verified in one transaction. **A repeatable toolkit + runbook were saved** so next cycle is easy. |
| **evidence_location** | **Read-only recompute** via Postgres MCP (per-PH replay of the strict-rank engine as SELECTs; utharsika category-split). **Writes** via direct psycopg2 as `temp_user` (creds env-only). Backups under `evidence/final_outputs/REQ-05_ph-asin-segmentation/`: `2026-07-10_ph_task_id5_PRE-UPDATE_backup.html`, `2026-07-10_per_ph_PRE-UPDATE_backups/` (22 files), `2026-07-10_deleted_rows_backup/` (2 full rows). Toolkit + runbook: `capability/2026-07-10_monthly_rebuild_toolkit/` + `capability/2026-07-10_monthly-rebuild-and-push-runbook.md`. Built HTML: `evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-07-10_ph_asin_dashboard_all_ph_leader_corrected_2026-07.html`. |
| **blos_keys_used** | NONE. |
| **hardcoded_thresholds** | **No classification/engine change.** Method-A CVR, benchmark top-30/10/needs-manual(<10), Option-B undefined-combo map (HLL→HLH, LHL→HHL), FBM/UK/Amazon (which_channel=1) scope, strict segment-rank movement (HHH=1…LLL=6), returning-aware NEW, 4-week windows — all unchanged. Only the **input data** and the **roster** changed. |
| **three_am_standard** | PASS |
| **llm_queryable** | YES |
| **company_knowledge_candidate** | YES |
| **domain** | SEGMENTATION \| DASHBOARD \| DATABASE-WRITE \| AMAZON-LISTINGS \| ROSTER \| REPEATABLE-PROCESS |
| **user** | Bietrick |
| **benefit_status** | **DELIVERED** — the whole team now sees corrected July numbers: leader + 30 individual holder dashboards, all validated cell-by-cell against the live DB, all reversible (backups), and the process is captured as a reusable toolkit + runbook. |

## File path:
# 2026-07-10__abiraj__ph-asin__REQ-05-D10.md
# DigitWeb_Works_Abiraj/10_07_2026/

---

## SECTION 1 · SYSTEM STATE
- **Start.** The live 2026-07 report/dashboards were the 3-Jul clarity build (leader id-5 md5 `1f657a1b`, 8,149 ASINs / 24 PHs). Since then the DB changed: for the SAME window, 467 of the old ASINs no longer appear and 51 had corrected metrics, **and ownership was restructured** (orphan assignments + roster changes).
- **Trigger (Abiraj).** "Regenerate with corrected counts, then upload all PH dashboards."
- **Approach.** Recompute **read-only** (do not touch `analytics.ph_segment_report`), rebuild the HTML from the exact live template, **validate every count against the DB**, then push with backup-first + md5-verify.

> **In plain terms:** the database was fixed after the July dashboards went out, so the dashboards were stale. I recalculated the July report from the corrected data (without changing any rules), rebuilt the same dashboards, checked every number against the live database, and then updated the team dashboard and each person's dashboard — keeping a backup of everything first.

## SECTION 2 · WHAT CHANGED TODAY
- **Corrected recompute (read-only).** Same July window (6–27 Jun), current data → **9,947 ASINs / 30 PHs**. Segments **42 / 580 / 173 / 10 / 626 / 8,516** (HHH…LLL). Movement 831 improved / 773 declined / 189 new / 8,154 same.
- **Roster grew 24 → 30.** +7 new holders (Akalika, Akanila, Dilakshiga, Jathisha, Ramsika, Sarbavi, Vaishnavi) + new hire **thanusha**; **Poovitha left**, **thanucha left**. Names taken exactly from the `user`+`ph_categories`+`ph_cate_products` join (`PH_assigned_user_Standard.docx`).
- **Leader push.** `ph_task` id 5 `html_content`: `1f657a1b` (891,320) → `35fa7b66` (971,526), verified.
- **Per-PH push.** 30 rows: **22 UPDATE** (existing) + **8 INSERT** (ids 145–152), one transaction, each md5-verified; all `assigned_user_team='ph_priors'`.
- **Cleanup.** Deleted **Poovitha #65** and **thanucha #79** (departed) after full-row backup → project shows **31 rows**.
- **Toolkit + runbook saved** for repeatability (see evidence_location).

## SECTION 3 · POSTGRESQL / MCP / DATABASE FINDING
- **Recompute is faithful read-only.** The strict-rank engine replays exactly as SELECTs; validated by `03_validate_counts.sql` matching the built HTML cell-by-cell (total + 6 segments + 30 per-PH).
- **`analytics.ph_segment_report` still STALE** (old 8,149 build). The dashboards are self-contained HTML snapshots and are correct; the source table is unchanged (its rebuild is a DROP/CREATE reserved for the authorised DB session). Anything querying that table directly is still stale — carried gap.
- **Write path.** `temp_user` (psycopg2), not MCP. All writes backup-first, md5-verified in-transaction, atomic.
- **Schema surprise.** `ph_task` has `assigned_user_team` (NOT in the shared sample DDL); ph-asin rows must be `'ph_priors'`. The 8 inserts initially defaulted NULL — fixed.

## SECTION 4 · GAP FOUND
- **Gap A — source table not rebuilt (MEDIUM, OPEN).** `analytics.ph_segment_report` = old build; rebuild in the authorised DB session so table == dashboards. Owner: abiraj.
- **Gap B — roster sign-off (Bietrick).** 30-PH roster (7 new, 2 left) is live but not formally ratified. Owner: Bietrick.
- **Gap C — MCP timeout ceiling.** Full/2-window recompute times out > ~1300 ASINs; mitigated by per-PH + category-split (documented in runbook). Owner: abiraj (process).
- **Gap D — monthly in-DB routine still old UI** (carried from D06–D09). Owner: abiraj.

> `GAP: no blocking gap for today — all 31 rows pushed, validated, backed up. Carried items are the source-table rebuild and sign-offs.`

## SECTION 5 · VALIDATION RULE ADDED OR CHANGED
- **Regenerate = same rules, corrected data, same period** (unless explicitly rolling forward). The window `rn` offsets are the only thing that changes correction (rn 2..5) vs roll-forward (rn 1..4).
- **Push discipline (reaffirmed + extended to per-PH & inserts):** backup-first → md5-verify in-transaction → atomic. INSERTs must set `assigned_user_team='ph_priors'`. Names exact from the roster join. Departed holders are deleted only after a full-row backup.
- **Cross-check the built artifact against the live DB** before any push (cell-by-cell counts).

> `VALIDATION RULE: a dashboard push is valid only if the built HTML's counts match a fresh live-DB recompute (total + segments + per-PH) AND the write is backup-first + md5-verified + atomic; per-PH INSERTs carry assigned_user_team='ph_priors'.`

## SECTION 6 · FAILURE MODE OR EDGE CASE
- **Stale-source trap.** Updating the dashboard HTML does NOT update `analytics.ph_segment_report`; consumers of that table stay stale until the engine is re-run. Flagged, not hidden.
- **Roster drift.** Adding/removing holders means UPDATE + INSERT + DELETE, not just UPDATE; the id↔name map must be refreshed from `ph_task` each cycle or inserts/updates hit the wrong rows.
- **Name collisions.** thanucha (left) vs thanusha (new hire) — different people; merging them would corrupt ownership.
- **Query timeout.** Big PH → category-split (safe because benchmark is per PH+category and no ASIN spans categories); recompute the per-PH rank after merging.

## SECTION 7 · DECISIONS MADE TODAY
- **D-70 — Correct the 2026-07 report (same 6–27 Jun window), not roll forward.** "Corrected counts" = fix the published period.
- **D-71 — Recompute read-only; do NOT rebuild `analytics.ph_segment_report`** (that write stays in the authorised DB session).
- **D-72 — Push leader (id 5) + 30 per-PH; INSERT 8 new incl. thanusha; assigned_user_team='ph_priors'.**
- **D-73 — thanucha ≠ thanusha** (leaver vs new hire) — do not merge.
- **D-74 — Delete departed holders Poovitha #65 + thanucha #79** (backup-first) → 31 rows.
- **D-75 — Save a reusable toolkit + runbook** (this is a monthly repeatable task).
- (D-0…D-65 from D01–D09 remain in force.)

## SECTION 8 · COMPANY KNOWLEDGE EXTRACT
### Business Rule
When the warehouse is corrected after a report is published, **regenerate the same period with the
corrected data using the identical rules** — do not change the method and do not silently roll the
window forward. The roster (who the holders are) is authoritative from `user`+`ph_categories`+`ph_cate_products`;
names are used exactly as stored.

### Operational Assumption
Dashboards in `ph_task` are **baked HTML snapshots**: a data change requires a rebuilt-and-verified push,
and it does **not** update the underlying `analytics.ph_segment_report` table. Keep the two in sync
deliberately (engine re-run) — never assume a dashboard push refreshed the source table.

### Reusable Logic / Formula
- **Read-only engine replay:** the strict-rank engine as pure SELECTs → validate → build → push (no source-table write needed to refresh dashboards).
- **Per-PH + category-split** to beat the MCP timeout ceiling; **merge + re-rank** in Python.
- **Roster diff → UPDATE/INSERT/DELETE:** match current holders to existing rows; insert new; delete leavers (backup-first).
- **Backup-first + md5-verify-in-transaction + atomic** for every live write.

### Canonical Vocabulary
| Term | Meaning |
| :---- | :---- |
| correction window | `rn 2..5` — same weeks as the published report, with corrected data (period unchanged) |
| roll-forward window | `rn 1..4` — the next cycle's window (period advances) |
| assigned_user standard | holder names from the `user`+`ph_categories`+`ph_cate_products` join, used exactly |
| assigned_user_team | `ph_task` column (`'ph_priors'` for this project) — required on inserts, absent from the sample DDL |
| baked snapshot | a `ph_task.html_content` dashboard — self-contained; a data change needs a rebuilt push |

### Cross-Project Applicability
- **Read-only replay + cell-by-cell validation** — any "correct a published report from fixed data" task.
- **Roster diff (UPDATE/INSERT/DELETE) with backups** — any per-person artifact set that tracks a changing team.
- **Chunk-to-beat-timeout (per-entity, then split)** — any heavy per-entity recompute over a capped SQL endpoint.

---

## SECTION 9 · LLM STANDARD CHECK
| Check | YES / NO |
| :---- | :---- |
| Could an unknown developer continue from this file (+ runbook/toolkit) without reading source code? | ✅ YES |
| Is every business threshold visible (not buried in code)? | ✅ YES — counts, roster, window, ph_priors all in S1/S2/S5 + runbook |
| Is the GAP FOUND section completed or marked NONE? | ✅ YES — 4 carried gaps |
| Is the COMPANY KNOWLEDGE EXTRACT substantive? | ✅ YES |
| Are evidence locations referenced? | ✅ YES — backups, built HTML, toolkit, runbook |
| Is metadata complete (incl. blos_keys_used + hardcoded_thresholds)? | ✅ YES |
| Are section names per standard template (1–9)? | ✅ YES |
| Is this extracting knowledge — not just logging activity? | ✅ YES |

### Three-AM Standard Self-Assessment
- **WHAT** — corrected the 2026-07 report read-only (9,947/30), rebuilt leader + 30 per-PH dashboards, validated every count vs live DB, pushed all 31 rows (22 UPDATE + 8 INSERT + leader; deleted 2 leavers), fixed `assigned_user_team`, saved a reusable toolkit + runbook.
- **NOT DONE (carried)** — rebuild `analytics.ph_segment_report` (source table still 8,149); Bietrick roster sign-off; align the in-DB monthly routine to the new UI.
- **WHY** — the DB was corrected after publish, so the dashboards were stale; regenerate same-period with corrected data, verify against the DB, push reversibly.
- **WHO / WHERE / NEXT** — owner abiraj (sign-off → Bietrick); live: `ph_task` 31 rows (leader `35fa7b66` + 30 per-PH, `ph_priors`); next: re-run the engine to refresh the source table, get roster sign-off.

---

## ── SUBMISSION CHECKLIST ─────────────────────────────────────────────────────
- [x] File named `2026-07-10__abiraj__ph-asin__REQ-05-D10.md`
- [x] Metadata complete (incl. blos_keys_used NONE, hardcoded_thresholds, user, benefit_status)
- [x] Live write evidence (backup-first + md5-verify + atomic; leader `35fa7b66`; 31 rows)
- [x] Sections 1–9 present
- [x] No credentials/passwords in this file or the toolkit (env-var only; source in Downloads)
- [x] Reusable toolkit + runbook saved and referenced
- [x] ✅ **DONE:** corrected 9,947/30 · leader + 30 per-PH pushed · 2 leavers deleted · assigned_user_team fixed · all backed up + verified
- [x] **NEXT (carried):** rebuild `analytics.ph_segment_report` (engine re-run) · Bietrick roster sign-off · monthly-routine UI
