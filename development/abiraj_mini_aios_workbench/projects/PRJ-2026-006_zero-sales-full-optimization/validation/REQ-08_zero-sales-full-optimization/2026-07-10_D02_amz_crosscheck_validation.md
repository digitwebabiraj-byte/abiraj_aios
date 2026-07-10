# Validation — ZSFO REQ-08-D02 (Amazon AMZ_2026 cross-check) — 2026-07-10

**Task:** REQ-08_zero-sales-full-optimization · **Deliverable:** D02 (AMZ-cross-checked corrected report)
**Input:** revised handoff `2026-07-10_REVISED_PROJECT_CONTEXT_amz-crosscheck.md` + planner files
`ZSFO_Utharsika_report_CORRECTED.xlsx` (1,065 rows + 189 "Removed" tab) and dashboard.
**Method:** independent read-only verification against the live DB (Postgres MCP) and the
**authoritative `AMZ_2026` tab** of `utharsika team July to September-KPI Sheet (1).xlsx`.

---

## 1. The handoff's claim
> "189 of 1,254 zero-sale ASINs actually sold £12,394.76 in Jun/Jul 2026 per Amazon — sales our
> `vendor_sales` is MISSING. The gap is entirely on **vendor (1P)** ASINs (e.g. B093T3TR2Y: Amazon
> £2,659, our DB £0). Corrected report = 1,065. Fix: re-sync `vendor_sales`."

## 2. What the direction gets RIGHT
Cross-checking the D01 zero-sale set (1,250) against Amazon's own `AMZ_2026` "Ordered Product Sales"
report **does** surface ASINs that show Amazon activity — so a postgres-only, per-ASIN report is
**over-inclusive** relative to Amazon's product-level view. Independently reproduced:

| Rule (exclude if AMZ Jun or Jul …) | Excluded | Corrected count |
|---|---|---|
| **order items > 0** | **191** | **1,059** |
| revenue £ > 0 | 138 | 1,112 |
| July revenue £ > 0 only | 74 | 1,176 |

The planner's **1,065** sits between the items-rule (1,059) and £-rule (1,112) — within 6 ASINs of
the items-based cut. The report row-set is therefore directionally sound.

## 3. What the handoff gets WRONG (verified, with evidence)

**(a) The mechanism is not a vendor gap — it is per-ASIN vs per-product attribution.**
For all **191** AMZ-flagged ASINs (live DB):

| Explanation | Count | % |
|---|---|---|
| SKU sold via a **UK seller (3P) sibling ASIN** — already in our DB | 147 | 77% |
| SKU sold via a **non-UK sibling** — in our DB | 19 | 10% |
| Own-ASIN **vendor** units in Jun/Jul (the claimed cause) | **0** | **0%** |
| No trace in our DB at all | 25 | 13% |

→ **0 of 191 are explained by vendor sales; 87% are seller sibling-ASIN sales already present in
`order_transaction`.** Re-syncing `vendor_sales` would correct essentially none of them. The true
mechanism is **listing sprawl**: one product/SKU has many ASINs; impressions accrue to the "hero"
ASIN (e.g. `B093T3TR2Y`) while conversions land on a sibling listing (e.g. `B0CPBX49HJ`).

**(b) The flagship example is wrong.** `AMZ_2026` shows `B093T3TR2Y` = **June £0 / 332 items,
July £730.64 / 88 items** — not "£2,659". Our DB and Amazon **agree** its own-ASIN sales ≈ £0; its
SKU sold under sibling `B0CPBX49HJ`. The "£2,659" traces to the KPI sheet's stale IMPORTRANGE
*Utharsika tab* (which the handoff itself flags as unreliable), not `AMZ_2026`.

**(c) The £ total does not reproduce.** Handoff £12,394.76 vs verified `AMZ_2026` Jun+Jul achieved
**£5,101.24** across the 191 (see `removed_191_amz_reconciliation.csv`).

**(d) `vendor_sales` is not wholesale missing for 2026.** It holds 1,772 rows / 997 ASINs spanning
2026-01-01 → 2026-07-08 (covers the window). No evidence of a vendor sync gap for this population.

**(e) Data-quality flag on `AMZ_2026` itself.** The June block shows **£0 with positive order
items** for many ASINs (e.g. B093T3TR2Y June = £0/332 items), and per-ASIN items look inflated
(likely summed across duplicate marketplace rows). The "items > 0" exclusion rule is therefore
sensitive to this anomaly — hence the 1,059 vs 1,112 spread.

## 4. Consequence for the deliverable
- The **1,065 corrected report is usable** as a "zero at ASIN level **and** no Amazon product-level
  activity" view — but the **reason** an ASIN is in the "Removed" tab is **product-level (sibling)
  sales, not a vendor-data gap**.
- The prescribed **fix "re-sync `vendor_sales`" is not warranted** by the evidence and is a DB-write
  task **outside this project's read-only scope** — NOT performed.
- The real open decision is unchanged from D01's carried item: **should ZSFO be per-ASIN (dead
  listings, keep all 1,250 + flag siblings) or per-product (dead SKUs, exclude the ~191)?** The
  planner has implicitly chosen per-product; that choice should be confirmed by Satheesvaran with
  the **correct mechanism** in view (not the vendor-gap premise).

## 5. Evidence files
- `D02_amz_crosscheck/ZSFO_Utharsika_report_CORRECTED.xlsx` — planner's 1,065 + 189-Removed (imported).
- `D02_amz_crosscheck/ZSFO_Utharsika_dashboard_CORRECTED.html` — planner's dashboard (imported).
- `D02_amz_crosscheck/removed_191_amz_reconciliation.csv` — my reproducible 191-ASIN list with
  `AMZ_2026` Jun/Jul items + £ (total £5,101.24 / 1,660 items).

## Verdict
**AMBER.** The corrected report's row-set is directionally sound (1,065 ≈ verified 1,059), but the
handoff's **diagnosis (vendor gap) and prescription (re-sync `vendor_sales`) are refuted** — the
cause is per-ASIN-vs-per-product attribution (87% sibling-ASIN, 0% vendor). Onboarded as D02 with
this correction on record. **Blocked on:** (1) owner/Satheesvaran confirming per-product vs
per-ASIN definition with the correct mechanism; (2) the exclusion rule (items vs £) that swings the
count by ~120 ASINs; (3) the `AMZ_2026` June £0/items data-quality anomaly.
