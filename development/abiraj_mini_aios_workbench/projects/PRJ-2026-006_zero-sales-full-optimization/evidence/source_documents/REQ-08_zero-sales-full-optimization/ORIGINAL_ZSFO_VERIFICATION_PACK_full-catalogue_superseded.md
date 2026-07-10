# ZSFO Report — Independent Verification Pack

Hand this to another developer. They run each query themselves (psql / pgAdmin / any
DB-connected chat) against the **same Postgres database**, then compare their output to the
**Expected** value. If everything matches, the ZSFO report is confirmed correct.

**Run context**
- Run date (Monday): `2026-07-10`
- Qualification window (last completed 30 days): **2026-06-10 → 2026-07-09** (current day excluded)
- Previous calendar month: June 2026
- "Zero sales" = 0 units across **FBA + FBM** (`order_transaction`) **and Vendor/1P** (`vendor_sales`)

No query below writes anything — all read-only.

---

## Check 1 — Window formula matches the task spec's own example
The spec says: report on **Mon 3 Aug** → period **4 Jul – 2 Aug**.

```sql
SELECT (DATE '2026-08-03' - INTERVAL '30 days')::date AS start,   -- Expected 2026-07-04
       (DATE '2026-08-03' - INTERVAL '1 day')::date  AS end_;     -- Expected 2026-08-02
```
**Expected:** 2026-07-04 and 2026-08-02.

---

## Check 2 — Funnel counts
```sql
WITH b AS (SELECT DATE '2026-06-10' ws, DATE '2026-07-09' we),
L AS (SELECT DISTINCT ref_id AS asin FROM public.listing_data
      WHERE which_channel=1 AND market_place='UK' AND wrong_sku=0 AND is_parent=0
        AND COALESCE(sku,'') NOT LIKE 'amzn.gr.%'),
S AS (SELECT ot.asin, SUM(ot.quantity) u FROM public.order_transaction ot,b
      WHERE ot.source_name='AMAZON' AND ot.market_place='UK' AND ot.order_status='Completed'
        AND ot.order_date::date BETWEEN b.ws AND b.we GROUP BY ot.asin),
V AS (SELECT vs.asin, SUM(vs.ordered_units) vu FROM public.vendor_sales vs,b
      WHERE vs.start_time::date BETWEEN b.ws AND b.we GROUP BY vs.asin)
SELECT
  (SELECT COUNT(*) FROM L)                                                    AS active_uk_listings,      -- Expected 30,782
  COUNT(*) FILTER (WHERE COALESCE(s.u,0)=0)                                   AS zero_sale_fba_fbm_only,  -- Expected 28,320
  COUNT(*) FILTER (WHERE COALESCE(s.u,0)=0 AND COALESCE(v.vu,0)=0)            AS zero_sale_after_vendor,  -- Expected 28,318
  COUNT(*) FILTER (WHERE COALESCE(s.u,0)=0 AND COALESCE(v.vu,0)>0)            AS removed_by_vendor        -- Expected 2
FROM L LEFT JOIN S s ON s.asin=L.asin LEFT JOIN V v ON v.asin=L.asin;
```
**Expected:** 30,782 · 28,320 · 28,318 · 2.

---

## Check 3 — Integrity: NO reported ASIN has any sale in the window
Reconstruct the zero-sale set and confirm the max sales figure is 0.

```sql
WITH b AS (SELECT DATE '2026-06-10' ws, DATE '2026-07-09' we),
L AS (SELECT DISTINCT ref_id AS asin FROM public.listing_data
      WHERE which_channel=1 AND market_place='UK' AND wrong_sku=0 AND is_parent=0
        AND COALESCE(sku,'') NOT LIKE 'amzn.gr.%'),
S AS (SELECT ot.asin, SUM(ot.quantity) u FROM public.order_transaction ot,b
      WHERE ot.source_name='AMAZON' AND ot.market_place='UK' AND ot.order_status='Completed'
        AND ot.order_date::date BETWEEN b.ws AND b.we GROUP BY ot.asin),
V AS (SELECT vs.asin, SUM(vs.ordered_units) vu FROM public.vendor_sales vs,b
      WHERE vs.start_time::date BETWEEN b.ws AND b.we GROUP BY vs.asin),
report AS (SELECT L.asin FROM L LEFT JOIN S s ON s.asin=L.asin LEFT JOIN V v ON v.asin=L.asin
           WHERE COALESCE(s.u,0)=0 AND COALESCE(v.vu,0)=0)
SELECT
  COUNT(*) AS report_rows,                                                  -- Expected 28,318
  COALESCE(MAX(s.u),0)  AS max_fba_fbm_units_in_report,                     -- Expected 0
  COALESCE(MAX(v.vu),0) AS max_vendor_units_in_report                       -- Expected 0
FROM report r
LEFT JOIN S s ON s.asin=r.asin
LEFT JOIN V v ON v.asin=r.asin;
```
**Expected:** 28,318 rows, and both max columns = 0.

