# SOURCE_MANIFEST — REQ-14_ebay-return-analysis (eBay Return Analysis Dashboard)

Provenance record for the onboarding import. **COPY-only** — the originals in the user's
Downloads (`files (6).zip` + `Thinesh task (2).xlsx`) are preserved untouched; these registered
copies are the project's canonical copies. Imported **2026-07-20**.

## Origin
- Delivery archive: `C:\Users\digit\Downloads\files (6).zip` (5 files) — produced in a prior
  Claude chat session that authored the SQL, the build script and a **reference** June-2026 build.
- Requester mockup: `C:\Users\digit\Downloads\Thinesh task (2).xlsx` — the target dashboard layout
  with illustrative (dummy) figures.
- Import type: COPY-only registration with SHA-256 verification. No original modified.

## Imported files & SHA-256

### Spec / handoff → `evidence/source_documents/REQ-14_ebay-return-analysis/`
| File | SHA-256 | Role |
|---|---|---|
| `CLAUDE_CODE_HANDOFF.md` | `489afa0dd93dda4e644ca422eb65ce308159d43b435ea94c16ac1d31a479ffa4` | **Execution brief / RUNBOOK** — self-contained: package, environment, task parameters, runbook, acceptance criteria, intentional blanks, pitfalls, re-run steps |
| `eBay_Return_Analysis_HANDOFF.md` | `c6ba23bc01f10d03dc1c5c5e95dcd1377252f63a71f262c53d393c269a5ac6db` | **Long-form column/derivation reference** — scope, 19-column derivation table, the CPC+CPS advertising gotcha, assumptions & caveats, re-run, pitfalls |
| `Thinesh task (2).xlsx` | `e7005bad2df802e5afd74fa5af8e7ea30070cef919acbe23b5c2aeeca89d7712` | **Requester's mockup** — target 19-column layout + Return-Reason Breakdown + Filter Options + Before/After efficiency block (dummy figures; never the answer) |

### Query → `sql/REQ-14_ebay-return-analysis/`
| File | SHA-256 | Role |
|---|---|---|
| `ebay_return_analysis.sql` | `1f7d1222fa6b298588e24dc3529434730cfe4fe3fd55606ed3d74fd1f1b97e8a` | **Source of truth for the data.** Statement 1 = the 19-column per-SKU dataset; statement 2 = the Return-Reason breakdown. Six editable dates at the top drive the reporting/comparison windows. |

### Reproduction assets → `evidence/final_outputs/REQ-14_ebay-return-analysis/`
| File | SHA-256 | Role |
|---|---|---|
| `build_dashboard.py` | `5874fb237083592ee896d9b3a6f45f3f2f06c2f682772088fa26ab74b3fb62fd` | Formats the two TSV query outputs into the styled workbook. **Formatting only; no data logic / no remap.** Needs `openpyxl`; recalc with LibreOffice after write. |
| `eBay_Return_Analysis_June2026.xlsx` | `764802969bc5f6cf814bdbe6381375af87bd4b19ebf95c2894a1f1d9f5e338a9` | **Reference output** produced in the prior chat session (June 2026). Diff target for a fresh live build. **NOT yet reproduced against the live Ledsone DB from this workbench** — see status. |

## Referenced by the handoff but external to this package
- Live **Ledsone PostgreSQL** (normalised domain schemas `customer_service`, `order_management`,
  `listings`, `inventory`, `ebay_campaigns`, `accounting`), reached via the **Ledsone Database MCP**
  (`execute_sql` / `search_objects`). This is the data source for a live build — read-only.
- The `public.*` denormalised layer belongs to a **different** DB and returns nothing here — do not use.

## Verification
- All 6 files copied byte-for-byte; SHA-256 recomputed post-copy and matches the source archive exactly
  (5 zip files verified against the extraction hashes; the Thinesh mockup hashed at import).
- **Reference dataset (from the reference xlsx, June 2026):** 144 SKU rows · 153 returns · blended
  return rate 17.7% (0.17729) · Refund £2,937.37 · Return Cost £869.39 · Ad Spend £1,387.96 ·
  Ad Sales £9,343.63 · ACOS 14.9% (0.14855) · ROAS 6.73x. Reason breakdown sums to 153. These are the
  handoff's stated acceptance numbers — re-verified by reading the reference workbook at import.
- Real account names present in the reference data: Sunsone, Ledsone, Electricalsone, Ledsone DE,
  Vintage Interior, Retroled (UK + DE marketplaces).
