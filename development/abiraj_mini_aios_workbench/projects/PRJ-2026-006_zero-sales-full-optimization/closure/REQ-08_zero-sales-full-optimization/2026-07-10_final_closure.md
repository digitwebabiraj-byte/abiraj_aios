# Closure Record — REQ-08-D01 ZSFO (2026-07-10)

**Project:** PRJ-2026-006_zero-sales-full-optimization · **Task:** REQ-08_zero-sales-full-optimization
**Deliverable:** D01 — ZSFO weekly report, Utharsika, Amazon UK, window 2026-06-10 → 2026-07-09.

## What was delivered
1. **Corrected canonical query** `generate_dataset.sql` — applied the two open-TODO fixes:
   - vendor **OVERLAP** logic (replacing `start_time`-only);
   - **NULL-channel** `listing_data` bridge for Utharsika;
   - plus parameterised `run_date`, **Last Vendor / Last Amazon Sale (lifetime)** + **Vendor Units
     (lifetime)** columns, week-by-week impressions/clicks (5 buckets) and a derived **Root-cause hint**.
2. **Governed pull** `data.json` — 1,250 rows + run metadata.
3. **Deliverables** — `ZSFO_Zero_Sales_Full_Optimization_Utharsika.xlsx` (template-matching) and
   `ZSFO_Utharsika_dashboard.html` (interactive: KPIs, sparklines, root-cause filters, last-sale
   columns). Both built from `data.json`; both carry 1,250 rows.
4. **Corrected verification pack** — rewritten from the full-catalogue draft to the real Utharsika
   population + OVERLAP + NULL-channel trace; re-run live **6/6 PASS**.
5. **Full workbench onboarding** — README, PROJECT_HOME, SYSTEM_REFERENCE, CLAUDE, TASK_REGISTER,
   validation + this closure; registered as PRJ-2026-006 in `PROJECT_REGISTER.md`.

## Open-TODO disposition (from PROJECT_CONTEXT.md §8)
| # | TODO | Disposition |
|---|---|---|
| 1 | Apply vendor-overlap fix | **DONE** — in `generate_dataset.sql`; 0 row-count impact on Utharsika, retained as correct rule. |
| 2 | Add "Last vendor sale date" | **DONE** — plus Last Amazon Sale + Vendor Units (lifetime), in xlsx + dashboard. |
| 3 | Parameterise run_date + schedule | **PARTIAL** — run_date + week ranges parameterised in SQL with instructions; actual scheduling deferred to REQ-08-D02 (needs owner confirmation). |
| 4 | Confirm rules with Satheesvaran | **OPEN** — carried as the one next action (business sign-off). |
| 5 | Decide HTML vs xlsx | **RESOLVED — both produced** (mirrors T7); no decision needed. |

## Defects found & fixed while finishing
- Verification pack validated the **wrong population** (full catalogue 30,782→28,318, not the 1,719→
  1,250 deliverable). **Fixed** — rewritten to the Utharsika population; original preserved as
  `…_full-catalogue_superseded.md`.
- Pack's Check 6 stock trace filtered `which_channel=1` on `listing_data` — returns **0** for
  Utharsika (NULL channel), contradicting its own "Expected 765". **Fixed** — NULL-channel bridge.

## Reconciliation (live 2026-07-10)
1,719 universe → 1,250 zero-sale · sold FBA/FBM 469 · vendor in-window 34 (all inside the 469) ·
0 vendor-only false exclusions · max in-window units in report 0/0 · top-ASIN trace 221027/2427/765/39.
Verification pack 6/6 PASS.

## Governance
- **Read-only** DB throughout; no `INSERT`/`UPDATE`/`DELETE`, no DDL, no view created.
- No data invented; all figures trace to `schema.table.column` or an explicit derivation.
- Downloads originals preserved; project copies under `evidence/`.
- **Not committed/pushed** — awaiting explicit instruction.

## Status & next action
**GREEN (technical) — CLOSED pending BUSINESS VALIDATION.**
**One next action:** hand the dashboard + verification pack to **Satheesvaran** for edge-case
sign-off (`order_status` set + universe definition). On PASS → mark REQ-08-D01 business-validated
and (optionally) open REQ-08-D02 for the scheduled Monday run.
