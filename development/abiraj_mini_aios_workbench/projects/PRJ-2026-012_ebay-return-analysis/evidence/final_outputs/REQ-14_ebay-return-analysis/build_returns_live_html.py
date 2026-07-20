# -*- coding: utf-8 -*-
"""Build the eBay Return Analysis dashboard WITH working in-month date-range presets (dropdown).

Each preset (Full month / 1st half / 2nd half / Week 1-4) is a real re-scope of the whole dashboard:
KPIs, the 19-column per-SKU table AND the reason breakdown are all recomputed for the chosen sub-window.
We run the canonical query once PER window against the live `ledsone` DB (read-only), then render every
view statically and switch between them with a dropdown backed by hidden CSS-radios -- so it degrades to
Full month with zero JavaScript (works inside the no-JS ph_task viewer).

Importable:  generate(month, conn, mockup_path) -> (html, views_data, cache, stats)
CLI:         python build_returns_live_html.py [YYYY-MM] [output.html]   (default month 2026-06)

Reuses the light-theme CSS + formatters + column layout from build_returns_html.py.
"""
import sys, os, re, json, calendar
from datetime import datetime
import psycopg2
import build_returns_html as B   # CSS, HERO, MAIN_THEAD, DEFINITIONS, formatters

HERE = os.path.dirname(os.path.abspath(__file__))
SECRETS = r"C:\Users\digit\OneDrive\Desktop\Abiraj_AIOS\development\abiraj_mini_aios_workbench\projects\PRJ-2026-011_ebay-account-performance-dashboard\automation\ebpd_secrets.bat"
# canonical query lives in the project's sql/ folder (works from either the worktree or the main tree)
def _sqlfile():
    for base in (
        os.path.abspath(os.path.join(HERE, "..", "..", "..", "sql", "REQ-14_ebay-return-analysis", "ebay_return_analysis.sql")),
        r"C:\Users\digit\OneDrive\Desktop\Abiraj_AIOS\development\abiraj_mini_aios_workbench\projects\PRJ-2026-012_ebay-return-analysis\sql\REQ-14_ebay-return-analysis\ebay_return_analysis.sql",
    ):
        if os.path.exists(base): return base
    raise FileNotFoundError("ebay_return_analysis.sql not found")
SQLFILE = _sqlfile()

# ---------------- month context ----------------
def month_ctx(month):
    yy, mm = int(month[:4]), int(month[5:7])
    ndays = calendar.monthrange(yy, mm)[1]
    def d(day): return "%04d-%02d-%02d" % (yy, mm, day)
    dnext = ("%04d-01-01" % (yy + 1)) if mm == 12 else ("%04d-%02d-01" % (yy, mm + 1))
    presets = [
        ("full", "Full month", d(1), dnext, None),
        ("h1", "1st half", d(1), d(16), (1, 15)),
        ("h2", "2nd half", d(16), dnext, (16, ndays)),
        ("w1", "Week 1", d(1), d(8), (1, 7)),
        ("w2", "Week 2", d(8), d(15), (8, 14)),
        ("w3", "Week 3", d(15), d(22), (15, 21)),
        ("w4", "Week 4", d(22), dnext, (22, ndays)),
    ]
    return {"yy": yy, "mm": mm, "ndays": ndays, "label": "%s %d" % (calendar.month_name[mm], yy),
            "mlab": calendar.month_abbr[mm], "presets": presets}

# ---------------- DB ----------------
def cred(key):
    for line in open(SECRETS, encoding="utf-8", errors="ignore"):
        m = re.match(r'\s*set\s+"?%s=([^"\r\n]*)"?' % re.escape(key), line, re.I)
        if m: return m.group(1).strip()
    return None

def make_conn():
    c = psycopg2.connect(host=cred("LED_PGHOST"), port=cred("LED_PGPORT") or 5432,
                         dbname=cred("LED_PGDATABASE"), user=cred("LED_PGUSER"),
                         password=cred("LED_PGPASSWORD"), connect_timeout=30)
    c.set_session(readonly=True, autocommit=True)
    return c

