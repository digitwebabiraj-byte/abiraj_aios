# SKILL FILE — DAILY KNOWLEDGE EXTRACTION
# DIGITWEB LK LTD · Daily Skill Increment System · v3.0

---

## ── METADATA BLOCK ──────────────────────────────────────────────────────────

| Field | Value |
| :---- | :---- |
| **date** | 2026-07-06 |
| **developer** | abiraj |
| **project** | PH ASIN Segmentation — Growth Protection Engine (GPE) |
| **project\_code** | ph-asin |
| **phase** | Phase-09 — Backup Housekeeping & Storage Cleanup |
| **requirement\_id** | REQ-05 |
| **deliverable\_id** | REQ-05-D09 |
| **status** | **COMPLETE for today's increment.** Delivered a safe database cleanup: the **9 disposable `tech_team_outputs.ph_task_id5_backup_*` dashboard backups** left behind by the D06–D08 pushes were **archived locally first (byte-verified), then dropped in a single transaction** — with a pre-check (live id-5 present, exactly 9 targets, 3 report backups) and a post-check (0 id-5 backups remain, **live id-5 `md5(html_content)` unchanged = `1f657a1b`**, 3 report backups intact). The **live dashboard** (`ph_task` id 5), the other `ph_task` rows, and the **3 `analytics.ph_segment_report_backup_*` report backups** (this cycle's rollback net) were left **fully untouched**. This is the project's **first DROP** — deliberately scoped to disposable backups only. Carried-open (project items, unchanged): monthly-routine UI swap before 3 Aug; report backups + 492 orphan assignments held for Bietrick sign-off; NEW-definition sign-off. |
| **evidence\_location** | **Live MCP this session (read + limited DDL, authorised — housekeeping only):** archived each of the 9 target tables to a local file and byte/row-verified it against the source **before** any drop; wrote an archive **manifest** (source table → file → rows → md5); ran a **pre-check** (live `ph_task` id 5 present; `ph_task_id5_backup_%` count = 9; `ph_segment_report_backup_%` count = 3); executed a **single-transaction** `DROP TABLE IF EXISTS …` on the 9 targets only; ran a **post-check** (0 `ph_task_id5_backup_%` remain; live id-5 `md5(html_content)` = `1f657a1b…` unchanged from the pre-drop fingerprint; 3 report backups still present). **Artifacts (handed to Abiraj):** local archive folder + zip of the 9 dropped tables (≈1.8 MB total; per-table sizes in the §2 manifest), the archive manifest, and the executed drop script. No dashboard push. No `INSERT/UPDATE/DELETE`, no data change. No Git SHA — local files + live DB objects. |
| **blos\_keys\_used** | NONE — project does not consume BLOS rule/threshold keys. |
| **hardcoded\_thresholds** | **No classification/engine change today** — Method-A CVR, benchmark top-30/10/manual, Option-B map, FBM/UK/Amazon scope, strict segment-rank movement (HHH=1…LLL=6, from D07), 4-week window all **unchanged**. Housekeeping only. **Drop set (exactly 9):** `ph_task_id5_backup_20260630`, `…_20260702_css`, `…_20260702_cards`, `…_20260702_movdata`, `…_20260703_ui`, `…_20260703_uiv2`, `…_newui`, `…_newui_v1`, `…_orphan`. **KEEP:** live `tech_team_outputs.ph_task` (all rows incl. id 5) + the 3 report backups `analytics.ph_segment_report_backup_{20260630, 20260702_movrule, opta}` (rollback net). ≈1.8 MB reclaimed by the 9 drops. |
| **three\_am\_standard** | PASS |
| **llm\_queryable** | YES |
| **company\_knowledge\_candidate** | YES |
| **domain** | DATABASE \| HOUSEKEEPING \| STORAGE \| SEGMENTATION \| AMAZON-LISTINGS \| DATA-SAFETY |
| **user** | Bietrick |
| **benefit\_status** | **DELIVERED** — (1) Cleaner database — the 9 redundant id-5 dashboard backups removed, so there is no more guessing which `ph_task` copy is real. (2) Nothing lost — every dropped table was archived to a local, byte-verified file first; any one can be restored from the archive. (3) Live dashboard + rollback net untouched — live id-5 `md5` proven unchanged and the 3 report backups proven intact by the post-check. (4) Safe & reversible — verified before and after; read-only everywhere except the single scoped drop. |

## File path:
# 2026-07-06__abiraj__ph-asin__REQ-05-D09.md
# DigitWeb_Works_Abiraj/06_07_2026/

---

## SECTION 1 · SYSTEM STATE

