# PRJ-2026-018 — B2B Session Drop Tracker · Germany (Amazon.de) (`bsdt`)

**End user / requester:** **Jensika** (verified live `staff.users` id **99**, username `jensika`, Active, Nelliady, role User). `ph_task` publish audience/team still to confirm.
**Owner/developer:** Abiraj · **Requirement:** REQ-21 *(provisional)* · **Code:** `bsdt` *(provisional)*
**Onboarded:** 2026-07-31 · **Source:** `B2B_Session_Drop_Tracker_DE.xlsx` (Downloads, delivered by owner)
**Status:** ONBOARDING — task understood, data source proven reproducible; **not built, not published, not committed.**

## What this is
A watch-list that catches **Amazon.de (Germany) ASINs whose B2B (business-customer) traffic dropped**
between two matching 30-day windows ("Previous 30 Days" → "Last 30 Days"), so a real decline in
visibility to **business buyers** gets investigated. It deliberately does **not** use B2B Conversion %
— per-ASIN B2B session volume on .de is too low for a percentage to mean anything — and instead tiers
each ASIN by its **B2B Sessions** volume and assigns a fixed action per tier.

## The defining fact — 🔴 THE WAREHOUSE DATA IS INCOMPLETE FOR THIS TASK
The right table exists (`business_reports.amz_traffic_by_asin` carries every B2B column, mapping proven),
**but its B2B coverage is missing for ~77% of the sheet's ASINs.** Full 526-ASIN completeness test
(`evidence/DATA_SOURCE_ANALYSIS.md`):
- **359 / 526 (68%)** sheet ASINs have **zero** B2B sessions in the DB (all-time, DE/sub_source 8).
- **406 / 526 (77%)** have **fewer** all-time DB B2B sessions than their 60-day total on the sheet —
  **mathematically impossible** if the DB were the source (a 60-day window can't exceed all-time).
- Only **120 / 526 (23%)** are even *potentially* reproducible (and the true windowed match is lower).
- **May 2026 is entirely absent** from the DE feed; Jun/Jul 2026 nearly empty; 51 ASINs not in the table at all.

⚠️ The earlier "fully reproducible" read was **wrong** — it rested on one coincidental exact match
(`B0DLWRP73C`: DB 19 = sheet 15+4), which proved the **column mapping** but not **coverage**. The sheet
was built from a **fuller source** (almost certainly a direct Amazon Seller Central Business Reports
export), not this warehouse table. **So this is NOT a clean DB→report pipeline.** Next step is to find
the real source (owner) and/or raise the broken DE B2B sync with Sajeesan — see OPEN QUESTIONS.

## Source data (from the sheet's "Objective & Guide" tab)
Amazon Seller Central **Business Reports → Detail Page Sales and Traffic by Child Item**, Amazon.de,
two matching 30-day windows. Uses **B2B-only** columns — *Sessions · Total · B2B*, *Page Views · Total
· B2B*, *Units ordered · B2B* — never the blended B2B+B2C totals. **Only ASINs with some B2B traffic in
either window are included**; ASINs with zero B2B traffic in both cycles are excluded (no B2B signal).

## Warehouse source mapping (proven)
| Sheet column | `business_reports.amz_traffic_by_asin` column |
|---|---|
| ASIN | `child_asin` |
| Prev / Current B2B Sessions | `sessions_b2b` (windowed) |
| Prev / Current B2B Page Views | `page_views_b2b` (windowed) |
| Prev / Current B2B Orders | `units_ordered_b2b` (windowed) |
| Buy Box % (Current) | `buy_box_percentage_b2b` (current window) |
| — filter — | `market_place = 10` (Germany = id 10 in `order_management.market_place`) · `sub_source = 8` (amazon Ledsone) |

## The tier / action engine (from the "Thresholds" tab — editable, never hardcode)
Tier is set purely by **MAX(Prev, Current) B2B Sessions** against two editable session boundaries; Status
and Action follow directly from the Tier. Session Change (Current − Prev) is **context/trend only** — it
does **not** change tier or action. Units Orders and Buy Box % are context, not gates.

| Tier | Rule (MAX sessions) | Action (summary) |
|---|---|---|
| Tier 1 – Low | `< 5` | Set Business Price (5–10% below retail) + Quantity Discount tiers; add bulk/case-pack info |
| Tier 2 – Moderate | `≥ 5` and `< 10` | Light check — Buy Box %, confirm Business Price/Qty Discount active, scan title + main image |
| Tier 3 – High | `≥ 10` | Priority review — Buy Box % + stock, Business Price/Qty tiers, spec table, A+ content, B2B-only offers, VAT invoicing, backend B2B search terms, certifications |

**Source sheet result (528 ASINs):** Tier 1 – Low **506** · Tier 2 – Moderate **16** · Tier 3 – High **4**.

## Deliverable shape (the built sheet — "Tracker" tab, 12 columns)
`ASIN · Prev B2B Sessions · Prev B2B Page Views · Prev B2B Orders · Current B2B Sessions · Current B2B
Page Views · Current B2B Orders · Buy Box % (Current) · Session Change · Tier · Status · Action`.

## OPEN QUESTIONS (must resolve before BUILD — nothing invented)
0. ✅ **DATA SOURCE — RESOLVED (owner-confirmed 2026-07-31).** The sheet was generated **from a direct
   Amazon Seller Central Business Report export** — NOT the database. The DB's `amz_traffic_by_asin` is
   a partial, gappy mirror of that report (May 2026 missing, ~half the ASINs absent), which is why it
   can't reproduce the sheet. ⇒ **Build FRRC-style: the owner-supplied Amazon report export is the
   system of record; the DB is not used as the source.** Each future cycle needs a fresh 2-window export.
1. ✅ **Publish audience — RESOLVED + PUBLISHED (2026-07-31).** End user **Jensika** (`staff.users`
   id 99), `assigned_user_team=**ah_priors**`. Live on `tech_team_outputs.ph_task` **id 669**
   (`order_management_copy` warehouse), guarded `temp_user` INSERT, read-back md5-verified. Business
   sign-off from Jensika pending.
2. ✅ **The two 30-day windows — RESOLVED (owner-confirmed 2026-07-31):**
   - **Current cycle:** 2026-06-16 → 2026-07-15
   - **Previous cycle:** 2026-05-17 → 2026-06-15
   (Corroborates the DB being unusable: the DB holds **no May 2026 DE data at all**, so the previous
   window could never be reproduced from it — the Amazon report export is the only viable source.)
3. ✅ **Scope — RESOLVED (owner-confirmed 2026-07-31): Amazon.de (Germany) account ONLY**, single
   account. The source is the DE Seller Central Business Report, so it is DE-only by definition; the
   earlier DB "UK/FR matches" were just noise from the incomplete DB mirror and are irrelevant (the DB
   is not the source).
4. **IDs** — `REQ-21` and code `bsdt` are provisional; confirm (REQ-18 was reserved `fauto`; eBay
   sequence reached REQ-20/`eckr`). See [[task-id-naming]].
5. **Parent vs child ASIN grain** — sheet uses child ASIN; confirm no parent-level rollup wanted.

## Governance / safety
Read-only throughout. No `ph_task` publish, no scheduled task, no git commit, no writes — this is an
onboarding record only. Deliverable will be a read-only report (xlsx + dashboard) like the other trackers.
