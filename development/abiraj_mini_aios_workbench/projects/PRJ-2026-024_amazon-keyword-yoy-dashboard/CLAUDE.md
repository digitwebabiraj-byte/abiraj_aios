# CLAUDE.md — PRJ-2026-024 Amazon PPC Keyword YoY Performance Dashboard

Project execution rules. Inherits the workbench `CLAUDE.md`; the rules below are additional.

## Identity
- Project `PRJ-2026-024_amazon-keyword-yoy-dashboard` · code `akyp` · Task `REQ-28` (**provisional**
  — the source is a spec HTML with no requirement number; REQ-26 is `esdt`). A new day/session does
  NOT mint a new Task ID.
- Owner Abiraj. Task assigned by **HR**. User / Business Validator = **Meshika** (`staff.users` id
  182). Technical Reviewer **Sajeesan** (added the keyword tables 2026-08-14).

## 1. The spec HTML is the specification, not data
`2026-08-14_source_amazon-keyword-yoy-dashboard-spec.html` defines the desired **UI, columns,
period engine, YoY maths and diagnosis/priority/root-cause/action logic**. Its `DEMO` provider and
every sample keyword ("pendant lamp shade" etc.) are illustrative — never ship a demo number.
Every delivered figure is live from the ledsone DB.

## 2. Keyword-only — no ASIN logic
This is a keyword report by design. Do not add ASIN/product roll-ups. Grain is
keyword × campaign × ad group.

## 3. Correct source + True YoY
Primary source is **`amazon_campaigns.keyword_performance_data`** (+ `keywords` for bid/state),
NOT `search_term_performance_data`. The keyword table is the true keyword entity (manual targeting
only; auto search terms excluded) and carries history back to 2023 so YoY works. Do NOT revert to
`search_term_performance_data` — it is a different, larger universe (includes auto) and starts only
2025-11-16. Attribution = **7-day** (`sales_7d`/`purchases_7d`). Comparison is **current vs same
window one year back**, exactly as specced; do not switch to period-over-period without owner sign-off.
The current MTD window legitimately under-reports vs the settled prior year (7-day attribution not
matured on the last ~7 days) — state it, never "fix" it by inflating current numbers.

## 4. Don't invent the business rules
The decline thresholds (50/30/20 %) and the Reason/Action vocabulary are the **spec's defaults**,
pending Business Validator confirmation. Keep them, keep them flagged as provisional, do not silently
change them. They are also user-configurable in the UI — that is the spec's design, not a rule change.

## 5. Currency never blends across marketplaces
Each marketplace renders in its own currency (UK £, US $, CA $, DE/FR/IT €). The dashboard shows one
marketplace at a time; never sum or compare a £ figure with a € one.

## 6. Read-only; one generator; never fabricate
- READ-ONLY on all source tables. No INSERT/UPDATE/DELETE/DDL. The only future write is a guarded
  `ph_task` publish on explicit owner instruction after the audience is named and each recipient
  verified.
- The report (and any scheduled run) comes from the single pair
  `sql/REQ-28_amazon-keyword-yoy-dashboard/build_akyp_d01.py` + `render_akyp_dashboard.py`. Do not
  fork a second fetch or render path.
- `suggestedBid` has no source → stays `null`; the current MTD window is 7-day-attribution-immature
  (reads low vs the settled prior year) → stated, never inflated. Neither is ever guessed.
  Credentials come from the git-ignored shared store, never committed.

## 7. Stop conditions (in addition to the workbench's)
- A rule (period, thresholds, diagnosis vocabulary, grain) is needed but unconfirmed → stop and flag,
  keep the documented spec default.
- A publish is requested before the audience is named and each recipient verified.
- Any request to blend currencies across marketplaces, or to add ASIN logic.
- No approved implementation prompt exists for a change → do not start it.

## Vocabulary
YoY % = (Current − Previous) ÷ Previous × 100 · ACOS = spend ÷ sales · CTR = clicks ÷ impressions ·
CVR = orders ÷ clicks · sub_source 8 = amazon Ledsone · null suggestedBid = no source column ·
empty previous = prior-year history not yet backfilled (not zero sales).
