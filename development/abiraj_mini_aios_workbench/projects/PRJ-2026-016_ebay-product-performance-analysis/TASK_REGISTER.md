# TASK REGISTER — PRJ-2026-016 eBay Product Performance Analysis

Canonical index of tasks/deliverables within this project. Detail lives in `PROJECT_HOME.md` /
`SYSTEM_REFERENCE.md`.

| Task | Deliverable | Description | Status |
|---|---|---|---|
| REQ-19 | **REQ-19-D01** | Per-listing eBay Product Performance dashboard (Excel), 35 columns, one row per eBay listing, UK+DE, all accounts | **BUILT — warehouse-only interim, 2026-07-27.** 9,781 rows; 28/35 columns populated, 7 NO DATA. Not published, not signed off. |
| REQ-19 | REQ-19-D02 | Scheduled refresh (automation) | NOT STARTED (gated on D01 sign-off + publish decision) |

## REQ-19-D01 artefacts
- Deliverable: `evidence/final_outputs/REQ-19_.../REQ-19-D01_ebay_product_performance_v4_final.xlsx`
- Builder: `sql/REQ-19_.../eppr_build_d01.py` (single read-only module, direct psycopg2)
- Source: `evidence/source_documents/REQ-19_.../` (`Thinesh task (5).xlsx`, SHA-256 in SOURCE_MANIFEST)
- Requirement doc: `DigitWeb_Works_Abiraj/27_07_2026/2026-07-27_abiraj_REQ-eppr_REQ-19-D01.md`

## Open items
- 🔴 **Cost Price source** — blocks 4 profit columns (Cost, Gross, Net, Margin). Needs `ledsone` or Thinesh.
- Decision sheet to Thinesh: cost/profit semantics, scope/window confirmation, Sales-Trend bands, Watchers/Clicks handling.
- Confirm IDs (Varmen): `PRJ-2026-016` / `REQ-19` / code `eppr`.
- Reviewer gates: Sajeesan (technical), Tamil Selvan (queryability), Thinesh (business).
- Publish audience (`ph_task`) not decided; no publish, no git commit yet.
- Validation note (independent verification of D01) — TODO.
