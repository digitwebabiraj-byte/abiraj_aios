# Validation — ZSFO REQ-08-D01 (run 2026-07-10)

**Task:** REQ-08_zero-sales-full-optimization · **PH:** utharsika · **Marketplace:** Amazon UK
**Window:** 2026-06-10 → 2026-07-09 (last completed 30 days, current day excluded)
**Method:** read-only queries via the Postgres MCP against `order_management_copy`; results below are
the live figures returned on 2026-07-10.

## 1. Headline reconciliation (live)

| Metric | Source | Expected (handoff §6) | Live 2026-07-10 | Result |
|---|---|---|---|---|
| Universe — utharsika Amazon-UK ASINs | `traffic_data` wc=1, UK, user=utharsika | 1,719 | **1,719** | ✅ |
| Sold in window (FBA+FBM) | `order_transaction` Completed | 469 | **469** | ✅ |
| Vendor sellers in window (units>0) | `vendor_sales` OVERLAP | 34 | **34** | ✅ |
| **Zero-sale rows (the report)** | universe − any-sale | 1,250 | **1,250** | ✅ |
| Max window FBA/FBM units in report | integrity | 0 | **0** | ✅ |
| Max window vendor units in report | integrity | 0 | **0** | ✅ |

`1,719 − 469 = 1,250`. All 34 positive-unit vendor sellers are already inside the 469 FBA/FBM
sellers → **0 vendor-only false exclusions**.

## 2. Vendor OVERLAP vs start_time (the fix that was applied)

- Rule applied: `NOT (end_time::date < ws OR start_time::date > we)` (overlap), replacing the
  earlier `start_time BETWEEN ws AND we`.
- **Count impact on utharsika: 0** (row count 1,250 under both) — confirming the handoff note that
  overlap is *correct for other users* but neutral here. Retained because it is the correct rule.
- Nuance: **35** ASINs have a vendor period overlapping the window; **34** carry positive units
  (one overlap = 0 units). The report keys on units>0, so the 0-unit overlap ASIN is correctly kept.

## 3. Lifetime-vs-window (the original "wrong data" report — resolved)

Top ASIN `B093T3TR2Y`: **vendor lifetime = 1,142 units** (last vendor sale **2025-10-29**), but
**vendor in-window = 0** and **FBA/FBM in-window = 0** → correctly a zero-sale row. The report and
dashboard now carry **"Last Vendor Sale (lifetime)"**, **"Last Amazon Sale (lifetime)"** and
**"Vendor Units (lifetime)"** columns so this can never be misread as an in-window sale again.

## 4. Column trace — `B093T3TR2Y` (top row)

| Field | Expected | Live | Result |
|---|---|---|---|
| SKU | LSCY290GR+RPR44WH | LSCY290GR+RPR44WH | ✅ |
| Impressions (window) | 221,027 | 221,027 | ✅ |
| Clicks (window) | 2,427 | 2,427 | ✅ |
| Local UK Warehouse stock | 765 | 765 | ✅ |
| Amazon FBM Stock | 39 | 39 | ✅ |

Bridge used the **NULL-channel** rule (no `which_channel=1` on `listing_data`), per gotcha #1.

## 5. Independent verification pack

`ZSFO_VERIFICATION_PACK.md` (final_outputs) rewritten to the **Utharsika** population + OVERLAP
vendor rule + NULL-channel stock trace, and all six checks re-run live — **6/6 PASS**. The original
full-catalogue pack is preserved as
`evidence/source_documents/.../ORIGINAL_ZSFO_VERIFICATION_PACK_full-catalogue_superseded.md`.

## 6. Deliverable integrity

- `data.json` — 1,250 rows, 474 KB; asserted `len==1250` at build time.
- `ZSFO_Zero_Sales_Full_Optimization_Utharsika.xlsx` — read back: 1,250 data rows, 22 columns,
  headers match the task sheet (+ helpers), conversion rate formatted `0.00%`, top row correct.
- `ZSFO_Utharsika_dashboard.html` — rendered live in-browser (local static server): 1,250 rows,
  1,250 weekly sparklines, 6 KPIs, filters verified (Out-of-stock 214, Zero-impressions 148,
  back-to-all 1,250), **no console errors**. (Full-page screenshot capture times out due to the
  1,250 inline SVGs — cosmetic only; interactivity confirmed via DOM assertions.)

## 7. Root-cause distribution (derived, for optimisation triage)

| Bucket | Count |
|---|---|
| Impressions but 0 clicks — main image / title / price | 680 |
| Clicks but 0 sales — detail page / price / reviews | 323 |
| Out of stock — no UK warehouse + no FBM | 214 |
| Zero impressions — listing not surfacing | 33 |
| **Total** | **1,250** |

(Out-of-stock takes priority over the traffic buckets, so 214 out-of-stock rows include some that
also had zero impressions; total zero-impression ASINs in the raw data = 148.)

## Verdict

**GREEN (technical).** Logic, numbers and deliverables reconcile to the live DB and pass an
independent 6-check pack. **Business validation by Satheesvaran remains open** (rule edge cases:
order-status set, universe definition) — so the requirement is technically complete but **not yet
business-signed-off**. See closure doc for carried-open items.
