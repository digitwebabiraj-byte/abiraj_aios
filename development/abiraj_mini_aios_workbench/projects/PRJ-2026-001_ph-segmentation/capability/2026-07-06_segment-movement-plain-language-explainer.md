# Segment & Movement — Plain-Language Explainer (Bietrick clarification)

## What this is

A reusable, plain-language explanation of how the PH dashboard's **segments** and **movement** work,
and how the **filter chips combine**. Written 2026-07-06 to resolve end-user (Bietrick) confusion about
how a top segment can show an "Improved" count, and whether "New" is needed. Reusable for any future PH
or reviewer with the same questions.

- **Scope note:** this is a **clarification / knowledge artifact**, independent of the 2026-07-06 D09
  housekeeping requirement (backup-table cleanup). It records no live-DB action.
- **Source of truth:** the classification logic in the live dashboard JS
  (`evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-07-02_ph_asin_dashboard_v3_cards_preview.html`)
  and the strict-rank movement rule adopted in REQ-05-D07. Numbers below are counted from the 24
  imported per-PH views (`.../2026-07-02_ph_per_holder_views/`).

---

## 1. The segment code (where a product stands now)

Each product gets a 3-letter code — each letter is **High or Low** of one signal, versus its per-PH,
per-category benchmark:

| Letter position | Signal |
|---|---|
| 1st | **Impressions** (H/L) |
| 2nd | **Clicks** (H/L) |
| 3rd | **CVR / conversion** (H/L) |

The six named segments, best → worst:

| Rank | Segment | Name |
|---:|---|---|
| 1 | HHH | Champions |
| 2 | HHL | Leaky Buckets |
| 3 | HLH | Wallflowers |
| 4 | LHH | Hidden Gems |
| 5 | LLH | Niche Winners |
| 6 | LLL | Dead Horses |

(The "strict rank" 1–6 was adopted in D07 so every segment is a distinct rung — replacing the older
tie where HHL/HLH/LHH counted equal.)

---

## 2. Movement (how a product changed vs LAST month)

Movement compares **this month's segment rank vs the same product's rank last month** — the product
against **its own past**, not against HHH.

- **Improved** = moved **up** the ladder (was on a lower rung last month).
- **Declined** = moved **down** the ladder (was on a higher rung last month).
- **Same** = stayed on the same rung.
- **New** = **wasn't on the ladder at all last month** — nothing to compare, so no up/down can be given.

---

## 3. The two things that can NEVER happen (this is the confusing part)

Because the ladder has a top and a bottom, movement is asymmetric at the ends:

- **HHH (top) can never be "Declined."** Nothing is above rank 1 to fall from. It can only be Improved,
  Same, or New.
- **LLL (bottom) can never be "Improved."** Nothing is below rank 6 to climb from. But it **can** be
  Declined — products fall *into* the bottom from higher segments.

**Verified in the real data (24 per-PH views, 2026-07 cycle):**

| Segment | IMPROVED | DECLINED | SAME | NEW |
|---|---:|---:|---:|---:|
| HHH (top) | 46 | **0** ← never | 4 | 1 |
| LLL (bottom) | **0** ← never | 530 | 6378 | 180 |

So "HHH + Improved = 46" is real: those are products that **climbed up into Champions** from a lower
segment. "HHH + Declined = 0" always. And the mirror: "LLL + Declined = 530" is real (products fell to
the bottom), while "LLL + Improved = 0" always.

### Worked example (HHL)
- **HHL + Improved** = rose into HHL from any lower rung — HLH, LHH, LLH, or LLL (one of four sources).
- **HHL + Declined** = fell into HHL from the only rung above it — **HHH only** (exactly one source).

---

## 4. Why "New" is a separate category (and is NOT about impressions)

A common wrong guess: *"New means impressions went from 0 to some number."* **False.**

**New means the product was not in last month's window at all**, so there is **no previous segment to
compare** — you cannot honestly call it Improved/Declined/Same. Its current traffic is irrelevant to the
label.

**Verified:** NEW rows in the data have impressions ranging from **1 up to 6,972**. A brand-new product
can land straight into a strong segment with thousands of impressions and still be "New" — because it
simply had no "before" picture.

Without a New bucket, a first-seen product would have to be forced into "Same" or "Improved," which
would be a lie. New = "first time seen, no history yet."

> Returning-aware note (from D06): a product absent from the narrow 4-week previous window but present
> further back (8-week lookback) is **not** called New — it is "returning." So New = genuinely no recent
> history, not merely "outside the narrow window."

---

## 5. How the filter chips combine (segment × movement = intersection / AND)

On the dashboard, the **Segment mix** chips and the **Movement** chips are two independent single-select
filters. Clicking one segment and one movement shows the rows that match **both** — the intersection
(logical AND), applied in the render step:

```
list = this PH's rows
if a segment chip is on → keep only that segment
if a movement chip is on → AND keep only that movement   (and category too, in the per-PH builds)
```

- One segment and one movement at a time (clicking another **replaces**, it does not add a second).
- Click the same chip again to switch it **off**.
- **The numbers on the chips are static** — they are full-portfolio totals, counted before filtering, so
  they do **not** shrink when you combine filters. The true count of what you're viewing is the hint line
  above the table ("— N shown · segment HHL · DECLINED"). Trust that, not the chip badges.

Example: `HHL` + `DECLINED` → "Leaky Buckets that slipped this month" (former Champions now HHL) — an
action list, not the sum of the two chip numbers.

---

## 6. One-line answer for a leader

> Improved/Declined = the product moved **up or down our 6-step ranking vs last month**; the **top step
> can't decline**, the **bottom step can't improve**, and **"New" just means it wasn't there last month
> to compare** (nothing to do with how many impressions it has).
