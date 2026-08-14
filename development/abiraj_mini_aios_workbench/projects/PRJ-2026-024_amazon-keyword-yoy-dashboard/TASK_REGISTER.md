# TASK_REGISTER — PRJ-2026-024 Amazon PPC Keyword YoY Performance Dashboard

| Task ID | Deliverable | Description | Status |
|---|---|---|---|
| `REQ-28_amazon-keyword-yoy-dashboard` | `REQ-28-D01` | Keyword-level Amazon PPC YoY dashboard for amazon Ledsone across UK/US/CA/DE/FR/IT, rendered from live data per the supplied spec HTML. | **Draft delivered — YoY live** (Sajeesan added the keyword tables 2026-08-14). Not published, not automated, not committed. |

**Task ID note:** `REQ-28` is **provisional** — the source (spec HTML) carries no requirement
number. REQ-26 = `esdt`, REQ-27 = `merge` (merged-dashboards), so REQ-28 is the next free number;
confirm/formalise before closure. One project = one Project ID; one requirement = one Task ID; a new day/session does not mint
a new one.

## Deliverables
- **REQ-28-D01** — `evidence/final_outputs/REQ-28_amazon-keyword-yoy-dashboard/REQ-28-D01_amazon_keyword_yoy_dashboard.html`
  - Built by `sql/REQ-28_amazon-keyword-yoy-dashboard/build_akyp_d01.py` → `akyp_payload.json`
  - Rendered by `sql/REQ-28_amazon-keyword-yoy-dashboard/render_akyp_dashboard.py`

## Open items
1. Formalise the requirement number (REQ-28 provisional).
2. Business Validator to confirm the spec's decline thresholds and Reason/Action vocabulary.
3. ~~Sajeesan: backfill prior-year Amazon keyword history.~~ **DONE 2026-08-14** — keyword tables
   added; rebuilt on `keyword_performance_data`, YoY now live across all markets.
4. On owner instruction only: `ph_task` publish and/or scheduled refresh.
