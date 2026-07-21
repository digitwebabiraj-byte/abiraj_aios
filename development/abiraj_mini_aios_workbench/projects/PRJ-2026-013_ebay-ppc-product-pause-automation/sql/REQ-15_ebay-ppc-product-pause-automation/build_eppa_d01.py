"""
REQ-15-D01 — eBay PPC Product Pause Automation, LEDSone eBay UK.
Builds the Pause Log dashboard (HTML) + workbook (xlsx) from live data pulled 2026-07-21
from the raw `ledsone` DB via the Ledsone Postgres MCP (read-only).

Grain: CAMPAIGN — the same grain as the source task sheet (its "Item ID" column holds
campaign IDs). Rule engine is the source HTML's evaluate() implemented exactly.

Anchor date 2026-07-20 — the latest COMPLETE day. MAX(date) was 2026-07-21, but that day held
only ~1% of a normal day's traffic (8 clicks / GBP 1.39), which made the '30-day' window 29 days
plus a stub and understated every money figure by ~3.5%. Windows: 30D / 14D / 7D.
"""
import json, os, sys
from datetime import date

OUT = os.path.dirname(os.path.abspath(__file__))
FINAL = os.path.abspath(os.path.join(OUT, "..", "..", "evidence", "final_outputs",
                                     "REQ-15_ebay-ppc-product-pause-automation"))
os.makedirs(FINAL, exist_ok=True)

ANCHOR = "2026-07-20"

# ---- thresholds: from the source workbook's "Pause Rules" sheet. Configuration, never hardcoded
# logic — change them here and the whole report recomputes.
TH = dict(stock_floor=5, acos_ceiling=40.0, acos_rescue=20.0,
          clicks_min=20, spend_floor=2.50, prio_high=40.0, prio_med=15.0)

