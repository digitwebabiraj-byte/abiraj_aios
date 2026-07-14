# Validation — REQ-10_fba-returns-root-cause (D01)

**Date:** 2026-07-14 · **DB:** `order_management_copy` (read-only, Postgres MCP) · **By:** Abiraj (Claude Code executor)
**Decision:** **GREEN (technical)** — reviewer gates (Tamil Selvan / Sajeesan) + business sign-off (Satheesvaran, items A–G) **PENDING**. Published per-PH (rows 216–234).

## What was validated
The FRRC returns root-cause report: **91 returning Amazon-FBA ASINs / 105 return units**, 15 columns,
built from the validated handoff SQL (`generate_report.sql` = HANDOFF §5), reconciled to DB control
totals and cross-checked against the source tracker; rendered as an all-owners console + 19 per-PH
dashboards and published per-PH to `tech_team_outputs.ph_task`.

## Live checks this session (read-only Postgres MCP)
| # | Check | Expected | Result | Verdict |
|---|---|---|---|---|
| 1 | Dataset control totals (`frrc30.json`) | 91 ASINs / 105 return units | 91 / 105 | ✅ PASS |
| 2 | Per-row bucket arithmetic (5 buckets sum to total_returns) | 0 failures | 0 failures | ✅ PASS |
| 3 | Flag distribution | — | CRITICAL 44 · HIGH 20 · OK 9 · N/A 18 | ✅ recorded |
| 4 | Owner coverage | 19 named + 18 unassigned (N/A) | 19 + 18 | ✅ PASS |
| 5 | PH roster match vs canonical `ph_priors` roster | 19/19 exact | 19/19 (incl. `Tharsiga(nelli)`, lowercase names) | ✅ PASS |
| 6 | Live `ph_task` schema carries `assigned_user_team` | 18 cols incl. `assigned_user_team` | confirmed (col absent from sample DDL) | ✅ PASS |
| 7 | Publish integrity (MCP re-verify) | 19 rows, `ph_priors`, `released`, html present | 19/19; `version_level=5`; stored md5 == local | ✅ PASS |

## Inherited from the handoff's own validation (prior build session, live DB — `HANDOFF §6`)
- Report query **executed** via `postgres:execute_sql`, real rows returned; report population == DB
  control totals (`COUNT(DISTINCT asin)`, `SUM(qty)` on `amazon_returns` FBA in window).
- Cross-check vs source tracker (Rebecca's 2026-05-11→07-12 window): **Returns 95/101 exact**, **Units
  65/101 exact** (all misses 1–3 higher in live = post-snapshot orders) — settled the Units-Sold rule
  and the `request_date`-based returns window.
- Excel recalc (3-tab tracker): **0 formula errors**.
- Live data quirks confirmed: `fulfilment` lowercase `fba`; `order_status` American `Canceled`;
  returns SKUs = listing-variants vs sales base SKUs (⇒ ASIN anchor + `listing_data` bridge).

## Output reconciliation
- `frrc30.json`: 91 rows — **system of record**; keys per SYSTEM_REFERENCE §10.
- All-owners console `FRRC_FBA_Returns_Console_REQ-10-D01_30day.html`: embedded payload diffed against
  `frrc30.json` → **91/91 row tuples match exactly, 0 differences**.
- 19 per-PH dashboards (`per_ph/<PH>.html`): row counts reconcile to **73/91** owned ASINs (the 18
  unassigned N/A ASINs route to no holder — open item G).
- **Published** to `tech_team_outputs.ph_task` ids **216–234** (`project_code=frrc`,
  `assigned_user_team=ph_priors`, `version_status=released`); iterated V1→**V5** (UI only; identity and
  data unchanged), each a guarded md5-verified in-place UPDATE.

## Duplicate-risk
- **GREEN.** New Project ID `PRJ-2026-008` (next sequential) and new task `REQ-10_fba-returns-root-cause`
  (source's real `REQ-10-D01`, project_code `frrc`). No existing FBA-returns / root-cause asset in the
  workbench — this is the first. `project_code='frrc'` confirmed unused before publish (0 rows). No
  canonical asset overwritten; source docs imported COPY-only (Downloads originals preserved).

## Evidence
- SQL: `sql/REQ-10_.../generate_report.sql`, `reason_domain_check.sql`, `validation_checks.sql`.
- Data + outputs: `evidence/final_outputs/REQ-10_.../` (`frrc30.json`, `build_*.py`, all-owners console,
  `per_ph/` ×19 + `_manifest.json`).
- Source provenance: `evidence/source_documents/REQ-10_.../SOURCE_MANIFEST.md`.
- Import + publish evidence: `evidence/logs_or_screenshots/REQ-10_.../2026-07-14_import_checksum_evidence.md`,
  `2026-07-14_per_ph_publish_record.md`.

## Open items (Satheesvaran — do NOT decide)
A. order-status set · B. marketplace scope · C. window length/cadence · D. returns↔sales alignment ·
E. rare reason codes · **F. return-status filter (the only item that changes the numbers)** ·
G. attribute the 18 unassigned owners via `listing_data`. Reviewer gates: Tamil Selvan (queryability),
Sajeesan (technical).

## Result
**GREEN (technical).** Query correct (executed in the handoff session, integrity re-verified here),
control totals reconciled, cross-checks pass, outputs parity-exact, **no source table written**,
per-PH publish md5-verified and live (rows 216–234), committed + pushed to `main`. **Reviewer sign-off
(Tamil Selvan / Sajeesan) and business validation (Satheesvaran, A–G) are the remaining gates.**
