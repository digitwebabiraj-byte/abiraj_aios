# PRJ-2026-006 — ZSFO (Zero Sales Full Optimization)

One-screen landing page. Canonical context is `PROJECT_HOME.md`; full functional detail is
`SYSTEM_REFERENCE.md`.

**What:** weekly (Monday) list of **Utharsika's Amazon-UK ASINs with 0 units sold in the last
completed 30 days** (FBA+FBM **and** Vendor), plus stock + traffic diagnostics to explain why.
**Task:** REQ-08_zero-sales-full-optimization (`PH-2026-07-UTHAR04`, req `REQ-08-D01`). **Dev:** Abiraj.

## Run 2026-07-10 (window 2026-06-10 → 2026-07-09)
- **1,719** UK ASINs → **1,250 zero-sale** · sold 469 · vendor in-window 34.
- Root cause: 680 impr-no-click · 323 click-no-sale · **214 out of stock** · 33 zero-impr.
- Verification pack: **6/6 PASS**. Validation: **GREEN (technical)** — business sign-off pending.

## Key files
| File | What |
|---|---|
| `PROJECT_HOME.md` | Governance: purpose, scope, reviewers, status |
| `SYSTEM_REFERENCE.md` | Locked rules, data model, logic, columns |
| `TASK_REGISTER.md` | Tasks in this project |
| `sql/REQ-08_.../generate_dataset.sql` | Canonical read-only rebuild query |
| `evidence/final_outputs/REQ-08_.../ZSFO_Utharsika_dashboard.html` | Interactive dashboard (key deliverable) |
| `evidence/final_outputs/REQ-08_.../ZSFO_Zero_Sales_Full_Optimization_Utharsika.xlsx` | Template-matching spreadsheet |
| `evidence/final_outputs/REQ-08_.../ZSFO_VERIFICATION_PACK.md` | Independent 6-check pack (Utharsika population) |
| `evidence/final_outputs/REQ-08_.../data.json` | Governed 1,250-row pull + metadata |
| `validation/REQ-08_.../2026-07-10_validation.md` | Live reconciliation evidence |
| `closure/REQ-08_.../2026-07-10_final_closure.md` | Closure record |

## Regenerate
`generate_dataset.sql` (set run_date + week ranges) → run via Postgres MCP → `data.json` →
`python build_report.py` + `python build_html.py` → re-run the verification pack (require 6/6).

## Rules
Read-only DB. No writes/DDL. No invented data. Do not commit/push without instruction. See root
`CLAUDE.md` + this project's `CLAUDE.md`.
