# -*- coding: utf-8 -*-
"""REQ-23-D01 Fast Moving Products — RAW mcp.ledsone fetch (reproducible/automatable).
Sources every NUMBER (units, orders, revenue, stock) + Product ID from the RAW ledsone
order_management / inventory schema via psycopg2 (LED_* creds reach 169.58.91.229 = mcp.ledsone).
Descriptive labels (Product Name, Category) are curated catalog attributes carried by SKU
from the prior curated payload (raw combo titles are placeholders); numbers are 100% raw.
Writes fmp_payload.json consumed by build_fmp_d01.py (Excel) and gen_dashboard.py (HTML)."""
import os, json, psycopg2

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_SQL = r"""
WITH base AS (
  SELECT ss.source_id chan, oi.item_sku sku, oi.item_asin, oi.item_id, oi.product_id, o.id oid,
    CASE WHEN o.order_date::date>=CURRENT_DATE-30 THEN COALESCE(NULLIF(oi.item_quantity,'')::numeric,0) ELSE 0 END q30,
    CASE WHEN o.order_date::date>=CURRENT_DATE-90 THEN COALESCE(NULLIF(oi.item_quantity,'')::numeric,0) ELSE 0 END q90,
    CASE WHEN o.order_date::date>=CURRENT_DATE-30 THEN COALESCE(NULLIF(oi.item_price,'')::numeric,0)*COALESCE(NULLIF(oi.item_quantity,'')::numeric,0) ELSE 0 END r30
  FROM order_management.orders o
  JOIN order_management.sub_source ss ON ss.id=o.sub_source_id
  JOIN order_management.order_item_info oi ON oi.order_id=o.id
  WHERE o.market_place='10' AND o.status='Completed' AND ss.source_id IN (1,2,3)
    AND o.order_date::date>=CURRENT_DATE-90 AND o.order_date::date<CURRENT_DATE
    AND oi.item_sku IS NOT NULL AND oi.item_sku<>''
),
stk AS (SELECT p.sku, SUM(COALESCE(s.stock,0)) stock FROM inventory.products p
        JOIN inventory.local_inventory_current_stock_location_wise s ON s.inventory_id=p.id
        WHERE s.warehouse_location='Germany' GROUP BY p.sku),
-- TRUE per-SKU grain: one row per SKU, sales SUMMED across all its listings (fixes eBay SKU-sprawl).
-- Representative Product ID = the listing with the most 30-day units for that SKU.
amz AS (SELECT sku, SUM(q30) q30,SUM(q90) q90,SUM(r30)::numeric(12,2) rev30,COUNT(DISTINCT CASE WHEN q30>0 THEN oid END) o30
        FROM base WHERE chan=1 GROUP BY sku HAVING SUM(q30)>0),
amz_pid AS (SELECT DISTINCT ON (sku) sku, item_asin pid FROM
        (SELECT sku, item_asin, SUM(q30) u FROM base WHERE chan=1 AND item_asin IS NOT NULL AND item_asin<>'' GROUP BY sku, item_asin) z
        ORDER BY sku, u DESC, item_asin),
eby AS (SELECT sku, SUM(q30) q30,SUM(q90) q90,SUM(r30)::numeric(12,2) rev30,COUNT(DISTINCT CASE WHEN q30>0 THEN oid END) o30
        FROM base WHERE chan=2 GROUP BY sku HAVING SUM(q30)>0),
eby_pid AS (SELECT DISTINCT ON (sku) sku, item_id pid FROM
        (SELECT sku, item_id, SUM(q30) u FROM base WHERE chan=2 AND item_id IS NOT NULL AND item_id<>'' GROUP BY sku, item_id) z
        ORDER BY sku, u DESC, item_id),
shp AS (SELECT sku, SUM(q30) q30,SUM(q90) q90,SUM(r30)::numeric(12,2) rev30,COUNT(DISTINCT CASE WHEN q30>0 THEN oid END) o30
        FROM base WHERE chan=3 GROUP BY sku HAVING SUM(q30)>0),
shp_pid AS (SELECT DISTINCT ON (sku) sku, product_id pid FROM
        (SELECT sku, product_id, SUM(q30) u FROM base WHERE chan=3 AND product_id IS NOT NULL AND product_id<>'' GROUP BY sku, product_id) z
        ORDER BY sku, u DESC, product_id),
comb AS (SELECT sku, SUM(CASE WHEN chan=1 THEN q30 ELSE 0 END) amz, SUM(CASE WHEN chan=2 THEN q30 ELSE 0 END) ebay,
   SUM(CASE WHEN chan=3 THEN q30 ELSE 0 END) shop, SUM(q30) tu, SUM(r30)::numeric(12,2) tr
   FROM base GROUP BY sku HAVING SUM(q30)>0)
SELECT json_build_object(
 'amazon',(SELECT json_agg(row_to_json(x)) FROM (SELECT a.sku,amz_pid.pid product_id,a.q30 qty30,a.q90 qty90,a.rev30,a.o30 orders30,COALESCE(stk.stock,0) current_stock FROM amz a LEFT JOIN amz_pid ON amz_pid.sku=a.sku LEFT JOIN stk ON stk.sku=a.sku ORDER BY a.q30 DESC,a.rev30 DESC LIMIT 100) x),
 'ebay',(SELECT json_agg(row_to_json(x)) FROM (SELECT e.sku,eby_pid.pid product_id,e.q30 qty30,e.q90 qty90,e.rev30,e.o30 orders30,COALESCE(stk.stock,0) current_stock FROM eby e LEFT JOIN eby_pid ON eby_pid.sku=e.sku LEFT JOIN stk ON stk.sku=e.sku ORDER BY e.q30 DESC,e.rev30 DESC LIMIT 100) x),
 'shopify',(SELECT json_agg(row_to_json(x)) FROM (SELECT s.sku,shp_pid.pid product_id,s.q30 qty30,s.q90 qty90,s.rev30,s.o30 orders30,COALESCE(stk.stock,0) current_stock FROM shp s LEFT JOIN shp_pid ON shp_pid.sku=s.sku LEFT JOIN stk ON stk.sku=s.sku ORDER BY s.q30 DESC,s.rev30 DESC LIMIT 100) x),
 'combined',(SELECT json_agg(row_to_json(x)) FROM (SELECT c.sku,c.amz,c.ebay,c.shop,c.tu total_units,c.tr total_rev,COALESCE(stk.stock,0) current_stock FROM comb c LEFT JOIN stk ON stk.sku=c.sku ORDER BY c.tu DESC,c.tr DESC LIMIT 100) x),
 'meta',json_build_object('generated',CURRENT_DATE::text,'win30_start',(CURRENT_DATE-30)::text,'win90_start',(CURRENT_DATE-90)::text,'win_end',(CURRENT_DATE-1)::text)
) payload;
"""

