#!/usr/bin/env python3
"""
REQ-28-D01 - Amazon PPC Keyword YoY Performance Dashboard (akyp) - builder
PRJ-2026-024 - account amazon Ledsone (sub_source 8) - markets UK/US/CA/DE/FR/IT

Read-only. Connects to the live ledsone DB via LED_* env creds, reads the KEYWORD-LEVEL
Amazon PPC table per marketplace, computes like-for-like current vs previous-YEAR windows,
and writes a single payload consumed by render_akyp_dashboard.py:
  - akyp_payload.json   (per-market keyword rows + daily series, for audit/repro + render)

Confirmed scope (Abiraj, 2026-08-14):
  account = amazon Ledsone (sub_source 8) ONLY, across UK=23, US=24, CA=26, DE=10, FR=9, IT=14.
  Comparison = TRUE YoY exactly as the spec HTML defines (current window vs same window one
  year back).

SOURCE (rev 2026-08-14, after Sajeesan added the keyword tables to amazon_campaigns):
  Primary = amazon_campaigns.keyword_performance_data - one row per KEYWORD per day, the
  keyword total (manual-targeting keywords only: BROAD/PHRASE/EXACT; auto-targeting search
  terms are NOT keywords and are excluded by design). Correct entity for a keyword dashboard
  and, unlike search_term_performance_data (Nov-2025 onward only), it carries history back to
  2023, so TRUE YoY populates. Joined to:
    - campaigns  (sub_source / market_place filter + campaign_name)
    - ad_groups  (ad_group_name)
    - keywords   (current keyword_bid + state)

Grain: one row per keyword target (keyword_id) = keyword x campaign x ad_group.
Attribution: Amazon SP default = 7-day -> sales = SUM(sales_7d), orders = SUM(purchases_7d)
(matches the spec's "7 day total sales/orders" header priority). spend = SUM(cost).
bid = current keywords.keyword_bid. suggestedBid has no source column -> null (spec treats
null as "no suggested bid"). status = active unless current keyword state <> ENABLED.
Every figure is live; nothing is copied from the spec demo data.

Note: the CURRENT window under-reports vs a fully-settled prior-year window because Amazon's
7-day attribution has not matured on the most recent ~7 days - inherent to any fresh-vs-settled
comparison, not a data gap.
"""
import os, json, datetime as dt
import psycopg2

HERE = os.path.dirname(os.path.abspath(__file__))
PAYLOAD = os.path.join(HERE, "akyp_payload.json")

ACCOUNT_SUB_SOURCE = 8
ACCOUNT_NAME = "amazon Ledsone"

# spec marketplace key -> (market_place id, currency, symbol, locale)
MARKETS = {
    "UK": (23, "GBP", "£", "en-GB"),
    "US": (24, "USD", "$",      "en-US"),
    "CA": (26, "CAD", "$",      "en-CA"),
    "DE": (10, "EUR", "€", "de-DE"),
    "FR": (9,  "EUR", "€", "fr-FR"),
    "IT": (14, "EUR", "€", "it-IT"),
}

# Keyword-level current + previous-year roll-up for one marketplace, in one pass.
KW_SQL = """
SELECT p.keyword_id,
       MAX(p.keyword_text)                       AS keyword_text,
       c.campaign_name,
       COALESCE(ag.ad_group_name, '—')           AS ad_group_name,
       MAX(p.match_type)                         AS match_type,
       CASE WHEN COALESCE(MAX(kw.state),'ENABLED')='ENABLED' THEN 'active' ELSE 'paused' END AS status,
       MAX(kw.keyword_bid)                       AS bid,
       -- current window
       COALESCE(SUM(p.sales_7d)     FILTER (WHERE p.date BETWEEN %(cs)s AND %(ce)s),0) AS c_sales,
       COALESCE(SUM(p.purchases_7d) FILTER (WHERE p.date BETWEEN %(cs)s AND %(ce)s),0) AS c_orders,
       COALESCE(SUM(p.impressions)  FILTER (WHERE p.date BETWEEN %(cs)s AND %(ce)s),0) AS c_impr,
       COALESCE(SUM(p.clicks)       FILTER (WHERE p.date BETWEEN %(cs)s AND %(ce)s),0) AS c_clicks,
       COALESCE(SUM(p.cost)         FILTER (WHERE p.date BETWEEN %(cs)s AND %(ce)s),0) AS c_spend,
       -- previous-year window
       COALESCE(SUM(p.sales_7d)     FILTER (WHERE p.date BETWEEN %(ps)s AND %(pe)s),0) AS p_sales,
       COALESCE(SUM(p.purchases_7d) FILTER (WHERE p.date BETWEEN %(ps)s AND %(pe)s),0) AS p_orders,
       COALESCE(SUM(p.impressions)  FILTER (WHERE p.date BETWEEN %(ps)s AND %(pe)s),0) AS p_impr,
       COALESCE(SUM(p.clicks)       FILTER (WHERE p.date BETWEEN %(ps)s AND %(pe)s),0) AS p_clicks,
       COALESCE(SUM(p.cost)         FILTER (WHERE p.date BETWEEN %(ps)s AND %(pe)s),0) AS p_spend
FROM amazon_campaigns.keyword_performance_data p
JOIN amazon_campaigns.campaigns  c  ON c.campaign_id  = p.campaign_id
LEFT JOIN amazon_campaigns.ad_groups ag ON ag.ad_group_id = p.ad_group_id
LEFT JOIN amazon_campaigns.keywords  kw ON kw.keyword_id   = p.keyword_id
WHERE c.sub_source = %(sub)s AND c.market_place = %(mkt)s
  AND p.keyword_text IS NOT NULL AND p.keyword_text <> ''
  AND (p.date BETWEEN %(cs)s AND %(ce)s OR p.date BETWEEN %(ps)s AND %(pe)s)
GROUP BY p.keyword_id, c.campaign_name, COALESCE(ag.ad_group_name, '—')
HAVING COALESCE(SUM(p.impressions) FILTER (WHERE p.date BETWEEN %(cs)s AND %(ce)s),0)
     + COALESCE(SUM(p.impressions) FILTER (WHERE p.date BETWEEN %(ps)s AND %(pe)s),0) > 0;
"""

