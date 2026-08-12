# TASK REGISTER — PRJ-2026-023 eBay UK Top 50 Sales Drop

Canonical index of tasks/deliverables within this project. Detail lives in `PROJECT_HOME.md` /
`SYSTEM_REFERENCE.md`.

| Task | Deliverable | Description | Status |
|---|---|---|---|
| REQ-26 | **REQ-26-D01** | **eBay UK Top-50 Sales Drop** report for Kobiga (account ELECTRICALSONE). Compares current vs previous equal period, excludes SKUs with no prior sales and any that rose, ranks the Top 50 by absolute £ loss (tie-break Drop %), and attaches CTR/CVR/ROAS/Stock + a Priority band and Action. 14 columns: Rank · SKU · Item ID · Product · Previous Sales · Current Sales · Loss £ · Drop % · CTR · CVR · ROAS · Stock · Priority · Action. Excel (Notes + table) + interactive HTML dashboard, from one read-only builder joining RAW `ledsone` (sales/PPC/stock) with warehouse `traffic_data` (organic). | 🟡 **SETUP / SCAFFOLD ONLY (2026-08-12).** Folder tree + source import + governance docs created; task understood, data foundation mapped from prior eBay projects. **No SQL run, no deliverable, nothing committed.** Awaiting Kobiga's discovery answers + a GPT-approved implementation prompt. |

## Source
- `evidence/source_documents/REQ-26_ebay-top50-sales-drop/2026-08-12_source_top50-sales-drop-spec.xlsx`
  (from `kobiga task (2).xlsx`) — 14-column layout mock-up with sample rows.
- `evidence/source_documents/REQ-26_ebay-top50-sales-drop/2026-08-12_source_top50-sales-drop-workflow.pdf`
  (from `eBay UK Top 50 Sales Drop Automation Workflow.pdf`) — full 12-section method.
Both are **spec, not data** — they define columns / thresholds / Action vocabulary, never delivered figures.

## Deliverables (planned)
- Excel: `evidence/final_outputs/REQ-26_ebay-top50-sales-drop/REQ-26-D01_ebay_top50_sales_drop.xlsx`
- HTML dashboard: `.../REQ-26-D01_ebay_top50_sales_drop.html`
- Builder: `sql/REQ-26_ebay-top50-sales-drop/build_esdt_d01.py`

## Open items (all pending Kobiga — block the build)
- **Scope** — ELECTRICALSONE only vs all eBay UK accounts.
- **Period** — length, cadence (weekly report / monthly recurrence per PDF §10) and anchor date.
- **Ranking grain** — SKU vs eBay Item ID (89% multi-SKU listings).
- **Alert thresholds** — confirm 50 / 30 / 15% bands.
- **Reason/Action** vocabulary — Kobiga's own list vs the PDF §8 default matrix.
- **CPS £0-spend** handling for ROAS/ACOS.
- **Publish audience** (`ph_task` team, likely `ebay_priors`) + automation cadence.
- Confirm provisional identity `PRJ-2026-023` / `REQ-26` / `esdt` with Abiraj (cosmetic).
- Reviewer gates: Sajeesan (technical), Tamil Selvan (queryability), Kobiga (business).

## Automation
✅ **AUTOMATED 2026-08-12** — Windows task **`ESDT_Monthly_Sales_Drop`**, **the 6th of each month at 10:00**
(free fleet slot; SEG=3rd, SMP=4th, ERA=5th). Fail-closed runner `automation/esdt_monthly_run.py`:
build (`build_esdt_d01.py`, live raw ledsone, CURRENT_DATE window) → render (`render_esdt_dashboard.py`) →
row-floor (≥20) + collapse gates → size-check → **refresh all 6 `ph_task` esdt rows** via
`publish_esdt_ph_task.py --refresh` (only if PGPASSWORD present) → Desktop `ESDT_ALERT.txt` on failure,
last-good rollback. Git-ignored `esdt_secrets.bat` (LED_* + temp_user); template committed. **Proven:
manual run + Start-ScheduledTask → LastTaskResult 0x0** (50 rows, portal md5 OK). Next run 2026-09-06 10:00.
Register/re-register: `automation/register_esdt_task.ps1`.

