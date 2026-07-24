# TASK_REGISTER — PRJ-2026-007_paused-campaign-report

Canonical index of tasks in this project. One requirement = one Task ID.

## Tasks

| Task ID | Deliverable | Source ref | Status | Evidence | Validation |
|---|---|---|---|---|---|
| REQ-09_paused-campaign-report | **D01** — Paused Campaign report (SQL + xlsx + HTML dashboard + verification pack), run 2026-07-13: 33 still-paused ad targets / 32 ASINs. **Published** to `tech_team_outputs.ph_task` **id 215** (`project_code=PC`, `task_id=PC_utharsika_paused_campaigns_dashboard-V1`, released). | `Utharsika_task.xlsx` `REQ-09-D01` (`PH-2026-07-UTHAR10`) | **COMPLETE (technical) — PUBLISHED (row 215); VALIDATION GREEN; BUSINESS SIGN-OFF PENDING** | `evidence/final_outputs/REQ-09_paused-campaign-report/` | `validation/REQ-09_paused-campaign-report/2026-07-13_validation.md` |

## D01 — Deliverable detail
- **Query:** `sql/REQ-09_.../generate_report.sql` — util_camp (scope) → pauses (latest per target,
  automation-only) → still-paused join → ASIN/SKU from `ppc_performance`; `json_agg` form for the pull.
- **Validation queries:** `sql/REQ-09_.../validation_checks.sql` — count check (targets / ASINs) +
  still-paused-vs-all-pauses.
- **Data:** `evidence/final_outputs/REQ-09_.../data.json` — 33 rows + run metadata.
- **Outputs:** `Utharsika_Paused_Campaigns_Report.html` (**published dashboard**, hand-finished,
  owner-supplied; data parity with `data.json` verified exact) + `Paused_Campaign_Report_Utharsika.xlsx`
  (via `build_report.py`). `build_html.py` is a secondary audit renderer only.
- **Verification:** `PAUSED_CAMPAIGN_VERIFICATION_PACK.md` — 4/4 PASS (live 2026-07-13).
- **Reconciliation:** 41 total automation pauses → 33 still paused (report) · 8 re-activated (excluded);
  32 distinct ASINs; pause waves 2026-06-10 (18) and 2026-06-17 (15).

## Open / next (route to Satheesvaran — do NOT decide)
- **A. Scope key** — name-token `%utharsika%` vs an upstream owner field. **OPEN.**
- **B. Grain** — one row per paused ASIN (current) vs one aggregated row per campaign. **OPEN.**
- **C. Included set** — still-paused only (33) vs all pauses incl. re-activated (41). **OPEN.**
- **D. Platform** — Amazon only vs include eBay/SD/SB if pause automation is added there. **OPEN.**
- **E. Manual pauses** — automation-only (`applied_by='0'`) vs also include manual pauses. **OPEN.**
- **REQ-09-D02 (separable, not opened):** schedule a recurring run (query already `CURRENT_DATE`-based).
  Needs owner confirmation.

## Rule
A new day or Claude session does **not** create a new Task ID. Keep using
`REQ-09_paused-campaign-report` until D01 is formally closed; only a genuinely new requirement (with
owner confirmation) gets a new deliverable/task id.

---

## 2026-07-24 — AUTOMATED (REQ-09 automation complete)

`PC_Weekly_PausedCampaigns` registered on the permanent path — **Wednesdays 09:00**, first run
**2026-07-29**. `automation/pc_weekly_run.py` + `run_pc_weekly.bat` + `pc_alert.ps1` +
`AUTOMATION_README.md`; task XML backed up in `05_documentation/capability/scheduled_tasks/`.

Keeps the EXACT hand-finished dashboard: the runner reads `Utharsika_Paused_Campaigns_Report.html`
as a read-only template and re-injects the `<script id="payload">` rows + `const RUN` /
`TOTAL_PAUSES` / `WINDOW` each run. SQL already uses CURRENT_DATE (run-date safe, no
parameterization). The 3 pause rules' label/summary/metric-chips are derived from each verbatim
reason string; WARN logs any reason format that fails to parse. Weekly REPLACE in place (task_id
`…-V1`, id 215), backup-first, md5-verified.

Proven 2026-07-24 (dry-run + Task-Scheduler temp run `LastTaskResult=0`): 69 still-paused of 88
total (was 33/41 at D01 — more campaigns paused since), all 11 payload keys present, every rule's
chips parsed cleanly (0 unparsed), constants updated. Nothing published — first real publish is the
scheduled 2026-07-29 run. Owner authorised proceeding without the pending Satheewaran edge-case
sign-off (core report already delivered/validated).
