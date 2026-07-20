# -*- coding: utf-8 -*-
"""Build the eBay Return Analysis dashboard as a self-contained, light-theme HTML page.

Reads the built workbook (eBay_Return_Analysis_June2026.xlsx) and renders:
  - KPI cards (returns, blended rate, refund, return cost, ads, ACOS/ROAS, open cases)
  - the 19-column per-SKU table (sticky header + pinned SKU, RAG pills, rank badges, TOTAL row)
  - Return-Reason Breakdown (with bars) + Filter Options + Before/After efficiency panels
  - a Definitions block

The full table is rendered as STATIC HTML (visible with zero JavaScript, so it shows inside the
ph_task viewer). Account/Reason/SKU filtering + CSV export are progressive-enhancement JS that only
activate in a real browser; nothing is hidden without them.

Style mirrors PRJ-2026-011 (EBPD) — same teal/slate light theme, KPI cards, grouped sticky headers.

USAGE:  python build_returns_html.py [input.xlsx] [output.html] ["Month Label"]
"""
import sys, math, html
from datetime import datetime
import openpyxl

INP = sys.argv[1] if len(sys.argv) > 1 else "eBay_Return_Analysis_June2026.xlsx"
OUT = sys.argv[2] if len(sys.argv) > 2 else "eBay Return Analysis Dashboard - June 2026 - FINAL.html"
MONTH_LABEL = sys.argv[3] if len(sys.argv) > 3 else "June 2026"

HEADERS = ["SKU","Product Title","Account","Orders","Returns","Return Rate","Last Month Returns",
    "Last Year Returns","Refund (£)","Return Cost (£)","Main Return Reason","Return Rank",
    "Negative Feedback","Open Cases","Stock","Ad Spend (£)","Ad Sales (£)","ACOS","ROAS"]

