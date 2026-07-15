# PRJ-2026-008 — FRRC: FBA Returns Root-Cause (Rebecca)

One-screen landing page. Canonical context is `PROJECT_HOME.md`; full functional detail is
`SYSTEM_REFERENCE.md`.

**What:** a **read-only, repeatable Amazon FBA returns report** — for every FBA ASIN returned in the
window, one row with real Units Sold · Total Returns · Return Rate % · the return split across five
reason buckets (Listing Mismatch / Quality / Buyer Preference / Shipping / Unknown) · a threshold-driven
**Flag Status / Root Cause / Recommended Action** · the **Responsible Person (PH)**. Turns the hand-built
tracker `_Amazon_FBA_Returns_Tracker_-_Rebecca.xlsx` into live data.
**Task:** REQ-10_fba-returns-root-cause (req `REQ-10-D01`, project_code `frrc`). **Dev:** Abiraj.

## Run — window 2026-06-14 → 2026-07-13 · **data refreshed 2026-07-15 (D02)**
- **101** returning ASINs · **118** return units · **CRIT 50 · HIGH 24 · OK 9 · N/A 18** · 83 owned / 18 unassigned.
- **Account split (display only):** DCVoltage 49 ASINs / 61 units · LEDSone 52 / 57 — report is **not** account-filtered.
- Refreshed because the FBA returns feed back-fills: the D01 (2026-07-14) snapshot was ~12% short. Published **V6**.

### D01 original (2026-07-14)
- **91** returning Amazon FBA ASINs · **105** return units · per-row bucket sum = total_returns (0 failures).
- Flag distribution: **CRITICAL 44 · HIGH 20 · OK 9 · N/A 18** · **19** named owners + 18 unassigned.
- Reproduces the source tracker on cross-check (Returns 95/101, Units 65/101 exact; misses 1–3 higher
  in live). Excel recalc 0 errors. Validation **GREEN (self-checked)**; reviewer + business sign-off pending.
- **PUBLISHED per-PH 2026-07-14** to `tech_team_outputs.ph_task` (ids 216–234) — 19 rows, one per named
  holder, each sees only their own ASINs (`project_code=frrc`, `ph_priors`, released). 18 unassigned
  ASINs route to nobody. See `evidence/logs_or_screenshots/REQ-10_.../2026-07-14_per_ph_publish_record.md`.

## Key files
| File | What |
|---|---|
| `PROJECT_HOME.md` | Governance: purpose, scope, reviewers, status, open items A–G |
| `SYSTEM_REFERENCE.md` | Locked rules, window, reason map, thresholds, logic, data model, columns |
| `TASK_REGISTER.md` | Tasks in this project |
| `sql/REQ-10_.../generate_report.sql` | Canonical read-only report query (from HANDOFF §5) |
| `sql/REQ-10_.../reason_domain_check.sql` | Live reason-domain check — **run first** |
| `sql/REQ-10_.../validation_checks.sql` | Completeness / arithmetic / ownership / status-split checks |
| `evidence/final_outputs/REQ-10_.../frrc30.json` | Governed 91-row pull — **system of record** |
| `evidence/final_outputs/REQ-10_.../build_frrc30.py` | Builds the 3-tab threshold-driven Excel |
| `evidence/final_outputs/REQ-10_.../build_console.py` | Builds the full-screen HTML console (owner dropdown) |
| `evidence/final_outputs/REQ-10_.../FRRC_FBA_Returns_Console_REQ-10-D01_30day.html` | **Rendered console (key deliverable)** — owner dropdown, KPI tiles, per-ASIN cards; parity-exact with `frrc30.json` |
| `evidence/source_documents/REQ-10_.../HANDOFF_FRRC_REQ-10-D01.md` | **Single source of truth** (locked rules, SQL, open items) |
| `evidence/source_documents/REQ-10_.../SOURCE_MANIFEST.md` | Provenance + SHA-256 |

## Regenerate
`reason_domain_check.sql` (flag unmapped reasons) → `generate_report.sql` via Postgres MCP
(`json_agg` form, read-only) → `frrc30.json` → assert `validation_checks.sql` (91/105, 0 bucket
failures) → `python build_frrc30.py` (xlsx) + `python build_console.py` (HTML). To roll daily: swap
`DATE '2026-07-14'` for `CURRENT_DATE` in the SQL and update `WIN_START/WIN_END/RUN` in both scripts.

## Rules
Read-only DB. No writes/DDL/seed. Report is a per-run extract (no DB object). Thresholds come from the
editable Thresholds tab — never hardcoded in the SQL. Reproduce the Flag-vs-Root-Cause independence
quirk faithfully. The tracker's sample rows are illustrative — never reproduce them. Unclear rules
(A–G) go to **Satheesvaran** — do not decide silently. Not published, not committed. See root `CLAUDE.md`
+ this project's `CLAUDE.md`.
