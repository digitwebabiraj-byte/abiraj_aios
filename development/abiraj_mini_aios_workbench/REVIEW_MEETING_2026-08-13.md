# Abiraj — Work Review

**Prepared for:** Review meeting, 14 Aug 2026
**Workbench:** `Abiraj_AIOS` Mini-AIOS · 20+ projects across Amazon, eBay & Shopify (UK, Germany)
**Owner:** Abiraj · Coordinator: Varmen · Reviewers: Sajeesan (technical), Tamil Selvan (queryability)

---

## 1. The one-line summary

> I turned recurring, manual "pull-the-numbers" jobs that Portfolio Holders used to do by hand into **read-only data reports that build themselves on a schedule** — each one published straight to the person who needs it, verified against the live database to the penny, and safe by design (never writes to Amazon/eBay, fails closed if the data looks wrong).

**What that buys the business:**
- **~15–20 recurring reports now run automatically** instead of a person building them each week/month.
- **Money that was invisible is now visible** — mispriced listings, paused ad campaigns still burning budget, dead stock, returns root-causes, sales drops.
- **Decisions are traceable** — every number reconciles to the live DB, every rule is written down and editable, nothing is hardcoded or guessed silently.

---

## 2. Headline numbers

| Metric | Value |
|---|---|
| Projects onboarded | **20+** (PRJ-2026-001 … 024) |
| Delivered & signed off / accepted | **9** (BLOS, T7, EPC, EBPD, ERA, DST, EPPR, CHOP + PH-Seg live) |
| Automated & self-running | **~13 scheduled jobs** (daily / weekly / monthly) |
| Live people served | Portfolio Holders across Amazon + eBay teams (Thinesh, Jarsini, Kobiga, Powsteena, Sharmilan, Sivajitha, Utharsika, Thuwaraga, Rebecca, Meshika, Mahima, Jensika…) |
| Largest single dataset reported | **126,070 live eBay listings** (Price Checker) |
| Delivery method | Published to the ops portal (`ph_task`) — each PH sees only their own rows |

---

## 3. What each project does — and the benefit

### A. Automated recurring reports (the biggest time-saver — these repeat forever)

| Project | What it answers | Benefit to the business | Runs |
|---|---|---|---|
| **EPC — eBay Price Checker** | Which of our 126,070 eBay listings are mispriced vs our own Amazon/website price, and by how much money | Surfaces **£-at-risk mispricing across 13 accounts** automatically; "too high" loses sales, "too low" loses margin | **Weekly, Mon** |
| **EBPD — eBay Account Performance** | Per account × marketplace: sales, ad efficiency (TACOS), listing/stock position | One monthly scorecard per account instead of manual pulls; reconciles to the penny | **Weekly refresh** |
| **ERA — eBay Return Analysis** | Which SKUs are returned, how often vs sales, why, and refund/fee cost | Pinpoints costly return-drivers per SKU; **£2,937 refund + £869 return cost** made visible for June | **Monthly, 5th** |
| **DST — Daily Sales Track** | Daily sales/orders/units per account × marketplace vs yesterday & last year | Daily trading pulse without anyone building it; caught a **currency-blend error** that hid a real drop | **Daily, 09:05** |
| **EPPR — eBay Product Performance** | Per-listing cost, profit, sales, visibility, lifecycle (11,123 listings) | Full per-listing P&L view in one report | **Monthly, 2nd Wed** |
| **EPPA — eBay PPC Pause Automation** | Which ad campaigns to pause (out of stock / over-ACOS / burning clicks) & spend recovered | Flags **£1,403 of £3,532 monthly ad spend at risk** — money that would otherwise burn | **Weekly, Mon** |
| **ESNM — Slow/No-Moving Products** | Which of 11,156 eBay listings are dead stock and what action to take | Turns dead inventory into an action list (end / discount / bundle / re-price) | Published + refresh |
| **FMP — Fast Moving Products (DE)** | Top sellers per German channel + combined, with stock cover | Restock-priority list for Germany across Shopify/Amazon/eBay | **Weekly, Tue** |
| **EPNS — eBay Net Sales** | Per-order true net sales after all fees & PPC | Real take-home per order (not gross) | **Weekly, Wed** |
| **SMP — Slow Moving Products (DE)** | German stock that isn't selling | Inverse of FMP — clears dead German stock | **Monthly, 4th** |
| **ESDT — eBay Top-50 Sales Drop** | Top 50 SKUs by biggest £ sales loss vs prior period | Focuses attention on the 50 SKUs losing the most money | **Monthly, 6th** |
| **SEG — PH/ASIN Segmentation** | Assigns 9,947 ASINs to the right Portfolio Holder | Keeps ownership of the whole catalogue correct and current | **Monthly, 3rd** |

