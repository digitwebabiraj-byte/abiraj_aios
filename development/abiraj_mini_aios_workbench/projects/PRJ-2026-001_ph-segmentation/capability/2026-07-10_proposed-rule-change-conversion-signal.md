# Proposed Rule Change — the Conversion signal (count vs rate)

> **Status (conversion signal):** ✅ **APPROVED by Bietrick 2026-07-10** → switch to **count-based**.
> Engine prepared: `sql/REQ-05_ph-asin-segmentation/2026-07-10_ph_segment_engine_strict_rank_count_conv.sql`
> (one line changed in both windows: `a.cvr>=b.bv` → `a.conv>=b.bcv`). **STORED, not executed** — the
> re-run + HTML regenerate + live push must be done in the authorised DB session, and the result validated
> before going live.
> **Status (undefined-combo mapping HLL→HLH / LHL→HHL):** still PENDING — unchanged in the new engine.
> **Raised:** 2026-07-10, from a review of the live July 2026 dashboard. **Owner:** Abiraj → Bietrick.

## The issue (in one line)
On some rows the **segment** and the **Status** column say the **opposite thing about conversion**,
because they measure conversion two different ways.

- **Segment** uses conversion **RATE** (CVR = sales ÷ clicks) vs the benchmark CVR%.
- **Status** uses conversion **COUNT** (number of sales) vs the category's average sales.

When a product's *rate* is below benchmark but its *number of sales* is above average, the two disagree.

## Current rule (per Protocol v1.0)
> Conversion = **HIGH** if the ASIN's **CVR% ≥ the category benchmark CVR%**, else LOW.
> (Impressions and Clicks, by contrast, use **count vs average count**.)

## Proposed rule (Bietrick's request)
> Conversion = **HIGH** if the ASIN's **conversions ≥ the category's Avg conversions (count)**, else LOW —
> i.e. treat conversion the **same way as impressions and clicks** (count vs average count).

## Worked example — `B0CR319CXS` (Mail Bags), current live dashboard
Benchmark: Avg impressions 264 · Avg clicks 3.0 · Avg conversions **1.4** · Benchmark CVR% **49.8%**.
Row: Impr 474 · Clicks 5 · Conversions **2** · CVR **40%**.

| | Today (rate) | Proposed (count) |
|---|---|---|
| Conversion signal | 40% < 49.8% → **L** | 2 ≥ 1.4 → **H** |
| **Segment** | HH**L** (Leaky Bucket) | HH**H** (Champion) |
| **Status** | ABOVE avg | ABOVE avg |
| Agree? | ❌ contradict | ✅ match |

## What the change buys — and costs
**Pros**
- The **segment and Status always agree** (both count-based) — no more contradictory rows.
- All **three signals use one consistent method** (count vs average count) — simpler to explain.

**Cons / trade-off (flag to Bietrick)**
- CVR (rate) is what catches a **"Leaky Bucket"** — lots of traffic, poor at converting *per click*.
- Switching to **count** means a product with lots of traffic and a good *number* of sales — even at a
  **weak rate** — becomes a **Champion (HHH)** instead of a Leaky Bucket (HHL).
- So the change **re-segments some ASINs** (Leaky Buckets → Champions) and **loses some "leaking" detection**.

## Related edge-case item (same review, same sign-off)
The **undefined-combo mapping `HLL→HLH` and `LHL→HHL`** is also **not in Protocol v1.0** (the protocol lists
only 6 of the 8 possible codes). It's a build add-on that makes the badge contradict the signals — e.g. a
**0-conversion** product shows as **HLH** ("converts well"). This should be decided in the same pass.
See [[2026-07-06_segment-movement-plain-language-explainer]].

## Decision needed from Bietrick
1. **Conversion signal:** keep **CVR rate** (current protocol) · switch to **count** (proposed) · or **show both**?
2. **Undefined combos (HLL, LHL):** keep the Option-B action-mapping · show the true raw code alongside · or leave the badge as the raw code?

Nothing changes live until Bietrick decides; the engine + dashboard would then be updated in the authorised DB session and re-recorded here.
