# SOURCE_MANIFEST — REQ-12_ebay-price-checker (eBay Price Checker)

Provenance record for the REQ-12 onboarding import. **COPY-only** — the originals in the user's
`Downloads` folder are preserved untouched; these registered copies are the project's canonical copies.
Imported **2026-07-16**.

## Origin
- Source location: `C:\Users\digit\Downloads\` (loose file).
- Author/session: `Ebay System Task -Thinesh.xlsx` handed over by **Thinesh** (requester). The **CONFIRMED
  BUSINESS RULE** and **Q1–Q8 decisions** arrived as **chat text** (no file), and were captured verbatim
  into this folder — they are the most fragile inputs and are now the canonical record.
- Import type: COPY-only registration with SHA-256 verification. No original modified.

## Imported files & SHA-256

### Spec → `evidence/source_documents/REQ-12_ebay-price-checker/`
| File | SHA-256 | Bytes | Role |
|---|---|---|---|
| `Ebay System Task -Thinesh.xlsx` | `0cbfd8f32ee7a3a7ff1f9f6d8b3bf20fbccab3ad1bebbd3423cadc56818ce353` | 54,301 | Requester's spec sheet — single tab `Price checker `: **13-column target shape**, a rules legend (rows 18–27), and **7 illustrative (mock) sample rows**. ⚠ Its `Target eBay Price` and `Status` columns are **superseded by the confirmed rule and are known-wrong** |
| `2026-07-16_CONFIRMED_BUSINESS_RULE_target_ebay_price.md` | *(authored at onboarding)* | — | The owner's authoritative target-price rule, verbatim. **Supersedes the spreadsheet.** Arrived as chat text |
| `2026-07-16_thinesh_decisions_Q1-Q8.md` | *(authored at onboarding)* | — | Thinesh's answers to the decision sheet's Q1–Q8 + the 13 account labels. Arrived as chat text |

## Contents of `Ebay System Task -Thinesh.xlsx` (single tab: `Price checker `)
- **Rows 1–8** — header (13 columns) + **7 mock sample rows**. SKUs `LED001`–`LED007`, images
  `image1.jpg`–`image7.jpg`, accounts `LEDSONE UK`, `LEDSONE UK REG DE`, `SUNSONE UK`, `ELECTRICALSONE`,
  `HOMIN`, `LEDSONE DE`, `SUNSONE DE`. **The four cells that look computed contain typed constants
  (`=+0.21`, `=+1.91%`) — the sheet does not recalculate.** `A6` = `265660307012)` (stray bracket, text).
  **Illustrative only — never reproduce as an answer, never validate the build against them.**
- **Rows 18–27** — legend: column dictionary, status rules, tolerance band table, Low/High Price alerts.
  ⚠ **The tolerance threshold is stated twice, contradictorily**: `£15` (legend A24) vs `£20` (band table
  E25:G27). Resolved to **£20** by Thinesh (Q4).
- Sheet declares 991 × 27 but only rows 1–27 carry data.

## Duplicate-risk check (Existing-Asset-First rule)
- `C:\Users\digit\Downloads\Ebay System Task -Thinesh (1).xlsx` — **content-identical** to the canonical
  file (same 54,301 bytes, same 7 rows), different SHA-256
  (`e4370e8b1cbff072ff999993d8001e986e30225dc0f1a854347ea8d046c21b9b`) — a re-export differing in package
  metadata only. **NOT imported** (same pattern as ebft's `Untitled spreadsheet (3).xlsx`).
- **No existing workbench project covers eBay price checking** — checked PRJ-2026-001 → PRJ-2026-009.
  PRJ-2026-010 is unique. No duplicate project risk.
- **No existing price-checker asset in the database** — swept both `ledsone` and `order_management_copy`
  by table + column; the only pricing estate is `staging_ai.pricing_safe_*` on `order_management_copy`,
  a 21-SKU / 63-row pilot, **not** a price checker (see the source-audit log).

## Referenced by the sources but NOT in this import (verified live, never assumed)
- **The confirmed rule names its sources only as "the approved Amazon/website PostgreSQL source"** — no
  object. Identified live (source audit) on the **`ledsone`** DB: `listings.amazon_listings`,
  `listings.shopify_listings`, `listings.ebay_listings`; SKU-normalisation via `inventory.products`
  (ENC → `sku_original`) and `inventory.product_pk` (pack quantities).
- **AIOS knowledge base rules** applied (`Ledsone-aios-mcp` — `docs.ledsone.co.uk`):
  `business/rules/cross-platform-pricing-markup.md`, `business/rules/sku-format-rules.md`,
  `business/rules/ebay-listing-sku-filter.md`.

## Derived assets (created during onboarding / delivery, not in the source files)
- The five standing project docs (README, PROJECT_HOME, SYSTEM_REFERENCE, CLAUDE, TASK_REGISTER).
- `evidence/final_outputs/REQ-12_.../` — the UI xlsx, the dashboard HTML, the decision sheet, and the
  three canonical build/publish scripts.
- `sql/REQ-12_.../` — the canonical extraction query + the source-audit queries.
- `evidence/logs_or_screenshots/REQ-12_.../` — import evidence, the source audit + AIOS-rules correction,
  the D01 delivery + publish record.

## Verification
- The source file copied byte-for-byte; SHA-256 recomputed post-copy and matched the origin exactly
  (`0cbfd8f3…`). Origin re-hashed after the copy and confirmed unchanged. See
  `evidence/logs_or_screenshots/REQ-12_.../2026-07-16_import_checksum_evidence.md`.
- Spreadsheet parsed at import (`openpyxl`, `data_only=True`): 1 sheet, rows 1–27 populated, 13 target
  columns — reconciles with the manifest above.
- **Data-quality flags raised at import:** (i) all 7 sample rows are **mock**; (ii) the sheet's
  `Target eBay Price`/`Status` are computed from the wrong rule and are **known-wrong** under the confirmed
  rule (7/7 targets website-derived where Amazon existed; Status flips on rows 7 & 8); (iii) the tolerance
  threshold **self-contradicts** (£15 vs £20).