# ---------------- read the workbook ----------------
def load(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["eBay Return Analysis"]
    rows, brk, eff = [], [], []
    filters = []
    mode = None
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        v = list(row)
        c0 = v[0]
        if i <= 4:  # banner (0-2) + blank (3) + header (4) rows
            continue
        if isinstance(c0, str) and c0.startswith("TOTAL"):
            mode = "after_total"; continue
        if mode is None and c0 not in (None, ""):
            rows.append(v)                       # a SKU data row
        if isinstance(c0, str) and c0.startswith("Return Reason Breakdown"):
            mode = "brk"; continue
        if mode == "brk":
            if c0 in ("Return Reason", None, ""):
                # filter block sits in cols 5-6 on the same rows
                if len(v) > 5 and v[4] not in (None, "") and v[4] != "Filter":
                    filters.append((v[4], v[5]))
                continue
            if isinstance(c0, str) and c0 == "Total":
                mode = "post_brk"   # non-None so no further data rows are collected
            else:
                brk.append((c0, v[1], v[2]))
                if len(v) > 5 and v[4] not in (None, "") and v[4] != "Filter":
                    filters.append((v[4], v[5]))
        if isinstance(c0, str) and c0.startswith("Return Workflow"):
            mode = "eff"; continue
        if mode == "eff":
            if c0 in ("KPI", None, ""): continue
            eff.append((v[0], v[1], v[2], v[3]))
    return rows, brk, filters, eff

# ---------------- formatting helpers ----------------
def _r(n): return math.floor(n + 0.5)
def esc(s): return html.escape("" if s is None else str(s))
def is_blank(x): return x is None or x == ""
DASH = '<span class="na">&mdash;</span>'
def gbp2(n): return DASH if is_blank(n) else "&pound;" + format(float(n), ",.2f")
def integ(n): return DASH if is_blank(n) else format(int(_r(float(n))), ",")
def pct1(n):  return DASH if is_blank(n) else ("%.1f%%" % (float(n) * 100))
def roasf(n): return DASH if is_blank(n) else ("%.2f&times;" % float(n))

def rate_cls(x):
    if is_blank(x): return ""
    x = float(x)
    return "rr" if x >= 0.5 else "y" if x >= 0.20 else "g"
def acos_cls(x):
    if is_blank(x): return ""
    x = float(x)
    return "g" if x < 0.12 else "y" if x <= 0.18 else "rr"
def roas_cls(x):
    if is_blank(x): return ""
    x = float(x)
    return "g" if x > 8 else "y" if x >= 5 else "rr"
def rank_badge(s):
    if is_blank(s): return DASH
    try: n = int(str(s).lstrip("#"))
    except ValueError: return esc(s)
    c = "rk1" if n == 1 else "rk2" if n == 2 else "rk3" if n == 3 else "rkn"
    return '<span class="rk %s">%d</span>' % (c, n)

REASON_TINT = {  # subtle left-tint by reason family
    "Wrong Size":"#e0a366","Ordered Wrong Item":"#c4cfdd","Not as Described":"#dc2626",
    "No Longer Needed":"#94a3b8","Defective Item":"#dc2626","Ordered Different Item":"#c4cfdd",
    "Ordered Accidentally":"#94a3b8","Arrived Damaged":"#dc2626","Buyer No-Show":"#94a3b8",
    "No Reason Given":"#cbd5e1","Withdrawn from Purchase":"#94a3b8"}

# ---------------- build ----------------
def build(path):
    rows, brk, filters, eff = load(path)
    n = len(rows)
    # totals
    def col(j): return [r[j] for r in rows]
    def s(j): return sum(float(x) for x in col(j) if not is_blank(x))
    t_orders, t_returns = s(3), s(4)
    t_lm, t_ly = s(6), s(7)
    t_refund, t_rcost = s(8), s(9)
    t_negfb, t_open = s(12), s(13)
    t_spend, t_sales = s(15), s(16)
    blended = t_returns / t_orders if t_orders else None
    acos = t_spend / t_sales if t_sales else None
    roas = t_sales / t_spend if t_spend else None
    accounts = sorted({(r[2] or "").strip() for r in rows if r[2]})

    # ---- KPI cards ----
    def kpi(ic, lbl, val, sub, cls=""):
        rib = ('<span class="rib">%s</span>' % ("GOOD" if cls == "g" else "WATCH")) if cls in ("g","a") else ""
        return ('<div class="kpi %s">%s<div class="ic">%s</div><div class="lbl">%s</div>'
                '<div class="val">%s</div><div class="sub">%s</div></div>'
                % (cls, rib, ic, lbl, val, sub))
    KP = [
        kpi("&#128260;","Total Returns", integ(t_returns), "%d SKUs returned" % n),
        kpi("&#128201;","Blended Return Rate", pct1(blended), "returns &divide; units ordered",
            "a" if (blended or 0) >= 0.15 else "g"),
        kpi("&#128181;","Total Refund", gbp2(t_refund), "seller refund paid"),
        kpi("&#129534;","Return Cost", gbp2(t_rcost), "refund + selling fees"),
        kpi("&#128227;","Ad Spend", gbp2(t_spend), "CPC + CPS combined"),
        kpi("&#127919;","ACOS", pct1(acos), "ad spend &divide; ad sales",
            "g" if (acos is not None and acos < 0.12) else "a"),
        kpi("&#128200;","ROAS", roasf(roas), "ad sales &divide; ad spend",
            "g" if (roas is not None and roas > 8) else "a"),
        kpi("&#128203;","Open Cases", integ(t_open), "%s negative feedback" % integ(t_negfb)),
    ]
    kpis = "".join(KP)

    # ---- main table body ----
    tb = []
    for r in rows:
        rate, ac, ro = r[5], r[17], r[18]
        stock = r[14]
        stock_cls = ' class="warn"' if (not is_blank(stock) and float(stock) == 0) else ""
        reason = r[10]
        tint = REASON_TINT.get((reason or "").strip(), "#cbd5e1")
        reason_html = ('<span class="reason" style="border-left:3px solid %s">%s</span>'
                       % (tint, esc(reason))) if reason else DASH
        rate_html = (('<span class="pill %s">%s</span>' % (rate_cls(rate), pct1(rate)))
                     if not is_blank(rate) else DASH)
        ac_html = (('<span class="pill %s">%s</span>' % (acos_cls(ac), pct1(ac)))
                   if not is_blank(ac) else DASH)
        ro_html = (('<span class="pill %s">%s</span>' % (roas_cls(ro), roasf(ro)))
                   if not is_blank(ro) else DASH)
        neg = r[12]
        neg_html = ('<span class="chip warn">%s</span>' % integ(neg)) if (not is_blank(neg) and float(neg) > 0) else '<span class="na">0</span>'
        opn = r[13]
        opn_html = ('<span class="chip amber">%s</span>' % integ(opn)) if (not is_blank(opn) and float(opn) > 0) else '<span class="na">0</span>'
        data_attr = 'data-acct="%s" data-reason="%s" data-sku="%s" data-rate="%s"' % (
            esc((r[2] or "").strip()), esc((reason or "").strip()),
            esc((r[0] or "")).lower(), (float(rate) if not is_blank(rate) else -1))
        tb.append(
          '<tr %s>' % data_attr +
          '<td class="sku">%s</td>' % esc(r[0]) +
          '<td class="title"><span title="%s">%s</span></td>' % (esc(r[1]), esc(r[1])) +
          '<td class="acct"><span class="flag">%s</span></td>' % esc(r[2]) +
          '<td class="sep">%s</td>' % integ(r[3]) +
          '<td class="strong">%s</td>' % integ(r[4]) +
          '<td>%s</td>' % rate_html +
          '<td class="dim">%s</td><td class="dim">%s</td>' % (integ(r[6]), integ(r[7])) +
          '<td class="sep">%s</td><td>%s</td>' % (gbp2(r[8]), gbp2(r[9])) +
          '<td class="sep lft">%s</td><td>%s</td>' % (reason_html, rank_badge(r[11])) +
          '<td class="sep">%s</td><td>%s</td><td%s>%s</td>' % (neg_html, opn_html, stock_cls, integ(stock)) +
          '<td class="sep">%s</td><td>%s</td><td>%s</td><td>%s</td>' % (
              gbp2(r[15]), gbp2(r[16]), ac_html, ro_html) +
          '</tr>')
    # total row
    tb.append(
      '<tr class="tot"><td class="sku">TOTAL / AVG</td><td class="title">%d SKUs</td><td></td>' % n +
      '<td class="sep">%s</td><td class="strong">%s</td>' % (integ(t_orders), integ(t_returns)) +
      '<td><span class="pill %s">%s</span></td>' % (rate_cls(blended), pct1(blended)) +
      '<td class="dim">%s</td><td class="dim">%s</td>' % (integ(t_lm), integ(t_ly)) +
      '<td class="sep">%s</td><td>%s</td>' % (gbp2(t_refund), gbp2(t_rcost)) +
      '<td class="sep">&mdash;</td><td>&mdash;</td>' +
      '<td class="sep">%s</td><td>%s</td><td>&mdash;</td>' % (integ(t_negfb), integ(t_open)) +
      '<td class="sep">%s</td><td>%s</td>' % (gbp2(t_spend), gbp2(t_sales)) +
      '<td><span class="pill %s">%s</span></td><td><span class="pill %s">%s</span></td></tr>' % (
          acos_cls(acos), pct1(acos), roas_cls(roas), roasf(roas)))
    tbody = "".join(tb)

    # ---- reason breakdown (bars) ----
    bmax = max((float(b[1]) for b in brk), default=1)
    br_rows = []
    for label, cnt, p in brk:
        tint = REASON_TINT.get((label or "").strip(), "#0d9488")
        w = (float(cnt) / bmax * 100) if bmax else 0
        br_rows.append(
          '<tr><td class="rlab"><span class="rdot" style="background:%s"></span>%s</td>'
          '<td class="rbarcell"><span class="rbar" style="width:%.1f%%;background:%s"></span></td>'
          '<td class="rt strong">%s</td><td class="rt dim">%s</td></tr>'
          % (tint, esc(label), w, tint, integ(cnt), pct1(p)))
    reason_tbl = "".join(br_rows)

    # ---- filters panel (static reference from the mockup) ----
    filt_rows = "".join('<tr><td class="fk">%s</td><td class="fv">%s</td></tr>' % (esc(k), esc(v))
                        for k, v in filters)

    # ---- before/after ----
    eff_rows = "".join(
        '<tr><td>%s</td><td class="rt">%s</td><td class="rt">%s</td><td class="rt up"><b>%s</b></td></tr>'
        % (esc(a), esc(b), esc(c), esc(d)) for a, b, c, d in eff)

    # ---- account filter options for the JS dropdown ----
    acct_opts = '<option value="">All accounts</option>' + "".join(
        '<option value="%s">%s</option>' % (esc(a), esc(a)) for a in accounts)
    reason_opts = '<option value="">All reasons</option>' + "".join(
        '<option value="%s">%s</option>' % (esc(b[0]), esc(b[0])) for b in brk)

    updated = datetime.now().strftime("%Y-%m-%d %H:%M")
    html_out = (HEAD + CSS + "</head><body>" +
        HERO % (MONTH_LABEL, n, updated) +
        '<div class="wrap">' +
        '<div class="kpis">%s</div>' % kpis +
        # toolbar (JS progressive enhancement)
        '<div class="toolbar">'
        '<span class="tbl">&#128269; Filter:</span>'
        '<select id="fAcct">%s</select>'
        '<select id="fReason">%s</select>'
        '<input id="fSku" type="text" placeholder="Search SKU / title&hellip;">'
        '<label class="chk"><input type="checkbox" id="fHigh"> High rate only (&ge;50%%)</label>'
        '<span class="spacer"></span>'
        '<span class="shown" id="shown"></span>'
        '<button id="csv" class="btn">&#8681; Export CSV</button>'
        '</div>' % (acct_opts, reason_opts) +
        # main table
        '<div class="shead"><h2><span class="d"></span> Per-SKU Returns '
        '<span class="count">%d SKUs</span></h2></div>' % n +
        '<div class="tcard"><div class="snote">&#8596; Scroll for all 19 columns &middot; SKU pinned &middot; '
        'headers fixed. Blank Return Rate = no orders in the period; blank ACOS/ROAS = no ad sales / spend '
        '(real, not errors).</div>'
        '<div class="scroll mainscroll"><table class="main" id="tbl">%s<tbody>%s</tbody></table></div></div>'
        % (MAIN_THEAD, tbody) +
        # reason + filters
        '<div class="grid2">'
        '<div class="panel"><h3>&#128202; Return-Reason Breakdown &mdash; %s</h3>'
        '<table class="mini rbrk"><tr><th>Reason</th><th></th><th class="rt">Returns</th><th class="rt">%%</th></tr>%s'
        '<tr class="ftot"><td>Total</td><td></td><td class="rt strong">%s</td><td class="rt dim">100.0%%</td></tr>'
        '</table></div>' % (MONTH_LABEL, reason_tbl, integ(t_returns)) +
        '<div class="panel"><h3>&#9881;&#65039; Filter Options</h3>'
        '<table class="mini filt">%s</table></div>'
        '</div>' % filt_rows +
        # before/after
        '<div class="panel wide"><h3>&#9889; Return Workflow &mdash; Before / After</h3>'
        '<table class="mini"><tr><th>Process</th><th class="rt">Before</th><th class="rt">After</th>'
        '<th class="rt">Improvement</th></tr>%s</table></div>' % eff_rows +
        DEFINITIONS % MONTH_LABEL +
        '<div class="foot">EBRA &middot; REQ-14 &middot; per-SKU eBay Return Analysis &middot; '
        'reporting period %s &middot; read-only from live Ledsone PostgreSQL &middot; generated %s</div>'
        % (MONTH_LABEL, updated) +
        '</div>' + SCRIPT + '</body></html>')
    return html_out, dict(n=n, returns=t_returns, refund=t_refund, rcost=t_rcost,
                          spend=t_spend, sales=t_sales, blended=blended, acos=acos, roas=roas,
                          brk_total=sum(float(b[1]) for b in brk))

# ---------------- static template chunks ----------------
HEAD = ('<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        '<title>eBay Return Analysis &mdash; June 2026</title>')

HERO = ('<header class="hero"><div class="hin">'
        '<div class="htitle"><span class="hicon">&#128260;</span>'
        '<div><h1>eBay Return Analysis Dashboard</h1>'
        '<div class="hsub">Reporting period <b>%s</b> &middot; all eBay stores &amp; marketplaces (UK, DE) '
        '&middot; one row per variant SKU with a return &middot; %d SKUs</div></div></div>'
        '<div class="hmeta"><span class="hchip">Source: live Ledsone PostgreSQL</span>'
        '<span class="hchip">Updated %s</span></div>'
        '</div></header>')

CSS = r'''<style>
:root{--bg:#eef1f5;--bg2:#e7ebf1;--card:#fff;--ink:#111a2b;--ink2:#28344a;--muted:#5b6a86;--faint:#8592a8;
--line:#e3e8ef;--line2:#eef1f6;--slate:#1e293b;--slate2:#334155;--teal:#0d9488;--teal2:#14b8a6;--tealbg:#d6f2ee;--teald:#0b7d72;
--green:#15803d;--greenbg:#dcf5e4;--amber:#b45309;--amberbg:#fceccb;--red:#dc2626;--redbg:#fce1e1;--gold:#d99e00;
--sh-sm:0 1px 2px rgba(17,26,43,.07);--sh:0 10px 28px -14px rgba(30,41,59,.32);--r:16px;}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;min-height:100vh;color:var(--ink);background:linear-gradient(180deg,var(--bg),var(--bg2));
font-family:"Segoe UI",-apple-system,BlinkMacSystemFont,Roboto,Arial,sans-serif;font-size:14.5px;line-height:1.5;-webkit-font-smoothing:antialiased}
.hero{background:linear-gradient(120deg,#0f2942,#123a4d 45%,#0d5f57);color:#fff;padding:11px 12px}
.hin{display:flex;align-items:center;justify-content:space-between;gap:18px;flex-wrap:wrap;max-width:none;margin:0}
.htitle{display:flex;align-items:center;gap:14px}
.hicon{width:46px;height:46px;border-radius:12px;background:rgba(255,255,255,.13);display:grid;place-items:center;font-size:24px}
.hero h1{margin:0;font-size:18px;font-weight:800;letter-spacing:.2px}
.hsub{font-size:11.5px;color:#c9dbe4;margin-top:2px}
.hicon{width:34px!important;height:34px!important;font-size:18px!important}
.hmeta{display:flex;gap:8px;flex-wrap:wrap}
.hchip{font-size:11px;font-weight:700;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.18);padding:5px 11px;border-radius:20px;color:#e8f2f5}
.wrap{width:100%;max-width:none;margin:0;padding:8px 3px 28px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin:6px 0 2px}
.kpi{position:relative;background:var(--card);border:1px solid var(--line);border-radius:11px;padding:8px 11px;box-shadow:var(--sh-sm);overflow:hidden}
.kpi .ic{width:24px;height:24px;border-radius:7px;display:grid;place-items:center;font-size:13px;background:var(--tealbg);margin-bottom:4px}
.kpi.g .ic{background:var(--greenbg)}.kpi.a .ic{background:var(--amberbg)}.kpi.r .ic{background:var(--redbg)}
.kpi .lbl{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;font-weight:700}
.kpi .val{font-size:17px;font-weight:800;margin-top:2px;color:var(--ink)}
.kpi .sub{font-size:10.5px;color:var(--faint);margin-top:2px}
.kpi .rib{position:absolute;top:0;right:0;padding:2px 9px;border-bottom-left-radius:10px;font-size:9px;font-weight:800}
.kpi.g .rib{background:var(--greenbg);color:var(--green)}.kpi.a .rib{background:var(--amberbg);color:var(--amber)}
.toolbar{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin:8px 0 3px;padding:8px 12px;background:var(--card);border:1px solid var(--line);border-radius:11px;box-shadow:var(--sh-sm)}
.toolbar .tbl{font-size:12.5px;font-weight:800;color:var(--slate2)}
.toolbar select,.toolbar input[type=text]{font:inherit;font-size:12.5px;padding:6px 10px;border:1px solid var(--line);border-radius:8px;background:#f7f9fc;color:var(--ink2)}
.toolbar input[type=text]{min-width:190px}
.toolbar .chk{font-size:12px;font-weight:600;color:var(--slate2);display:flex;align-items:center;gap:5px}
.toolbar .spacer{flex:1}
.toolbar .shown{font-size:12px;color:var(--muted);font-weight:700}
.btn{cursor:pointer;font:inherit;font-size:12.5px;font-weight:700;color:#fff;background:var(--teal);border:1px solid var(--teald);border-radius:8px;padding:7px 14px}
.btn:hover{background:var(--teald)}
.shead{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin:8px 0 5px}
.shead h2{font-size:15.5px;margin:0;display:flex;align-items:center;gap:9px;font-weight:700}
.shead h2 .d{width:9px;height:9px;border-radius:2px;background:var(--teal);transform:rotate(45deg)}
.count{font-size:12px;font-weight:700;color:var(--teal);background:var(--tealbg);padding:3px 10px;border-radius:20px}
.tcard{background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh);overflow:hidden}
.snote{font-size:11.5px;color:var(--faint);padding:9px 16px 0}
.scroll{overflow-x:auto}.mainscroll{overflow:auto;max-height:calc(100vh - 6px)}
table{border-collapse:separate;border-spacing:0;width:100%;font-variant-numeric:tabular-nums}
table.main{min-width:1580px;font-size:13px}
thead th{background:var(--slate2);color:#fff;font-weight:600;padding:10px 11px;white-space:nowrap;position:sticky;top:0;z-index:2;font-size:11.5px;vertical-align:middle}
thead tr.grp th{background:var(--slate);font-size:11px;text-transform:uppercase;letter-spacing:.9px;text-align:center;border-left:2px solid rgba(255,255,255,.14);padding:8px 10px}
thead tr.grp th.tealh{background:var(--teal)}
thead tr.cols th{top:34px;text-align:right;border-left:1px solid rgba(255,255,255,.08)}
th.sku,td.sku{position:sticky;left:0;text-align:left;min-width:132px}
thead th.sku{z-index:5;background:var(--slate2)}
tbody td.sku{background:var(--card);z-index:1;font-weight:800;font-size:12px;color:var(--ink)}
tbody td{padding:9px 11px;text-align:right;white-space:nowrap;border-bottom:1px solid var(--line2);color:var(--ink2)}
tbody tr:hover td{background:#f2fbf9}tbody tr:hover td.sku{background:#e9f7f4}
td.title{text-align:left;max-width:300px;overflow:hidden;text-overflow:ellipsis;color:var(--ink2)}
td.title span{display:block;max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
td.acct{text-align:left}td.strong{font-weight:800;color:var(--ink)}td.dim{color:#7986a0}
.sep{border-left:2px solid #dbe2ec}.lft{text-align:left}
.flag{display:inline-block;text-align:center;font-weight:800;color:#fff;background:var(--teal);border-radius:6px;padding:2px 8px;font-size:11px}
.pill{display:inline-block;padding:3px 9px;border-radius:7px;font-weight:800;font-size:12px}
.g{background:var(--greenbg);color:var(--green)}.y{background:var(--amberbg);color:var(--amber)}.rr{background:var(--redbg);color:var(--red)}
.chip{display:inline-block;padding:2px 8px;border-radius:6px;font-weight:800;font-size:11.5px}
.chip.warn{background:var(--redbg);color:var(--red)}.chip.amber{background:var(--amberbg);color:var(--amber)}
td.warn{background:var(--amberbg)!important;color:var(--amber);font-weight:800}
.reason{display:inline-block;padding:2px 8px 2px 8px;font-size:12px;font-weight:600;color:var(--ink2);background:#f4f7fb;border-radius:5px}
.na{color:var(--faint);font-style:italic;font-weight:600}
.rk{display:inline-grid;place-items:center;width:24px;height:24px;border-radius:50%;font-weight:800;font-size:11px;color:#fff}
.rk1{background:linear-gradient(145deg,#f3ca3e,#d99e00)}.rk2{background:linear-gradient(145deg,#c4cfdd,#94a3b8)}.rk3{background:linear-gradient(145deg,#e0a366,#c07b3a)}.rkn{background:#e4e9f0;color:#67728a}
tr.tot td{background:#eef4f3!important;font-weight:800;border-top:2px solid var(--teal);border-bottom:none;font-size:13px;color:var(--ink)}
tr.tot td.sku{background:#eef4f3!important}
.grid2{display:grid;grid-template-columns:1.15fr .85fr;gap:18px;margin-top:24px}@media(max-width:900px){.grid2{grid-template-columns:1fr}}
.panel{background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh-sm);overflow:hidden}
.panel.wide{margin-top:18px}
.panel h3{margin:0;padding:14px 18px;font-size:13.5px;background:var(--tealbg);color:#0b5f57;border-bottom:1px solid var(--line)}
.mini{width:100%;border-collapse:collapse;font-size:12.6px}.mini td,.mini th{padding:9px 14px;text-align:left;border-bottom:1px solid var(--line2)}
.mini th{color:var(--muted);font-weight:700;font-size:11px;text-transform:uppercase}.mini .rt{text-align:right}
.mini .strong{font-weight:800;color:var(--ink)}.mini .dim{color:var(--faint)}
.rbrk .rlab{font-weight:600;color:var(--ink2);white-space:nowrap}
.rdot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:7px;vertical-align:middle}
.rbarcell{width:99%}.rbar{display:block;height:11px;border-radius:6px;min-width:3px}
.rbrk .ftot td{background:#f4f8f7;font-weight:800;border-top:2px solid var(--teal)}
.filt .fk{font-weight:800;color:var(--slate2);white-space:nowrap;vertical-align:top;width:120px}
.filt .fv{color:var(--ink2)}
.up{color:var(--green)}
details.notes{margin-top:22px;background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh-sm);overflow:hidden}
details.notes summary{cursor:pointer;padding:15px 18px;font-weight:700;color:#0b5f57;background:var(--tealbg)}
details.notes .nb{padding:14px 22px;font-size:12.8px}details.notes ul{margin:0;padding-left:18px}details.notes li{margin:6px 0}
.foot{margin-top:26px;text-align:center;font-size:11.5px;color:var(--faint)}
@media print{.toolbar{display:none}.mainscroll{max-height:none;overflow:visible}table.main{min-width:0;font-size:9px}thead th{position:static}}
</style>'''

MAIN_THEAD = (r'''<thead><tr class="grp">'''
    r'''<th class="sku" rowspan="2">SKU</th><th rowspan="2">Product Title</th><th rowspan="2">Account</th>'''
    r'''<th colspan="5">Returns</th><th colspan="2">Cost</th><th colspan="2">Reason</th>'''
    r'''<th colspan="3">Service &amp; Stock</th><th colspan="4" class="tealh">Advertising</th></tr>'''
    r'''<tr class="cols"><th class="sep">Orders</th><th>Returns</th><th>Rate</th><th>LM</th><th>LY</th>'''
    r'''<th class="sep">Refund</th><th>Return Cost</th><th class="sep">Main Reason</th><th>Rank</th>'''
    r'''<th class="sep">Neg FB</th><th>Open</th><th>Stock</th>'''
    r'''<th class="sep">Ad Spend</th><th>Ad Sales</th><th>ACOS</th><th>ROAS</th></tr></thead>''')

DEFINITIONS = r'''<details class="notes"><summary>Definitions, data sources &amp; notes</summary><div class="nb"><ul>
<li><b>Grain</b> = one row per variant SKU with at least one eBay return in %s. SKU resolved via <code>transaction_id</code> &rarr; order line (not item_id, which maps to many variants).</li>
<li><b>Return Rate</b> = period returns &divide; period units ordered. <b>Blank</b> where there were no orders in the period (a return of an earlier-period purchase) &mdash; real, not an error. Rate &ge;50%% is flagged red, &ge;20%% amber.</li>
<li><b>Refund</b> = seller refund paid on the SKU's returns. <b>Return Cost</b> = eBay refund fees + selling fees (REFUND + FINAL_VALUE_FEE) on returned orders; &pound;0 where no matching fee row upstream (~65%% fee coverage).</li>
<li><b>Ad Spend / Ad Sales</b> = eBay Promoted Listings <b>CPC + CPS combined</b> (Advanced/ON_SITE spend from campaign performance + Standard/COST_PER_SALE ad fees). <b>ACOS</b> = spend &divide; sales &middot; <b>ROAS</b> = sales &divide; spend. Blank where a denominator is zero.</li>
<li><b>Negative Feedback</b> and <b>Open Cases</b> (latest state &ne; CLOSED) are period figures. <b>Stock</b> is a live snapshot (all locations), never period-bound; a zero stock cell is highlighted.</li>
<li><b>Return Rank</b> = SKUs ranked by period return count (ties broken by refund). Currency is mixed GBP (UK) + EUR (DE), not FX-normalised.</li>
</ul></div></details>'''

SCRIPT = r'''<script>
(function(){
 var tb=document.getElementById('tbl'); if(!tb) return;
 var rows=[].slice.call(tb.tBodies[0].rows).filter(function(r){return !r.classList.contains('tot')});
 var tot=tb.tBodies[0].querySelector('tr.tot');
 var fA=document.getElementById('fAcct'),fR=document.getElementById('fReason'),
     fS=document.getElementById('fSku'),fH=document.getElementById('fHigh'),shown=document.getElementById('shown');
 function apply(){
   var a=fA.value,rz=fR.value,q=(fS.value||'').toLowerCase().trim(),hi=fH.checked,c=0;
   rows.forEach(function(r){
     var ok=(!a||r.dataset.acct===a)&&(!rz||r.dataset.reason===rz)&&
            (!q||r.dataset.sku.indexOf(q)>-1)&&(!hi||parseFloat(r.dataset.rate)>=0.5);
     r.style.display=ok?'':'none'; if(ok)c++;
   });
   if(tot) tot.style.display=(a||rz||q||hi)?'none':'';
   shown.textContent=c+' / '+rows.length+' SKUs';
 }
 [fA,fR,fH].forEach(function(e){e.addEventListener('change',apply);});
 fS.addEventListener('input',apply); apply();
 document.getElementById('csv').addEventListener('click',function(){
   var head=[].slice.call(tb.querySelectorAll('thead tr.cols th')).map(function(th){return th.textContent;});
   head=['SKU','Product Title','Account'].concat(head);
   var out=[head.join(',')];
   rows.forEach(function(r){ if(r.style.display==='none')return;
     var cells=[].slice.call(r.cells).map(function(td){
       var t=td.textContent.replace(/—/g,'').replace(/\s+/g,' ').trim();
       return /[",\n]/.test(t)?'"'+t.replace(/"/g,'""')+'"':t; });
     out.push(cells.join(',')); });
   var blob=new Blob([out.join('\n')],{type:'text/csv;charset=utf-8;'}),u=URL.createObjectURL(blob),a=document.createElement('a');
   a.href=u; a.download='eBay_Return_Analysis.csv'; a.click(); URL.revokeObjectURL(u);
 });
})();
</script>'''

if __name__ == "__main__":
    out, stats = build(INP)
    open(OUT, "w", encoding="utf-8").write(out)
    print("wrote", OUT)
    print("  SKU rows       :", stats["n"])
    print("  Returns        :", int(stats["returns"]), " reason-breakdown total:", int(stats["brk_total"]))
    print("  Refund         : £%.2f" % stats["refund"])
    print("  Return Cost    : £%.2f" % stats["rcost"])
    print("  Ad Spend/Sales : £%.2f / £%.2f" % (stats["spend"], stats["sales"]))
    print("  Blended rate   : %.4f  ACOS %.4f  ROAS %.2f" % (stats["blended"], stats["acos"], stats["roas"]))
