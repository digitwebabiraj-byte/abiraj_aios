# ZSFO Report — Independent Verification Pack (CORRECTED — Utharsika population)

Hand this to a second developer. They run each query themselves (psql / pgAdmin / any
DB-connected chat) against the **same Postgres database** (`order_management_copy`), then compare
their output to the **Expected** value. If all six pass, the ZSFO report is confirmed correct.

> **Why this pack was rewritten (2026-07-10).** The first draft validated the **full catalogue**
> population (`listing_data which_channel=1`, no user filter → 30,782 → 28,318) and used a
> `which_channel=1` stock trace. Neither matches the actual deliverable, which is scoped to
> **utharsika's Amazon-UK ASINs** and whose `listing_data` rows carry **`which_channel = NULL`**.
> Every check below is now scoped to the real report population and uses the corrected bridge and
> the vendor **OVERLAP** rule.

**Run context**
- Run date (Monday): `2026-07-10`
- Qualification window (last completed 30 days): **2026-06-10 → 2026-07-09** (current day excluded)
- Population: **utharsika's Amazon-UK ASINs**, defined from `traffic_data`
  (`which_channel=1, market_place='UK', user_name='utharsika'`)
- "Zero sales" = 0 units across **FBA + FBM** (`order_transaction`) **and Vendor/1P** (`vendor_sales`)

All queries are read-only.

---

## Check 1 — Window formula matches the task spec's own example
Spec says: report on **Mon 3 Aug** → period **4 Jul – 2 Aug**.
```sql
SELECT (DATE '2026-08-03' - INTERVAL '30 days')::date AS start,  -- Expected 2026-07-04
       (DATE '2026-08-03' - INTERVAL '1 day')::date  AS end_;    -- Expected 2026-08-02
```
**Expected:** 2026-07-04 and 2026-08-02.   **Actual (2026-07-10): PASS.**

---

## Check 2 — Funnel counts (Utharsika population, vendor OVERLAP)
```sql
WITH b AS (SELECT DATE '2026-06-10' ws, DATE '2026-07-09' we),
uthar AS (SELECT DISTINCT ref_id AS asin FROM public.traffic_data
          WHERE which_channel=1 AND market_place='UK' AND user_name='utharsika'),
S AS (SELECT ot.asin, SUM(ot.quantity) u FROM public.order_transaction ot,b
      WHERE ot.source_name='AMAZON' AND ot.market_place='UK' AND ot.order_status='Completed'
        AND ot.order_date::date BETWEEN b.ws AND b.we GROUP BY ot.asin),
V AS (SELECT vs.asin, SUM(vs.ordered_units) vu FROM public.vendor_sales vs,b
      WHERE NOT (vs.end_time::date < b.ws OR vs.start_time::date > b.we) GROUP BY vs.asin)  -- OVERLAP
SELECT
  (SELECT COUNT(*) FROM uthar)                                              AS universe_uk_asins,   -- Expected 1,719
  COUNT(*) FILTER (WHERE COALESCE(s.u,0)>0)                                 AS sold_fba_fbm,        -- Expected 469
  COUNT(*) FILTER (WHERE COALESCE(v.vu,0)>0)                                AS vendor_in_window,    -- Expected 34
  COUNT(*) FILTER (WHERE COALESCE(s.u,0)=0 AND COALESCE(v.vu,0)=0)          AS zero_sale_report     -- Expected 1,250
FROM uthar u LEFT JOIN S s ON s.asin=u.asin LEFT JOIN V v ON v.asin=u.asin;
```
**Expected:** 1,719 · 469 · 34 · 1,250.   **Actual (2026-07-10): 1,719 · 469 · 34 · 1,250 — PASS.**

