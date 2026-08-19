# Implementation plan — how we build REQ-30 exactly as the requirement document specifies

**Date:** 2026-08-19 · **Source:** `BGCT_Keyword_Workflow_Phase1_Phase2_v2.1.pdf` ·
**Status:** PLAN — not yet built. Per the workbench rule, a GPT-approved implementation prompt is required
before code is written.

This maps **every numbered step in the requirement document** to exactly what the build will do, which table
it uses, and whether the rule is confirmed or still open.

**Confirmed rules applied throughout** (Abiraj, 2026-08-19 — Thuwaraga's confirmation still pending):
- **Q1** — report only. **No write to Amazon.**
- **Q5** — Top-Moving = **above 5 units in ALL 3 months** (May/Jun/Jul 2026) → **103 ASINs**.
- **Q6** — base SKU = strip pack size, trailing letters, account suffixes. **Bundles (`A+B+C`) stay whole.**
- **Q8** — sales drop = **strictly falling** (May > Jun > Jul). Zero sales = 0 units in 6 months,
  catalogue-anchored.
- **Q9** — a keyword is "present" if **all its words appear anywhere** in the text, any order, ignoring case
  and punctuation.
- **Q12** — listings with **no content at all are split into Part A** (one row each, "needs rewrite"), not
  reported keyword-by-keyword.

**✅ Final pilot on this rule set (2026-08-19): 79 candidate pairs → Part A 39 empty listings + Part B 40
listings / 1,130 keyword rows (922 real gaps).** See
`evidence/logs_or_screenshots/REQ-30_.../2026-08-19_feasibility_assessment.md` §11.

---

# PHASE 1 — collect the proven keywords

### Step 1 — Identify Top-Moving ASINs
> *Document:* "Pull the Business Report … separately for DCVOLTAGE UK and LEDSone UK. Rank ASINs by
> units/sessions and record each Top-Moving ASIN together with its SKU."

**Build:** query `business_reports.amz_sales_and_traffic_by_asin`, `market_place = 23`, **run separately for
`sub_source = 6` and `sub_source = 8`**. Rank by `SUM(units_ordered)` descending, carrying `SUM(sessions)`
as the secondary figure. Join `listings.amazon_listings` for the SKU.

✅ **The rule is a MONTHLY THRESHOLD, not a Top-N** (requester, 2026-08-19): an ASIN is Top-Moving if it
had **sales above 5 units** in the months of the period. Period = the document's Step 4 window, the **last 3
complete months** (May/June/July 2026; August excluded, data ends on the 17th).

Measured 2026-08-19 — all 3 months contained qualifying ASINs (DCV 154/143/149, LEDSone 178/178/164):

| Qualifying rule | DCVOLTAGE | LEDSone | **Distinct ASINs** |
|---|---|---|---|
| above 5 in ≥1 of 3 months | 290 | 331 | **621** |
| above 5 in ≥2 of 3 months | 109 | 133 | **242** |
| **above 5 in all 3 months** | 47 | 56 | **103** ← *recommended* |

6-month fallback (the document's "extend to 6 if thin"): 913 / 218 / 25 respectively.

✅ **CONFIRMED (Abiraj, 2026-08-19): above 5 units in ALL 3 months → 103 Top-Moving ASINs.**
Pilot run on this rule produced **71 candidate pairs** and **2,212 report rows** — see
`evidence/logs_or_screenshots/REQ-30_.../2026-08-19_feasibility_assessment.md` §10.

### Step 2 — Brand Analytics → SQP → **ASIN View**
> *Document:* navigate Seller Central; use ASIN View, not Brand View.

**Build:** `business_reports.amz_search_query_performance` is **already ASIN-level** (it has an `asin`
column), which is exactly the ASIN View the document requires. Brand-level aggregation is never used.
No Seller Central navigation needed — see *Deviation 1* below.

### Step 3 — Enter one Top-Moving ASIN, loop per ASIN
> *Document:* "Only brand ASINs return data here. For multiple products, loop through each ASIN separately."

**Build:** `WHERE asin IN (…)` — the loop becomes one set-based query. Same result, no per-ASIN iteration.

### Step 4 — Monthly range, last 3 months one at a time, extend to 6 if thin
> *Document:* "Set Reporting Range → Monthly. Check the last 3 consecutive months one month at a time, not
> as a combined range … If 3 months doesn't return enough usable data extend to 6."

🟠 **This needs care — the table has no monthly rows.** Every row is `report_period = 'WEEK'`.

**Build:** assemble each calendar month from its weeks, and keep the months **separate**, as the document
insists:
- **Counts and volumes are summed:** `search_query_volume`, `total_query_impression_count`,
  `asin_impression_count`, `total_click_count`, `asin_click_count`, `total_purchase_count`,
  `asin_purchase_count`.
- **Rates, shares and medians are RECOMPUTED from their numerator and denominator — never averaged.**
  `asin_impression_share = SUM(asin_impression_count) / SUM(total_query_impression_count)`;
  `total_click_rate = SUM(total_click_count) / SUM(total_query_impression_count)`; and so on.
  Averaging weekly percentages would be arithmetically wrong.
- **"Thin data" test** implementing the 3→6 month fallback: if an ASIN returns fewer than the required
  number of usable terms across 3 months, widen that ASIN to 6 months. Applied **per ASIN**, as written.

⚠ **Account freshness differs** — LEDSone SQP runs to 2026-08-08, DCVOLTAGE to 2026-07-25. Each account's
window ends at **its own latest complete month**, and the report states the window per account, so a full
month is never silently compared against a partial one. *(Open #4 — confirm this is what is wanted.)*

### Step 5 — Sort by Search Query Volume, take the top 30–50
**Build:** `ORDER BY search_query_volume DESC LIMIT n` per ASIN per month.
🟠 **Open (#10):** the document says "30–50". A single number is needed. **Default 50** unless told otherwise.

### Step 6 — Secondary filters
> *Document:* "Cross-filter by Click Rate and ASIN Share % … Filter out terms with zero conversion."

**Build:**
- **Zero-conversion filter** (stated, so applied): drop terms where `total_purchase_count = 0`.
- **Click Rate** → `total_click_rate`. **ASIN Share** → `asin_impression_share`.
- The document names no thresholds, so these are **not used to delete rows**. Instead both are **kept as
  columns**, plus an **opportunity flag** for the pattern the document itself calls out: *"low share on
  high-volume = opportunity gap"* → high `search_query_volume` + low `asin_impression_share`.
  🟠 **Open (#10)** if numeric cut-offs are wanted.

### Step 7 — Identify long-tail candidates
> *Document:* "3–6 word phrases with moderate volume (50–500/mo) and high click or conversion rates."

**Build:** derived flag `is_long_tail` = word count of `search_query` between 3 and 6 **AND**
`search_query_volume` between 50 and 500 **AND** above-median `total_click_rate` or `total_purchase_rate`.
All three conditions are stated in the document, so this needs no new decision.

### Step 8 — Export CSV
> *Document:* required columns `search_term, search_query_score, search_query_volume, total_count,
> asin_count, asin_share, click_rate`; naming `SQP_[ASIN]_[YYYY-MM].csv`.

**Build — `REQ-30-D01`,** with the document's exact column contract:

| Document column | Source column |
|---|---|
| `search_term` | `search_query` |
| `search_query_score` | `search_query_score` |
| `search_query_volume` | `search_query_volume` |
| `total_count` | `total_query_impression_count` |
| `asin_count` | `asin_impression_count` |
| `asin_share` | `asin_impression_share` |
| `click_rate` | `total_click_rate` 🟠 *(or `asin_click_share` — open #10, the document doesn't say which)* |

Delivered as **one Excel workbook per account**, one sheet per month, keeping the document's
`SQP_[ASIN]_[YYYY-MM]` naming inside the sheet. **This output is the input to Phase 2.**

---

# PHASE 2 — find the gaps on the dying listings

### Step 1 — Find Drop-Sales & Non-Sales ASINs
> *Document:* "(a) Sales Drop — orders declined or stopped over the last 3 consecutive months, or (b) Zero
> Sales — no orders at all in the last 6 months."

🔴 **We must depart from the literal method here — see *Deviation 2*.** The sales table only contains an
ASIN on days it received traffic, so **4,650 of 16,963 LEDSone UK ASINs (27%) never appear in it** — and
those are the deadest listings, exactly the ones this step is meant to find.

**Build:** start from `listings.amazon_listings` (the full catalogue, per account, UK), **LEFT JOIN** the
monthly sales aggregate, and **treat a missing row as zero**.
- `zero_sales_6mo` — `SUM(units_ordered) = 0` (or no rows at all) across the last 6 months.
- `sales_drop_3mo` — ✅ **CONFIRMED: strictly falling** — May > Jun > Jul, with May > 0. *(Original question kept below for the record.)* Does "declined" mean each month lower than the last (strictly
  falling), or simply materially lower than 3 months ago, and by what percentage? Both are one line of SQL;
  the choice is the requester's.
- 🟠 **open (#8)**: whether out-of-stock listings are excluded (a dead listing that is simply out of stock is
  not a keyword problem).

### Step 2 — Normalise SKUs & match to the Top-Moving group ✅ CONFIRMED
> *Document:* "Strip pack-size suffixes before matching — e.g. LDMG95E278 vs LDMG95E2782PK / LDMG95E2785PK
> … Where a listing's stored SKU doesn't match its real product, correct it against the SKU mapping table."

**Build — the confirmed rule (Q6):**
1. Strip the Amazon junk prefix: `amzn.gr.XXXX-<random>` → keep the real stem.
2. Strip account suffixes: `_DCVV`, `_AMD`, `_AMN`, `_AML`, `_KP`, `_UK`, `-DC`.
3. Strip pack size: `2PK`, `3PK`, `5PK`, `6PK`, …
4. Strip trailing letters: ` M`, ` R`, ` A`, ` AM`, `-a`.
5. **Bundles / kits (`A+B+C`) are kept whole** — a kit is its own product.

> ⚠ **Why step 5 matters.** Splitting bundles on `+` and matching the first part grouped **1,151 unrelated
> products** under base `CRSF100BM`, because every kit containing that one ceiling rose looked like the same
> product. Report size jumped from 58 to 10,801 pairs. Bundles stay whole.

Then: match the underperforming listing's base SKU to a Top-Moving ASIN's base SKU, **within the same
account only**. Proceed only where the base SKUs are equal.

🟠 **Open (#7):** the document's "SKU mapping table" is not identified. `amazon_listings` has `mapped_sku`
and a `wrong_sku` flag — but `mapped_sku` is known to be unreliable (the T7 project documented this), so it
will not be used until confirmed.

**Measured result of this step** (Top-50 cut-off): **58 candidate pairs** — 27 DCVOLTAGE, 31 LEDSone.

### Step 3 — Compare the top terms against the underperforming listing
**Build:** cross-join each matched pair with that Top-Moving ASIN's confirmed Phase 1 terms. One row per
(pair × keyword). At Top-50 and 30 terms this is roughly **1,700 rows** — a workable review size.

### Step 4 — Method 1: Title / Bullets / Description scan ✅ CONFIRMED
> *Document:* "Scan Title, Bullets and Description together as one group. If a keyword appears in any one of
> these three places, that's enough — mark it placed."

**Build:**
- Text sources: `amazon_listings.title` + all `amazon_listing_bullet_points.points` (joined on
  `product_id = amazon_listings.id`) + `amazon_listings.product_description`.
- **Match rule (Q9, confirmed):** lowercase, strip punctuation, then a keyword is **present if every one of
  its words appears somewhere** in that text — any order, not necessarily together.
- The document's **"one place is enough"** rule sets `in_frontend = true`. But the build **also keeps a
  separate flag per surface** (title / bullets / description), because §2.7's directional logic needs to know
  *which* place, and because it makes the report explainable.
- 🔴 **Empty surface = NO DATA, not `false`.** If a listing has no bullets and no description, "keyword
  missing" is not a checked miss. **1,966 LEDSone listings (11%) are title-only.** These are flagged, not
  scored as 30 separate failures.

### Step 5 — Method 2: Backend / Generic keyword scan ✅ CONFIRMED
> *Document:* "Separately scan the backend (generic) keyword field … This check is independent of Method 1."

**Build:** same match rule, run **independently** over `amazon_listing_search_engine_keywords.keyword`
(joined on `product_id`). A term can pass one method and fail the other, exactly as the document requires.

🔴 **3,711 LEDSone listings (20%) have a completely empty backend field.** For those, `in_backend` is
**NO DATA**, and the finding is *"backend keyword field is empty"* — one fact, not 30 separate misses.

### Step 6 — Automated review dashboard
> *Document:* "The system pre-computes every check above — no manual cross-checking. Each ASIN pair shows a
> keyword-by-keyword tick/missing status for both methods, with exactly two possible actions."

**Build:** an interactive HTML dashboard, in the same style as the existing AIOS dashboards:
- one panel per ASIN pair — Top-Moving ASIN → underperforming ASIN, base SKU, `duplicate_status`;
- a keyword table per pair — ✅/❌ for Method 1, ✅/❌ for Method 2, and the `add_target`;
- KPI tiles, search, sort, and per-account filtering;
- **DCVOLTAGE and LEDSone rendered separately, never merged.**

### Step 7 — Monthly cadence
**Build:** one scheduled monthly job, run once per account, each reported independently — matching the
existing AIOS automation pattern. 🟠 **Open (#11):** which day, and who receives it.

---

# §2.7 — Review buttons and directional add logic ✅ implemented exactly as written

| `in_frontend` | `in_backend` | `status` | `add_target` |
|---|---|---|---|
| ✅ | ✅ | `present` | `none` |
| ✅ | ❌ | `gap` | **`backend`** |
| ❌ | ✅ | `gap` | **`bullet`** — bullets only, *not* title, *not* description |
| ❌ | ❌ | `gap` | **`backend_and_bullet`** |

- **Button 1 "All Keywords Present · Mark Reviewed"** — shown **only** when every top term ticks both
  methods. Records `action_state = reviewed` with the cycle date.
- **Button 2 "Add Missing Keywords"** — shown whenever any gap exists. **Records the recommendation and sets
  `action_state = pending_add`.**

🔴 **The one place we do not follow the document.** §2.7 says the button writes to Amazon automatically via
SP-API. **Confirmed with Abiraj: report only — no automatic write.** See *Deviation 3*.

---

# §2.9 — Output contract (the 12 columns, exactly as specified)

`brand` · `top_asin` · `base_sku` · `duplicate_asin` · `duplicate_status` · `keyword` · `in_frontend` ·
`in_backend` · `status` · `add_target` · `action_state` · `date_checked`

Delivered as **`REQ-30-D02`** — Excel + the dashboard, both from one read-only builder.
`brand` uses the document's own values: `dcvoltage_uk` / `ledsone_uk`.

---

# §2.10 — QA checklist, built as automated assertions

Each of the document's seven checks becomes a test the builder runs on itself, and the result is printed in
the report's Notes sheet:

| # | Document's check | Automated assertion |
|---|---|---|
| 1 | Account separation | assert no output row mixes `sub_source` 6 and 8 |
| 2 | SKU normalisation applied | assert every `base_sku` is the normalised form; log the rule version used |
| 3 | One-place-is-enough | assert `in_frontend` = OR of the three surface flags |
| 4 | Dual-method coverage | assert `in_frontend` and `in_backend` are computed independently |
| 5 | Directional add logic | assert `add_target` matches the §2.7 truth table for 100% of rows |
| 6 | Zero manual lookup | assert every keyword traces to a Phase 1 SQP row, none hand-entered |
| 7 | Monthly cadence | assert `date_checked` is the run date and the window is stated per account |

---

# Where we differ from the document — 3 places, each with a reason

### Deviation 1 — Phase 1 comes from the database, not from Seller Central *(needs approval, open #2)*
The document describes 8 manual Seller Central steps. **That export already exists in our warehouse** —
137,048 SQP rows for LEDSone UK alone. Doing it by query is the same data, and it is what makes the
document's own "zero manual lookup" instruction achievable. **The requester should approve this**, because
it changes Phase 1 from a human task into an automatic one.

### Deviation 2 — zero-sales is found from the product list, not the sales report *(a correction)*
The document's Step 1 implies searching the sales report. The sales report only lists an ASIN on days it had
traffic, so **27% of ASINs — the deadest ones — are not in it at all**. We start from the full product list
and treat "absent" as zero. Following the document literally here would silently skip the very listings the
report exists to find. **No decision needed; we are telling you, not asking.**

### Deviation 3 — no automatic write to Amazon *(confirmed by Abiraj)*
§2.7 ends in automatic SP-API writes to live listings. Editing a live listing is permanent and public, and
one wrong rule would change thousands of listings with no undo. **Confirmed: the system produces a report;
a person applies the keywords.** The dashboard still tells them exactly where each keyword should go.

---

# What is still needed before the build starts

| | Question | Effect |
|---|---|---|
| ~~#5~~ | ~~Top-Moving threshold~~ — ✅ **ANSWERED: above 5 units in all 3 months → 103 ASINs** | Done |
| **#8** | Exact "sales drop over 3 months" test | Changes which listings qualify |
| **#10** | Number of top terms (30 or 50); which column is `click_rate` | Changes rows per pair |
| — | A **GPT-approved implementation prompt** (workbench rule) | Required before code is written |

Everything else — #2, #3, #4, #7, #11, #12 — can be answered while the build proceeds, with a documented
default clearly labelled as unconfirmed in the output.

**Build order once approved:** Phase 1 builder → reconcile against a live anchor → Phase 2 matcher →
reconcile → Excel → dashboard → validation report → then, only on instruction, publish and schedule.
