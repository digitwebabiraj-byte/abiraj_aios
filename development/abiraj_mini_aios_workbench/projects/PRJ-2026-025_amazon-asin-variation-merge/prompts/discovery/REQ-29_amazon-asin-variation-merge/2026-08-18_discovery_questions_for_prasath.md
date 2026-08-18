# Questions for Prasath — Amazon ASIN Variation Merge report

**Date:** 2026-08-18 · **From:** Abiraj · **About:** the ASIN Rating Analysis & Variation Merging report
you asked for (`996_ASIN_Variation_Merge_Dashboard.xlsx`)

Hello Prasath,

I've read your requirement and set the project up. Before I build the report I need a few answers from you —
your sheet gives me the **columns** but not the **rules**, and I don't want to guess and give you the wrong
products to merge.

Most of these take a second to answer. **Question 1 is the important one** — I can't start without it.

---

## 🔴 Question 1 — Where do I get the star ratings and review counts?

**Why I'm asking:** Your report is built around finding ASINs with *no reviews* or a *low rating*. I checked
our database thoroughly, and **we do not store Amazon star ratings or review counts anywhere.** We store them
for eBay, but not for Amazon.

So right now I have no way to know which ASINs are low-rated. Everything else in your report I can get —
just not this.

**Which of these should we do?**

- [ ] **(a)** I pull the ratings directly from the Amazon website / API for each ASIN
      *(we did this for a similar project — it works, but it's slow, so it would help to limit how many
      products we check)*
- [ ] **(b)** Someone on your team downloads a report from Seller Central that has the ratings, and sends it
      to me *(if such a report exists — do you know one?)*
- [ ] **(c)** I ask Sajeesan to start storing Amazon ratings in the database
      *(he did exactly this for another project recently and it was ready the same day — this is the
      cleanest long-term fix)*
- [ ] **(d)** We build the report without ratings, and pick the merge candidates a different way
      *(you'd need to tell me what that other way is)*

**My suggestion:** (c) if you can wait a little, or (a) if you need it soon.

---

## Question 2 — Which Amazon account?

Your sheet doesn't say. We have three:

- [ ] **amazon Ledsone**
- [ ] **amazon Dcvoltage**
- [ ] **amazon SRM Amazon**
- [ ] All three

---

## Question 3 — Which country?

Your sheet says Amazon UK. Just confirming:

- [ ] **UK only**
- [ ] UK plus others *(we also have Germany, France, Spain, Italy, Ireland, US, Canada and more)*

---

## Question 4 — What counts as a "low rating"?

You wrote "low rating" but not a number. In your example rows, 2.9 and 1.8 were treated as low, and 4.4 and
4.6 were treated as good.

- **Low rating means below:** ______ stars *(e.g. 3.0? 3.5?)*
- **"No reviews" means:** [ ] exactly 0 reviews  [ ] fewer than ______ reviews

---

## Question 5 — How do I choose the parent to merge into?

When a product family has more than one possible parent, which one wins?

- [ ] The one with the **highest star rating**
- [ ] The one with the **most reviews**
- [ ] Highest rating first, and if two are equal, the one with more reviews
- [ ] Something else: ________________

**And if no good parent exists in that family** — nothing is highly rated — what should the report do?

- [ ] Skip that family entirely
- [ ] Still show it, marked "no suitable parent"

---

## Question 6 — How strict should the duplicate colour check be?

A parent can't have two children with the same colour. But our colour names are messy — I see "Black",
"black", "Black Without Bulb" and "Chrome With Bulb - 1 Pack" all in the system.

- [ ] **Exact match only** — "Black" and "black" count as *different* (safer, but will miss some duplicates)
- [ ] **Smart match** — ignore capital letters and spacing, so "Black" and "black" count as the *same*
      (catches more, small risk of a false alarm)

**Also — should I check size as well as colour, or colour only?**

- [ ] Colour only
- [ ] Colour and size

*(For context: one parent in our system has 227 children but only 51 different colour names — so this check
is going to flag a lot.)*

---

## Question 7 — What about products that are out of stock?

In your example, an out-of-stock child was rejected.

- [ ] **Always reject** out-of-stock products — don't even show them
- [ ] **Show them with a warning**, and let the operator decide

---

## Question 8 — How will you tick "Approved"?

Your rule is clear: nothing gets merged without approval. I just need to know the practical steps.

- [ ] I send you an **Excel file**, you type Y or N in the Approved column and send it back
- [ ] You want a **web page** where you click Approve / Reject and it saves automatically
      *(this takes longer to build — the Excel route is faster to get started)*

---

## Question 9 — The three things you already flagged

On your dashboard sheet you wrote: *"PH team input is required for template, sample file and variation
fields."* Could you send me:

- [ ] The **Seller Central flat-file template** you use for merging
- [ ] A **sample completed file** from a merge you've done before
- [ ] The list of **variation fields** that matter *(colour, size, anything else?)*

---

## Question 10 — Stock: which number do you mean?

- [ ] The stock quantity **shown on the Amazon listing**
- [ ] The **actual warehouse stock**

*(These are often different numbers.)*

---

## Question 11 — Later, not now

Once you've seen the first report and you're happy with it:

- Should it **run automatically** on a schedule? How often — weekly? monthly?
- Should it appear on your **portal page**, or is a file enough?

*(No need to answer today.)*

---

## What happens next

Once you answer **Question 1**, I can start building. Questions 2–8 I need before I can finish. Questions
9–11 can follow later.

If it's easier to talk it through than to write answers, that's fine — just tell me when.

Thanks,
Abiraj

---

### For the file (internal — not part of the message to Prasath)
Maps to `PROJECT_HOME.md` open items: Q1→#1 · Q2→#2 · Q3→#3 · Q4→#4 · Q5→#6 · Q6→#7 · Q7→#8 · Q8→#9 ·
Q9→#10 · Q10→(stock definition, noted under #8/traps) · Q11→#11. Open item **#5** (which parent definition
is authoritative — `amazon_listings.parent_sku`/`is_parent` vs `amz_sales_and_traffic_by_asin.parent_asin`)
is **deliberately not asked** — it is a technical modelling decision for Sajeesan/Abiraj, not a business
question Prasath can be expected to answer. Resolve it internally and record the choice in
`SYSTEM_REFERENCE.md` §3.
