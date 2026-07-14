# Evidence — FRRC REQ-10-D01 per-PH publish to ph_task (2026-07-14)

## What was published
19 per-PH dashboards published **LIVE** to `tech_team_outputs.ph_task` (DB `order_management_copy`),
one row per named portfolio holder — each holder sees **only their own** returning Amazon FBA ASINs.

- **project_code** `frrc` · **project_name** "FRRC — FBA Returns Root-Cause (weekly Amazon FBA returns tracker & root-cause action report) — LEDsONE analytics platform"
- **task_name** (Task Name from `2026-07-14_abiraj_REQ-frrc_REQ-10-D01.md`)
- **task_id** `frrc_<PH-slug>_fba_returns_root_cause-V1` (unique per holder; PSLD precedent)
- **team** Development · **developer** Abiraj · **assigned_user_team** `ph_priors` (owner-confirmed)
- **phase_level** 1 · **version_level** 1 · **version_status** released
- **description** one line per holder with their product/return/critical counts.

## Rows (ids 216–234, INSERT-only, no existing row touched)
| id | assigned_user | ASINs | returns | crit | task_id |
|---|---|---|---|---|---|
| 216 | Abinayaa | 4 | 7 | 4 | frrc_Abinayaa_fba_returns_root_cause-V1 |
| 217 | Akanila | 1 | 1 | 1 | frrc_Akanila_fba_returns_root_cause-V1 |
| 218 | Dilani | 2 | 4 | 2 | frrc_Dilani_fba_returns_root_cause-V1 |
| 219 | Illakkiya | 1 | 1 | 0 | frrc_Illakkiya_fba_returns_root_cause-V1 |
| 220 | Jasmini | 14 | 15 | 6 | frrc_Jasmini_fba_returns_root_cause-V1 |
| 221 | Jathisha | 2 | 3 | 1 | frrc_Jathisha_fba_returns_root_cause-V1 |
| 222 | Jubista | 4 | 4 | 3 | frrc_Jubista_fba_returns_root_cause-V1 |
| 223 | mothajini | 2 | 2 | 1 | frrc_mothajini_fba_returns_root_cause-V1 |
| 224 | paulr | 2 | 3 | 1 | frrc_paulr_fba_returns_root_cause-V1 |
| 225 | prasath | 1 | 1 | 0 | frrc_prasath_fba_returns_root_cause-V1 |
| 226 | Renuha | 2 | 3 | 1 | frrc_Renuha_fba_returns_root_cause-V1 |
| 227 | Sarbavi | 1 | 3 | 1 | frrc_Sarbavi_fba_returns_root_cause-V1 |
| 228 | Shanthini | 3 | 3 | 2 | frrc_Shanthini_fba_returns_root_cause-V1 |
| 229 | Tharsiga(nelli) | 1 | 1 | 1 | frrc_Tharsiga_nelli_fba_returns_root_cause-V1 |
| 230 | Tharsika(jaffna) | 3 | 3 | 2 | frrc_Tharsika_jaffna_fba_returns_root_cause-V1 |
| 231 | Theepana | 4 | 4 | 1 | frrc_Theepana_fba_returns_root_cause-V1 |
| 232 | Thojika | 1 | 1 | 0 | frrc_Thojika_fba_returns_root_cause-V1 |
| 233 | thuwaraga | 4 | 4 | 1 | frrc_thuwaraga_fba_returns_root_cause-V1 |
| 234 | utharsika | 21 | 24 | 16 | frrc_utharsika_fba_returns_root_cause-V1 |

Total across holders: **73 of 91 ASINs** (the **18 unassigned** N/A ASINs have no PH owner → not routed to anyone; open item G).

## How it was done (guarded write)
- Write path: **direct psycopg2 as `temp_user`** (host 149.28.134.54:5435, db `order_management_copy`) — the owner-supplied write path (sample `temp_user 1.py`), NOT the read-only MCP. This was an **owner-directed** publish from an otherwise read-only session (ph-asin / PC / ZSFO precedent).
- **One transaction**, INSERT-only. Read-only pre-flight asserted `project_code='frrc'` had 0 rows and all 19 `task_id`s were free (max prior id 215).
- Each row's stored `html_content` md5 re-checked **before commit**; commit only after all 19 matched; auto-rollback on any mismatch.
- Independent post-commit verification via the **read-only MCP connector** (separate connection): 19 rows / 19 distinct users / all `assigned_user_team='ph_priors'` / all `version_status='released'` / all `html_content` present / ids 216–234. PASS.
- The credential-bearing publish script (`push_frrc_per_ph.py`) is kept in the **session scratchpad only** — never committed.

## Reversibility
New rows only (216–234); rollback = `DELETE FROM tech_team_outputs.ph_task WHERE id BETWEEN 216 AND 234` (or `WHERE project_code='frrc'`). No pre-existing row was modified.

## Data integrity
Each per-PH dashboard is a filtered render of the governed `frrc30.json` (single owner). Row counts per holder reconcile to the dataset; sum = 73 named-owner ASINs. (`length(html_content)` in Postgres counts characters, so it reads a few less than the local byte count where the UI uses multi-byte —/→ glyphs — not a discrepancy; md5 of the exact stored text matched local.)
