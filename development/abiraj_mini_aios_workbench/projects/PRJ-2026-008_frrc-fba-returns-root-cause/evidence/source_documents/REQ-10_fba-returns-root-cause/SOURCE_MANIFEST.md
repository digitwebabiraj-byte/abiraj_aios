# SOURCE_MANIFEST — REQ-10_fba-returns-root-cause (FRRC)

Provenance record for the FRRC onboarding import. **COPY-only** — the originals in the user's
Downloads bundle (`files (5).zip`) are preserved untouched; these registered copies are the
project's canonical copies. Imported **2026-07-14**.

## Origin
- Delivery archive: `C:\Users\digit\Downloads\files (5).zip` (6 files).
- Author/session: the prior build session that produced and validated REQ-10-D01 on the live DB.
- Import type: COPY-only registration with SHA-256 verification. No original modified.

## Imported files & SHA-256

### Spec / handoff → `evidence/source_documents/REQ-10_fba-returns-root-cause/`
| File | SHA-256 | Role |
|---|---|---|
| `HANDOFF_FRRC_REQ-10-D01.md` | `a48b6af8473f8b38453dfad7ce90a042619f6dbc8e96238a51ab86b9483ed486` | **Single source of truth** — locked rules (§4), final SQL (§5), validation (§6), regen steps (§8), open items (§9) |
| `2026-07-14_abiraj_REQ-frrc_REQ-10-D01.md` | `adaba09886a30e6cb1da64e90a1fde1371f3d8b9e7ffef70ef8c90b55570e2e4` | Full daily requirement / spec document (metadata, business logic, data enrichment) |
| `FRRC_REQ-10-D01_execution_prompt.md` | `aae4ab0c42f9f897f7a31624709c3a99ab07b98272aafe8d79bd80ed4fb978b5` | Self-contained execution prompt (Steps 0–10, method, thresholds, stop conditions) |

### Reproduction assets → `evidence/final_outputs/REQ-10_fba-returns-root-cause/`
| File | SHA-256 | Role |
|---|---|---|
| `frrc30.json` | `2cbfe13d0a5e6451498150d05eaab0cf94c2dfb1b0be85658b672edc2f35cbca` | **Governed dataset (system of record)** — 91 rows, executed & validated (30-day window 2026-06-14→2026-07-13) |
| `build_frrc30.py` | `b50ac6968d9eb6db21175c3ef392654e3c06c843423ba0045d8581ea3da9c541` | Builds the 3-tab threshold-driven Excel from `frrc30.json` (needs `openpyxl`) |
| `build_console.py` | `e13adc841c223b2247a58e991cd08fb6452b05c06458d17321a7c4f1e04bad0f` | Builds the full-screen HTML console (owner dropdown) from `frrc30.json` |
| `FRRC_FBA_Returns_Console_REQ-10-D01_30day.html` | md5 `fb00ff20fff5f13af1582a61fb72ae8f` (35,625 bytes) | **Rendered console output** — the actual `build_console.py` result, added 2026-07-14; data parity with `frrc30.json` verified exact (91 rows / 105 returns / all tuples match) |

## Derived assets — REQ-10-D02 (2026-07-15)
- `evidence/final_outputs/REQ-10_.../frrc_refresh_2026-07-15.json` — **refreshed dataset**, same window (2026-06-14→2026-07-13) re-run live on 2026-07-15 under unchanged D01 rules, **+ `account`** (LEDSone/DCVoltage) and `n_accounts` guard. 101 ASINs / 118 units. This supersedes `frrc30.json` **as the render input only** — `frrc30.json` remains the D01 system-of-record and is **unmodified** (SHA-256 above still valid).
- `sql/REQ-10_.../generate_report_with_account.sql` — the canonical query + account enrichment used for that pull.
- `evidence/final_outputs/REQ-10_.../per_ph/` — 19 per-PH dashboards (V6) + `_manifest.json`, rebuilt from the refreshed dataset by `build_per_ph.py`.

## Derived assets (created during onboarding, not in the zip)
- `sql/REQ-10_.../generate_report.sql` — the canonical query, extracted verbatim from HANDOFF §5 (with a `CURRENT_DATE` roll note).
- `sql/REQ-10_.../reason_domain_check.sql` — the Step-1 live reason-domain check.
- `sql/REQ-10_.../validation_checks.sql` — the control-total / arithmetic / ownership / status-split checks.

## Referenced by the handoff but NOT in this import package (kept in the platform project knowledge)
- `_Amazon_FBA_Returns_Tracker_-_Rebecca.xlsx` — the source spec workbook (Objective & Guide / Thresholds / Tracker tabs). **The ground-truth spec + editable Thresholds live here.**
- `project_knowledge/`: `SKILL_multi_table.md`, `SKILL_ppc_stock_lookup.md`, `SKILL_single_table.md`, `TABLE_amazon_returns.md`, `TABLE_order_transaction.md`, `TABLE_listing_data_1.md`.
- The prior-session **rendered outputs**: `FRRC_FBA_Returns_Tracker_REQ-10-D01_30day.xlsx` and `FRRC_FBA_Returns_Report_REQ-10-D01_30day.html` (simpler grouped HTML) — still to import; regenerable from `frrc30.json`. **`FRRC_FBA_Returns_Console_REQ-10-D01_30day.html` is now imported** (see the final_outputs table above).

## Verification
- All 6 imported files copied byte-for-byte; SHA-256 recomputed post-copy (see `2026-07-14_import_checksum_evidence.md`).
- Dataset integrity re-checked independently at import: 91 ASIN rows · 105 return units · bucket-sum = total_returns on every row (0 mismatches) · flag distribution CRITICAL 44 / HIGH 20 / OK 9 / N/A 18 · 19 named owners + 18 unassigned (no in-window FBA-UK sale).