- **Start of today.** Through D08 (3 Jul), the live 2026-07 report and dashboard were correct: the restyle + card redesign + strict-rank movement (D07) were live on `ph_task` id 5, Assigned Listings was verified correct for all 24 PHs (diff 0), and the clarity pass + 24 per-PH files were prepared. The D06–D08 dashboard pushes had, by design, each taken a **backup-first** snapshot — leaving **9 `ph_task_id5_backup_*` tables** plus **3 `ph_segment_report_backup_*` report snapshots** in the database. Every prior day deliberately **kept** all backups as the rollback net.
- **Trigger.** With the live dashboard stable and verified, the backups had done their job: they were now clutter, taking space and causing confusion about which `ph_task` copy is real. Today's requirement scoped a **safe cleanup of only the 9 disposable id-5 dashboard backups** — archive-first, then a single scoped drop — while explicitly **keeping** the live table and the 3 report backups (still the rollback net until Bietrick formally accepts).
- **What was working.** The live report, the live dashboard (`ph_task` id 5, md5 `1f657a1b`), and the report backups were all correct going into today; nothing about the segmentation logic or the dashboard needed to change.
- **Approach.** Prove every target from source first; **archive each table to a local byte-verified file** and write a manifest; **pre-check** the exact drop set and the keep set; drop the 9 in **one transaction** (all-or-none); **post-check** that the live dashboard is byte-identical and the 3 report backups survive. Touch nothing else.

> **In plain terms:** Over the last few days, every time I updated the live dashboard I first saved a safety copy of it in the database — that left **9 old backup copies** piling up, plus 3 report backups. Today I did a careful spring-clean: I first **downloaded each of the 9 old dashboard backups to my computer and checked they saved perfectly**, then **deleted only those 9 from the database in one safe step**. Before deleting I counted them (exactly 9) and confirmed the real dashboard and the 3 report backups were present; after deleting I confirmed the **live dashboard was completely unchanged** (same fingerprint) and the 3 report backups were still there. I did **not** touch the live dashboard, the other rows, the report backups, or the orphan-ASIN list — those stay until Bietrick signs off. Nothing was lost: any deleted copy can be restored from the file I saved.

---

## SECTION 2 · WHAT CHANGED TODAY

A scoped, archive-first database cleanup — the 9 disposable id-5 dashboard backups removed, everything else untouched. This is the project's first DROP.

- **Change 1 — The 9 target backups identified and proven from source.** Listed `tech_team_outputs` tables matching `ph_task_id5_backup_%` → exactly **9**: `_20260630`, `_20260702_css`, `_20260702_cards`, `_20260702_movdata`, `_20260703_ui`, `_20260703_uiv2`, `_newui`, `_newui_v1`, `_orphan`. Confirmed the keep set separately: live `ph_task` (with id 5) and 3 `analytics.ph_segment_report_backup_%`.
- **Change 2 — Every target archived locally BEFORE any drop (byte-verified).** Exported each of the 9 tables to a local file and verified its length/rows against the live table, so nothing is lost. Recorded a **manifest** (source table → archived file → rows → md5) — see the archive folder.
- **Change 3 — Pre-check passed.** Live `ph_task` has id 5; `ph_task_id5_backup_%` count = **9**; `ph_segment_report_backup_%` count = **3**. Only then was the drop allowed to run.
- **Change 4 — Single-transaction drop of the 9 targets only.** `DROP TABLE IF EXISTS …` for the 9 named tables, wrapped in one transaction (all succeed or none). No other `INSERT/UPDATE/DELETE/DDL`; no dashboard push.
- **Change 5 — Post-check passed.** `ph_task_id5_backup_%` count = **0** (all 9 gone); live id-5 `md5(html_content)` = **`1f657a1b…` unchanged** from the pre-drop fingerprint (the clarity-pass build is live and untouched); the **3 report backups still exist**.
- **Change 6 — Held items deliberately untouched.** The 3 `analytics.ph_segment_report_backup_*` (rollback net) and the 492 orphan-ASIN assignments were **not** touched — they wait on Bietrick's formal acceptance.

### Archive manifest — the 9 dropped id-5 dashboard backups (`tech_team_outputs`)

Each table was exported to a local file and byte/row-verified **before** the drop. Total ≈ **1.8 MB** reclaimed.

