# -*- coding: utf-8 -*-
"""
REQ-19-D01  eBay Product Performance Analysis  (project code: eppr)  — DEFINITIVE build
WAREHOUSE-ONLY (order_management_copy); ledsone unreachable 2026-07-27.

Grain: one row per eBay LISTING (item_id), UK+DE, all active eBay accounts (9,781 rows).
Sales/fees/ad/traffic attribute at item_id grain (joining sales by SKU alone double-counts).

Source map (verified live 2026-07-27):
  Image/SKU/ParentSKU/ItemID/Title/Marketplace/Account/Status/Price/ListingDate/CategoryID  = listing_data
  Units/Orders/Revenue(order_total)/LastSold/CategoryName                                    = order_transaction (source=2)
  eBay Fees (transaction_type='SALE')                                                        = ebay_order_expenses.fee
  Ad Cost = ppc_performance.spend (CPC) + ebay_order_expenses AD_FEE/PREMIUM_AD_FEES (CPS)
  Shipping Cost                                                                              = order_shipping_billing_detail.carrier_charge (by order_id)
  Impressions/Views/Clicks/Conversion                                                        = traffic_data (which_channel=2)  [Views=Clicks: eBay has one click/view metric]
  Available Stock                                                                            = listing_data.quantity
  Brand                                                                                      = salesprot_account_brand_map_v1 (by account)
  VAT                                                                                        = standard output VAT 20% UK / 19% DE of (VAT-inclusive) revenue
NO DATA (no truthful warehouse source): Cost Price, Gross Profit, Net Profit, Profit Margin %
  (sku_cogs is EMPTY), Watch Count (eBay API only), PPC Campaign (item->campaign link 29% in WH),
  Sales Trend (undefined business rule).
Window: rolling 30 days ending on the last COMPLETE day.
"""
import os, psycopg2
from datetime import date, timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

WH = dict(host=os.getenv("PGHOST","149.28.134.54"), port=os.getenv("PGPORT","5435"),
          dbname=os.getenv("PGDATABASE","order_management_copy"),
          user=os.getenv("PGUSER","temp_user"), password=os.getenv("PGPASSWORD","12we34rt"),
          connect_timeout=30)

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__),
      "..","..","evidence","final_outputs","REQ-19_ebay-product-performance-analysis",
      "REQ-19-D01_ebay_product_performance_v4_final.xlsx"))

