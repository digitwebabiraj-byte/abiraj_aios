# PRJ-2026-024 — Amazon PPC Keyword YoY Performance Dashboard (`akyp`)

Keyword-level year-over-year performance for **amazon Ledsone** Amazon PPC, built to the
supplied spec HTML. One row per PPC **keyword** (no ASIN logic): current vs previous-year
sales, spend, orders, clicks, impressions and efficiency, with a per-keyword
diagnosis / priority / root-cause / recommended-action engine, charts, filters and CSV export.

| | |
|---|---|
| Project ID | `PRJ-2026-024_amazon-keyword-yoy-dashboard` |
| Code | `akyp` |
| Task | `REQ-28_amazon-keyword-yoy-dashboard` (**provisional** — source is a spec HTML with no requirement number) |
| Owner | Abiraj |
| Task assigned by | HR |
| User | **Meshika** (`staff.users` id 182, Active, Nelliady) — also Business Validator |
| Account / scope | amazon Ledsone (`sub_source 8`) · markets UK, US, CA, DE, FR, IT |
| Data source | `amazon_campaigns.keyword_performance_data` (+ `keywords`, `campaigns`, `ad_groups`), 7-day attribution, live ledsone DB, read-only |
| Deliverable | `evidence/final_outputs/REQ-28_.../REQ-28-D01_amazon_keyword_yoy_dashboard.html` |
| Status | **Draft delivered — YoY live** (Sajeesan added the keyword tables 2026-08-14). Not published to ph_task, not automated. |

## The one thing to know
The correct source is **`amazon_campaigns.keyword_performance_data`** — the true keyword entity
(manual-targeting keywords only; auto search terms excluded), with history back to **2023**, so
**true YoY populates**. (Not `search_term_performance_data`, which is a larger auto-inclusive
universe starting only 2025-11-16.) The current MTD window legitimately reads lower than the
settled prior year because Amazon's 7-day attribution has not matured on the last ~7 days — a
banner states this plainly.

## Build
```bash
cd sql/REQ-28_amazon-keyword-yoy-dashboard
python build_akyp_d01.py       # live fetch -> akyp_payload.json
python render_akyp_dashboard.py # payload + spec template -> REQ-28-D01 dashboard HTML
```
`LED_*` DB credentials come from the git-ignored shared store (already set globally).

See `PROJECT_HOME.md` (governance) and `SYSTEM_REFERENCE.md` (full functional detail).