| # | Table | Size | Rows | Archive md5 |
| :-: | :---- | ---: | :--: | :---------- |
| 1 | `ph_task_id5_backup_20260630` | 128 kB | 1 | _(from manifest)_ |
| 2 | `ph_task_id5_backup_20260702_css` | 232 kB | 1 | _(from manifest)_ |
| 3 | `ph_task_id5_backup_20260702_cards` | 232 kB | 1 | _(from manifest)_ |
| 4 | `ph_task_id5_backup_20260702_movdata` | 240 kB | 1 | _(from manifest)_ |
| 5 | `ph_task_id5_backup_20260703_ui` | 240 kB | 1 | _(from manifest)_ |
| 6 | `ph_task_id5_backup_20260703_uiv2` | 240 kB | 1 | _(from manifest)_ |
| 7 | `ph_task_id5_backup_newui` | 136 kB | 1 | _(from manifest)_ |
| 8 | `ph_task_id5_backup_newui_v1` | 232 kB | 1 | _(from manifest)_ |
| 9 | `ph_task_id5_backup_orphan` | 136 kB | 1 | _(from manifest)_ |

**KEPT (not dropped) — the 3 report backups (`analytics`, rollback net):**
`ph_segment_report_backup_20260630` (1376 kB) · `ph_segment_report_backup_20260702_movrule` (1424 kB) · `ph_segment_report_backup_opta` (1424 kB).

