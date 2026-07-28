# TASK REGISTER — PRJ-2026-016 eBay Product Performance Analysis

Canonical index of tasks/deliverables within this project. Detail lives in `PROJECT_HOME.md` /
`SYSTEM_REFERENCE.md`.

| Task | Deliverable | Description | Status |
|---|---|---|---|
| REQ-19 | **REQ-19-D01** | Per-listing eBay Product Performance report (Excel + interactive dashboard + static portal HTML), 34 columns, one row per eBay listing, UK+DE, all accounts | ✅ **CLOSED — DELIVERED · PUBLISHED · SIGNED OFF (Thinesh) 2026-07-28.** 11,123 rows; **34/34 populated (no empty columns)**. Cost Price = 20% estimate → profit derived (flagged). Published to `ph_task` ids **472–475** (`ebay_priors`), v3. |
| REQ-19 | **REQ-19-D02** | Scheduled monthly refresh (automation) | ✅ **AUTOMATED · LIVE · PROVEN 2026-07-28.** Windows task **`EPPR_Monthly_Product_Performance`**, **2nd Wednesday of each month 10:00** (next 2026-08-12), fail-closed (refuses to publish on 0 rows / <8,000 / <60% of last good / missing HTML), status file + Desktop alert, git-ignored secrets, registered on the main-tree path. Proven end-to-end: manual runner OK + **Start-ScheduledTask → LastTaskResult 0**, refreshed ph_task 472-475. |

## Publish record — ph_task (2026-07-27)
| id | assigned_user | task_id | team | version |
|---|---|---|---|---|
| 472 | Thinesh | `eppr_Thinesh_ebay_product_performance` | ebay_priors | 3 |
| 473 | Jarsini | `eppr_Jarsini_ebay_product_performance` | ebay_priors | 3 |
| 474 | kobiga | `eppr_kobiga_ebay_product_performance` | ebay_priors | 3 |
| 475 | powsteena | `eppr_powsteena_ebay_product_performance` | ebay_priors | 3 |

Static no-JS HTML (portal viewer runs no JS). Guarded temp_user publish; SELECT-then-INSERT/UPDATE (no live UNIQUE on task_id); assigned_user_team set.

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