> Note: **35** ASINs have a vendor period *overlapping* the window, but only **34** carry positive
> units (one overlap has 0 ordered_units). The report keys on units>0, so it correctly keeps that
> one ASIN. All 34 positive-unit vendor sellers are already inside the 469 FBA/FBM sellers → net
> exclusion 469, giving 1,719 − 469 = 1,250. **Zero vendor-only false exclusions.**

---

## Check 3 — Integrity: NO reported ASIN has any sale in the window
```sql
WITH b AS (SELECT DATE '2026-06-10' ws, DATE '2026-07-09' we),
uthar AS (SELECT DISTINCT ref_id AS asin FROM public.traffic_data
          WHERE which_channel=1 AND market_place='UK' AND user_name='utharsika'),
S AS (SELECT ot.asin, SUM(ot.quantity) u FROM public.order_transaction ot,b
      WHERE ot.source_name='AMAZON' AND ot.market_place='UK' AND ot.order_status='Completed'
        AND ot.order_date::date BETWEEN b.ws AND b.we GROUP BY ot.asin),
V AS (SELECT vs.asin, SUM(vs.ordered_units) vu FROM public.vendor_sales vs,b
      WHERE NOT (vs.end_time::date < b.ws OR vs.start_time::date > b.we) GROUP BY vs.asin),
report AS (SELECT u.asin FROM uthar u LEFT JOIN S s ON s.asin=u.asin LEFT JOIN V v ON v.asin=u.asin
           WHERE COALESCE(s.u,0)=0 AND COALESCE(v.vu,0)=0)
SELECT COUNT(*) AS report_rows,                                             -- Expected 1,250
       COALESCE(MAX(s.u),0)  AS max_fba_fbm_units_in_report,                -- Expected 0
       COALESCE(MAX(v.vu),0) AS max_vendor_units_in_report                  -- Expected 0
FROM report r LEFT JOIN S s ON s.asin=r.asin LEFT JOIN V v ON v.asin=r.asin;
```
**Expected:** 1,250 rows, both max columns = 0.   **Actual (2026-07-10): 1,250 · 0 · 0 — PASS.**

---

## Check 4 — Positive spot-check (this IS in the report → every stream must be 0)
Top ASIN by impressions, `B093T3TR2Y`.
```sql
WITH b AS (SELECT DATE '2026-06-10' ws, DATE '2026-07-09' we)
SELECT
  (SELECT COALESCE(SUM(quantity),0) FROM public.order_transaction o,b
     WHERE o.source_name='AMAZON' AND o.market_place='UK' AND o.order_status='Completed'
       AND o.asin='B093T3TR2Y' AND o.order_date::date BETWEEN b.ws AND b.we)      AS ot_units,        -- Expected 0
  (SELECT COALESCE(SUM(vs.ordered_units),0) FROM public.vendor_sales vs,b
     WHERE vs.asin='B093T3TR2Y'
       AND NOT (vs.end_time::date<b.ws OR vs.start_time::date>b.we))              AS vendor_in_window, -- Expected 0
  (SELECT COALESCE(SUM(ordered_units),0) FROM public.vendor_sales
     WHERE asin='B093T3TR2Y')                                                     AS vendor_lifetime;  -- Expected 1,142
```
**Expected:** 0 · 0 · 1,142.   **Actual (2026-07-10): 0 · 0 · 1,142 — PASS.**
This is the crux of the earlier "vendor shows wrong data" report: **1,142 units lifetime but 0
in the 30-day window** → correctly a zero-sale row. (Report/dashboard now show "Last Vendor Sale".)

---

## Check 5 — Negative spot-checks (these SOLD → must be ABSENT from the report)
```sql
WITH b AS (SELECT DATE '2026-06-10' ws, DATE '2026-07-09' we)
SELECT o.asin, SUM(o.quantity) AS units_in_window
FROM public.order_transaction o,b
WHERE o.source_name='AMAZON' AND o.market_place='UK' AND o.order_status='Completed'
  AND o.asin IN ('B0D7ZTRLBH','B0F1D3FS5C','B0GQ48BNBZ')
  AND o.order_date::date BETWEEN b.ws AND b.we
GROUP BY o.asin ORDER BY 2 DESC;
```
**Expected:** B0D7ZTRLBH = 30, B0F1D3FS5C = 29, B0GQ48BNBZ = 27 — all > 0, so none appear in the
report.   **Actual (2026-07-10): 30 · 29 · 27 — PASS (all absent from report).**

