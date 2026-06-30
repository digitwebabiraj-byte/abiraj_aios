# PH Segmentation — Weekly-Snapshot Window & Data-Quality Findings (Documentation)

> Reusable data-understanding record from the 30 June 2026 session. It explains how `traffic_data`
> is actually shaped and why several "looks wrong" patterns are correct behaviour. **Status of the
> specifics below: REPORTED_BY_ABIRAJ** — recomputed in the live Claude Chat session against the
> database; no result set, query file or screenshot is imported into this project as evidence yet.
> Related: `SYSTEM_REFERENCE.md` (§2 signals, §3 benchmark, §7 engine, §10 data sources);
> delivery record `handover/REQ-05_ph-asin-segmentation/2026-06-30_delivery_final-june-refresh-and-data-quality-validation.md`.

## 1. Key discovery — `traffic_data` is weekly, not daily

- `traffic_data` rows are **weekly snapshots, each dated on the week-ending Saturday** — not daily
  rows. Confirmed against the screenshot's weeks 22–26.
- Consequence: a **calendar-month window catches a variable number of weeks** — **May = 5 weeks,
  June = 4 weeks** — which makes raw month-over-month movement slightly **unfair** (a 5-week month
  accumulates more impressions/clicks than a 4-week month for the same ASIN).

## 2. The clean fix — a "last 4 complete weeks" window

- The clean correction is a **"last 4 complete weeks"** window instead of a calendar month.
- It does **not** change the ASIN universe: **8,134 = 8,134** (same ASINs in and out).
- The **current report already uses 4 complete weeks for June**, so the existing report is **correct**.
  Only two things are refinements, not fixes:
  1. the **report header label** should say "last 4 complete weeks" (cosmetic/clarity);
  2. the **previous-window (May) consistency** — May should also be measured as 4 complete weeks so
     the month-over-month comparison is like-for-like.
- **Recommendation (reported):** trial the 4-complete-weeks method, then run it past **Bietrick**
  before adopting it as the standing window definition.

## 3. Why CVR can exceed 100% (not an error)

- Clicks and conversions are **counted independently** and **across different weeks**. An ASIN making
  8 sales on 1 click is a **genuinely strong converter**, not a data error.
- This is consistent with `SYSTEM_REFERENCE.md` §7: `conversions > clicks → HIGH` (a documented edge
  rule, not a bug).

## 4. Why conversions ÷ clicks (the CVR definition)

- Dividing conversions by clicks **isolates the product page's selling power** — how well the listing
  converts the shoppers who actually reach it — **separate from** visibility (impressions) and search
  appeal (clicks). That separation is the whole point of the three-signal model.

## 5. Zero-click rows are genuine zeros (safe)

- Across all **four June weeks** there are **zero NULLs**. The ~**16,000 zero-click rows per week**
  are **genuine zeros** (the ASIN was seen but not clicked) — the **normal long-tail** of a large
  catalogue, **not missing data** and **not a date artefact**.
- This supports the engine's `clicks = 0 → LOW` conversion rule (`SYSTEM_REFERENCE.md` §7) being a
  correct treatment of real zeros, not a NULL workaround.

## 6. Conversions without clicks — normal attribution

- Real examples: `B0CCD4KL94`, `B0B9Y59487` (twice).
- Cause: Amazon attributes the **click and the sale to different weeks**, or buyers reach the product
  via **cart / Buy-Again** without a fresh tracked click.
- This is **normal attribution behaviour**; the engine **correctly** reads these as strong converters
  (segments **LLH / HLH**).

## 7. The four protocol-undefined points (documented engine choices, not errors)

Flagged in the 30 June validation. Three are already written into `SYSTEM_REFERENCE.md`; one is not.

| # | Point | Engine choice | Already documented? |
|---|---|---|---|
| 1 | Zero clicks | Conversion → LOW | YES — `SYSTEM_REFERENCE.md` §7 |
| 2 | Conversions > clicks | Conversion → HIGH | YES — `SYSTEM_REFERENCE.md` §7 |
| 3 | Undefined combos | `HLL → HLH`, `LHL → HHL` (Option B) | YES — `SYSTEM_REFERENCE.md` §4 / §11 |
| 4 | **66 "lateral SAME" moves** | Treated as **SAME** movement (no escalation) | **NO — not yet written down** |

> Follow-up: document the **66 lateral-SAME** treatment explicitly (what counts as a lateral move
> between equal h-count segments, and why it is "SAME" not "Improved/Declined"). The other three are
> already canonical.

## 8. Evidence Gap

To upgrade this record from REPORTED_BY_ABIRAJ to VERIFIED, import into the project:

- the query result sets behind the weekly-snapshot finding and the zero-NULL check;
- the screenshot showing weeks 22–26;
- the 8,134-universe comparison output (calendar-month vs 4-complete-weeks);
- the benchmark-recompute output (135 sellers, Imp 2,097, Clk 24.9, CVR 91.46%).

## 9. Do-Not

- Do not change the engine's window definition (calendar month → 4 complete weeks) until trialled,
  approved by Bietrick, and a governed task is opened.
- Do not execute SQL from this documentation record.
- Do not treat these findings as a protocol change — they are an interpretation/clarity layer until
  ratified.