def parametrize(sql_text):
    """Split canonical SQL into (stmt1, stmt2) templates. Tokenize ONLY the reporting-window bounds
    (both spaced and no-space forms); last-month '< 2026-06-01' and last-year windows stay literal.
    Substitution is plain text (no psycopg2 %-binding), so the literal '%' in a comment is harmless."""
    mark = sql_text.index("BONUS")
    s1 = sql_text[:sql_text.index("/* ---", sql_text.index("ORDER BY returns DESC"))].strip().rstrip(";")
    s2 = sql_text[sql_text.index("WITH fr", mark):].strip().rstrip(";")
    def tok(s):
        s = s.replace(">= '2026-06-01'", ">= '__PS__'").replace(">='2026-06-01'", ">='__PS__'")
        s = s.replace("< '2026-07-01'", "< '__PE__'").replace("<'2026-07-01'", "<'__PE__'")
        return s
    return tok(s1), tok(s2)

def pull(conn, s1, s2, ps, pe):
    q1 = s1.replace("__PS__", ps).replace("__PE__", pe)
    q2 = s2.replace("__PS__", ps).replace("__PE__", pe)
    cur = conn.cursor()
    cur.execute(q1)
    rows = [[("" if v is None else v) for v in r] for r in cur.fetchall()]
    cur.execute(q2)
    brk = [[("" if v is None else v) for v in r] for r in cur.fetchall()]
    cur.close()
    return rows, brk