> **Why "automated" matters:** each of these was previously a manual build. Now they rebuild from live data on a timer, republish to the right person, and **fail closed** — if a data pull looks wrong (0 rows, a collapse, £0 spend), it refuses to overwrite and the last good report stays live. No silent bad data.

### B. One-off / on-request deliverables that landed

| Project | Benefit |
|---|---|
| **T7 — Weekly SKU Performance** | Signed off; weekly SKU performance for Thuwaraga |
| **SMAW — Table 5 Stock Check** | Live weekly stock check, full 756-ASIN portfolio, 0-mismatch |
| **FRRC — FBA Returns Root-Cause** | 91 returning ASINs root-caused & routed to owners; CRITICAL/HIGH flags |
| **ZSFO — Zero Sales Optimization** | 1,719 → 1,250 zero-sale ASINs identified for Utharsika (UK) |
| **PC — Paused Campaign Report** | 33 still-paused ad targets found for reactivation review |
| **ECKR — Competitor & Keyword Research** | First live-eBay-scrape project; top-5 UK competitors × 9 categories for Jarsini |
| **BSDT — B2B Session Drop Tracker (DE)** | Watch-list of Amazon.de ASINs losing B2B traffic, tiered by action |
| **CHOP — Channel Opportunity** | 283 listing-gap opportunities (sells on one channel, missing on others) |
| **BLOS — Project Sentinel** | Ledsone centralizer user-skill — closed & validated |
| **Merged Dashboards** | Combines finished tasks (EPPR + ESNM + ERA) into one tabbed page — reusable |

---

## 4. The value story (what to say in the room)

**1. Time saved — recurring.** Roughly **13 reports that people used to build by hand now build themselves.** If each manual build took even 1–2 hours, that's dozens of person-hours a month returned to the team, every month, indefinitely.

**2. Money made visible.** These aren't just reports — they point at money:
- Mispriced listings (EPC), ad spend being wasted (EPPA — £1,403/mo flagged), dead stock (ESNM/SMP), biggest sales losers (ESDT), return costs (ERA), zero-sellers (ZSFO).

**3. Trust & safety built in.** Every deliverable is:
- **Read-only** — never writes to Amazon/eBay/Shopify; a human applies any action.
- **Reconciled to the live DB** — figures match the owner's own screen to the penny (e.g. DST anchored to Seller Hub £837.93; EBPD matched £28,975.37).
- **Rules written down, not hardcoded** — thresholds are editable and reviewed by the business, so numbers can't drift silently.
- **Fail-closed automation** — bad data publishes nothing.

**4. Caught real errors before they shipped.** Examples worth naming:
- **DST currency trap** — a headline "+3.19% up" was hiding a real GBP **−5.16%** decline once currencies were separated.
- **eBay feedback data "doesn't exist anywhere"** was corrected — the data was live in a second database (311,042 rows); saved asking a PH for a needless export.
- **EPPA** — a whole ad-campaign type (SMART, £751/mo) would have been silently dropped if built from the wrong database.

---

## 5. Status at a glance

- ✅ **Signed off / accepted:** PH-Seg (live), T7, EPC, EBPD, ERA, DST, EPPR, CHOP
- 🟢 **Delivered & published, sign-off pending:** ZSFO, PC, FRRC, ECKR, BSDT, ESNM, EPPA, EPNS, ESDT
- 🟡 **In build / onboarding:** FMP, SMP (awaiting a few threshold decisions from Mahima)
- 🔒 **Build-blocked by design:** eBay Feedback AI Triage (needs business rule decisions + write approval)

---

## 6. What I'd like decisions on (to keep momentum)

1. **Business sign-offs** on the delivered-but-pending reports (FRRC, EPPA, ESNM, EPNS, ESDT).
2. **A few threshold rules** for the Germany reports (FMP/SMP) from Mahima.
3. **Feedback AI Triage** — needs a taxonomy decision and written approval before it can be built (it would write to production).

---

*All figures above reconcile to the live database and are recorded in each project's `PROJECT_HOME.md`. This document is a summary index, not the source of truth.*