# ---- live pull 1: campaign metrics ------------------------------------------------------------
# campaign_id ~ name ~ target_type ~ status ~ stock_units_raw ~ nsku ~ nlist
#             ~ spend30 ~ sales30 ~ ord30 ~ spend7 ~ sales7 ~ ord14 ~ clicks14 ~ spend14
PERF = """13950665012~JD | MH | LEDSONE Cable | Manual~MANUAL~RUNNING~68.77~410.48~60~20.57~111.41~26~185~32.29
14841895012~JD | PH | Tharsika | Lamp Holders | Manual~MANUAL~RUNNING~121.42~241.34~34~32.71~99.82~18~352~55.05
15405839012~JD | PLA | Pendent Lights | Smart~SMART~RUNNING~117.85~254.99~18~29.11~0.00~9~267~59.18
15405904012~JD | PLA | Light Product | Smart~SMART~RUNNING~93.54~344.69~31~18.35~71.20~14~211~37.79
15603840012~JD | PH | PLA | Power Supply | Transformer | Manual~MANUAL~PAUSED~120.11~385.51~24~23.47~25.08~8~232~50.82
17109990012~JD | Spider Light | Manual~MANUAL~RUNNING~64.23~32.89~1~20.16~0.00~0~119~31.97
17371404012~JD | Sm wall | smart~SMART~PAUSED~91.20~194.54~11~18.13~18.89~4~241~40.01
22831214012~JD | Target product | Manual~MANUAL~PAUSED~93.55~336.79~29~14.88~15.48~15~148~35.15
26896653012~JD | PH | Flush light | Manual~MANUAL~RUNNING~80.46~206.62~21~23.39~52.80~14~247~47.04
28863417012~JD | MH | Cables | Jasmini | Smart~SMART~RUNNING~86.88~196.60~32~20.57~37.58~14~207~41.57
28863466012~JD | PH | power supply (fast moving) | Transformer  | smart~SMART~RUNNING~117.47~342.17~28~27.76~93.38~13~290~55.04
28863477012~JD | stock clearance products | Smart~SMART~RUNNING~92.94~244.38~18~17.34~132.58~9~196~38.04
34199100012~JD | PH | PSU 4 types | Transformer | Manual~MANUAL~RUNNING~128.55~555.55~34~27.26~147.39~17~278~58.30
38338866012~JD | MH | Wall lights | Shimee | Manual~MANUAL~RUNNING~50.74~160.76~11~12.94~106.64~7~168~28.57
85734687012~JD | Mixed Product | Manual~MANUAL~ENDED~57.37~145.01~6~0.00~0.00~2~19~3.98
129690774012~JD | PH |  All type | Transformer | Manual~MANUAL~RUNNING~126.39~385.92~32~25.63~75.04~13~258~53.21
129690966012~JD | PH | Lampshade  | Utharsika | Manual~MANUAL~PAUSED~90.09~150.68~14~14.35~13.89~6~215~35.41
135730419012~JD | MH | 3 head Pendent | Smart~SMART~RUNNING~95.46~301.05~10~18.58~0.00~2~168~39.14
144201913012~JD | Without general | Manual~MANUAL~RUNNING~90.66~273.33~34~14.42~85.82~11~152~36.17
149867100012~JD | Flush light | Smart~SMART~ENDED~57.03~47.47~3~0.00~0.00~0~2~0.52
153333633012~JD | PSU+Bulbs | Transformer | Manual~MANUAL~RUNNING~96.34~400.53~33~16.26~36.35~14~169~38.25
155212621012~JD | MH | Hemp Lights | Renuha | Manual~MANUAL~RUNNING~78.60~158.32~4~13.78~0.00~1~165~37.53
155338191012~JD | PH | BULB | TUWA | MANUAL~MANUAL~RUNNING~124.15~399.56~48~28.23~45.35~31~258~59.48
155945896012~JD | PH | Abinayaa | Light Fittings | Manual~MANUAL~RUNNING~100.02~353.25~40~21.09~124.72~20~216~44.05
156649526012~JD | Promotion Dec 2025  | smart~SMART~ENDED~62.74~131.09~11~0.00~0.00~0~33~6.28
157961601012~AK | PH | Pipe Lights | Theepana | Manual~MANUAL~ENDED~0.00~0.00~0~0.00~0.00~0~0~0.00
159695736012~JD | MH | Wire Cage | Paulroshan | Manual~MANUAL~ENDED~52.30~98.19~11~0.00~0.00~0~31~4.47
159902435012~JD | MH | Flush Light & Lamp Shade | Shanthini | Manual~MANUAL~RUNNING~85.63~388.11~30~22.74~118.34~18~305~47.44
159997785012~JD | MH | Lighting Accessories & Hardware | Tharsika.T | Manual~MANUAL~ENDED~23.41~66.37~9~0.00~0.00~2~4~0.48
160677049012~JD | PH | Pendant Light Fitting  | Tharshana | Manual~MANUAL~RUNNING~80.15~185.32~13~23.34~45.78~6~232~44.24
161244718012~JD | Cables | Target | Manual~MANUAL~RUNNING~86.72~577.92~77~21.43~79.57~42~231~42.41
161245031012~JD | Target Transformer | Manual~MANUAL~RUNNING~85.75~670.14~47~20.25~260.63~26~214~41.11
161303270012~JD | MH | Ceiling rose & Tapes | Prasath | Manual~MANUAL~ENDED~51.62~129.52~17~0.00~0.00~1~20~3.85
161307317012~MH | CHANDELIERS | Manual~MANUAL~ENDED~0.00~0.00~0~0.00~0.00~0~0~0.00
161412023012~PH | MH | Table Lamp | Ilakkiya | Manual~MANUAL~ENDED~0.00~0.00~0~0.00~0.00~0~0~0.00
161735955012~JD | LJ | Lighting Parts | Thojika | Manual~MANUAL~RUNNING~86.83~334.04~25~19.44~40.75~16~271~39.03
162961217012~JD | PH | Pendant - II | Manual~MANUAL~RUNNING~59.27~215.68~14~9.61~64.97~9~130~19.63
163055118012~JD | Wall light + video campaign~MANUAL~PAUSED~67.11~152.50~10~17.10~0.00~6~166~32.83
163193938012~JD | Ceiling Lights | Manual~MANUAL~RUNNING~92.09~192.56~11~20.40~85.13~5~259~41.04
163710397012~JD  | Shade+video campaign~SMART~RUNNING~57.63~133.83~11~4.37~0.00~2~102~18.02
164113429012~JD | Target Mixed | New | ST | smart~SMART~RUNNING~117.91~679.60~49~33.14~258.45~31~299~63.48
164195009012~JD | Wall lights | New | Manual~MANUAL~RUNNING~89.40~387.15~25~18.25~44.36~11~262~38.36
164267739012~JD | Plug in light | Manual~MANUAL~RUNNING~76.63~443.51~30~17.71~68.19~17~279~38.25
164421244012~JD | PH | 3 head pendant light | Manual~MANUAL~RUNNING~85.39~210.03~7~22.20~109.67~3~265~47.19
165065723012~JD | Cables | Video | Manual~MANUAL~RUNNING~28.01~250.58~35~12.09~54.12~13~114~22.49"""