# ---------------- render one window (KPIs + tbody + reason) ----------------
def render_view(rows, brk, is_full):
    n = len(rows)
    def s(j): return sum(float(r[j]) for r in rows if not B.is_blank(r[j]))
    t_orders, t_returns = s(3), s(4)
    t_lm, t_ly = s(6), s(7)
    t_refund, t_rcost = s(8), s(9)
    t_negfb, t_open = s(12), s(13)
    t_spend, t_sales = s(15), s(16)
    blended = t_returns / t_orders if t_orders else None
    acos = t_spend / t_sales if t_sales else None
    roas = t_sales / t_spend if t_spend else None

    def kpi(ic, lbl, val, sub, cls=""):
        rib = ('<span class="rib">%s</span>' % ("GOOD" if cls == "g" else "WATCH")) if cls in ("g", "a") else ""
        return ('<div class="kpi %s">%s<div class="ic">%s</div><div class="lbl">%s</div>'
                '<div class="val">%s</div><div class="sub">%s</div></div>' % (cls, rib, ic, lbl, val, sub))
    kpis = "".join([
        kpi("&#128260;", "Total Returns", B.integ(t_returns), "%d SKUs returned" % n),
        kpi("&#128201;", "Blended Return Rate", B.pct1(blended), "returns &divide; units ordered",
            "a" if (blended or 0) >= 0.15 else "g"),
        kpi("&#128181;", "Total Refund", B.gbp2(t_refund), "seller refund paid"),
        kpi("&#129534;", "Return Cost", B.gbp2(t_rcost), "refund + selling fees"),
        kpi("&#128227;", "Ad Spend", B.gbp2(t_spend), "CPC + CPS combined"),
        kpi("&#127919;", "ACOS", B.pct1(acos), "ad spend &divide; ad sales",
            "g" if (acos is not None and acos < 0.12) else "a"),
        kpi("&#128200;", "ROAS", B.roasf(roas), "ad sales &divide; ad spend",
            "g" if (roas is not None and roas > 8) else "a"),
        kpi("&#128203;", "Open Cases", B.integ(t_open), "%s negative feedback" % B.integ(t_negfb)),
    ])

    tb = []
    for r in rows:
        rate, ac, ro, stock, reason = r[5], r[17], r[18], r[14], r[10]
        lm = "" if not is_full else r[6]
        ly = "" if not is_full else r[7]
        stock_cls = ' class="warn"' if (not B.is_blank(stock) and float(stock) == 0) else ""
        tint = B.REASON_TINT.get((reason or "").strip(), "#cbd5e1")
        reason_html = ('<span class="reason" style="border-left:3px solid %s">%s</span>' % (tint, B.esc(reason))) if reason else B.DASH
        rate_html = ('<span class="pill %s">%s</span>' % (B.rate_cls(rate), B.pct1(rate))) if not B.is_blank(rate) else B.DASH
        ac_html = ('<span class="pill %s">%s</span>' % (B.acos_cls(ac), B.pct1(ac))) if not B.is_blank(ac) else B.DASH
        ro_html = ('<span class="pill %s">%s</span>' % (B.roas_cls(ro), B.roasf(ro))) if not B.is_blank(ro) else B.DASH
        neg, opn = r[12], r[13]
        neg_html = ('<span class="chip warn">%s</span>' % B.integ(neg)) if (not B.is_blank(neg) and float(neg) > 0) else '<span class="na">0</span>'
        opn_html = ('<span class="chip amber">%s</span>' % B.integ(opn)) if (not B.is_blank(opn) and float(opn) > 0) else '<span class="na">0</span>'
        data_attr = 'data-acct="%s" data-reason="%s" data-sku="%s" data-rate="%s"' % (
            B.esc((r[2] or "").strip()), B.esc((reason or "").strip()),
            B.esc((r[0] or "")).lower(), (float(rate) if not B.is_blank(rate) else -1))
        tb.append(
          '<tr %s>' % data_attr +
          '<td class="sku">%s</td>' % B.esc(r[0]) +
          '<td class="title"><span title="%s">%s</span></td>' % (B.esc(r[1]), B.esc(r[1])) +
          '<td class="acct"><span class="flag">%s</span></td>' % B.esc(r[2]) +
          '<td class="sep">%s</td>' % B.integ(r[3]) +
          '<td class="strong">%s</td>' % B.integ(r[4]) +
          '<td>%s</td>' % rate_html +
          '<td class="dim">%s</td><td class="dim">%s</td>' % (B.integ(lm), B.integ(ly)) +
          '<td class="sep">%s</td><td>%s</td>' % (B.gbp2(r[8]), B.gbp2(r[9])) +
          '<td class="sep lft">%s</td><td>%s</td>' % (reason_html, B.rank_badge(r[11])) +
          '<td class="sep">%s</td><td>%s</td><td%s>%s</td>' % (neg_html, opn_html, stock_cls, B.integ(stock)) +
          '<td class="sep">%s</td><td>%s</td><td>%s</td><td>%s</td>' % (B.gbp2(r[15]), B.gbp2(r[16]), ac_html, ro_html) +
          '</tr>')
    tb.append(
      '<tr class="tot"><td class="sku">TOTAL / AVG</td><td class="title">%d SKUs</td><td></td>' % n +
      '<td class="sep">%s</td><td class="strong">%s</td>' % (B.integ(t_orders), B.integ(t_returns)) +
      '<td><span class="pill %s">%s</span></td>' % (B.rate_cls(blended), B.pct1(blended)) +
      '<td class="dim">%s</td><td class="dim">%s</td>' % (B.integ(t_lm) if is_full else B.DASH, B.integ(t_ly) if is_full else B.DASH) +
      '<td class="sep">%s</td><td>%s</td>' % (B.gbp2(t_refund), B.gbp2(t_rcost)) +
      '<td class="sep">&mdash;</td><td>&mdash;</td>' +
      '<td class="sep">%s</td><td>%s</td><td>&mdash;</td>' % (B.integ(t_negfb), B.integ(t_open)) +
      '<td class="sep">%s</td><td>%s</td>' % (B.gbp2(t_spend), B.gbp2(t_sales)) +
      '<td><span class="pill %s">%s</span></td><td><span class="pill %s">%s</span></td></tr>' % (
          B.acos_cls(acos), B.pct1(acos), B.roas_cls(roas), B.roasf(roas)))
    tbody = "".join(tb)

    bmax = max((float(b[1]) for b in brk), default=1)
    brh = []
    for label, cnt, p in brk:
        tint = B.REASON_TINT.get((label or "").strip(), "#0d9488")
        w = (float(cnt) / bmax * 100) if bmax else 0
        brh.append('<tr><td class="rlab"><span class="rdot" style="background:%s"></span>%s</td>'
                   '<td class="rbarcell"><span class="rbar" style="width:%.1f%%;background:%s"></span></td>'
                   '<td class="rt strong">%s</td><td class="rt dim">%s</td></tr>'
                   % (tint, B.esc(label), w, tint, B.integ(cnt), B.pct1(p)))
    reason_tbl = ('<div class="panel"><h3>&#128202; Return-Reason Breakdown</h3>'
        '<table class="mini rbrk"><tr><th>Reason</th><th></th><th class="rt">Returns</th><th class="rt">%</th></tr>'
        + "".join(brh) +
        '<tr class="ftot"><td>Total</td><td></td><td class="rt strong">%s</td><td class="rt dim">100.0%%</td></tr>'
        '</table></div>' % B.integ(t_returns))
    return {"kpis": kpis, "tbody": tbody, "reason": reason_tbl, "n": n,
            "returns": t_returns, "refund": t_refund, "spend": t_spend, "sales": t_sales,
            "blended": blended, "acos": acos, "roas": roas}

