# PROJECT_HOME — PRJ-2026-024 Amazon PPC Keyword YoY Performance Dashboard

## Purpose
Give the Amazon PPC team a keyword-level view of how each search **keyword** is performing
this period versus the same period last year — sales, spend, orders, clicks, impressions and
efficiency (CTR/CVR/CPC/ACOS) — with each keyword automatically diagnosed (what changed, why,
and what to do), so declines and opportunities surface without manual spreadsheet work.

## Scope (confirmed with Abiraj, 2026-08-14)
- **Account:** amazon Ledsone only (`order_management.sub_source.id = 8`).
- **Marketplaces:** UK (23), US (24), CA (26), DE (10), FR (9), IT (14). Selectable in the UI;
  currency follows the marketplace (GBP / USD / CAD / EUR).
- **Grain:** one row per keyword (keyword × campaign × ad group). **No ASIN logic** anywhere —
  this is a keyword report by design.
- **Comparison:** **true Year-over-Year** exactly as the spec defines — current window vs the
  same calendar window one year earlier (MTD by default).
- **Out of scope:** DC Voltage, Neighbour Market, non-Amazon channels, ASIN/product roll-ups,
  changing the spec's diagnosis thresholds (those are user-configurable in the UI, defaults kept).

## Data-coverage verdict (rev 2026-08-14 — after Sajeesan added the keyword tables)
- **Correct source = `amazon_campaigns.keyword_performance_data`** (one row per keyword per day,
  the keyword total) + `keywords` (current bid + state), joined to `campaigns`/`ad_groups`. This is
  the true keyword entity — **manual-targeting keywords only** (BROAD/PHRASE/EXACT); auto-targeting
  search terms are excluded by design, which is exactly what a "keyword" dashboard should show.
  Carries every spec field: keyword_text, match_type, impressions, clicks, ctr, cost(spend), cpc,
  purchases/sales (1/7/14/30-day attribution), acos, roas, conversion_rate, keyword state, campaign
  state. **Attribution used = 7-day** (Amazon SP default; matches the spec's header priority).
  `suggestedBid` has **no source anywhere** → `null` (the Bid-Opportunity rule simply never fires).
- **YoY history: RESOLVED.** The new table goes back to **2023-07**; Aug-2025 is populated
  (70,015 rows). True YoY now populates for all markets. (The earlier build used
  `search_term_performance_data`, which starts only 2025-11-16 AND mixes in auto search terms — a
  different, larger universe — so it was both source-wrong and history-short. Corrected.)
- **Nuance (not a gap):** the current MTD window under-reports vs the settled prior-year window
  because Amazon's 7-day attribution has not matured on the last ~7 days. Inherent to fresh-vs-
  settled comparison.
- **Current snapshot (2026-08-01 → 2026-08-14, verified in-browser):** UK 2,202 kw ·
  cur £1,378.69 / prev-yr £14,788.32 (−90.7%) · DE 406 · 235.54/2,556.84 · FR 218 · 123.17/1,312.29 ·
  IT 87 · 71.27/600.24 · CA 177 · 0/1,727.73 · US 10 · 0/0. 3,100 keyword rows total.

## Deliverable
`REQ-28-D01_amazon_keyword_yoy_dashboard.html` — the spec's full dashboard, rendered as a
self-contained static snapshot with the live figures embedded. The spec's live-Amazon-API data
layer is swapped for the embedded snapshot; **all** spec UI and business logic (YoY calc,
diagnosis/priority/root-cause/action engine, filters, charts, table, CSV export) is preserved.

## Assignment / user
- **Task assigned by: HR.**
- **User: Meshika** (`staff.users` id **182**, username `meshika`, role User, Active, Nelliady) — the
  end user, and Business Validator for the spec's diagnosis thresholds and Reason/Action vocabulary.

## Reviewers
- Coordinator: Varmen · Technical Reviewer: **Sajeesan** (added the keyword data 2026-08-14) ·
  Queryability: Tamil Selvan · Business Validator / end user: **Meshika**.

## Status & next actions
- **Draft delivered**, current-period data live and verified. Not published to `ph_task`, not
  automated, not committed (workbench Git rule — awaits GPT review).
- Open items:
  1. Confirm the requirement number / mint `REQ-28` formally (currently provisional).
  2. Business Validator to confirm the spec's decline thresholds (50/30/20 %) and Reason/Action
     wording are the agreed rules, not just spec defaults.
  3. ~~Sajeesan: backfill prior-year keyword history.~~ **DONE 2026-08-14** — keyword tables added;
     rebuilt on `keyword_performance_data`, YoY now live across all markets.
  4. On owner instruction: publish to `ph_task` and/or schedule a refresh (automation folder is
     scaffolded but empty pending that decision).