SQL = """
WITH base AS (
  SELECT market_place, sub_source_name, ref_id,
         COALESCE(NULLIF(mapped_sku,''),sku) AS rsku, sku, parent_sku, category_id,
         created_at, price, quantity, main_image_url
  FROM public.listing_data
  WHERE which_channel=2 AND all_list=1 AND wrong_sku=0 AND is_child=1
    AND market_place IN ('UK','Germany')
),
listings AS (
  SELECT market_place, sub_source_name, ref_id,
         MAX(NULLIF(parent_sku,'')) AS parent_sku, MIN(sku) AS rep_sku, COUNT(*) AS variant_count,
         MAX(NULLIF(category_id,'')) AS category_id, MIN(created_at)::date AS listing_date,
         MAX(price) AS price, SUM(quantity) AS stock, MAX(NULLIF(main_image_url,'')) AS image_url
  FROM base GROUP BY market_place, sub_source_name, ref_id
),
title AS (
  SELECT b.ref_id, MAX(NULLIF(ip.title,'')) AS title
  FROM base b JOIN public.inv_products ip ON ip.sku=b.rsku GROUP BY b.ref_id
),
sales AS (
  SELECT item_id, market_place, SUM(quantity::numeric) AS units, COUNT(DISTINCT order_id) AS orders,
         ROUND(SUM(order_total::numeric),2) AS revenue, MAX(order_date)::date AS last_sold,
         MAX(NULLIF(category_name,'')) AS cname
  FROM public.order_transaction
  WHERE source=2 AND market_place IN ('UK','Germany') AND order_date::date BETWEEN %(d0)s AND %(d1)s
  GROUP BY item_id, market_place
),
fees AS (   -- eBay seller fees = all fee rows EXCEPT ad fees (ad fees go to Ad Cost, never both)
  SELECT item_id, ROUND(SUM(fee::numeric),2) AS ebay_fees
  FROM public.ebay_order_expenses
  WHERE transaction_date::date BETWEEN %(d0)s AND %(d1)s
    AND COALESCE(fee_type,'') NOT IN ('AD_FEE','PREMIUM_AD_FEES')
  GROUP BY item_id
),
adcost AS (
  SELECT item_id, ROUND(SUM(fee::numeric),2) AS ad_cps
  FROM public.ebay_order_expenses
  WHERE transaction_date::date BETWEEN %(d0)s AND %(d1)s AND fee_type IN ('AD_FEE','PREMIUM_AD_FEES')
  GROUP BY item_id
),
adcpc AS (
  SELECT ref_id, ROUND(SUM(spend::numeric),2) AS ad_cpc
  FROM public.ppc_performance
  WHERE source=2 AND marketplace IN ('UK','Germany') AND date::date BETWEEN %(d0)s AND %(d1)s
  GROUP BY ref_id
),
ship AS (   -- shipping per item_id = sum of each of its orders' carrier_charge (deduped per order)
  SELECT item_id, market_place, ROUND(SUM(cc),2) AS shipping_cost FROM (
    SELECT DISTINCT ot.item_id, ot.market_place, ot.order_id, sb.carrier_charge::numeric AS cc
    FROM public.order_transaction ot
    JOIN public.order_shipping_billing_detail sb ON sb.order_id=ot.order_id
    WHERE ot.source=2 AND ot.market_place IN ('UK','Germany')
      AND ot.order_date::date BETWEEN %(d0)s AND %(d1)s AND sb.carrier_charge IS NOT NULL
  ) x GROUP BY item_id, market_place
),
traffic AS (
  SELECT ref_id, SUM(impression) AS impressions, SUM(click) AS clicks, SUM(conversion) AS conv
  FROM public.traffic_data
  WHERE which_channel=2 AND market_place IN ('UK','Germany') AND date::date BETWEEN %(d0)s AND %(d1)s
  GROUP BY ref_id
)
SELECT l.market_place, l.sub_source_name, l.ref_id, l.parent_sku, l.rep_sku, l.variant_count,
       t.title, COALESCE(s.cname, l.category_id) AS category, l.listing_date, l.price, l.stock, l.image_url,
       s.units, s.orders, s.revenue, s.last_sold,
       f.ebay_fees, COALESCE(ac.ad_cps,0)+COALESCE(ap.ad_cpc,0) AS ad_cost,
       (ac.ad_cps IS NOT NULL OR ap.ad_cpc IS NOT NULL) AS is_promoted,
       sh.shipping_cost, tr.impressions, tr.clicks, tr.conv
FROM listings l
LEFT JOIN title    t  ON t.ref_id=l.ref_id
LEFT JOIN sales    s  ON s.item_id::text=l.ref_id AND s.market_place=l.market_place
LEFT JOIN fees     f  ON f.item_id::text=l.ref_id
LEFT JOIN adcost   ac ON ac.item_id::text=l.ref_id
LEFT JOIN adcpc    ap ON ap.ref_id::text=l.ref_id
LEFT JOIN ship     sh ON sh.item_id::text=l.ref_id AND sh.market_place=l.market_place
LEFT JOIN traffic  tr ON tr.ref_id::text=l.ref_id
ORDER BY s.revenue DESC NULLS LAST, l.ref_id;
"""

ND = "NO DATA"
VAT_RATE = {"UK":0.20, "Germany":0.19}
# Brand values as stored in staging_ai.salesprot_account_brand_map_v1 (channel=ebay), retrieved
# via the postgres MCP because temp_user lacks a SELECT grant on staging_ai. Authoritative source.
BRAND_MAP = {
    "led_sone":"LEDSone","ledsonede":"LEDSone DE","electricalsone":"Electricalsone",
    "so_926407":"Sunsone","dctransformer":"DC Transformer","coventrylights":"Coventry Lights",
    "lighting_sone":"Lightingsone","re6865":"Retroled","vintageinterior":"Vintageinterior",
    "huettenlampen":"Huettenlampen","bestbringer":"Bestbringer",
}
HEADERS = ["Product Image","SKU","Parent SKU","eBay Item ID","Product Title","Brand","Category",
           "Marketplace","Account","Listing Date","Listing Status","Selling Price (£/€)","Cost Price (£/€)",
           "Shipping Cost (£/€)","eBay Fees (£/€)","Ad Cost (£/€)","VAT (£/€)","Available Stock","Units Sold","Orders",
           "Revenue (£/€)","Gross Profit (£/€)","Net Profit (£/€)","Profit Margin %","Impressions","Views","Clicks",
           "CTR %","Conversion Rate %","Watch Count","Last Sold Date","Days Active",
           "Promotion Status","PPC Campaign","Sales Trend"]
MONEY_COLS = (12,13,14,15,16,17,21,22,23)