# ---------------- assemble multi-view HTML ----------------
def build(ctx, views_data, filters, eff, accounts, all_reasons, updated):
    label, mlab = ctx["label"], ctx["mlab"]
    radios = "".join('<input type="radio" name="ebrange" id="r-%s" class="rsel"%s>'
                     % (k, " checked" if i == 0 else "") for i, (k, _, _, _, _, _) in enumerate(views_data))
    css = [".rsel{position:absolute;opacity:0;pointer-events:none;width:0;height:0}", ".view{display:none}"]
    for k, _, _, _, _, _ in views_data:
        css.append("#r-%s:checked ~ .wrap .view-%s{display:block}" % (k, k))
    css.append(".rangesel{font:inherit;font-size:13px;font-weight:700;color:var(--slate2);background:#f3f6fa;"
               "border:1px solid var(--line);border-radius:8px;padding:7px 30px 7px 12px;cursor:pointer;"
               "appearance:none;-webkit-appearance:none;"
               "background-image:url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'><path d='M2 4l4 4 4-4' fill='none' stroke='%230b7d72' stroke-width='1.6'/></svg>\");"
               "background-repeat:no-repeat;background-position:right 10px center}")
    css.append(".rangesel:hover{border-color:var(--teal2)}")
    css.append(".rangenote{font-size:12px;color:var(--muted);font-weight:600;margin-left:4px}")
    toggle_css = "<style>" + "".join(css) + "</style>"

    def note_for(rr):
        return "whole month" if rr is None else ("%s %d &ndash; %s %d" % (mlab, rr[0], mlab, rr[1]))
    opts = "".join('<option value="%s" data-note="%s">%s</option>' % (k, note_for(rr), lab)
                   for k, lab, _, _, rr, _ in views_data)
    bar = ('<div class="rangebar"><span class="rblbl">&#128197; Date range (within %s):</span>'
           '<select id="rangeSel" class="rangesel" aria-label="Date range">%s</select>'
           '<span class="rangenote" id="rangeNote"></span></div>' % (label, opts))

    acct_opts = '<option value="">All accounts</option>' + "".join('<option value="%s">%s</option>' % (B.esc(a), B.esc(a)) for a in accounts)
    reason_opts = '<option value="">All reasons</option>' + "".join('<option value="%s">%s</option>' % (B.esc(a), B.esc(a)) for a in all_reasons)
    toolbar = ('<div class="toolbar"><span class="tbl">&#128269; Filter:</span>'
        '<select id="fAcct">%s</select><select id="fReason">%s</select>'
        '<input id="fSku" type="text" placeholder="Search SKU / title&hellip;">'
        '<label class="chk"><input type="checkbox" id="fHigh"> High rate only (&ge;50%%)</label>'
        '<span class="spacer"></span><span class="shown" id="shown"></span>'
        '<button id="csv" class="btn">&#8681; Export CSV</button></div>' % (acct_opts, reason_opts))

    blocks = []
    for k, lab, ps, pe, rr, v in views_data:
        if rr is None:
            note = "Showing <b>Full month</b> &middot; whole reporting month %s &middot; LM/LY comparison columns apply here." % label
        else:
            note = ("Showing <b>%s</b> &middot; %s %d &ndash; %s %d &middot; Sales/Returns/Ads recomputed for this range; "
                    "<b>LM/LY comparison blank for sub-ranges &middot; Stock is a live snapshot</b>." % (lab, mlab, rr[0], mlab, rr[1]))
        blocks.append(
          '<div class="view view-%s">' % k +
          '<div class="rnote">%s</div>' % note +
          '<div class="kpis">%s</div>' % v["kpis"] +
          '<div class="shead"><h2><span class="d"></span> Per-SKU Returns <span class="count">%d SKUs</span></h2></div>' % v["n"] +
          '<div class="tcard"><div class="snote">&#8596; Scroll for all 19 columns &middot; SKU pinned &middot; headers fixed. '
          'Blank Return Rate = no orders in the window; blank ACOS/ROAS = no ad sales / spend (real, not errors).</div>'
          '<div class="scroll mainscroll"><table class="main">%s<tbody>%s</tbody></table></div></div>' % (B.MAIN_THEAD, v["tbody"]) +
          '<div class="grid2">%s' % v["reason"] +
          '<div class="panel"><h3>&#9881;&#65039; Filter Options</h3><table class="mini filt">%s</table></div></div>' % filters +
          '</div>')

    eff_rows = "".join('<tr><td>%s</td><td class="rt">%s</td><td class="rt">%s</td><td class="rt up"><b>%s</b></td></tr>'
                       % (B.esc(a), B.esc(b), B.esc(c), B.esc(dd)) for a, b, c, dd in eff)
    after = ('<div class="panel wide"><h3>&#9889; Return Workflow &mdash; Before / After</h3>'
             '<table class="mini"><tr><th>Process</th><th class="rt">Before</th><th class="rt">After</th>'
             '<th class="rt">Improvement</th></tr>%s</table></div>' % eff_rows +
             (B.DEFINITIONS % label) +
             '<div class="foot">ERA &middot; REQ-14-D01 &middot; per-SKU eBay Return Analysis &middot; reporting period %s '
             '&middot; in-month date presets &middot; read-only from live Ledsone PostgreSQL &middot; generated %s</div>'
             % (label, updated))
    hero = B.HERO % (label, views_data[0][5]["n"], updated)
    body = '<div class="wrap">' + bar + toolbar + "".join(blocks) + after + '</div>'
    return (B.HEAD + B.CSS + toggle_css + "</head><body>" + radios + hero + body + SCRIPT + "</body></html>")

