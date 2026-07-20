# TASK_REGISTER — PRJ-2026-012_ebay-return-analysis

Canonical index of tasks in this project. One requirement = one Task ID.

## Tasks

| Task ID | Deliverable | Source ref | Status | Evidence | Validation |
|---|---|---|---|---|---|
| REQ-14_ebay-return-analysis | eBay Return Analysis Dashboard — a per-SKU eBay returns dashboard (Excel), one row per variant SKU with ≥ 1 eBay return in the period; 19 columns (SKU · Title · Account · Orders · Returns · Return Rate · Last Month/Last Year Returns · Refund £ · Return Cost £ · Main Reason · Rank · Neg Feedback · Open Cases · Stock · Ad Spend/Sales · ACOS · ROAS) + Return-Reason Breakdown + Filter Options + Before/After efficiency. Built from the live Ledsone PostgreSQL; reference period June 2026. **DELIVERED · PUBLISHED (ids 387–390) · AUTOMATED (monthly, 5th) · SIGNED OFF 2026-07-20.** | `files (6).zip` (5 files: 2 handoff docs, SQL, build script, reference June-2026 xlsx) + `Thinesh task (2).xlsx` (mockup). Imported COPY-only + SHA-256 (`evidence/source_documents/REQ-14_.../SOURCE_MANIFEST.md`). **Governance identity CONFIRMED by owner 2026-07-20:** project = eBay Return Analysis, `project_code=ERA`, phase = Reporting & Presentation (first governed report), requirement `REQ-14`, deliverable `REQ-14-D01`. | **LIVE-VERIFIED 2026-07-20** — canonical SQL run against the `ledsone` DB via a direct read-only psycopg2 connection (no MCP); reproduces the reference to the penny: 144 rows / 153 returns / 17.7% / £2,937.37 refund / £869.39 return cost / £1,387.96 ad spend / £9,343.63 ad sales / 14.9% ACOS / 6.73x ROAS; reason breakdown sums to 153 (live Orders 863). `validation/REQ-14_.../2026-07-20_live_count_verification.md`. Full 144-row diff + workbook rebuild still pending. | `evidence/source_documents/REQ-14_.../` (handoffs, mockup, manifest) · `sql/REQ-14_.../ebay_return_analysis.sql` · `evidence/final_outputs/REQ-14_.../` (build script + reference xlsx) · `validation/REQ-14_.../2026-07-20_live_count_verification.md` | Aggregate totals + reason breakdown LIVE-VERIFIED; no publish, no reviewer/business sign-off yet. |

## REQ-14-D01 — intended deliverable detail
- **Scope:** a populated read-only per-SKU eBay Return Analysis dashboard for the reporting period,
  reproduced against the live Ledsone PostgreSQL, matching the reference June-2026 file.
- **Method (from the handoff):** SKU via `transaction_id` bridge (not `item_id`); Return Cost = REFUND +
  FINAL_VALUE_FEE; Advertising = **CPC + CPS** combined (performance_data is CPC-only; CPS is the
  AD_FEE/PREMIUM_AD_FEES per-sale fee); text-typed numerics cast; earliest-row reason/refund vs
  newest-row state; intentional blanks preserved. See `SYSTEM_REFERENCE.md`.
- **Build recipe:** run statement 1 → `main.tsv`, statement 2 → `reason_breakdown.tsv`, then
  `build_dashboard.py` → recalc with LibreOffice (0 errors) → diff vs the reference figures.
- **project_code `ERA`** — minted with owner confirmation pending; to be verified in `ph_task` only if/when published.
- **Publish (only when authorised):** per-user to `tech_team_outputs.ph_task`, `project_code=ERA`,
  `assigned_user_team` set (missing from the sample DDL), pre-DELETE by task_id + plain INSERT (no real
  UNIQUE on task_id) — the PRJ-2026-010/011 precedent. **Not yet done.**

## REQ-14-D01 — HTML dashboard built 2026-07-20 (Phase A)
Two generators in `evidence/final_outputs/REQ-14_.../`, both in the **PRJ-2026-011 (EBPD) house style**
(teal/slate light theme, KPI cards, grouped sticky headers, RAG pills, rank badges, panels):
- **`build_returns_html.py`** — single full-month view, renders from the output Excel (offline path).
- **`build_returns_live_html.py`** — the delivered build: pulls **live from `ledsone`** (read-only,
  direct psycopg2, no MCP) and renders **7 in-month date-range views** with pure-CSS radio toggles.
- **Output:** `eBay Return Analysis Dashboard - June 2026 - FINAL.html` (~520 KB) + `returns_windows_2026-06.json`
  (cached per-window datasets). 8 KPI cards, the **19-column per-SKU table** (SKU pinned, headers fixed),
  **Return-Reason Breakdown** (bars) + **Filter Options** + **Before/After** panels + Definitions.
