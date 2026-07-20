# TASK_REGISTER — PRJ-2026-011_ebay-account-performance-dashboard

Canonical index of tasks in this project. One requirement = one Task ID.

## Tasks

| Task ID | Deliverable | Source ref | Status | Evidence | Validation |
|---|---|---|---|---|---|
| REQ-13_ebay-account-performance-dashboard | eBay Account Performance Dashboard — monthly account × marketplace KPIs (Sales · Advertising · Listings · Stock) over the 12 active eBay accounts × their marketplaces (22 rows), June 2026. Revenue = SUM(order_total) Completed; Conversion = whole-account (traffic_data which_channel=2); Advertising = eBay Promoted Listings ON_SITE only, shown as TACOS; New Listings from ledsone ebay_listings.created_at. **D01 DELIVERED · PUBLISHED (4 users: ids 333–336, released) · ACCEPTED — CLOSED 2026-07-20.** | `Thinesh task (1).xlsx` (target layout, dummy June figures) + Thinesh's clarifications across the day (chat-captured; logged in `2026-07-17_ebpd_questions-for-Thinesh.md`). Task ID + `project_code=ebpd` **minted with owner confirmation** — the source carries no requirement id. | **D01 DELIVERED (read-only) 2026-07-17, ACCEPTED 2026-07-20.** `ph_task` ids **333–336**. Every headline reconciled to the owner's own live-DB check (led_sone UK £28,975.37; so_926407 UK ON_SITE ad £884.07). | `evidence/final_outputs/REQ-13_.../` (HTML · Excel · build + publish scripts) + `sql/REQ-13_.../*.sql` + `validation/REQ-13_.../2026-07-20_validation.md` | Excel recalc'd 0 errors; HTML JS clean; totals tie across both formats (Rev £95,455.18, ad £7,788.75, TACOS 8.16%). Business acceptance ("all ok") 2026-07-20. Reviewer gates (Sajeesan, Tamil Selvan) not formally recorded. |

## REQ-13-D01 — deliverable detail
- **Scope:** a populated read-only dashboard, June 2026, over the 12 active eBay accounts × their
  marketplaces (**22 rows**), in two consistent formats: interactive HTML + 3-sheet Excel.
- **Method applied:** Revenue = `SUM(order_total)` Completed; rows = account × marketplace; whole-account
  conversion (`which_channel=2`); Advertising = eBay Promoted Listings **ON_SITE only** shown as
  **TACOS** + Return (attributed ACOS/ROAS omitted); New Listings from the ledsone DB; Sales Rank by revenue.
- **project_code `ebpd`** — minted with owner confirmation; verified in `ph_task`.
- **Requirement doc:** `evidence/source_documents/REQ-13_.../2026-07-17_abiraj_REQ-ebpd_REQ-13-D01.md`.
  **Skill file:** `evidence/logs_or_screenshots/REQ-13_.../2026-07-17__abiraj__ebpd__REQ-13-D01.md`.
- **Published — 4 users** to `tech_team_outputs.ph_task`, all `project_code=ebpd`,
  `assigned_user_team=ebay_priors`, `released`: **id 333 (Thinesh), 334 (Jarsini), 335 (kobiga), 336
  (powsteena)**. Guarded `temp_user` publish (pre-DELETE by task_id + plain INSERT — **no UNIQUE on
  `task_id`**; `assigned_user_team` set — it is **missing from the sample DDL**). Re-pushed on each
  correction (ids +4 each: 309→313→317→321→325→329→333).

## Corrections during the build (honest record — the defining story)
Five owner-flagged reconciliation rounds, each moving real numbers:
1. **Revenue → `SUM(order_total)`** — was `item_price*qty` (+ my template-postage, which over-stated
   postage). `order_total` is eBay's settled paid value. led_sone UK £28,975.37 then reconciled.
2. **Rows → account × marketplace** — whole-store put led_sone's cross-border (mostly German) sales into a
   "UK" row (£36k vs the verified £28,975). Per-marketplace rows fixed it.
3. **Conversion → whole-account** — `traffic_data which_channel=2` (eBay), not ad-only.
4. **New Listings → ledsone DB** — warehouse `listing_data` has no creation date; `listings.ebay_listings.created_at` does.
5. **Advertising → ON_SITE + TACOS** — attributed Ad Sales over-counted (>revenue at campaign level, all
   types); dropped ACOS/ROAS → TACOS; then filtered to ON_SITE (Priority) only. so_926407 UK £884.07 reconciled.
   Ad Sales later restored (ON_SITE-attributed stays under revenue).

## Onboarding (this session)
- Registered the project as PRJ-2026-011; authored the five standing docs; added the row to the root
  `PROJECT_REGISTER.md`.
- Imported the source mockup + the daily requirement doc + the clarification log + the end-of-day skill file;
  registered the delivered HTML + Excel + build/publish scripts; captured the canonical SQL and a validation record.
- **No source table written.** The only DB writes are the guarded publishes of the dashboard to `ph_task`
  (ids 309→…→333–336), all on owner instruction.

## REQ-13-D02 — weekly automation + viewer fixes + date-range presets (2026-07-20)
Delivered same day, after D01 acceptance, as the recurring/automated evolution of the dashboard:
- **Fully autonomous weekly pipeline** — `automation/ebpd_weekly_run.py`: dynamic last-complete-month window,
  discovers active accounts, pulls all metrics via **direct psycopg2 (no MCP)**, builds HTML, publishes to
  `ph_task`. Scheduled (Windows Task `EBPD_Weekly_Dashboard`, **Mon 09:30**, `run_ebpd_weekly.bat`).
- **New Listings wired direct** — ledsone DB (pgAdmin server "ukvm", `207.148.78.148/ledsone`, read-only).
- **Viewer render fix** — the ph_task viewer runs no JS, so all data is now **pre-rendered as static HTML**
  (`build_html_v3.build()`); fixed the earlier blank-tables symptom.
- **Publish scheme** — month-keyed `task_id` (`ebpd_<user>_ebay_account_performance_<YYYY-MM>`): refresh
  in-month, new row per month (archive).
- **Monitoring** — `ebpd_status.txt` (one plain line per run) + `check_status.bat` + Desktop failure alert
  (`ebpd_alert.ps1` → `EBPD_ALERT_FAILED.txt`, auto-clears on next success).
- **In-month date-range presets** — pure-CSS toggles (Full month / 1st half / 2nd half / Week 1–4) that work
  inside the no-JS viewer; pipeline embeds daily buckets. Active Listings & Stock stay current snapshots.
- **Security** — warehouse + ledsone passwords live only in the **git-ignored `ebpd_secrets.bat`**; no
  plaintext credentials in any tracked file.
- Live rows re-published under the month-keyed ids (latest 367–370, refreshed on each run).
- Docs: `automation/AUTOMATION_README.md`.

## One next action
**None outstanding.** D01 CLOSED/ACCEPTED; D02 automation live, scheduled, and monitored. Optional future
(only if requested): free type-any-dates picker as a browser-only JS layer; formal reviewer sign-off record.

## Rule
A new day or Claude session does **not** create a new Task ID. Keep using
`REQ-13_ebay-account-performance-dashboard` until a genuinely new requirement (with owner confirmation)
earns a new deliverable/task id.