SCRIPT = r'''<script>
(function(){
 function activeView(){var vs=document.querySelectorAll('.view');for(var i=0;i<vs.length;i++){if(vs[i].offsetParent!==null)return vs[i];}return null;}
 var fA=document.getElementById('fAcct'),fR=document.getElementById('fReason'),
     fS=document.getElementById('fSku'),fH=document.getElementById('fHigh'),shown=document.getElementById('shown');
 function apply(){
   var v=activeView(); if(!v)return; var tb=v.querySelector('table.main tbody');
   var rows=[].slice.call(tb.rows).filter(function(r){return !r.classList.contains('tot');});
   var tot=tb.querySelector('tr.tot');
   var a=fA.value,rz=fR.value,q=(fS.value||'').toLowerCase().trim(),hi=fH.checked,c=0;
   rows.forEach(function(r){
     var ok=(!a||r.dataset.acct===a)&&(!rz||r.dataset.reason===rz)&&
            (!q||r.dataset.sku.indexOf(q)>-1)&&(!hi||parseFloat(r.dataset.rate)>=0.5);
     r.style.display=ok?'':'none'; if(ok)c++;
   });
   if(tot)tot.style.display=(a||rz||q||hi)?'none':'';
   shown.textContent=c+' / '+rows.length+' SKUs';
 }
 [fA,fR,fH].forEach(function(e){e.addEventListener('change',apply);});
 fS.addEventListener('input',apply);
 document.querySelectorAll('input[name=ebrange]').forEach(function(rb){rb.addEventListener('change',apply);});
 var sel=document.getElementById('rangeSel'),note=document.getElementById('rangeNote');
 function syncNote(){if(note&&sel){var o=sel.options[sel.selectedIndex];note.innerHTML=o?('&middot; '+o.getAttribute('data-note')):'';}}
 if(sel){sel.addEventListener('change',function(){var rb=document.getElementById('r-'+sel.value);if(rb)rb.checked=true;syncNote();apply();});syncNote();}
 apply();
 document.getElementById('csv').addEventListener('click',function(){
   var v=activeView(),tb=v.querySelector('table.main');
   var head=['SKU','Product Title','Account'].concat([].slice.call(tb.querySelectorAll('thead tr.cols th')).map(function(th){return th.textContent;}));
   var out=[head.join(',')];
   [].slice.call(tb.tBodies[0].rows).forEach(function(r){ if(r.style.display==='none')return;
     var cells=[].slice.call(r.cells).map(function(td){var t=td.textContent.replace(/—/g,'').replace(/\s+/g,' ').trim();return /[",\n]/.test(t)?'"'+t.replace(/"/g,'""')+'"':t;});
     out.push(cells.join(',')); });
   var blob=new Blob([out.join('\n')],{type:'text/csv;charset=utf-8;'}),u=URL.createObjectURL(blob),a=document.createElement('a');
   a.href=u;a.download='eBay_Return_Analysis_'+(activeView().className.match(/view-(\w+)/)||[,'full'])[1]+'.csv';a.click();URL.revokeObjectURL(u);
 });
})();
</script>'''