DAILY_SQL = """
SELECT p.date::text AS d, COALESCE(SUM(p.sales_7d),0) AS sales
FROM amazon_campaigns.keyword_performance_data p
JOIN amazon_campaigns.campaigns c ON c.campaign_id = p.campaign_id
WHERE c.sub_source = %(sub)s AND c.market_place = %(mkt)s
  AND p.date BETWEEN %(start)s AND %(end)s
GROUP BY p.date ORDER BY p.date;
"""


def minus_one_year(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    y -= 1
    try:
        return dt.date(y, m, d).isoformat()
    except ValueError:
        return dt.date(y, m, 28).isoformat()   # clamp Feb-29 -> Feb-28


def connect():
    return psycopg2.connect(
        host=os.environ["LED_PGHOST"], port=os.environ.get("LED_PGPORT", 5432),
        dbname=os.environ["LED_PGDATABASE"], user=os.environ["LED_PGUSER"],
        password=os.environ["LED_PGPASSWORD"], connect_timeout=30)


def agg(sales, orders, impr, clicks, spend):
    return {"sales": round(float(sales), 2), "orders": int(orders),
            "impressions": int(impr), "clicks": int(clicks), "spend": round(float(spend), 2)}


def fetch_market(cur, mkt_id, cs, ce, ps, pe):
    p = dict(sub=ACCOUNT_SUB_SOURCE, mkt=mkt_id, cs=cs, ce=ce, ps=ps, pe=pe)
    cur.execute(KW_SQL, p)
    keywords = []
    for (kid, kw, camp, ag, match, status, bid,
         c_sales, c_orders, c_impr, c_clicks, c_spend,
         p_sales, p_orders, p_impr, p_clicks, p_spend) in cur.fetchall():
        keywords.append({
            "keyword": kw, "campaign": camp, "adGroup": ag,
            "matchType": (match or "").upper(), "status": status,
            "bid": float(bid) if bid is not None else None, "suggestedBid": None,
            "cur": agg(c_sales, c_orders, c_impr, c_clicks, c_spend),
            "prev": agg(p_sales, p_orders, p_impr, p_clicks, p_spend),
        })
    cur.execute(DAILY_SQL, dict(sub=ACCOUNT_SUB_SOURCE, mkt=mkt_id, start=cs, end=ce))
    cur_daily = [{"date": d, "sales": round(float(s), 2)} for (d, s) in cur.fetchall()]
    cur.execute(DAILY_SQL, dict(sub=ACCOUNT_SUB_SOURCE, mkt=mkt_id, start=ps, end=pe))
    prev_daily = [{"date": d, "sales": round(float(s), 2)} for (d, s) in cur.fetchall()]
    return keywords, cur_daily, prev_daily


def main():
    ref = os.environ.get("AKYP_REFERENCE_DATE") or dt.date.today().isoformat()
    d = dt.date.fromisoformat(ref)
    cur_start = d.replace(day=1).isoformat()
    cur_end = ref
    prev_start = minus_one_year(cur_start)
    prev_end = minus_one_year(cur_end)

    payload = {
        "generatedAt": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "referenceDate": ref,
        "account": ACCOUNT_NAME, "accountKey": "LEDSone", "accountSubSource": ACCOUNT_SUB_SOURCE,
        "periodLabel": "Month-to-Date",
        "source": "amazon_campaigns.keyword_performance_data (7-day attribution)",
        "curStart": cur_start, "curEnd": cur_end,
        "prevStart": prev_start, "prevEnd": prev_end,
        "markets": {},
    }

    conn = connect()
    try:
        cur = conn.cursor()
        for key, (mkt_id, currency, symbol, locale) in MARKETS.items():
            keywords, cur_daily, prev_daily = fetch_market(
                cur, mkt_id, cur_start, cur_end, prev_start, prev_end)
            prev_present = any(k["prev"]["impressions"] or k["prev"]["clicks"] or k["prev"]["sales"]
                               for k in keywords)
            payload["markets"][key] = {
                "marketPlaceId": mkt_id, "currency": currency, "symbol": symbol, "locale": locale,
                "previousAvailable": prev_present,
                "current": {"start": cur_start, "end": cur_end, "daily": cur_daily},
                "previous": {"start": prev_start, "end": prev_end, "daily": prev_daily},
                "keywords": keywords,
            }
            cs = sum(k["cur"]["sales"] for k in keywords)
            psum = sum(k["prev"]["sales"] for k in keywords)
            print(f"  {key:2s} mkt={mkt_id:<3} keywords={len(keywords):<5} "
                  f"cur_sales={cs:>10.2f}  prev_sales={psum:>10.2f}  "
                  f"prev={'YES' if prev_present else 'empty'}")
        cur.close()
    finally:
        conn.close()

    with open(PAYLOAD, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1, default=str)
    tot = sum(len(m["keywords"]) for m in payload["markets"].values())
    print(f"OK  markets={len(payload['markets'])}  total_keyword_rows={tot}")
    print(f"    current={cur_start}..{cur_end}  previous(YoY)={prev_start}..{prev_end}")
    print(f"    payload={PAYLOAD}")


if __name__ == "__main__":
    main()
