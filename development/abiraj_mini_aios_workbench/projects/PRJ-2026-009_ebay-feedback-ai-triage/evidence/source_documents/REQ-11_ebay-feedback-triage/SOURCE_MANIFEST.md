# SOURCE_MANIFEST — REQ-11_ebay-feedback-triage (eBay Feedback AI Triage)

Provenance record for the REQ-11 onboarding import. **COPY-only** — the originals in the user's
`Downloads` folder are preserved untouched; these registered copies are the project's canonical copies.
Imported **2026-07-15**.

## Origin
- Source location: `C:\Users\digit\Downloads\` (loose files, not a delivery archive).
- Author/session: `Thinesh task.xlsx` handed over by **Thinesh** (requester);
  `ebay_feedback_task_prompt.md` authored by the GPT brain as the execution prompt for this task.
- Import type: COPY-only registration with SHA-256 verification. No original modified.

## Imported files & SHA-256

### Spec / prompt → `evidence/source_documents/REQ-11_ebay-feedback-triage/`
| File | SHA-256 | Bytes | Role |
|---|---|---|---|
| `ebay_feedback_task_prompt.md` | `2c106aaa3de3ffcf412227644b1512624e9ed5ae338d05da4fd611d14e30567e` | 10,115 | **Single source of truth** — context block (goal, existing conventions, 20 target fields, business rules), Steps 1–9, stop-gates, sprint delivery order, drift guardrails |
| `Thinesh task.xlsx` | `3ef2be1df0dd960a83624a19a1832584f6435c24c06410274e53ea8ee41fdea0` | 52,912 | Requester's spec sheet — single tab `ebay Feedback`: 20-column target shape, **6 illustrative (mock) sample rows**, and the 18-row *Developer Business Rules* block |

## Contents of `Thinesh task.xlsx` (single tab: `ebay Feedback`)
- **Rows 1–7** — header + **6 sample rows**. ⚠ **Mock data**: SKUs `SKU-1001`–`SKU-1005`, parents
  `PARENT-100`–`PARENT-104`. Accounts seen: Huttenlampen, ELECTRICALSONE, SUNSONE, Coventry.
  **Illustrative only — never reproduce as an answer, never validate the build against them.**
- **Rows 10–27** — *Developer Business Rules*, an 18-row Condition → System Logic block: the 5 category
  routings, the Negative/Neutral overrides, the repeat-SKU escalation ladder (≥3 / ≥5 / ≥10), the
  health-score risk rule (<70), the confidence gate (>90%), and the 4 required analyses (Listing SKU,
  Parent SKU, Monthly Trend, Top 10 Worst SKU).
- Sheet declares 999 × 26 but only rows 1–27 / columns A–T carry data.

## Duplicate-risk check (Existing-Asset-First rule)
- `C:\Users\digit\Downloads\Untitled spreadsheet (3).xlsx` — **content-identical** to `Thinesh task.xlsx`:
  same single tab `ebay Feedback`, same 25 populated rows, byte-identical size (52,912). Its SHA-256
  differs (`cf75d91f92f042fc710014306c9b41c8679f5289b35542643f79ae49206662f6`) — a re-export of the same
  Google Sheet, differing in package metadata only.
  **NOT imported.** `Thinesh task.xlsx` is canonical. (Same pattern as `Untitled spreadsheet (2).xlsx`
  ↔ `Nivarnan task.xlsx` in Downloads.)
- `~$Thinesh task.xlsx` (165 bytes) is an Excel lock file, not content. Not imported.
- No existing workbench project covers eBay feedback triage — checked PRJ-2026-001 → PRJ-2026-008.
  PRJ-2026-009 is unique. **No duplicate project risk.**

## Referenced by the sources but NOT in this import (to be verified live, never assumed)
- **DB objects named by the prompt's context block:** `message.ebay_msg`, `message.amz_msg`,
  `message.shopify_msg`, `message.msg_tag_etl`, `message.message_app_logs`.
- **DB objects named by Step 2 for inspection:** `order_transaction`, `listing_data_1`, `inv_final_stock`.
- **Objects the prompt asks to CREATE** (none exist yet; **all blocked on written approval** — see the
  project `CLAUDE.md` *DDL Gate*): `message.ebay_feedback`, `message.ebay_feedback_ai`,
  `message.feedback_routing`, `message.ebay_feedback_enriched`.
- **External API:** eBay `GetFeedback` — returns FeedbackID, CommentType, CommentText, CommentTime,
  ItemID, TransactionID, OrderLineItemID, CommentingUser. Returns **no SKU / Parent SKU**.
- Platform `project_knowledge` table/skill references (`TABLE_order_transaction.md`, etc.) live in the
  Claude project knowledge, not here.

## Derived assets (created during onboarding, not in the source files)
- `PROJECT_HOME.md`, `SYSTEM_REFERENCE.md`, `CLAUDE.md`, `TASK_REGISTER.md`, `README.md` — the five
  standing project docs, authored from these two sources.
- `evidence/logs_or_screenshots/REQ-11_.../2026-07-15_import_checksum_evidence.md` — import evidence.
- **No SQL, no dataset, no output** — nothing has been built or pulled.

## Verification
- Both files copied byte-for-byte; SHA-256 recomputed post-copy and matched the origin exactly
  (see `2026-07-15_import_checksum_evidence.md`).
- Origin files re-hashed after the copy and confirmed unchanged.
- Spreadsheet parsed at import (`openpyxl`, `data_only=True`): 1 sheet, 25 populated rows, 20 declared
  columns — reconciles with the manifest above.
- **Data-quality flags raised at import** (recorded in `SYSTEM_REFERENCE.md` §13, open items G/H):
  (i) all sample SKUs/parents are placeholders — **mock data**;
  (ii) the `Date` column **mixes formats** — text `29/05/2026` (dd/mm) alongside Excel datetimes
  `2026-03-06 00:00:00` and `2026-08-06 00:00:00`, the latter **three weeks after** the 2026-07-15
  handoff date, so at least one value was parsed dd/mm as mm/dd. **Dates must come from the eBay API's
  `CommentTime`, never from this sheet.**