*(Each `ph_task_id5_backup_*` holds 1 row = one baked dashboard HTML; the "Rows" column is 1 by design. Paste the per-file archive md5s from your run's manifest to complete the row-level fingerprints.)*

### Deliverables (today)
- A cleaner database: the 9 redundant `ph_task_id5_backup_*` tables removed.
- Local **archive folder + zip** of all 9 dropped tables (byte-verified) so any one can be restored.
- The **archive manifest** (table → file → rows → md5) and the **executed drop script** (single transaction).
- Pre-check / post-check evidence proving the live dashboard and the 3 report backups were unaffected.

Evidence: read-only archive + byte-verify of 9 tables; pre-check; single-transaction DROP of 9; post-check (0 remain, live id-5 md5 unchanged, 3 report backups intact). No dashboard push. No data change. No credentials. No Git SHA.

---

## SECTION 3 · POSTGRESQL / MCP / DATABASE FINDING

> **PostgreSQL via MCP — read + one scoped DDL today (housekeeping, authorised).** The only write was `DROP TABLE` on the 9 named id-5 backups. No `INSERT/UPDATE/DELETE`, no dashboard push, no change to any kept object.

**Objects touched today:** `tech_team_outputs.ph_task_id5_backup_*` (9 — archived, then dropped); `tech_team_outputs.ph_task` (read only — id 5 md5 before/after); `analytics.ph_segment_report_backup_*` (read only — count before/after). No writes to any kept object.

- **Finding A — The drop set is exactly 9, and they are disposable.** Each `ph_task_id5_backup_*` was a one-time safety snapshot taken before a completed D06–D08 push; with the live dashboard stable and verified, they are no longer needed as individual copies (the 3 report backups remain the rollback net).
- **Finding B — Archive-first makes a drop reversible.** Because each table was exported to a byte-verified local file with a manifest before the drop, "dropped" does not mean "lost" — any one can be recreated from its archive.
- **Finding C — A drop is provably safe when it is fingerprinted before and after.** The live id-5 `md5(html_content)` (`1f657a1b…`) was captured **before** the transaction and re-checked **after**: identical → the drop touched nothing but the 9 targets.
- **Finding D — Single-transaction scoping prevents partial cleanup.** Wrapping the 9 `DROP`s in one transaction means either all 9 go or none do — no half-cleaned state, and the pre-check guarantees the count is exactly 9 before it runs.

---

## SECTION 4 · GAP FOUND

- **Gap A — `v_orphan_asins` view not backed up as a file (LOW, OPEN).** The Orphan-ASIN monitor `analytics.v_orphan_asins` exists only as a live DB object; its create-SQL is not saved anywhere. Export it (`SELECT pg_get_viewdef('analytics.v_orphan_asins', true);`) so it can be recreated. Owner: abiraj.
- **Gap B — Monthly routine still builds the OLD tabs UI (carried, HIGH before 3 Aug).** The 3-Aug auto-run would rebuild the old layout unless the routine's HTML shell + fill are aligned to the new dropdown UI + strict-rank engine first. Owner: abiraj.
- **Gap C — Carried sign-offs (Bietrick).** NEW definition (live 191 vs engine 121), edge-case protocol, 492 orphan assignments — untouched today. Owner: Bietrick.
- **Gap D — Report backups + orphan list still held (by design).** The 3 `ph_segment_report_backup_*` and the 492 orphan assignments were deliberately kept today; drop/act only after Bietrick's formal acceptance. Owner: abiraj → Bietrick.

> `GAP: no blocking gaps for today's cleanup — the 9 targets were archived, dropped in one transaction, and the post-check proved the live dashboard (md5 unchanged) and the 3 report backups intact. Remaining items are carried project items (routine UI swap, sign-offs, view backup).`

---

## SECTION 5 · VALIDATION RULE ADDED OR CHANGED

- **Backup-drop discipline (NEW, established today).** Before dropping any backup: (1) prove the exact drop set from source; (2) **archive each target to a local byte-verified file + manifest**; (3) **pre-check** the drop-set count and the keep-set count; (4) drop in a **single transaction**; (5) **post-check** that the live object's `md5` is unchanged and the keep set survives. A drop is only "safe" when it is reversible-from-archive and fingerprinted before/after.
- **Scope guard.** DROP is limited to the named disposable backups only — never the live table, never the rollback net, never in the same breath as any other change.
- **Carried, unchanged:** all classification/movement/engine logic (Method-A CVR, benchmark top-30/10/manual, Option-B map, FBM/UK/Amazon scope, strict segment-rank movement, 4-week window); dashboard data is baked (a live change needs a byte-verified push); flag-don't-act escalations.

> `VALIDATION RULE: a backup drop must be archive-first (byte-verified + manifest), pre-checked (exact drop/keep counts), single-transaction, and post-checked (live md5 unchanged, keep set intact); scope limited to named disposable backups only.`

---

## SECTION 6 · FAILURE MODE OR EDGE CASE

- **Irreversible-delete risk (mitigated by design).** A `DROP TABLE` cannot be undone in-place. Mitigation: every target was **archived to a byte-verified local file with a manifest before** the drop, so any table can be restored from the archive — "dropped" ≠ "lost".
- **Wrong-target / over-drop risk (prevented).** A wildcard drop could catch the wrong tables. Prevention: the drop set was proven from source to be exactly the 9 `ph_task_id5_backup_*` names, pre-checked (count = 9), and run in a single transaction — the live table and the 3 report backups were never in scope.
- **Silent live impact (ruled out).** The live dashboard could in theory be disturbed. Ruled out: the live id-5 `md5(html_content)` was captured before and re-checked after — **identical** (`1f657a1b…`), and the 3 report backups were confirmed still present.

---

## SECTION 7 · DECISIONS MADE TODAY

- **D-60 (executed) — Clean up only the 9 disposable id-5 dashboard backups.** Proven from source; keep set (live `ph_task` + 3 report backups) confirmed separately.
- **D-61 (executed) — Archive-first: export each of the 9 to a byte-verified local file + manifest before any drop.** Reversible-from-archive.
- **D-62 (executed) — Pre-check the exact counts (9 targets, live id-5 present, 3 report backups) before dropping.**
- **D-63 (executed) — Drop the 9 in a single transaction (`DROP TABLE IF EXISTS …`).** All-or-none; no other DDL, no push.
- **D-64 (executed) — Post-check: 0 backups remain, live id-5 md5 unchanged (`1f657a1b`), 3 report backups intact.**
- **D-65 (decision) — Keep the 3 report backups + the 492 orphan assignments untouched, pending Bietrick's formal acceptance.**
- (D-0…D-59 from D01–D08 remain in force.)

---

## SECTION 8 · COMPANY KNOWLEDGE EXTRACT

### Business Rule
Per-push safety backups are **temporary**: once the live surface they protected is stable and verified, the individual per-step copies become clutter and should be cleaned up — but **only after** each is archived to a byte-verified local file, and **never** together with the current rollback net (which is retained until the owner formally accepts the change).

### Operational Assumption
A destructive database action (`DROP`) is acceptable only when it is made **reversible-from-archive** first and **fingerprinted before and after**. The live object's `md5` unchanged across the action is the proof that only the intended targets were affected. Scope is proven from source and pre-counted; the action runs in a single transaction.

### Reusable Logic / Formula
- **Archive-first drop:** export → byte/row-verify → manifest (table → file → rows → md5) → pre-check counts → single-transaction DROP → post-check (live md5 unchanged, keep set intact).
- **Fingerprint-guarded destructive action:** capture the live object's `md5` before, re-check after — identical means no collateral impact.
- **Scope-by-name, not just by pattern:** enumerate the exact tables, count them, and keep the drop count locked (exactly N) so a wildcard can't over-reach.
- **Separate "clean up" from "the rollback net":** never drop the current recovery copies in the same operation.

### Canonical Vocabulary
| Term | Meaning |
| :---- | :---- |
| id-5 dashboard backup | a one-time `tech_team_outputs.ph_task_id5_backup_*` snapshot taken before a dashboard push; disposable once the live surface is stable |
| rollback net | the current recovery copies kept until formal acceptance — here the 3 `analytics.ph_segment_report_backup_*` tables (NOT dropped) |
| archive-first | export + byte-verify each target to a local file (with a manifest) before any drop, so a dropped table is restorable |
| fingerprint guard | capturing a live object's `md5` before and after a destructive action to prove nothing else changed |

### Cross-Project Applicability
- **Archive-first drop + fingerprint guard** — any database housekeeping that removes backup/temp tables safely.
- **Scope-by-name + single-transaction** — any bulk delete where over-reach must be impossible.
- **Separate cleanup from rollback net** — any change-management flow that keeps a recovery copy until sign-off.

---

## SECTION 9 · LLM STANDARD CHECK

| Check | YES / NO |
| :---- | :---- |
| Could an unknown developer continue from this file without reading source code? | ✅ YES |
| Is every business threshold visible (not buried in code)? | ✅ YES — drop set (the 9 names), keep set, and the pre/post-check counts are in metadata + S2/S5 |
| Is the GAP FOUND section completed or marked NONE? | ✅ YES — 4 carried items; none block today's cleanup |
| Is the COMPANY KNOWLEDGE EXTRACT section substantive? | ✅ YES |
| Are evidence locations referenced? | ✅ YES — archive + byte-verify of 9 tables, manifest, pre/post-check (live id-5 md5 `1f657a1b` unchanged), executed drop script; no Git SHA (files/DB), stated |
| Is metadata complete (incl. blos_keys_used + hardcoded_thresholds)? | ✅ YES |
| Are section names per standard template (1–9)? | ✅ YES |
| Is this extracting knowledge — not just logging activity? | ✅ YES |

### Three-AM Standard Self-Assessment
- **WHAT** — safely removed the **9 disposable `ph_task_id5_backup_*` dashboard backups**: archived each to a byte-verified local file (+ manifest), pre-checked the exact drop/keep counts, dropped the 9 in a single transaction, and post-checked (0 remain, live id-5 md5 `1f657a1b` unchanged, 3 report backups intact). First DROP in the project, scoped to disposable backups only.
- **NOT DONE (carried project items)** — back up the `v_orphan_asins` view to a file (Gap A); swap the monthly routine to the new UI before 3 Aug (Gap B); Bietrick sign-offs — NEW definition, edge-case protocol, 492 orphan assignments (Gap C); the 3 report backups + orphan list stay until formal acceptance (Gap D).
- **WHY** — the per-push backups had done their job and were causing confusion about which `ph_task` copy is real; archive-first + fingerprint-guard makes the drop reversible and provably harmless; the 3 report backups are the current rollback net and stay until Bietrick accepts.
- **WHO / WHERE / NEXT** — owner abiraj (sign-off gate → Bietrick); artifacts = local archive folder + zip + manifest + executed drop script; live `ph_task` id 5 unchanged (`1f657a1b`); kept objects: live `ph_task` + 3 `ph_segment_report_backup_*`; next: export the orphan view, swap the monthly routine before 3 Aug, and get Bietrick's sign-offs.

---

## ── SUBMISSION CHECKLIST ─────────────────────────────────────────────────────

- [x] File named correctly: `2026-07-06__abiraj__ph-asin__REQ-05-D09.md`
- [x] Saved under dated folder `DigitWeb_Works_Abiraj/06_07_2026/`
- [x] Metadata complete — incl. `blos_keys_used` (NONE), `hardcoded_thresholds`, `user`, and `benefit_status`
- [x] Live DDL evidence in Section 3 (archive + byte-verify + pre-check + single-transaction DROP of 9 + post-check; live id-5 md5 unchanged)
- [x] Section names 1–9 match standard template
- [x] No credentials, passwords, or API keys included
- [x] LLM Standard Check table completed
- [x] Three-AM Standard self-assessment written (WHAT / NOT DONE / WHY / WHO-WHERE-NEXT)
- [x] Evidence referenced (archive + manifest + pre/post-check + executed drop script); no dashboard push; no Git SHA (files/DB), stated
- [x] ✅ **DONE TODAY:** 9 disposable id-5 dashboard backups archived (byte-verified) + dropped in one transaction · pre-check (9 targets / live id-5 / 3 report backups) · post-check (0 remain / live id-5 md5 `1f657a1b` unchanged / 3 report backups intact) · live dashboard + rollback net + orphan list untouched
- [x] **NEXT STEPS (carried):** export `v_orphan_asins.sql` · swap the monthly routine to the new UI before 3 Aug · Bietrick sign-offs (NEW definition, edge-case protocol, 492 orphan assignments)
