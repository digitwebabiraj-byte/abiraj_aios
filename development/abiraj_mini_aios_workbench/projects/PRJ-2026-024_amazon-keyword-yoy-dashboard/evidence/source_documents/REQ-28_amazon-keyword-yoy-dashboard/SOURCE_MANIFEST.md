# SOURCE_MANIFEST — REQ-28 Amazon PPC Keyword YoY Performance Dashboard

| File | Origin | Role |
|---|---|---|
| `2026-08-14_source_amazon-keyword-yoy-dashboard-spec.html` | Supplied by Abiraj (`Amazon_Keyword_YoY_Dashboard_Final (1).html`, 2026-08-14) | The **specification** — full dashboard UI + client-side business logic (period engine, YoY maths, diagnosis/priority/root-cause/action engine, filters, charts, CSV export, demo + CSV providers). Defines *what* to build, not data. |

## How the source is used
The spec is the render **template**. `render_akyp_dashboard.py` embeds the live payload into it and
appends a thin delivery layer (embedded data instead of the spec's live Amazon API; account/period
locked; demo/CSV/sync hidden). No spec calculation or rendering code is altered.

## UI fixes applied to the template (2026-08-14)
Two presentation-only fixes were made to this template's render code (no data/business-logic change):
- **KPI delta:** arrow now reflects the numeric direction (▲ increase / ▼ decrease) while colour still
  reflects good/bad — so e.g. PPC Spend −85.5% shows a green ▼ and ACOS +55.8% a red ▲ (previously the
  arrow was tied to good/bad, giving a green ▲ next to a negative number).
- **Top-10 bar chart:** switched from a centre-axis layout (whose value labels overlapped the keyword
  column) to a clean left-aligned magnitude bar with the value at the bar's end.
The user's original untouched copy remains in Downloads; this working template drives the deliverable.

## Honesty
Every value in the spec (demo keywords like "pendant lamp shade", the simulated figures) is
illustrative and is **never** shipped. All delivered figures are live from
`amazon_campaigns.search_term_performance_data` and joined tables in the ledsone DB.
