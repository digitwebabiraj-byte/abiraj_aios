# Decision sheet — BGCT Keyword Workflow (REQ-30 / `bgct`)

**Date:** 2026-08-19 · **From:** Abiraj (AIOS) · **To:** **Thuwaraga** *(assigned by HR, 2026-08-19)*

**Good news first:** we checked the database and **everything this workflow needs to read is already there** —
the Search Query Performance (SQP) data, the sales history, and the title, bullets, description and backend
keyword fields for both accounts. Nothing is missing. **We are not blocked on data.**

What we need from you is a set of decisions the specification doesn't state. Each one below changes the
numbers in the report, so we don't want to guess. Please answer inline; a one-line answer per question is
enough.

---

## Q0 — ✅ Answered: who owns this report?
The source document is addressed to the "Automation Team" and mentions an "MD instruction", but names no
person. **HR has assigned this to you, Thuwaraga** (`staff.users` id 122) as the end user and Business
Validator — so the answers below are yours to give, and you are the sign-off for the finished report.

---

## Q1 — ✅ ANSWERED by Abiraj 2026-08-19: **report only, no automatic push**
*(Thuwaraga: please confirm you agree.)*

### Original question
Section 2.7 says clicking *Add Missing Keywords* writes to the live listing automatically via SP-API.

**Editing a live Amazon listing is permanent and public** — if a rule is wrong, thousands of listings are
changed before anyone notices, and there is no undo. AIOS has no Amazon write credential, and creating one is
outside this workbench's remit.

| Option | What you get |
|---|---|
| **(a) Report only — recommended** | Every gap listed with exactly where the keyword should go (backend / bullets / both), reviewed by a person, who then applies it. Safe, and we can start now. |
| (b) Report + push | Requires a separate, separately-approved system, an Amazon write credential, and written owner sign-off. A later phase, not this one. |

**Your answer:** ______________________

---

## Q2 — Phase 1: keep the manual Seller Central steps, or take it from the database?
Phase 1 is written as 8 manual steps (log in → Brand Analytics → ASIN View → set the range → sort → filter →
export CSV), repeated per ASIN.

**That export already sits in our database** — 137,048 rows of SQP for LEDSone UK alone, covering 3,368 ASINs
and 71,679 distinct search terms. We can produce the same result with a query, with no Seller Central work
at all.

| Option | What you get |
|---|---|
| **(a) From the database — recommended** | Phase 1 becomes automatic. Matches the "zero manual lookup" instruction. |
| (b) Keep the manual export | Someone still downloads a CSV per ASIN each month, and we read that file instead. |

**Your answer:** ______________________

---

## Q3 — Accounts: the same ASIN sometimes sits under both
The rule "DCVOLTAGE UK and LEDSone UK are never merged" is clear. But in the data, the *same ASIN* is
sometimes listed under both accounts — e.g. `B0CNPZDQHZ` appears under DCVOLTAGE as SKU `LDMG95E278-DC` and
under LEDSone as `LDMG95E278-DC_DCVV`.

Should each account's report only ever consider **that account's own listing rows** (so the same ASIN can
legitimately appear in both reports, judged separately)? Or should an ASIN belong to one account only?

**Your answer:** ______________________

---

## Q4 — "Last 3 months" — the data comes in weeks, not months
Amazon gives us SQP **weekly**. There is no monthly row. We can add weeks up into months, but two things
follow:
- Volumes and counts add up fine; **rates and shares have to be recalculated**, not averaged.
- **DCVOLTAGE's data currently stops on 2026-07-25, LEDSone's runs to 2026-08-08** — two weeks apart. If we
  run "last month" today, one account would get a complete month and the other a partial one.

Questions: should a "month" be calendar months, or rolling 4-week blocks? And when the two accounts are at
different freshness, do we (a) run each to its own latest complete month, or (b) hold both back to the
older account's latest complete month so they're comparable?

**Your answer:** ______________________

---

## Q5 — What counts as a "Top-Moving" ASIN?
Step 1 says "rank ASINs by units/sessions" but gives no cut-off.

- Rank by **units ordered**, by **sessions**, or a combination?
- **Top how many** per account — top 20? top 50? — or everything above a threshold (e.g. 10+ units a month)?
- Over what window — the last 30 days, or the same 3 months as the keywords?

**Your answer:** ______________________

---

## Q6 — ✅ ANSWERED by Abiraj 2026-08-19: **strip pack sizes, trailing letters AND account suffixes** — all are the same product.
**Bundle SKUs (`A+B+C`) are kept whole** — they are their own product. *(This part was decided by us: splitting them grouped 1,151 unrelated products together. Thuwaraga: please confirm.)*

### Original question
The example (`LDMG95E278` = `LDMG95E2782PK` = `LDMG95E2785PK`) is real. But the live data has more than pack
sizes on the end of a SKU:

`LDMG95E278 M` · `LDMG95E278 R` · `LDMG95E278-a` · `LDMG95E278-DC` · `LDMG95E278-DC_DCVV` ·
`LDMG95E2782PK_AMD` · `LDMG95E2782PK_KP` · `LDMG95E2783PK A` · `LDMG95E2785PK_AMN` ·
and Amazon-generated junk like `amzn.gr.TPOSBDBM-87P0SJqtG2g1zCHyzPHJ-LN`.

