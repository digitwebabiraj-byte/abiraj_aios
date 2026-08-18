# Abiraj — Task Brief (crisp, for review)

**Format for each task:** *What it does* → *How it works* → *Benefit the user gets*
All reports are **read-only** (never write to Amazon/eBay/Shopify), **reconciled to the live database**, and **published straight to the person who needs it** (they see only their own rows).

---

## Automated reports (build themselves on a schedule — recurring time saved)

**1. EPC — eBay Price Checker** · *Weekly, Mon*
- **Does:** Flags eBay listings priced wrong vs our own Amazon/website price.
- **Works:** Reads 126,070 live eBay listings across 13 accounts; target price = Amazon ×0.90 or website ×1.10; ranks by money-at-risk.
- **Benefit:** Stops listings from silently losing sales (too high) or margin (too low) — auto-refreshed every week.

**2. EBPD — eBay Account Performance Dashboard** · *Weekly refresh, monthly view*
- **Does:** One scorecard per eBay account × marketplace — sales, ad efficiency (TACOS), stock position.
- **Works:** Pulls settled sales (`order_total`), ON-SITE ad spend, and listing counts; reconciles to the penny.
- **Benefit:** Each account owner sees their month at a glance — no manual pull.

**3. ERA — eBay Return Analysis** · *Monthly, 5th*
- **Does:** Which SKUs get returned, how often vs sales, why, and at what refund/fee cost.
- **Works:** Bridges returns to SKU via transaction ID; return cost = refund + final-value fee.
- **Benefit:** Pinpoints the SKUs quietly costing money in returns (£2,937 refund + £869 cost surfaced for June).

**4. DST — Daily Sales Track** · *Daily, 09:05*
- **Does:** Daily sales/orders/units per account × marketplace vs yesterday and last year.
- **Works:** 30 rows, money kept in each marketplace's own currency (never blended).
- **Benefit:** A daily trading pulse for free — and it caught a hidden decline a blended figure was masking.

**5. EPPR — eBay Product Performance** · *Monthly, 2nd Wed*
- **Does:** Per-listing cost, profit, sales, visibility and lifecycle for 11,123 listings.
- **Works:** Sales/fees/ads from live eBay data + organic traffic from the warehouse.
- **Benefit:** Full per-listing P&L in one report instead of stitching several.

**6. EPPA — eBay PPC Pause Automation** · *Weekly, Mon*
- **Does:** Recommends which ad campaigns to pause (out of stock / over-ACOS / burning clicks) and how much spend that saves.
- **Works:** Rule engine over live PPC + stock; a human applies the pause (never auto-writes).
- **Benefit:** Flags **£1,403 of £3,532/month ad spend at risk** — money that would otherwise burn.

**7. ESNM — Slow / No-Moving Products (eBay UK+DE)** · *Published + refresh*
- **Does:** Finds dead-stock listings among 11,156 and recommends an action (end / discount / bundle / re-price / fix).
- **Works:** 12-rule action engine over 90-day sales, stock and traffic.
- **Benefit:** Turns dead inventory into a prioritised action list.

**8. FMP — Fast Moving Products (Germany)** · *Weekly, Tue*
- **Does:** Top sellers per German channel (Shopify/Amazon/eBay DE) + combined, with stock cover.
- **Works:** Units sold over 30/90 days from raw order data; stock from German warehouse.
- **Benefit:** A restock-priority list so best-sellers don't go out of stock.

**9. EPNS — eBay Net Sales** · *Weekly, Wed*
- **Does:** True net sales per order after all fees and PPC (not gross).
- **Works:** Net = Gross − fees − PPC − general costs; ties to the eBay payout.
- **Benefit:** Shows real take-home per order, not a misleading headline number.

**10. SMP — Slow Moving Products (Germany)** · *Monthly, 4th*
- **Does:** German stock that isn't selling (inverse of FMP).
- **Works:** Stock with no/low sales over 30/90/365 days, with reason + action.
- **Benefit:** Clears dead German stock before it ties up cash.

**11. ESDT — eBay Top-50 Sales Drop** · *Monthly, 6th*
- **Does:** The 50 SKUs with the biggest £ sales loss vs the previous period.
- **Works:** Current 30d vs prior 30d £ loss on account ELECTRICALSONE; priority + action.
- **Benefit:** Focuses attention on the 50 SKUs losing the most money.

**12. SEG — PH / ASIN Segmentation** · *Monthly, 3rd*
- **Does:** Assigns 9,947 ASINs to the correct Portfolio Holder.
- **Works:** Recomputes ownership per PH, auto-splits categories.
- **Benefit:** Keeps catalogue ownership correct so nothing falls through the cracks.

---

## On-request / delivered reports

**13. T7 — Weekly SKU Performance** *(signed off)*
- **Does / Benefit:** Weekly SKU performance for Thuwaraga — 218 families, reconciled live; automated Thursdays.

**14. SMAW — Table 5 Stock Check** *(live)*
- **Does / Benefit:** Weekly full-portfolio stock check (756 ASINs), 0-mismatch — reliable stock picture for the seller team.

**15. FRRC — FBA Returns Root-Cause** *(delivered)*
- **Does / Benefit:** Root-causes every FBA ASIN returned in 30 days (91 ASINs / 105 returns), flags CRITICAL/HIGH, routes to the owner — so returns get fixed at source.

**16. ZSFO — Zero Sales Optimization** *(delivered)*
- **Does / Benefit:** Finds Utharsika's zero-selling UK ASINs (1,719 → 1,250) — a clear worklist of what to fix or drop.

**17. PC — Paused Campaign Report** *(delivered)*
- **Does / Benefit:** 33 ad targets still paused today — a reactivation review list so campaigns don't stay dark by accident.

**18. ECKR — Competitor & Keyword Research** *(delivered)*
- **Does / Benefit:** First live-eBay-scrape task — top-5 UK competitors × 9 categories for Jarsini (price, sold volume, feedback, shipping) + target keywords, our own accounts excluded.

**19. BSDT — B2B Session Drop Tracker (Amazon.de)** *(delivered)*
- **Does / Benefit:** Watch-list of German ASINs losing B2B buyer traffic, tiered by action — catches B2B demand slipping early.

**20. CHOP — Channel Opportunity** *(signed off)*
- **Does / Benefit:** 283 listing-gap opportunities — products selling on one channel but missing/weak on others, so the gap can be closed.

**21. BLOS — Project Sentinel** *(closed, validated)*
- **Does / Benefit:** Ledsone centralizer user-skill — a validated reusable capability for the team.

**22. Merged Dashboards** *(reusable)*
- **Does / Benefit:** Combines finished reports (EPPR + ESNM + ERA) into one tabbed page — one place to look instead of many.

**23. eBay Feedback AI Triage** *(build-blocked by design)*
- **Does / Benefit (when unblocked):** Auto-classifies negative/neutral eBay feedback and routes it to the right team. Held pending a business rule decision + write approval — deliberately not shipped half-built.

---

## The three things that satisfy a reviewer

1. **Correct** — every number reconciles to the live database and to the owner's own screen (e.g. DST anchored to Seller Hub £837.93).
2. **Safe** — read-only, never touches the live marketplace; automations **fail closed** (bad data publishes nothing, last good report stays live).
3. **Transparent** — every rule/threshold is written down and editable, reviewed by the business — no silent guesses or hardcoded logic.

*Full detail per task lives in each project's `PROJECT_HOME.md`.*