- **Working date presets (within the month):** Full month · 1st/2nd half · Week 1–4 — each re-scopes the
  whole dashboard (KPIs, table, reason breakdown). Pure-CSS so they work in the no-JS ph_task viewer.
  Account/Reason/SKU filtering + CSV export are progressive-enhancement JS scoped to the active view.
- **Reconciliation (live, per window):** Full = **144 SKUs / 153 returns / £2,937.37 refund / £869.39 cost
  / £1,387.96 ad spend / £9,343.63 ad sales / 17.7% / ACOS 14.9% / ROAS 6.73x**. Windows partition cleanly:
  **h1(82)+h2(71)=153**, **w1+w2+w3+w4 = 27+46+43+37 = 153**, refund halves £1,584.59+£1,352.78 = £2,937.37.
  LM/LY comparison columns shown on the Full view only (blank for sub-ranges). Stock is a live snapshot.
- **Verified in-browser** (served via localhost): DOM renders, JS filters compute ("144/144 SKUs"), and the
  "1st half" preset correctly switches to 79 SKUs / 82 returns / £1,584.59 / ACOS 15.3% / ROAS 6.55x.

## REQ-14-D01 — PUBLISHED 2026-07-20 (4 users)
Published per-user to `tech_team_outputs.ph_task`, all `project_code=ERA`,
`assigned_user_team=ebay_priors`, `released` (the same eBay team group as PRJ-2026-010/011). Current live
rows (ids incremented across layout refreshes + the ebra→ERA re-key; old ebra rows retired):
| id | assigned_user | task_id |
|---|---|---|
| 387 | Thinesh | `ERA_Thinesh_ebay_return_analysis_2026-06` |
| 388 | Jarsini | `ERA_Jarsini_ebay_return_analysis_2026-06` |
| 389 | kobiga | `ERA_kobiga_ebay_return_analysis_2026-06` |
| 390 | powsteena | `ERA_powsteena_ebay_return_analysis_2026-06` |
Guarded `temp_user` publish (pre-flight read-only check; **pre-DELETE by task_id +
plain INSERT** — no real UNIQUE on `task_id`; `assigned_user_team` set — missing from the sample DDL).
Publisher = `automation/era_monthly_run.py`. Each row carries the ~521 KB dashboard HTML. Verified live
(read-only) post-publish. Recipients confirmed real — all four already receive the epc + ebpd dashboards.

## REQ-14-D02 — MONTHLY AUTOMATION LIVE 2026-07-20
Fully autonomous monthly refresh (the recurring evolution of D01):
- **`automation/era_monthly_run.py`** — dynamic **last-complete-month** window; connects **ledsone**
  (read, the data) + **warehouse** (ph_task publish) via **direct psycopg2 (no MCP)**; runs the canonical
  query per in-month preset window; builds the static HTML via `build_returns_live_html.generate()`;
  publishes month-keyed (`ERA_<user>_ebay_return_analysis_<YYYY-MM>`: refresh in-month, new row per month).
- **Scheduled:** Windows Task **`ERA_Monthly_Dashboard`**, **day 5 of every month @ 09:30** (next run
  **2026-08-05**, will report July 2026), `run_era_monthly.bat`.
- **Monitoring:** `era_status.txt` (one OK/FAILED line per run) + Desktop failure alert (`era_alert.ps1`
  → `ERA_ALERT_FAILED.txt`, auto-clears on next success).
- **Security:** all DB passwords in the **git-ignored** `automation/era_secrets.bat` (template provided);
  no plaintext credentials in any tracked file.
- **Verified:** end-to-end dry-run (`--no-publish`) resolves the dynamic month to June 2026 and reconciles
  144 SKUs / 153 returns / £2,937.37; the live publish then produced ids 375–378.
- Registrar: `automation/register_era_task.ps1` (`-Remove` to unschedule). Docs: `automation/` scripts.

## Onboarding (this session — 2026-07-20)
- Registered the project as **PRJ-2026-012**; authored the five standing docs (`README`, `PROJECT_HOME`,
  `SYSTEM_REFERENCE`, `CLAUDE`, `TASK_REGISTER`); added the row to the root `PROJECT_REGISTER.md`.
- Imported the handoff bundle COPY-only with SHA-256 verification: 2 handoff docs + the requester mockup
  → `evidence/source_documents/REQ-14_.../`; the SQL → `sql/REQ-14_.../`; the build script + the
  reference June-2026 xlsx → `evidence/final_outputs/REQ-14_.../`; provenance in `SOURCE_MANIFEST.md`.
- **No source table written; no live query run; nothing published.** The reference xlsx is the diff
  target, not a workbench-produced deliverable.

## One next action
Confirm the `REQ-14` / `ERA` identifiers with the owner; then, on owner go, run the RUNBOOK against the
live Ledsone DB to produce REQ-14-D01, diff it against the June-2026 reference, and record a validation
before any publish.

## Rule
A new day or Claude session does **not** create a new Task ID. Keep using
`REQ-14_ebay-return-analysis` until D01 is closed; a genuinely new requirement (with owner confirmation)
earns a new deliverable/task id.