---

## Check 4 — Positive spot-checks (these ARE in the report → every stream must be 0)
```sql
WITH b AS (SELECT DATE '2026-06-10' ws, DATE '2026-07-09' we)
SELECT a.asin,
  (SELECT COALESCE(SUM(quantity),0) FROM public.order_transaction o,b
     WHERE o.source_name='AMAZON' AND o.market_place='UK' AND o.order_status='Completed'
       AND o.asin=a.asin AND o.order_date::date BETWEEN b.ws AND b.we)         AS completed_units,   -- Expected 0
  (SELECT COUNT(*) FROM public.order_transaction o,b
     WHERE o.source_name='AMAZON' AND o.market_place='UK'
       AND o.asin=a.asin AND o.order_date::date BETWEEN b.ws AND b.we)         AS any_order_rows,     -- Expected 0
  (SELECT COALESCE(SUM(ordered_units),0) FROM public.vendor_sales v,b
     WHERE v.asin=a.asin AND v.start_time::date BETWEEN b.ws AND b.we)         AS vendor_units        -- Expected 0
FROM (VALUES ('B093T3TR2Y'),('B0GTQRN1PC')) AS a(asin);
```
**Expected:** all three columns = 0 for both ASINs.

---

## Check 5 — Negative spot-checks (these SOLD → must be ABSENT from the report)
```sql
WITH b AS (SELECT DATE '2026-06-10' ws, DATE '2026-07-09' we)
SELECT o.asin, SUM(o.quantity) AS completed_units_in_window
FROM public.order_transaction o,b
WHERE o.source_name='AMAZON' AND o.market_place='UK' AND o.order_status='Completed'
  AND o.asin IN ('B0CZXL6ZYG','B0CNQ1Q3BJ','B0DH4KYFPD')
  AND o.order_date::date BETWEEN b.ws AND b.we
GROUP BY o.asin ORDER BY 2 DESC;
```
**Expected:** B0CZXL6ZYG = 52, B0CNQ1Q3BJ = 48, B0DH4KYFPD = 44 — all > 0, so none of these appear in the report.

---

## Check 6 — Column-value trace for the top ASIN (B093T3TR2Y)
Report shows: UK stock 765, FBM 39, Impressions 221,027, Clicks 2,427, SKU LSCY290GR+RPR44WH.

```sql
WITH b AS (SELECT DATE '2026-06-10' ws, DATE '2026-07-09' we)
SELECT
  (SELECT COALESCE(SUM(impression),0) FROM public.traffic_data t,b
     WHERE t.which_channel=1 AND t.market_place='UK' AND t.ref_id='B093T3TR2Y'
       AND t.date BETWEEN b.ws AND b.we)                                        AS impressions,  -- Expected 221027
  (SELECT COALESCE(SUM(click),0) FROM public.traffic_data t,b
     WHERE t.which_channel=1 AND t.market_place='UK' AND t.ref_id='B093T3TR2Y'
       AND t.date BETWEEN b.ws AND b.we)                                        AS clicks,       -- Expected 2427
  (SELECT COALESCE(SUM(s.stock),0) FROM public.location_wise_inv_stock s
     WHERE s.location='UK' AND s.sku IN (
       SELECT DISTINCT CASE WHEN COALESCE(mapped_sku,'')<>'' THEN trim(mapped_sku)
         ELSE regexp_replace(regexp_replace(regexp_replace(trim(sku),'(-IDE|-CA|-IFR|-NL)$',''),'__[^_]*$',''),'_[^_]*$','') END
       FROM public.listing_data WHERE which_channel=1 AND market_place='UK' AND wrong_sku=0
         AND is_parent=0 AND ref_id='B093T3TR2Y'))                              AS uk_stock,     -- Expected 765
  (SELECT COALESCE(SUM(quantity),0) FROM public.listing_data
     WHERE which_channel=1 AND market_place='UK' AND wrong_sku=0 AND is_parent=0
       AND ref_id='B093T3TR2Y' AND fulfilment='merchant'
       AND NOT (substring(regexp_replace(trim(sku),'(-IDE|-CA|-IFR|-NL)$','') from '_([A-Za-z0-9]+)$') ILIKE 'AM%'))
                                                                               AS fbm_stock;     -- Expected 39
```
**Expected:** 221027 · 2427 · 765 · 39.

---

## Sign-off
| Check | Expected | Their result | Pass? |
|---|---|---|---|
| 1 Window | 2026-07-04 / 2026-08-02 | | |
| 2 Funnel | 30,782 / 28,320 / 28,318 / 2 | | |
| 3 Integrity | 28,318 rows, max 0 / 0 | | |
| 4 Positive | all 0 | | |
| 5 Negative | 52 / 48 / 44 | | |
| 6 Trace | 221027 / 2427 / 765 / 39 | | |

If all six pass, the ZSFO logic and numbers are independently confirmed.
