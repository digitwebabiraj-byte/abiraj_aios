# SYSTEM_REFERENCE — PRJ-2026-024 Amazon PPC Keyword YoY Performance Dashboard

Complete functional detail of what this system does and how each figure is produced. Derived
from the canonical sources: the spec HTML
(`evidence/source_documents/REQ-28_.../2026-08-14_source_amazon-keyword-yoy-dashboard-spec.html`),
`build_akyp_d01.py` and `render_akyp_dashboard.py`.

## 1. What the dashboard shows
A keyword-only Amazon PPC dashboard for amazon Ledsone. Sections (top→bottom):
- **Header chips:** account, marketplace, currency, period type, last synced, data status.
- **Snapshot banner:** states the data is a live snapshot, the current window vs the same window one
  year earlier, and that the current MTD side under-reports until its 7-day attribution matures.
- **Executive KPIs:** Keyword Sales, Ad Spend, ACOS, Orders (current, previous-year, Δ%).
- **YoY keyword sales trend:** daily current vs previous-year aggregate sales line chart.
- **Top 10 keywords:** bar chart, sortable by decline / growth / sales / spend.
- **Keyword diagnosis breakdown:** clickable tiles that filter the table.
- **Top movers:** biggest keyword growth and biggest keyword declines.
- **Keyword YoY detail table:** every keyword with current/previous metrics and YoY deltas,
  diagnosis, priority, root cause and recommended action. Sortable, filterable, CSV-exportable.
- **Data quality:** availability / currency / date-window / duplicate checks.

## 2. Data model — where every figure comes from
All live from the ledsone DB (read-only), schema `amazon_campaigns`. **Primary source =
`keyword_performance_data`** (one row per keyword per day; manual-targeting keywords only —
auto search terms excluded by design; history back to 2023 so YoY works):

| Field (spec) | Source |
|---|---|
| keyword | `keyword_performance_data.keyword_text` (denormalised; grain = one row per `keyword_id`) |
| campaign | `campaigns.campaign_name` (join on `campaign_id`) |
| adGroup | `ad_groups.ad_group_name` (join on `ad_group_id`) |
| matchType | `keyword_performance_data.match_type` (BROAD/PHRASE/EXACT, uppercased) |
| status | `active` unless the current `keywords.state` ≠ `ENABLED`, then `paused` |
| bid | `keywords.keyword_bid` (current bid) |
| suggestedBid | **null** — no source column anywhere in this schema |
| cur.sales / prev.sales | `SUM(sales_7d)` over the current / previous-year window (7-day attribution) |
| cur.orders / prev.orders | `SUM(purchases_7d)` |
| cur/prev impressions, clicks, spend | `SUM(impressions)`, `SUM(clicks)`, `SUM(cost)` |
| daily series | `SUM(sales_7d) GROUP BY date` per window (trend chart) |

Attribution: **7-day** (Amazon Sponsored Products default; matches the spec CSV header priority
`7 day total sales/orders`). CTR/CVR/ACOS/CPC are recomputed in-UI from these totals per the spec.
Account/market scoping: `campaigns.sub_source = 8` (amazon Ledsone) and `campaigns.market_place`
∈ {23 UK, 24 US, 26 CA, 10 DE, 9 FR, 14 IT}. **Why not `search_term_performance_data`:** that table
is search-term grain including auto-targeting (a different, ~5× larger click/spend universe) and
only starts 2025-11-16 — wrong entity for a keyword report and too short for YoY.

## 3. Period engine (from the spec, unchanged)
Current window is chosen by the Analysis-Period selector (MTD default; also Previous Month,
Last 7/14/30, Custom). The **previous** window is the same span shifted back exactly one calendar
year (Feb-29 clamps to Feb-28). MTD never compares against a full prior-year month — it is
like-for-like day span. In the delivered static snapshot the period is **locked to MTD** to match
the fetched data; the live spec supports all period modes against a live backend.

## 4. Business logic (from the spec — preserved verbatim)
- **YoY % change** = (current − previous) / previous × 100; previous = 0 → treated as no baseline.
- **Priority bands by sales-decline %** (user-configurable, defaults): Severe ≥ 50, High ≥ 30,
  Moderate ≥ 20, Stable < 20, Growth = sales change > 0.
- **Diagnosis / root cause / action:** a first-match rule engine — Paused, Low Impression Volume,
  No Sales (clicks but no orders), Sales Growth / Bid Opportunity, Stable, then for declines the
  dominant driver (Visibility Loss / CTR Decline / CVR Decline / High ACOS / general), each with a
  root-cause sentence and a recommended action. Efficiency metrics: CTR = clicks/impr, CVR =
  orders/clicks, ACOS = spend/sales, CPC = spend/clicks.
- These thresholds and the Reason/Action vocabulary are **spec defaults**, pending Business
  Validator confirmation — do not present as agreed logic, do not silently change.

## 5. Rendering / delivery
`build_akyp_d01.py` fetches all six markets into `akyp_payload.json`. `render_akyp_dashboard.py`
embeds that payload into the spec template and appends a thin delivery layer that (a) overrides
`API.getKeywordPerformance` to return the embedded market data, (b) locks account to LEDSone and
the period to the snapshot, (c) hides live-sync / demo / CSV controls, (d) swaps the demo banner
for the truthful snapshot banner. Switching the Marketplace selector re-renders from the embedded
data for that market. No spec calculation or rendering code is modified.

## 6. Honesty rules
Every displayed figure traces to a real `amazon_campaigns.*` column. `suggestedBid` is null (no
source), and the current MTD window reads low vs the settled prior year (7-day attribution not yet
matured) — both stated, never fabricated or inflated. Demo data
(the spec's simulated provider) is disabled in the deliverable. A `0` appears only where the true
value is zero. Credentials come from the git-ignored shared store, never committed.
