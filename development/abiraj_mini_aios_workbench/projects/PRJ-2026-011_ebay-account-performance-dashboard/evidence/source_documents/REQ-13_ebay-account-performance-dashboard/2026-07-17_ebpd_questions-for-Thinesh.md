# eBay Account Performance Dashboard — A Few Things to Confirm

**For:** Thinesh  ·  **Month:** June 2026  ·  **From:** Abiraj  ·  **Date:** 2026-07-17

I've built the June eBay dashboard (Excel + web version). Before I lock it, a few points need your confirmation. I've written what I'm doing now for each, so you can just say "yes, keep it" or tell me to change it.

---

## ✅ Answers received (2026-07-17) — applied to the web dashboard

- **1. Sales** → Completed orders. **Kept.**
- **2. Revenue** → Product price **+ Postage**, both. **Applied** (June revenue is now £97,019, up from £94,684).
- **4. Stock** → Total warehouse units. **Kept.**
- **5. Accounts** → All 12 eBay accounts. **Kept.**
- **9. Sales Rank** → Not from eBay, **manually entered by the team.** Now labelled as a manual field (shown with an auto placeholder until you supply the real ranks — *please send them, or tell me where they're kept*).

- **6. Excel** → Rebuilt to all 12 accounts + postage. **Done.**
- **8. Extra AOV columns** → Confirmed a duplicate. **Removed** from both dashboard and Excel.

- **7. New Listings** → Found a real source after all: the ledsone DB `listings.ebay_listings.created_at` tracks when each listing was created. **Now populated** (June: 248 new listings across the 12 accounts — e.g. LEDSONE UK 72, Electricalsone 36).
- **3. Conversion Rate** → Now based on the **whole account, not just ads**: account conversions ÷ page-views (traffic_data eBay). Works for all 12 accounts (~1–3%). **Done.**
- **Sales Rank** → Set to **rank by revenue** (highest = #1), as instructed. **Done.**

**All questions resolved.** One heads-up: the sheet's Conversion RAG threshold (green >4.5%) was set for a different basis — real whole-account eBay conversion is ~2–3%, so most cells now read amber/red. Suggest recalibrating the threshold (e.g. green >2.5%, amber 1.5–2.5%, red <1.5%) — your call.

---

---

## Please confirm these (they affect the numbers)

**1. Which sales should count?**
Right now I count only **completed orders**. Refunded and cancelled orders are left out.
→ *Keep as is, or should refunded orders still count?*

**2. Should Revenue include postage?**
Right now Revenue is the **product price only** — postage/shipping is not included.
→ *Leave postage out, or add it in?*

**3. What does "Conversion Rate" mean to you?**
eBay doesn't give us website visits, so I calculate it as **orders ÷ ad clicks** (from Promoted Listings).
→ *Is that the formula you want, or a different one?*

**4. What should "Stock" show?**
Right now it's the **total warehouse units** for all products an account sells. Note: the same stock is shared across several accounts, so the numbers overlap.
→ *Keep this total, or would you prefer "days of stock left", or something else?*

---

## Scope — your sheet listed 4 accounts, but there are more

**5. How many accounts?**
Your sheet named **4 accounts**. In reality **12 eBay accounts** had sales in June — including **Huettenlampen (DE)**, which is actually bigger than LEDSONE DE. I've included **all 12** in the web dashboard.
→ *Keep all 12, or show only the original 4?*

**6. Excel file — match the dashboard?**
The web dashboard now has all 12 accounts. The **Excel file still has only 4**.
→ *Should I update the Excel to all 12 as well?*

---

## These fields aren't in the system — please advise

**7. "New Listings" (products newly listed in June)**
The system doesn't record **when a listing was created**, so this column shows **N/A**.
→ *Leave it as N/A, or should I use "listings updated in June" as a rough stand-in?*

**8. The extra "AOV" columns in your sheet**
Your sheet has a **second AOV block** with small numbers (11–12) that don't match the real average order value (~£20). I don't know what these were meant to be, so I've left them blank.
→ *What should these columns show?*

**9. "Sales Rank" and "PPC Rank"**
eBay doesn't provide these, so I've **ranked the accounts myself** — Sales Rank by revenue, PPC Rank by ad sales.
→ *OK to keep these as calculated ranks?*

---

## Just so you know (no action needed)

- **LEDSONE DE has no last-year advertising figures** — eBay only started giving us ad data from **September 2025**, so there's nothing to compare June 2025 against.
- **Only 5 of the 12 accounts run eBay ads** — the other 7 have no advertising, so their ad columns show "—".
- **Ireland** is set up as a marketplace but had **0 orders in June**.

---

Once you confirm the points above, I'll update both the Excel and the dashboard to match.