---

## Check 6 — Column-value trace for the top ASIN (`B093T3TR2Y`)
Report shows: SKU `LSCY290GR+RPR44WH`, UK stock 765, FBM 39, Impressions 221,027, Clicks 2,427.
**⚠ Bridge note:** utharsika's `listing_data` rows have `which_channel = NULL` — do **not** filter
`which_channel=1` here (the first draft did, which wrongly returns 0). Match on
`ref_id + market_place='UK' + wrong_sku=0 + is_parent=0`.
```sql
WITH b AS (SELECT DATE '2026-06-10' ws, DATE '2026-07-09' we)
SELECT
  (SELECT COALESCE(SUM(impression),0) FROM public.traffic_data t,b
     WHERE t.which_channel=1 AND t.market_place='UK' AND t.ref_id='B093T3TR2Y'
       AND t.date BETWEEN b.ws AND b.we)                                          AS impressions,  -- Expected 221027
  (SELECT COALESCE(SUM(click),0) FROM public.traffic_data t,b
     WHERE t.which_channel=1 AND t.market_place='UK' AND t.ref_id='B093T3TR2Y'
       AND t.date BETWEEN b.ws AND b.we)                                          AS clicks,       -- Expected 2427
  (SELECT COALESCE(SUM(s.stock),0) FROM public.location_wise_inv_stock s
     WHERE s.location='UK' AND s.sku IN (
       SELECT DISTINCT CASE WHEN COALESCE(mapped_sku,'')<>'' THEN trim(mapped_sku)
         ELSE regexp_replace(regexp_replace(regexp_replace(trim(sku),'(-IDE|-CA|-IFR|-NL)$',''),'__[^_]*$',''),'_[^_]*$','') END
       FROM public.listing_data
       WHERE market_place='UK' AND wrong_sku=0 AND is_parent=0 AND ref_id='B093T3TR2Y'))  AS uk_stock,   -- Expected 765
  (SELECT COALESCE(SUM(quantity),0) FROM public.listing_data
     WHERE market_place='UK' AND wrong_sku=0 AND is_parent=0
       AND ref_id='B093T3TR2Y' AND fulfilment='merchant'
       AND NOT (substring(regexp_replace(trim(sku),'(-IDE|-CA|-IFR|-NL)$','') from '_([A-Za-z0-9]+)$') ILIKE 'AM%'))
                                                                                  AS fbm_stock;    -- Expected 39
```
**Expected:** 221027 · 2427 · 765 · 39.   **Actual (2026-07-10): 221027 · 2427 · 765 · 39 — PASS.**

---

## Sign-off
| Check | Expected | Actual 2026-07-10 | Pass? |
|---|---|---|---|
| 1 Window | 2026-07-04 / 2026-08-02 | 2026-07-04 / 2026-08-02 | ✅ |
| 2 Funnel | 1,719 / 469 / 34 / 1,250 | 1,719 / 469 / 34 / 1,250 | ✅ |
| 3 Integrity | 1,250 rows, max 0 / 0 | 1,250 / 0 / 0 | ✅ |
| 4 Positive | 0 / 0 / 1,142 | 0 / 0 / 1,142 | ✅ |
| 5 Negative | 30 / 29 / 27 | 30 / 29 / 27 | ✅ |
| 6 Trace | 221027 / 2427 / 765 / 39 | 221027 / 2427 / 765 / 39 | ✅ |

All six pass → the ZSFO logic and numbers are independently confirmed for run 2026-07-10.