## Publish record — ph_task
✅ **PUBLISHED 2026-08-12** to `tech_team_outputs.ph_task` (portal `order_management_copy`, temp_user @
149.28.134.54:5435) via `automation/publish_esdt_ph_task.py --ebay-team` (guarded INSERT … RETURNING + md5
read-back, all OK). HTML 61,020 chars, md5 `2a43b5cb…`. Audience = all 6 eBay PH users, team `Development`,
**assigned_user_team `ebay_priors`** (set post-insert — the portal filters on this column; matches
epns/eppr/ERA/ebpd/dst/esnm/epc), developer `Abiraj`, status `released`.

| id | project_code | task_id | assigned_user | team |
|---|---|---|---|---|
| 855 | esdt | esdt_kobiga_ebay_top50_sales_drop | kobiga | Development |
| 856 | esdt | esdt_Jarsini_ebay_top50_sales_drop | Jarsini | Development |
| 857 | esdt | esdt_powsteena_ebay_top50_sales_drop | powsteena | Development |
| 858 | esdt | esdt_Thinesh_ebay_top50_sales_drop | Thinesh | Development |
| 859 | esdt | esdt_Sharmilan_ebay_top50_sales_drop | Sharmilan | Development |
| 860 | esdt | esdt_Sivajitha_ebay_top50_sales_drop | Sivajitha | Development |

Re-publish/refresh a row: `python automation/publish_esdt_ph_task.py --update <id>`.

## Business decisions (Kobiga) — CONFIRMED 2026-08-12 ✅
- **Ranking grain = SKU** (not Item ID).
- **Period = monthly: last 30 days vs previous 30 days** (current `[today−30,today)` vs previous `[today−60,today−30)`).
- **Scope = ELECTRICALSONE only, eBay UK** (`orders.sub_source_id=22` AND `market_place='23'`, `status='Completed'`).
- Thresholds = PDF §6 as-is; Reason/Action = PDF §8 as-is; rank by £ loss desc, tie-break Drop % desc, Top 50.
- Deferred (not blocking): publish audience/automation until Kobiga sees the first report; CPS £0 → ROAS `n/a`.

## Build progress (2026-08-12)
- ✅ **Excel DELIVERED** — `evidence/final_outputs/REQ-26_slow.../REQ-26-D01_ebay_top50_sales_drop.xlsx`
  (3 tabs: Notes & Method · Top 50 Sales Drop · Diagnostics). 50 rows, 49 Critical, rank 1
  `LSCA2L600SG+LDMC35E144APK` (£515.78→£0). Builder `sql/REQ-26_.../build_esdt_d01.py` (read-only, LED_* env,
  reproducible) + `esdt_payload.json` snapshot. Columns 1–14 per spec + a 15th **Reason** flag (PDF §8).
  CTR=views/impr, CVR=units/views, ROAS=PPC sales/spend (`n/a` if unadvertised), Stock=UK warehouse.
- ✅ **HTML dashboard DELIVERED** — `evidence/final_outputs/REQ-26_.../REQ-26-D01_ebay_top50_sales_drop.html`
  (self-contained, light modern UI, full-screen). Renderer `sql/REQ-26_.../render_esdt_dashboard.py` reads the
  same `esdt_payload.json` as the Excel (identical data). Features: 6 live KPI tiles, search, priority filter
  chips, click-to-sort columns, colour-coded priority pills, Reason under each Action, eBay item links, CSV
  export, full-screen button. Verified live in-browser (search/filter/KPIs recompute).
- Status: draft on confirmed defaults, pending Kobiga review. Not published to ph_task, not automated, not committed.

## Sign-off
None yet. Project scaffolded 2026-08-12; awaiting discovery answers before build.