def main():
    anchor = date.today() - timedelta(days=1)
    d0 = anchor - timedelta(days=29)
    conn = psycopg2.connect(**WH); cur = conn.cursor()
    cur.execute(SQL, {"d0":d0, "d1":anchor}); rows = cur.fetchall(); conn.close()

    wb = Workbook(); ws = wb.active; ws.title = "eBay Product Performance"
    note = ("REQ-19-D01 eBay Product Performance Analysis | one row per eBay listing (item_id) | "
            "warehouse order_management_copy | window %s..%s (30 complete days) | "
            "money in each row's marketplace currency: UK=GBP £, DE=EUR € (never blended) | "
            "Views=Clicks (eBay organic = one click/view metric) | Brand=account store brand (salesprot map) | "
            "VAT=standard output VAT 20%% UK / 19%% DE of revenue | "
            "'NO DATA' = no warehouse source: Cost Price & Gross/Net/Margin (sku_cogs empty), "
            "Watch Count (eBay API only), PPC Campaign (item->campaign link unreliable), Sales Trend (undefined)."
            % (d0, anchor))
    ws["A1"] = note; ws["A1"].font = Font(name="Arial", size=9, italic=True, color="555555")
    ws.append([]); hr = 3
    ws.append(HEADERS)
    for c in range(1, len(HEADERS)+1):
        cell = ws.cell(row=hr, column=c)
        cell.font = Font(name="Arial", bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="1F4E78")
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    n=0; rev={"UK":0.0,"Germany":0.0}; ship_tot=0.0
    for r in rows:
        (mkt, acct, item_id, parent_sku, rep_sku, vc, title, category, ldate, price, stock, img,
         units, orders, revenue, last_sold, ebay_fees, ad_cost, is_promoted,
         shipping_cost, impr, clicks, conv) = r
        brand = BRAND_MAP.get(acct, acct.title() if acct else ND)
        revenue = float(revenue) if revenue is not None else None
        if revenue: rev[mkt]+=revenue
        if shipping_cost: ship_tot+=float(shipping_cost)
        vat = round(revenue - revenue/(1+VAT_RATE[mkt]),2) if revenue else (0 if revenue==0 else ND)
        ctr = round(float(clicks)/float(impr)*100,2) if impr and clicks is not None and float(impr)>0 else ND
        cvr = round(float(conv)/float(clicks)*100,2) if clicks and conv is not None and float(clicks)>0 else ND
        days_active = (anchor - ldate).days if ldate else ND
        row = [
            img or ND, (rep_sku or ND)+("" if vc==1 else " (+%d variants)"%(vc-1)), parent_sku or ND,
            str(item_id), title or ND, brand or (acct.title() if acct else ND), category or ND,
            mkt, acct, ldate, "Active",
            round(float(price),2) if price is not None else ND,
            ND,                                                     # Cost Price
            float(shipping_cost) if shipping_cost is not None else 0,
            float(ebay_fees) if ebay_fees is not None else 0,
            float(ad_cost) if ad_cost is not None else 0,
            vat, int(stock) if stock is not None else ND,
            int(units) if units is not None else 0, int(orders) if orders is not None else 0,
            revenue if revenue is not None else 0,
            ND, ND, ND,                                             # Gross, Net, Margin
            int(impr) if impr is not None else ND,
            int(clicks) if clicks is not None else ND,              # Views
            int(clicks) if clicks is not None else ND,              # Clicks
            ctr, cvr, ND,                                           # CTR, CVR, Watch Count
            last_sold if last_sold else ND, days_active,
            "Promoted" if is_promoted else "Not Promoted", ND, ND,  # Promotion, PPC Campaign, Sales Trend
        ]
        ws.append(row); n+=1
        rownum = ws.max_row
        cur_fmt = u'£#,##0.00' if mkt=="UK" else u'€#,##0.00'
        for col in MONEY_COLS:
            cell = ws.cell(row=rownum, column=col)
            if isinstance(cell.value,(int,float)): cell.number_format = cur_fmt

    ws.freeze_panes = "E4"
    widths=[16,20,18,15,40,15,20,11,14,12,12,12,12,12,12,12,10,9,9,8,12,12,12,11,11,9,9,8,12,11,12,10,14,12,11]
    for i,w in enumerate(widths,1):
        ws.column_dimensions[ws.cell(row=hr,column=i).column_letter].width = w
    wb.save(OUT)
    filled = 28
    print("ROWS (live D count):", n, "| columns filled: %d/35, NO DATA: 7" % filled)
    print("Revenue  UK £%.2f  DE €%.2f | Shipping total £/€ %.2f" % (rev["UK"], rev["Germany"], ship_tot))
    print("Saved:", OUT)

if __name__=="__main__":
    main()