# ---------------- top-level generate() ----------------
def generate(month, conn, mockup_path):
    """Pull every preset window live and render the full multi-view HTML. Returns (html, views_data, cache, stats)."""
    ctx = month_ctx(month)
    s1, s2 = parametrize(open(SQLFILE, encoding="utf-8").read())
    _, brk0, filters_list, eff = B.load(mockup_path)
    filters_html = "".join('<tr><td class="fk">%s</td><td class="fv">%s</td></tr>' % (B.esc(k), B.esc(vv)) for k, vv in filters_list)
    filters_html = filters_html.replace(
        "Today, Yesterday, Last 7 Days, Last 30 Days, This Month, Last Month, Last 90 Days, Last Year, Custom",
        "Full month &middot; 1st/2nd half &middot; Week 1&ndash;4 (working presets above &mdash; re-scope the whole dashboard)")

    views_data, accounts, all_reasons, cache = [], set(), [], {}
    for k, lab, ps, pe, rr in ctx["presets"]:
        rows, brk = pull(conn, s1, s2, ps, pe)
        v = render_view(rows, brk, is_full=(rr is None))
        views_data.append((k, lab, ps, pe, rr, v))
        cache[k] = {"window": [ps, pe], "rows": rows, "brk": brk}
        for r in rows:
            if r[2]: accounts.add((r[2] or "").strip())
        if k == "full":
            all_reasons = [b[0] for b in brk]
    updated = datetime.now().strftime("%Y-%m-%d %H:%M")
    html = build(ctx, views_data, filters_html, eff, sorted(accounts), all_reasons, updated)
    full = views_data[0][5]
    stats = {"month": ctx["label"], "n": full["n"], "returns": int(full["returns"]),
             "refund": full["refund"], "spend": full["spend"], "sales": full["sales"],
             "blended": full["blended"], "acos": full["acos"], "roas": full["roas"]}
    return html, views_data, cache, stats

if __name__ == "__main__":
    month = sys.argv[1] if len(sys.argv) > 1 else "2026-06"
    out = sys.argv[2] if len(sys.argv) > 2 else "eBay Return Analysis Dashboard - June 2026 - FINAL.html"
    mockup = os.path.join(HERE, "eBay_Return_Analysis_June2026.xlsx")
    conn = make_conn()
    print("connected:", cred("LED_PGDATABASE"), "as", cred("LED_PGUSER"), "| month", month)
    html, views_data, cache, stats = generate(month, conn, mockup)
    conn.close()
    for k, lab, ps, pe, rr, v in views_data:
        print("  %-5s %s..%s : %3d SKUs / %3d returns / £%.2f refund" % (k, ps, pe, v["n"], int(v["returns"]), v["refund"]))
    open(out, "w", encoding="utf-8").write(html)
    json.dump(cache, open("returns_windows_%s.json" % month, "w", encoding="utf-8"), default=str)
    print("wrote", out, "(%d bytes)" % len(html.encode("utf-8")))
    assert stats["n"] == 144 and stats["returns"] == 153 if month == "2026-06" else True
    print("stats:", stats)