# ---- live pull 2: stock position of the listings each campaign advertises ----------------------
# campaign_id ~ listings_total ~ listings_no_stock_data ~ listings_out_of_stock ~ listings_low_stock
STOCK = """13950665012~46~3~0~0
14841895012~56~0~0~0
15405839012~53~11~0~0
15405904012~23~4~0~0
15603840012~29~0~0~0
17109990012~20~6~1~0
17371404012~32~5~0~0
22831214012~58~14~1~0
26896653012~44~11~0~0
28863417012~6~0~0~0
28863466012~16~0~0~0
28863477012~36~4~0~0
34199100012~15~1~1~0
38338866012~17~6~0~0
85734687012~69~7~0~1
129690774012~60~1~0~0
129690966012~61~11~0~0
135730419012~30~1~0~0
144201913012~25~5~0~0
149867100012~40~13~0~0
153333633012~10~1~0~0
155212621012~8~1~0~0
155338191012~69~3~1~0
155945896012~51~12~1~1
156649526012~104~7~3~0
159695736012~31~6~0~0
159902435012~44~15~0~0
159997785012~19~2~0~0
160677049012~30~7~0~0
161244718012~15~0~0~0
161245031012~4~0~0~0
161303270012~11~2~0~0
161735955012~42~7~0~1
162961217012~92~14~2~0
163055118012~5~2~0~0
163193938012~77~17~0~0
163710397012~2~1~0~0
164113429012~24~4~1~0
164195009012~108~17~4~2
164267739012~36~4~0~0
164421244012~52~4~1~0
165065723012~8~0~0~0"""


def f(v):
    return float(v) if v not in ("", None) else 0.0


stock = {}
for line in STOCK.strip().split("\n"):
    cid, tot, nodata, oos, low = line.split("~")
    stock[cid] = dict(total=int(tot), nodata=int(nodata), oos=int(oos), low=int(low))

FIELDS = 12   # cid ~ name ~ type ~ status ~ s30 ~ sa30 ~ o30 ~ s7 ~ sa7 ~ o14 ~ c14 ~ s14
rows = []
for line in PERF.strip().split("\n"):
    p = line.split("~")
    # Guard the layout. An earlier snapshot carried 15 fields (three unused stock columns); silently
    # reading the wrong offsets would have produced a plausible-looking report with shifted numbers.
    assert len(p) == FIELDS, "PERF row has %d fields, expected %d: %s" % (len(p), FIELDS, p[0])
    cid = p[0]
    st = stock.get(cid, dict(total=0, nodata=0, oos=0, low=0))
    r = dict(
        campaign_id=cid, campaign=p[1], type=p[2].title() if p[2] != "-" else "-",
        status=p[3], listings=st["total"], no_stock_data=st["nodata"],
        out_of_stock=st["oos"], low_stock=st["low"],
        spend30=f(p[4]), sales30=f(p[5]), ord30=f(p[6]),
        spend7=f(p[7]), sales7=f(p[8]),
        ord14=f(p[9]), clicks14=f(p[10]), spend14=f(p[11]),
    )
    rows.append(r)


# ---- decisions: the ONE rule engine, shared with the weekly automation --------------------
sys.path.insert(0, OUT)
from eppa_engine import THRESHOLDS as TH_ENGINE, decide_all      # noqa: E402

rows, K = decide_all(rows, TH_ENGINE)
TH = TH_ENGINE
json.dump(dict(anchor=ANCHOR, thresholds=TH, kpis=K, rows=rows),
          open(os.path.join(FINAL, "eppa_d01_data.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("rows=%d paused=%d (stock %d / r1 %d / r2 %d) off=%d running=%d  at-risk=%.2f of %.2f"
      % (K["scope"], K["paused"], K["stock"], K["r1"], K["r2"], K["off"], K["running"],
         K["spend_at_risk"], K["spend_all"]))
