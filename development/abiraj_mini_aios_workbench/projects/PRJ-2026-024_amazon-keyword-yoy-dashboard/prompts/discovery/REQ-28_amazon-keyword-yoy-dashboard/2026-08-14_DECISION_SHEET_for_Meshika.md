# Decision Sheet — Amazon PPC Keyword YoY Dashboard (REQ-28-D01 / akyp)

**For:** Meshika (user / Business Validator · `staff.users` id 182) · **Assigned by:** HR · **Prepared by:** abiraj · **Date:** 2026-08-14

The dashboard is **built and live** on real data (amazon Ledsone, 6 markets, true YoY). Every rule
below is currently the **spec's default** — it works, but it is not yet *confirmed* as the agreed
business logic. Please confirm or change each. Nothing is published or automated until you sign off.

---

## A. Business rules (the diagnosis engine)

| # | Decision | Current default (in use) | Confirm / change |
|---|---|---|---|
| A1 | **Attribution window** — how many days after a click a sale still counts | **7-day** (Amazon Sponsored Products default) | ☐ keep 7-day · ☐ 14-day · ☐ 30-day |
| A2 | **Decline priority bands** (by YoY sales-decline %) | Severe ≥ 50 · High ≥ 30 · Moderate ≥ 20 · Stable < 20 · Growth = sales up > 0 | ☐ keep · ☐ change to ____ |
| A3 | **"Meaningful move" sensitivity** — % change that counts as a metric up/down | 15% | ☐ keep · ☐ ____ |
| A4 | **Stable band** — |sales change| under this = "Stable Performance" | 10% | ☐ keep · ☐ ____ |
| A5 | **Low-impression flag** — impressions under this in the current window = "Low Impression Volume" | 100 | ☐ keep · ☐ ____ |
| A6 | **High-ACOS flag** — ACOS above this = "High ACOS" | 35% | ☐ keep · ☐ ____ |
| A7 | **Reason / Action vocabulary** — the diagnosis labels + recommended actions (Visibility Loss, CTR Decline, CVR Decline, High ACOS, No Sales, Bid Opportunity, Paused, Sales Growth, Stable…) and their wording | spec ladder (first-match) | ☐ keep · ☐ reword ____ |

## B. Scope & period

| # | Decision | Current default | Confirm / change |
|---|---|---|---|
| B1 | **Default analysis period** | Month-to-Date (current month vs same span last year) | ☐ keep MTD · ☐ Previous Month · ☐ Last 30 days |
| B2 | **Marketplaces shown** | UK, US, CA, DE, FR, IT | ☐ keep all 6 · ☐ drop US & CA (near-zero current activity) · ☐ other ____ |
| B3 | **Account** | amazon Ledsone only (`sub_source 8`) | ☐ keep · ☐ add DC Voltage / Neighbour Market |

## C. Known honest limits (no action needed unless you want them changed)

- **C1 — Suggested bid is blank.** No "suggested bid" data exists anywhere in the warehouse, so that
  column is empty and the "Bid Opportunity" rule stays dormant. To light it up, Sajeesan would need
  to add a suggested-bid feed. ☐ accept blank · ☐ ask Sajeesan for a suggested-bid source.
- **C2 — Current month reads low.** The current window under-reports vs last year because Amazon's
  7-day attribution has not finished maturing on the most recent ~7 days. It firms up as the month
  completes; a banner states this. (Choosing a *settled* period like "Previous Month" avoids it.)

## D. Delivery (needed before publish / automation)

| # | Decision | Options | Your call |
|---|---|---|---|
| D1 | **Who sees it in the portal (`ph_task`)** | just Meshika · the Amazon PH team · other named users | ____ |
| D2 | **`assigned_user_team`** (portal filter group) | e.g. `ah_priors` / `amazon_priors` / other | ____ |
| D3 | **Refresh cadence** (for automation) | monthly · weekly · daily · manual only | ____ |

---

**How to respond:** tick/annotate inline, or reply with the item numbers you want changed. On sign-off
I formalise REQ-28, then (on your instruction) publish to the named audience and schedule the refresh.
