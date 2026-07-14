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

## V2 UI update (2026-07-14, same run)
The initial per-PH dashboards used a fixed `height:100vh` two-pane layout with an internal card
scroll — inside the `ph_task` portal frame this collapsed the card area to a small scrolling box and
left dead space in the sidebar. **Rebuilt with an embed-friendly layout** (`build_per_ph.py` V2):
document-flow (no forced viewport height / no internal overflow so cards fill the full height and the
portal supplies a single scroll), **sticky sidebar** + **sticky filter bar**, and a polished sidebar
(logo, holder avatar, mini stat tiles, **severity-split** mini-bar, footer). Verified locally
(Jasmini render: sidebar + all 14 cards flow as one document).

Published as a guarded **UPDATE** of the same 19 rows (match by `task_id`, one txn, md5-verified
pre-commit, auto-rollback on mismatch), **`version_level` 1→2**, `updated_at=now()`; identity fields
(`assigned_user`, `task_id`, `project_code`, `assigned_user_team`) unchanged. Independently re-verified
via read-only MCP: 19 rows at `version_level=2`, all `html_content` present; stored md5 matches local
(e.g. Jasmini `a7baa215…`, utharsika `84205a4a…`). Update script `push_frrc_update_v2.py` kept in
scratchpad (carries credential), NOT committed.

## V3 table redesign (2026-07-14, same run)
Owner feedback on the live V2: the card view still read as a small area with wasted space at the top
and duplicated stats between the header tiles and the sidebar. **Rebuilt as a full-width, full-height
data TABLE** (`build_per_ph.py` V3): columns **Status · Product · Units · Returns · Rate · Reasons
(mini reason-mix bar) · Likely cause · Recommended action**; **sticky toolbar** (title + count +
search + flag chips + sort) and **sticky column header** so both persist on scroll; removed the
redundant top KPI-tile row; trimmed the sidebar to holder identity + window + a single **severity
strip** (Critical/High/OK/N-A counts) + a reason-bucket legend + footer (dropped the duplicate mini
stat tiles). Rows flow full-height; the table scrolls horizontally inside its own container on narrow
widths (no page-level horizontal scroll). Verified locally (utharsika: 21-row full-width table, slim
toolbar, trimmed sidebar). Published as a guarded in-place **UPDATE** of the same 19 rows (match by
`task_id`, one txn, md5-verified pre-commit), **`version_level` 2→3**, identity fields unchanged.
Re-verified via read-only MCP: 19 rows at `version_level=3`; stored md5 matches local (utharsika
`9c43439c…`, Jasmini `daab1c3c…`).

## Reversibility
Rows 216–234 only. Rollback of the whole publish = `DELETE FROM tech_team_outputs.ph_task WHERE
project_code='frrc'`. No pre-existing (non-frrc) row was ever modified; the V2/V3 changes were in-place
UPDATEs of the 19 frrc rows.

## Data integrity
Each per-PH dashboard is a filtered render of the governed `frrc30.json` (single owner). Row counts per holder reconcile to the dataset; sum = 73 named-owner ASINs. (`length(html_content)` in Postgres counts characters, so it reads a few less than the local byte count where the UI uses multi-byte —/→ glyphs — not a discrepancy; md5 of the exact stored text matched local.)
