# TASK_REGISTER — PRJ-2026-006_zero-sales-full-optimization

Canonical index of tasks in this project. One requirement = one Task ID.

## Tasks

| Task ID | Deliverable | Source ref | Status | Evidence | Validation |
|---|---|---|---|---|---|
| REQ-08_zero-sales-full-optimization | **D01** — ZSFO weekly report (SQL + xlsx + HTML dashboard + verification pack) for window 2026-06-10 → 2026-07-09 | `utharsika task.xlsx` `REQ-08-D01` (`PH-2026-07-UTHAR04`) | **COMPLETE (technical) — VALIDATION GREEN; BUSINESS SIGN-OFF PENDING** | `evidence/final_outputs/REQ-08_zero-sales-full-optimization/` | `validation/REQ-08_zero-sales-full-optimization/2026-07-10_validation.md` |
| REQ-08_zero-sales-full-optimization | **D02** — AMZ_2026 cross-checked "corrected" report (1,065 zero in both postgres + Amazon; 189 "Removed") | `2026-07-10_REVISED_PROJECT_CONTEXT_amz-crosscheck.md` (revised handoff) | **ONBOARDED — VALIDATION AMBER (handoff diagnosis refuted; definition decision open)** | `evidence/final_outputs/REQ-08_.../D02_amz_crosscheck/` | `validation/REQ-08_.../2026-07-10_D02_amz_crosscheck_validation.md` |

## D01 — Deliverable detail
- **Query:** `sql/REQ-08_.../generate_dataset.sql` — vendor OVERLAP, NULL-channel bridge,
  parameterised run_date, + lifetime recency + 5 week-buckets + root-cause hint.
- **Data:** `evidence/final_outputs/REQ-08_.../data.json` — 1,250 rows + run metadata.
- **Outputs:** `ZSFO_Zero_Sales_Full_Optimization_Utharsika.xlsx` (via `build_report.py`),
  `ZSFO_Utharsika_dashboard.html` (via `build_html.py`).
- **Verification:** `ZSFO_VERIFICATION_PACK.md` — 6/6 PASS (Utharsika population, live 2026-07-10).
- **Reconciliation:** 1,719 → 1,250; sold 469; vendor in-window 34; max in-window units in report 0/0.

## D02 — Deliverable detail
- **Trigger:** revised handoff cross-checking D01 against Amazon's `AMZ_2026` "Ordered Product Sales".
- **Planner output (imported):** `ZSFO_Utharsika_report_CORRECTED.xlsx` (1,065 confirmed-zero +
  189 "Removed"), `ZSFO_Utharsika_dashboard_CORRECTED.html`.
- **Independent verification:** exclude-if-AMZ-Jun/Jul-items>0 → **191 removed → 1,059** (planner
  1,065 ≈ within 6). Reproducible list: `removed_191_amz_reconciliation.csv` (£5,101.24 / 1,660 items).
- **Key correction (see validation):** the handoff's "vendor (1P) data gap → re-sync `vendor_sales`"
  is **refuted** — 0/191 are vendor; **87% are seller sibling-ASIN sales already in our DB**
  (per-ASIN vs per-product attribution / listing sprawl). `vendor_sales` is NOT missing for 2026.
- **NOT done (out of scope):** DB re-sync of `vendor_sales`/`order_transaction` (read-only project;
  also unwarranted by the evidence).

## Open / next
- **Definition decision (owner / Satheesvaran):** per-ASIN "dead listings" (keep 1,250, flag
  siblings) vs per-product "dead SKUs" (exclude ~191). Confirm with the **correct mechanism**
  (sibling-ASIN), not the vendor-gap premise. **OPEN — blocks D02 sign-off.**
- **Exclusion rule** (AMZ items>0 vs £>0) swings the count ~120 ASINs (1,059 / 1,112 / 1,176). **OPEN.**
- **`AMZ_2026` June £0/positive-items data-quality anomaly** — needs source explanation.
- **Business sign-off (Satheesvaran)** — `order_status` set + universe definition (carried from D01). **OPEN.**
- **REQ-08-D03 (separable, not opened):** schedule the Monday run with a dynamic `CURRENT_DATE`
  window. Needs owner confirmation.

## Rule
A new day or Claude session does **not** create a new Task ID. Keep using
`REQ-08_zero-sales-full-optimization` until D01 is formally closed; only a genuinely new requirement
(with owner confirmation) gets a new deliverable/task id.

---

## 2026-07-24 — AUTOMATED (REQ-08 automation complete)

`ZSFO_Weekly_ZeroSales` registered on the permanent path — **Mondays 08:00**, first run
**2026-07-27**. `automation/zsfo_weekly_run.py` + `run_zsfo_weekly.bat` + `zsfo_alert.ps1` +
`AUTOMATION_README.md`; task XML backed up in `05_documentation/capability/scheduled_tasks/`.

Closes the "scheduling not wired — window set in SQL" gap: the runner computes run_date + the 5
weekly buckets from CURRENT_DATE and substitutes the canonical SQL's literals (guard aborts if any
reference literal survives). Reuses the signed-off `build_html.py` via env-var path overrides (no
duplication). Weekly REPLACE in place (task_id `…-V1`), backup-first, md5-verified.

Proven 2026-07-24: `--date 2026-07-10` reproduced the deliverable EXACTLY (1,250 zero-sale rows;
universe 1,720 vs 1,719 = +1 live-drift, a drift check not equality). Fresh window (24 Jun–23 Jul)
= 1,289 zero-sale. Task-Scheduler temp dry-run `LastTaskResult=0`, credentials resolved at launch;
temp task deleted. Nothing published — first real publish is the scheduled 2026-07-27 run.

**Note:** the owner authorised proceeding without waiting on Satheewaran's edge-case sign-off
(2026-07-24). The core report was already delivered + validated; the open items were edge-case
rules, flagged but not blocking per owner direction.

---

## 2026-07-24 — cadence changed to MONTHLY (owner decision)

Owner chose MONTHLY over the spec's weekly. Task re-registered `ZSFO_Monthly_ZeroSales`, **day 4,
08:00**, first run **2026-08-04 at 09:00** (clear of ESNM d2 / SEG d3 / ERA d5 / FRRC d8). No code change —
the runner is cadence-agnostic (run_date = today, window = last completed 30 days); only the trigger
changed. The 30-day rolling window is unchanged, so each monthly run still qualifies a product as
zero-sale on 30 days of data, just checked once a month instead of weekly. Old weekly task + its XML
removed; monthly XML exported to `05_documentation/capability/scheduled_tasks/`.
