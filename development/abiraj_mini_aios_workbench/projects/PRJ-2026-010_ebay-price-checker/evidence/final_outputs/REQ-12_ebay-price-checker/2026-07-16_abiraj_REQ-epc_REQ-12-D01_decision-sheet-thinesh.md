# eBay Price Checker — Decision Sheet

**To:** Thinesh  **From:** Abiraj  **Date:** 2026-07-16  **Ref:** REQ-12-D01

Your price checker is **built and running on live data** — all 76,126 live eBay UK listings, refreshed daily.

**Your target rule is correct.** I checked it against reality: your eBay prices already sit a median **9.11% below Amazon**, and your rule targets Amazon −10%. It is almost exactly right.

Before anyone acts on the report, **8 questions**. Each one changes real numbers. Every question has a recommended answer — if you agree with all of them, just reply **"all defaults"**.

---

## Q1 — When a product has more than one Amazon price, what do we use?

**Affects 13,834 listings (18% of the report) — the single biggest item.**

Your rule says never silently accept a duplicate match. But it doesn't say what to *do* with one. Right now those listings show **DATA MISSING** with no target — even though the prices are sitting there.

> **Example:** `CL3RBR5PK` has **5 different Amazon prices** (listed by more than one of our accounts / as several offers). Your eBay price is £13.49. We don't know which Amazon price to measure against.

| | Option |
|---|---|
| **A ✅ recommended** | Use the price from **one nominated Amazon account only** (see Q3). Deterministic, and honours your "never blend" rule |
| B | Use the **lowest** Amazon price |
| C | **Skip Amazon**, fall back to the website price |
| D | Leave as DATA MISSING (what it does today) |

**Cost of getting it wrong:** 13,834 listings either get a target price or stay blank.

**Your answer: ______**

---

## Q2 — What is the target price for a bundle/kit?

**Affects 9,113 listings (12%) — half of everything we genuinely cannot price.**

Many eBay listings are multi-product kits. They don't exist as a single product on Amazon or the website, so there is nothing to compare them to.

> **Example:** `CRSF100BM+PHCH1BMRBM+LSCY290BM+ICST64E27` — a 4-component kit, sold on eBay at £20.89. No such single product exists on Amazon or the website.

| | Option |
|---|---|
| **A ✅ recommended** | **Exclude bundles** from the report. This report is about price parity; a bundle has no comparator |
| B | **Add up the component prices**, then apply the normal rule |
| C | Leave as DATA MISSING |

**Cost of getting it wrong:** 9,113 listings — and if we guess a bundle target wrongly, we'd tell someone to reprice a kit against a single bulb.

**Your answer: ______**

---

## Q3 — Which Amazon account is "the approved Amazon source"?

**Affects ~5,800 listings.**

We sell on **three Amazon UK accounts** — `amazon Ledsone`, `amazon Dcvoltage`, `amazon SRM`. The same product is often on more than one, at **different prices**. Your rule says "the approved Amazon PostgreSQL source" but doesn't name which.

| | Option |
|---|---|
| **A ✅ recommended** | **`amazon Ledsone`** only — the largest (16,266 UK listings). This is what the current report uses |
| B | Whichever account also sells that product (may differ per row) |
| C | All three, and flag any disagreement |

**Cost of getting it wrong:** ~5,800 listings currently show DATA MISSING purely because their Amazon price lives on a different account.

**Your answer: ______**

---

## Q4 — Is the tolerance threshold £15 or £20?

**Affects 1,712 listings.**

Your sheet says **both**, in two places:

- **Legend (A24):** "£0.50 (under £15) or £1.00 (£15 and above)"
- **Table (E25:G27):** "Below £20 → ±£0.50; £20 and above → ±£1.00"

| | Option |
|---|---|
| **A ✅ recommended** | **£20** — the band table is the more explicit statement |
| B | £15 |

**Cost of getting it wrong:** 1,712 listings flip between "fine" and "needs action".

**Your answer: ______**

---

## Q5 — The tolerance is tighter than our actual pricing. Accept, or widen?

**This decides whether the report is usable.**

**70% of your listings currently flag as mispriced** (39% too high, 31% too low). That is **not a bug** — I verified it. Your rule is well-centred; the issue is that ±£0.50 on a £10 item is only **±5%**, while your real prices scatter about **±10%** around target.

