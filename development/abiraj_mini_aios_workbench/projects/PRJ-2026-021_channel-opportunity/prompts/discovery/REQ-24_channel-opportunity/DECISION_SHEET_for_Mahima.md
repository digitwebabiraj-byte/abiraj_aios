# Channel Opportunity (REQ-24-D01) — Decision Sheet for Mahima

**From:** Abiraj · **Date:** 2026-08-05 · **Status:** a working draft is already built from live data
(283 opportunity rows). The figures are verified against the raw database; the items below are **business
choices** that decide the final shape. Please tick / edit each. Nothing is published until you sign off.

> How to read this: each item shows **what I built by default**, **why**, and **the alternatives**. If a
> default is fine, just write "OK". Where you change one, the report re-runs the same day.

---

## 1. Market scope
- **Default built:** Germany only (matches your Fast Moving Products report).
- **Alternatives:** all marketplaces combined · a specific set (UK + DE) · per-market separate tabs.
- **Your call:** ______________________

## 2. What "Sales" means
- **Default built:** **units sold** (quantity). Chosen because the three channels sit side by side and
  units compare cleanly across currencies.
- **Alternative:** revenue (£/€) — but marketplace revenue is in each market's own currency with no FX
  conversion available, so a revenue comparison across channels is less clean.
- **Your call:** units ☐   revenue ☐   both ☐

## 3. Time window
- **Default built:** rolling **90 days** (through 2026-08-04).
- **Alternatives:** rolling 30 days · a fixed calendar month · 6 / 12 months.
- **Your call:** ______________________

## 4. "Selling well" floor
- **Default built:** a product is only flagged if its **best channel sold ≥ 10 units** in the window
  (filters out one-off noise).
- **Alternative:** raise/lower the floor (e.g. ≥ 5, ≥ 20).
- **Your call:** floor = ______

## 5. The Opportunity classes (the thresholds)
Current default rules — a product must clear the floor in #4, then:

| Class | Default rule | Meaning | Action |
|---|---|---|---|
| **Missing channel** | sells in ≥1 channel, **0 units** in another | proven demand, zero coverage | Create the missing listing |
| **Shopify winner** | all 3 > 0, Shopify is top AND ≥ **50%** of units | strong on web, weak on marketplaces | Improve the weak marketplace listing |
| **Marketplace winner** | all 3 > 0, Amazon+eBay ≥ **60%** of units AND Shopify ≤ **20%** | strong on marketplaces, weak on web | Add Shopify promotion |
| *(Balanced)* | anything else | selling evenly — not an opportunity | *excluded* |

- **Current counts under these rules:** 270 Missing · 10 Marketplace winner · 3 Shopify winner (283 total).
- **Your call:** keep 50% / 60% / 20% as-is ☐   or change → Shopify-winner ___% · Marketplace-winner ___% & Shopify ≤ ___%

## 6. Action wording
- **Default built:** "Create <channel> listing" / "Improve <marketplace> listing" / "Add Shopify promotion".
- **Your call:** keep ☐   or preferred wording: ______________________

## 7. Combos / bundle SKUs (the one real data judgement)
Some sales are of **bundle SKUs** (e.g. `CRSF100BM+PHSH1PBRBM+LSCY290BI`). By default these appear as their
own rows (a bundle selling on Amazon but not elsewhere is a genuine opportunity). A few also carry small
account tags that can split one bundle across two rows.
- **Options:** (a) keep bundles in *(default)* · (b) exclude bundles, show single products only ·
  (c) exclude only the tag-split noise.
- **Your call:** a ☐   b ☐   c ☐

## 8. Extra columns?
- **Default built:** SKU · Shopify · Amazon · eBay · Total Units · Opportunity · Action (matches your mock-up).
- **Optional add-ons:** Category · Product name · current stock · revenue alongside units.
- **Your call:** ______________________

## 9. Where it goes (publish audience)
- **Default:** not published yet. Your FMP report went to the `german_priors` portal tab.
- **Your call:** publish to `german_priors` ☐   other tab: __________   Excel only ☐

## 10. Refresh
- **Default:** one-off build. Can be automated weekly (like FMP) after sign-off.
- **Your call:** one-off ☐   weekly auto-refresh ☐ (day/time: ______)

---

### Fixed regardless of the above (already proven against the live DB)
- Source = raw `mcp.ledsone` `order_management` (orders + order_item_info + sub_source + source); Germany = market_place 10.
- Clean-SKU step = fold the `-IDE` listing suffix so a product's listings roll into one row (verified: LDMST64E274 = 96/0/43).
- eBay is summed per SKU across all its item_ids (no sprawl double-count).
- Read-only; every number traces to the database; zeros are true zeros (proven by absence).

**Once you return this sheet, the report is finalised, reconciled again, and (if you choose) published + automated the same day.**
