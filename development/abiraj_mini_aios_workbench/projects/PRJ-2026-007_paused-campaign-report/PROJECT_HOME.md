# PROJECT_HOME — Paused Campaign Report (Utharsika)

## Project ID
PRJ-2026-007_paused-campaign-report

## Project Name
Paused Campaign Report | Utharsika's automation-paused Amazon PPC ad targets that are still paused today

## Purpose
Produce the **Paused Campaign report for Utharsika**: the list of her Amazon PPC ad targets that the
PPC **automation engine paused** and that remain **paused today**, with the seven required columns
(Campaign Name, Ad Group Name, ASIN, SKU, Pause Reason, Campaign Pause Date, Days Paused). It is a
**read-only reporting task** — no source table is ever written to. Every value ties to a real
`schema.table.column`; the pause reason is taken **verbatim** from the automation log; unclear
business rules are flagged for Satheesvaran, never invented.

## Business Question
Which of Utharsika's Amazon ad targets did PPC automation pause, that are **still paused today**, and
for each — which campaign and ad group does it sit in, what ASIN/SKU is it, why did automation pause
it, on what date, and how many days has it been paused — so the team can review and decide whether to
re-activate or optimise?

Status: **CONFIRMED** from `Utharsika_task.xlsx` (sheet `PH-2026-07-UTHAR10 - Abiraj - 1`,
requirement `REQ-09-D01`) and the `CLAUDE_CODE_HANDOFF_Paused_Campaign.md` handoff. **Business
edge-case sign-off (Satheesvaran) is OPEN** — see Known Risks / One Next Action (items A–E).

## Owner and Reviewers
- Owner / Developer: **Abiraj**
- End user (Portfolio Holder): **Utharsika** (campaign-name token `Utharsika`)
- Coordinator: Varmen
- Technical Reviewer: Sajeesan
- Queryability Reviewer: Tamil Selvan
- Business Validator: **Satheesvaran** (rule edge cases A–E) — **sign-off pending**

## Original Requirement
- **REQ-09-D01 (2026-07-13)** — Paused Campaign report for Utharsika: a governed read-only query
  (`generate_report.sql`) returning the seven columns, plus a template-matching **.xlsx** and an
  interactive **HTML dashboard**, reconciled to the live DB, with an independent verification pack.
  The workbook's two sample rows (B0DH182H6J / B0CVKSQN9K, pause date 2026-07-06, Days Paused 0) are
  **illustrative only** and are not reproduced as the answer.

## Approved Scope
- Maintain this project folder (`projects/PRJ-2026-007_paused-campaign-report/`) only.
- **READ-ONLY** inspection of production PostgreSQL `order_management_copy` via the Postgres MCP, for
  discovery, the report pull and evidence.