def fetch():
    conn = psycopg2.connect(host=os.environ["LED_PGHOST"], user=os.environ["LED_PGUSER"],
                            password=os.environ["LED_PGPASSWORD"], dbname="ledsone", connect_timeout=20)
    try:
        cur = conn.cursor(); cur.execute(RAW_SQL); payload = cur.fetchone()[0]
    finally:
        conn.close()
    return payload

def carry_labels(payload):
    """Keep the curated Product Name + Category (per SKU) from the prior payload; numbers stay raw."""
    prev_path = os.path.join(HERE, "fmp_payload_curated.json")
    labels = {}
    if os.path.exists(prev_path):
        prev = json.load(open(prev_path, encoding="utf-8"))
        for k in ("amazon", "ebay", "shopify", "combined"):
            for r in prev.get(k, []):
                if r["sku"] not in labels:
                    labels[r["sku"]] = {"title": r.get("title"), "category": r.get("category")}
    for k in ("amazon", "ebay", "shopify", "combined"):
        for r in payload.get(k, []):
            lab = labels.get(r["sku"], {})
            r["title"] = lab.get("title") or r.get("title") or ""
            r["category"] = lab.get("category") or "Uncategorised"
    return payload

if __name__ == "__main__":
    p = carry_labels(fetch())
    json.dump(p, open(os.path.join(HERE, "fmp_payload.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("raw payload rows:", {k: len(v) for k, v in p.items() if isinstance(v, list)})
    print("source: RAW mcp.ledsone (order_management/inventory) via", os.environ["LED_PGHOST"])