Which of these should be stripped as "same product"? In particular:
- trailing single letters (` M`, ` R`, ` A`, `-a`) — same product or different?
- account markers (`_DCVV`, `_AMD`, `_AMN`, `_KP`, `_AML`, `-DC`) — same product?
- composite/bundle SKUs like `WCDTBM2PK+RPR44WH2PK` — treat as their own product, or split?

**Your answer:** ______________________

---

## Q7 — Which "SKU mapping table" do you mean?
Step 2 says to correct a wrong SKU "against the SKU mapping table". Our listings table has a `mapped_sku`
column and a `wrong_sku` flag. **Is that the mapping table you mean**, or is there a separate sheet the team
maintains? *(Note: another AIOS project already found `mapped_sku` to be partly unreliable, so we'd rather
confirm than assume.)*

**Your answer:** ______________________

---

## Q8 — Exactly what is a "sales drop" and a "zero sales" listing?
- **Sales Drop** — "orders declined or stopped over the last 3 consecutive months". Does that mean each month
  lower than the one before (strictly falling), or simply this month materially lower than 3 months ago? If
  the latter, **by how much** — any drop at all, or more than X%?
- **Zero Sales** — "no orders at all in the last 6 months". Zero **units ordered**, or zero **revenue**?
  (They can differ with refunds and cancellations.)
- Should a listing with **no stock** be excluded? A dead listing that's simply out of stock isn't a keyword
  problem.

**Your answer:** ______________________

---

## Q9 — ✅ ANSWERED by Abiraj 2026-08-19: **option (b) — all the words present anywhere, in any order**, ignoring capitals and punctuation.

### Original question
The backend keyword field isn't a tidy list — it's one long run of words. A real example from one of your
listings:

> *"E27 LED retro vintage g95 8w led dimmable globe edison style filament bulb smoked gold glass b22 edison
> screw energy class a+ …"*

So for a search term like **"dimmable led bulb e27"**, which of these counts as present?
- (a) the exact phrase, in that order, together
- (b) all the words present somewhere, in any order — **the looser, more forgiving option**
- (c) something in between (e.g. all words present, ignoring plurals and capitals)

Also: should **"bulbs" match "bulb"** (plurals), and should punctuation and capitals be ignored? (We'd
suggest ignoring capitals and punctuation regardless.)

**Your answer:** ______________________

---

## Q10 — How many keywords per ASIN, and which ones?
- Step 5 says "record the top 30–50 terms". **Pick a number** — 30, or 50?
- Step 6 says filter out zero-conversion terms and cross-filter on click rate and ASIN share. **Any specific
  thresholds**, or just "drop anything with zero purchases"?
- Step 7 describes long-tail terms (3–6 words, 50–500 searches/month). Should those be **included in the same
  list**, or shown as a **separate long-tail section**?
- Small technical one: the export asks for a column called `click_rate`. Amazon gives us two — the **overall
  click rate for that search term** and **your ASIN's share of those clicks**. Which do you want?

**Your answer:** ______________________

---

## Q11 — Who receives it, and when does it run?
Monthly is agreed. We need:
- **Which day** of the month it should run.
- **Who** should receive it (the AIOS `ph_task` audience), or whether it's an Excel file sent to a person.
- Whether the two accounts arrive as **two separate reports** or one file with two clearly separated tabs.

**Your answer:** ______________________

---

## Q12 — Some listings have no content at all. How should those be shown?
We found that **20% of LEDSone UK listings have a completely empty backend keyword field**, and **11% are
title-only** — no bullets, no description at all.

For one of those, every single keyword comes back "missing" — not because 50 keywords were each overlooked,
but because there is nothing on the listing to search. In our test pair the dead listing had **156 characters
of content in total** and an empty backend field.

Would you rather see:
- (a) one row saying **"this listing has no content — needs a full rewrite"** — **recommended**, or
- (b) all 50 keywords listed individually as gaps, or
- (c) both: the "no content" flag, with the keywords available underneath.

**Your answer:** ______________________

---

## One thing we found that we've already corrected
The specification's Step 1 implies finding zero-sale listings by looking in the sales report. We checked: the
sales report only contains an ASIN on days it received traffic, so **4,650 of your 16,963 LEDSone UK ASINs
(27%) don't appear in it at all** — the deadest listings are precisely the ones missing from it. We'll start
from the full product list instead and treat "not in the sales report" as zero sales. No decision needed from
you; we just wanted you to know the method differs slightly from the written spec, and why.

---

## Where we stand (2026-08-19)
**Q1, Q6 and Q9 are answered** — those were the three that decided what gets built and how big it is.
Measured result under those rules: **58 candidate ASIN pairs at a Top-50 cut-off** (27 DCVOLTAGE + 31
LEDSone), roughly 1,700 keyword rows. The next most useful answer is **Q5** — Top 20, 50 or 100 — which
moves that to 10 / 58 / 111 pairs.

## What happens next
The build can start. The remaining questions refine it and can be answered as we go. We will not
choose any of the above on your behalf — if we need a placeholder to demonstrate a first version, it will be
labelled in the output as an unconfirmed default.

**Reference:** full technical detail in `SYSTEM_REFERENCE.md`; the measured evidence behind every number
quoted here is in `evidence/logs_or_screenshots/REQ-30_amazon-keyword-gap-sync/2026-08-19_data_foundation_probe.md`.