- COPY-only import of the handoff brief + task workbook from `C:\Users\digit\Downloads\` (originals kept).
- Generate the report query + the xlsx/HTML renderers and their outputs. **No DB object created,
  dropped or altered** — this report is a per-run extract, not a view.

## Prohibited Scope
- No `INSERT`/`UPDATE`/`DELETE`, no DDL, no schema change anywhere in the DB.
- Do not invent campaigns, ASIN/SKU mappings, pause reasons or dates not present in the DB.
- Do not decide any of the open business rules (A–E) — flag them for Satheesvaran.
- Do not modify anything outside this project folder without written approval.
- Do not commit or push without explicit instruction.

## Systems and Sources (read-only)
- **PostgreSQL `order_management_copy`** (production), via the Postgres MCP (connector GUIDs rotate
  per session — rely on the DB name / the `execute_sql` tool, not the id).
- Key objects: `ppc` (campaign / ad-group / ad metadata + current status), `ppc_performance`
  (ASIN + SKU at ad grain), `ppc_etl_automation_log` (the pause events + reasons). Full per-table
  rules in `SYSTEM_REFERENCE.md` and the skill reference `TABLE_ppc.md`.
- Spec / acceptance source: `Utharsika_task.xlsx` (`PH-2026-07-UTHAR10`) +
  `CLAUDE_CODE_HANDOFF_Paused_Campaign.md`.

## Imported / Generated Assets
Under Task `REQ-09_paused-campaign-report` (COPY-only import; Downloads originals preserved):
- `evidence/source_documents/REQ-09_.../CLAUDE_CODE_HANDOFF_Paused_Campaign.md` — approved handoff.
- `evidence/source_documents/REQ-09_.../Utharsika_task.xlsx` — the task spec sheet.
- `evidence/source_documents/REQ-09_.../SOURCE_MANIFEST.md` — provenance + checksums.
- `sql/REQ-09_.../generate_report.sql` — canonical read-only report query.
- `sql/REQ-09_.../validation_checks.sql` — the count + still-paused validation queries.
- `evidence/final_outputs/REQ-09_.../`:
  - `data.json` — governed pull (33 rows + run metadata) — **system of record**.
  - `Utharsika_Paused_Campaigns_Report.html` — **published dashboard (canonical)**. Table-hero
    layout (slim KPI ribbon → table fills the height; rule-coded left bands + badges; heat-scaled
    Days Paused; system fonts, no CDN). Header shows the **performance window 11 May – 17 Jun 2026**
    (the assessed period, derived from the verbatim reasons) + "still paused as of 13 Jul 2026".
    LF, md5 `df9871a1d627c59c470c8345e8386654`, 34,321 chars. Same 33-row payload reused verbatim —
    data parity with `data.json` exact (33 rows / 32 ASINs / all tuples match).
  - `build_report.py` → `Paused_Campaign_Report_Utharsika.xlsx`.
  - `build_html.py` → `Utharsika_Paused_Campaigns_dataview.html` — secondary/audit renderer only,
    NOT the published artifact.
  - `PAUSED_CAMPAIGN_VERIFICATION_PACK.md` — independent 4-check pack.
- `validation/REQ-09_.../2026-07-13_validation.md` — live reconciliation evidence.
- `closure/REQ-09_.../2026-07-13_closure.md` — closure record.

## Source-of-Truth Locations
- **Published dashboard (key deliverable):** `evidence/final_outputs/REQ-09_.../Utharsika_Paused_Campaigns_Report.html`
  (hand-finished; spine `data.json`; query `generate_report.sql`). Refresh its embedded payload from
  a new `data.json` on re-run.
- **Data (system of record):** `…/data.json` — governed pull + metadata; carries the verbatim reason.
- **Spreadsheet:** `…/Paused_Campaign_Report_Utharsika.xlsx` (rebuild via `build_report.py`).
- **Locked rules / functional detail:** `SYSTEM_REFERENCE.md`.
- **Approved handoff/spec:** `evidence/source_documents/REQ-09_.../`.
- **Note:** the published dashboard loads IBM Plex fonts from Google Fonts (CDN); offline it degrades
  gracefully to `system-ui`. All data is embedded — no network call fetches report data.

## Run Snapshot (2026-07-13)
- **33** paused ad targets · **32** distinct ASINs (B0DXQ84YT7 sits under two ad groups →
  2 rows, 1 ASIN).
- **41** total automation pauses (successful, `applied_by='0'`) → **33** still paused ·
  **8** re-activated and correctly excluded.
- Two pause waves: **2026-06-10** → 18 targets @ 33 days · **2026-06-17** → 15 targets @ 26 days.
- Pause-rule mix (verbatim from the log): Rule 1 (ACOS), Rule 2 (zero orders + spend by price band),
  Rule 3 (spend based, orders dropped in last 7 days); one row carries a combined Rule 1 | Rule 3.
- **Live-DB note:** `ppc.record_status` is *current* status; "still paused" is as-of-today. Days
  Paused = `CURRENT_DATE − pause_date`, so it moves with the run date.

## Known Risks / Open Items (flag to Satheesvaran — do NOT decide)
- **A. Scope key:** is name-token matching (`Utharsika` in the campaign name) the intended owner
  definition, or should an owner field be added upstream? (No owner column exists today.)
- **B. Grain:** one row per paused ASIN (current) vs one aggregated row per campaign?
- **C. Included set:** still-paused only (current, 33) vs every pause event incl. re-activated (41)?
- **D. Platform:** Amazon only (all the pause log contains) vs include eBay/SD/SB if pause
  automation is added there later? SB is excluded by design (unrepresentative single-ASIN mapping).
- **E. Manual pauses:** automation-only (`applied_by='0'`, current) vs also include manual pauses?

## Live Publish
Published to the shared ops store `tech_team_outputs.ph_task` (DB `order_management_copy`) —
**row id 215**: `project_code=PC` · `task_id=PC_utharsika_paused_campaigns_dashboard-V1` ·
`task_name=PC · Paused Campaign Report — Utharsika (Amazon PPC)` · `team=Development` ·
`developer=Abiraj` · `assigned_user=utharsika` · `assigned_user_team=ph_priors` · `phase_level=1` ·
`version_status=released`. Created 2026-07-13 13:55 (Asia/Colombo) via a **guarded single-row INSERT**
as `temp_user` (owner-authorised), following the ZSFO precedent (row 167, `project_code=ZSFO`);
pre-flight confirmed `task_id`/`project_code` were free, no other row touched, no schema/DDL.
- **V2 update (2026-07-13 14:04):** `html_content` replaced with the table-hero redesign,
  `version_level 1→2` (guarded single-row UPDATE).
- **V3 update (2026-07-13 14:12):** header now shows the **performance window 11 May – 17 Jun 2026**;
  the row `description` shortened to one line; `version_level 2→3`, `updated_at=now()` — guarded
  `UPDATE … WHERE id=215 AND task_id=…`, identity fields unchanged. Live verified
  `md5=df9871a1d627c59c470c8345e8386654` (34,321 chars) — identical to the canonical file;
  `description` = "Utharsika's Amazon PPC ad targets paused by automation and still paused as of
  2026-07-13 — 33 targets / 32 ASINs. Performance window 11 May – 17 Jun 2026. Read-only."
- **Description cleared (2026-07-13 14:17):** on owner request the `description` column was set to
  **NULL** (guarded `UPDATE … WHERE id=215 AND task_id=…`; `html_content` md5 `df9871a1…` unchanged,
  `version_level` still 3). The report's context now lives in the dashboard itself, not the DB column.
- **V4 width fill (2026-07-13 14:23):** reduced the layout side padding (~22px → 7px) so the table runs
  near edge-to-edge and fills the viewer width. HTML-only guarded UPDATE (`description` left NULL);
  `version_level 3→4`, live md5 `b4a2b0ee9173c7c21dc7c7b14b7b1dd8`, 34,301 chars — matches the file.
Publish/update scripts kept in the session scratchpad (not committed — they carry the `temp_user`
credential).

## Status
- **D01: COMPLETE (technical) — PUBLISHED (row 215); VALIDATION GREEN; BUSINESS SIGN-OFF PENDING.** Validated query
  (still-paused filter, verbatim reasons), 33-row governed pull, xlsx + HTML dashboard, 4/4
  verification checks. Not committed/pushed.
- Not yet business-validated by Satheesvaran (items A–E).

## One Next Action
Take the five open items (A–E) to **Satheesvaran** for a business decision — primarily **grain**
(per-ASIN vs per-campaign) and **included set** (still-paused 33 vs all-pauses 41), since those two
change the row count. Then, if a recurring cadence is wanted, open **REQ-09-D02** to schedule the run
with a dynamic `CURRENT_DATE`. Do not change any locked rule without Satheesvaran sign-off.
