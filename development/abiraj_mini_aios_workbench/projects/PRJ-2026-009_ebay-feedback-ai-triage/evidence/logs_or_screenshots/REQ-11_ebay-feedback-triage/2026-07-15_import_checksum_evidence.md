# Import & Integrity Evidence — REQ-11_ebay-feedback-triage

**Date:** 2026-07-15 · **Task:** REQ-11_ebay-feedback-triage · **Project:** PRJ-2026-009_ebay-feedback-ai-triage
**Action:** COPY-only import of the 2 source files + onboarding integrity checks. **No DB accessed.**

## 1. Import method
- `cp -n` (no-clobber) from `C:\Users\digit\Downloads\` into
  `evidence/source_documents/REQ-11_ebay-feedback-triage/`.
- Originals left in place and re-hashed afterwards to prove they were not modified.

## 2. SHA-256 verification — origin vs registered copy

| File | Origin SHA-256 | Registered copy SHA-256 | Match |
|---|---|---|---|
| `ebay_feedback_task_prompt.md` | `2c106aaa3de3ffcf412227644b1512624e9ed5ae338d05da4fd611d14e30567e` | `2c106aaa3de3ffcf412227644b1512624e9ed5ae338d05da4fd611d14e30567e` | ✅ |
| `Thinesh task.xlsx` | `3ef2be1df0dd960a83624a19a1832584f6435c24c06410274e53ea8ee41fdea0` | `3ef2be1df0dd960a83624a19a1832584f6435c24c06410274e53ea8ee41fdea0` | ✅ |

**2/2 exact.** Originals re-hashed post-copy → unchanged. ✅

## 3. Spreadsheet integrity check
Parsed with `openpyxl` (`data_only=True`) at import:
- Sheets: **1** (`ebay Feedback`). Declared extent 999 × 26; **populated: 25 rows**, columns A–T.
- Rows 1–7: header + **6 sample rows**. Rows 10–27: *Developer Business Rules* (18 Condition → System Logic pairs).
- Reconciles with `SOURCE_MANIFEST.md`. ✅

## 4. Duplicate-risk check (Existing-Asset-First rule)
- **`Untitled spreadsheet (3).xlsx`** (Downloads, 52,912 bytes — identical size to `Thinesh task.xlsx`)
  was flagged and content-compared cell-by-cell:
  - sheet names equal: **True** (`['ebay Feedback']` both)
  - populated rows equal: **True** (25 = 25, zero differing rows)
  - SHA-256 differs (`cf75d91f…`) → package metadata only; a re-export of the same Google Sheet.
  - **Resolution:** NOT imported. `Thinesh task.xlsx` is canonical. No duplicate asset created. ✅
- `~$Thinesh task.xlsx` (165 bytes) — Excel lock file, not content. Not imported. ✅
- Checked PRJ-2026-001 → PRJ-2026-008: **no existing project covers eBay feedback triage.** PRJ-2026-009
  is unique; no project-level duplicate risk. ✅

## 5. Data-quality flags raised at import
Recorded in `SYSTEM_REFERENCE.md` §13 and as open items **G** / **H**:

- **G — Sample data is mock.** All 6 rows use placeholder identifiers (`SKU-1001`–`SKU-1005`,
  `PARENT-100`–`PARENT-104`). **Illustrative only** — never reproduce as an answer, never validate the
  build against them (FRRC/REQ-10 precedent).
- **H — Mixed & ambiguous date formats.** The `Date` column mixes:
  - text `29/05/2026`, `25/05/2026`, `21/06/2026` (dd/mm), with
  - Excel datetimes `2026-03-06 00:00:00` and `2026-08-06 00:00:00`.

  `2026-08-06` falls **three weeks after** the 2026-07-15 handoff, so at least one source value was
  parsed dd/mm as mm/dd (`06/08/2026` → Aug 6). The column is not trustworthy for any date logic.
  **Take dates from the eBay API's `CommentTime`, never from this sheet.**

## 6. Scope assertion for this session
- **No database connection opened. No SQL executed. No DDL. No sync job. No LLM call. No publish.**
- No file outside `projects/PRJ-2026-009_ebay-feedback-ai-triage/` modified, except the single new row
  added to the root `PROJECT_REGISTER.md` (required by the register's own indexing rule).
- No commit, no push.

## 7. Result
**Import GREEN.** 2/2 files registered and checksum-verified, originals intact, 1 duplicate correctly
excluded, spreadsheet integrity reconciled, 2 data-quality flags raised.

**Task status: ONBOARDING — BLOCKED** at the Step-1 decision-sheet gate (items A–F, owner: Thinesh) and
the DDL gate (item I, owner: Abiraj/Varmen). Nothing built — by design, not by omission.