So the report is telling the truth — it's just flagging **30,853 listings**, which nobody can work through.

| | Option |
|---|---|
| **A ✅ recommended** | Change the tolerance to a **percentage** (e.g. ±10%) so it matches how prices actually vary |
| B | Keep ±£0.50/±£1.00 and accept a 70% flag rate |
| C | Keep the rule, but only report the **worst N** listings each week |

**Cost of getting it wrong:** an exception report that flags almost everything gets ignored, and the genuinely bad prices hide in the noise.

**Your answer: ______**

---

## Q6 — How should Priority be set?

**Affects every row.**

There is **no priority rule** in any document. Your sample rows show: Normal → `Low`, anything flagged → `High`. I've used that. But the new **DATA MISSING** status has no priority at all, and **I have guessed `High`** — that value has no basis in anything you've written.

| | Option |
|---|---|
| **A ✅ recommended** | Confirm the mapping above, and tell me what DATA MISSING should be |
| B | Set priority by **money at risk** (bigger £ gap = higher priority) |
| C | Set priority by **sales volume** (mispriced bestsellers first) |

**Your answer: ______**

---

## Q7 — German accounts: in or out? And what is SUNSONE?

Your sheet names seven accounts, three of them German — `LEDSONE UK REG DE`, `LEDSONE DE`, `SUNSONE DE`.

**Two problems:**

1. **The report is UK-only right now.** Your tolerances are in **£**, but German listings are priced in **EUR**. Comparing them needs an exchange-rate rule that doesn't exist yet.
2. **`SUNSONE UK` and `SUNSONE DE` do not exist in our database under any name.** Our 13 real eBay accounts are: `led_sone`, `electricalsone`, `so_926407`, `ledsonede`, `coventrylights`, `huettenlampen`, `vintageinterior`, `re6865`, `dctransformer`, `lighting_sone`, `homin_gmbh`, `neighbourmarket`, `bestbringer`.

**Questions:**
- Do you want the German accounts in this report? If yes, what exchange rate rule?
- **What are SUNSONE UK and SUNSONE DE actually called?** Which of the 13 are they?
- Is `LEDSONE UK REG DE` an account, or the `led_sone` account selling on the German marketplace?

**Your answer: ______**

---

## Q8 — Status wording: we already have one (needs Sajeesan too)

We **already have a live pricing status vocabulary** in the system, used by the existing pricing work:

`SAFE_TO_LIST` · **`PRICE_TOO_LOW`** · `REVIEW_REQUIRED` · `MD_EXCEPTION_REQUIRED` · `COST_DATA_MISSING` · `SHIPMENT_DATA_MISSING` · `COMPETITOR_EVIDENCE_MISSING` · `APPROVED`

Your four values overlap it without matching:

- Your **Low Price** ≈ existing **`PRICE_TOO_LOW`** (which already says *"increase price or escalate"*)
- Your **Normal** ≈ existing **`SAFE_TO_LIST`**
- Your **DATA MISSING** maps to **three** existing statuses at once
- Your **High Price** has **no equivalent** — the existing vocabulary has no "too expensive" state

If we ship yours as-is, the company has **two competing pricing vocabularies**. That's a governance stop.

| | Option |
|---|---|
| **A ✅ recommended** | **Map onto the existing 8** where they match, and add "too expensive" as a new value |
| B | Keep your 4 and justify why this is a separate thing |
| C | Extend the existing 8 |

**Needs:** Thinesh + **Sajeesan**.

**Your answer: ______**

---

## What happens after you answer

- **Q1 + Q2 + Q3** together would cut DATA MISSING from **41.9% → roughly 18%**, with no new data needed.
- **Q5** decides whether the report is a usable shortlist or a 30,853-row wall.
- **Q8** decides whether it can ship at all.

Nothing is published or sent to anyone until you've signed this off.

---

### For reference — what already works

| | |
|---|---|
| Rows | **76,126** — every live eBay UK listing |
| Data | Live, refreshed daily (last: 2026-07-15) |
| Your target rule | **Verified correct** — median eBay is 9.11% below Amazon vs your −10% rule |
| Target from Amazon | 30,039 (39.5%) |
| Target from website | 14,151 (18.6%) |
| No target yet | 31,936 (41.9%) — **Q1–Q3 fix most of this** |

**File:** `2026-07-16_abiraj_REQ-epc_REQ-12-D01_price-checker.xlsx`
