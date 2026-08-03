# TASK REGISTER — PRJ-2026-019 eBay Product Net Sales

Canonical index of tasks/deliverables within this project. Detail lives in `PROJECT_HOME.md` /
`SYSTEM_REFERENCE.md`.

| Task | Deliverable | Description | Status |
|---|---|---|---|
| REQ-22 | **REQ-22-D01** | Per-order eBay **Net Sales (NNV)** report (Excel): 12-column table (Order ID · SKU · Account · Gross Sales · VAT 20% · Promotion % · Final Value Fee · Product Cost · Postage · PPC Cost · General · Net Sales) at eBay order-line grain, last 30 days, per marketplace currency. | 🟡 **ONBOARDED — DISCOVERY · BUILD PENDING.** Requirement captured; structure scaffolded 2026-08-03. Not built / published / committed / signed off. |
| REQ-22 | **REQ-22-D02** | **Net Sales Lookup** tab — enter any single Order ID, return its Net Sales and full deduction breakdown. | 🟡 **PLANNED** (same workbook, part of D01 build). |
| REQ-22 | *(future)* | Scheduled refresh (automation), if requested after sign-off. | ⚪ Not requested. |

## Source
`evidence/source_documents/REQ-22_.../Kobiga task.xlsx` (SHA-256 in `SOURCE_MANIFEST.md`, imported 2026-08-03).

## Open items
- 🔴 **Product Cost source** — no per-SKU COGS in any DB (`sku_cogs` empty). Blocks column 8 and the
  Net Sales value. Needs a cost basis from Kobiga or an explicit owner decision (`NO DATA` vs estimate).
- 🟠 **Deduction set / grain confirmation** — the exact deductions, their sign, `Promotion %` vs amount,
  the `General` bucket definition, and grain (order vs order-line vs SKU) must be confirmed with Kobiga.
- 🟠 **Marketplace scope** — UK only vs UK+DE (drives currency handling).
- Confirm IDs (Varmen): `PRJ-2026-019` / `REQ-22` / code `epns`.
- Reviewer gates: Sajeesan (technical), Tamil Selvan (queryability), Kobiga (business).
- Publish audience (`ph_task`, likely `ebay_priors`) not decided; no publish, no git commit yet.
- Validation harness (`verify_epns_d01.py`) — TODO once built.
