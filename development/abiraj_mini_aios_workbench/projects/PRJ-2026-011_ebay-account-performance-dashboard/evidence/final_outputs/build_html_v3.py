# -*- coding: utf-8 -*-
"""Generate the per-marketplace eBay dashboard (order_total sales). Rows = account x marketplace.

All data is rendered as STATIC HTML (works with zero JavaScript, so it shows inside the ph_task viewer).
Date-range PRESETS (Full month / 1st half / 2nd half / Week 1-4) are pure-CSS radio toggles -- they work
inside the viewer too. When `daily` per-day data is supplied (by the weekly pipeline) the sub-period views
are computed from it; without it, only the Full-month view is produced.
"""
import json, math, calendar

# name, store, mkt, mktCode, rev[j,m,l], ord[j,m,l], units[j,m,l], conv[j,m,l], ad[sp,sa,od,ck]|None, active, newl, stock
R = [
 ["LEDSONE UK","led_sone","UK","UK",[28975.37,33956.80,38047.84],[1517,1677,1896],[2452,3009,3344],[0.0226,0.0236,0.0211],[3495.23,17866.20,1512,18165],2779,48,2592263],
 ["LEDSONE UK","led_sone","Germany","DE",[7489.41,7350.77,9619.53],[310,358,490],[532,560,741],[0.0202,0.0217,0.0203],[698.81,3178.13,242,3841],1315,24,1302951],
 ["Electricalsone UK","electricalsone","UK","UK",[12285.07,13982.62,16692.88],[570,750,993],[930,1235,1518],[0.0215,0.0240,0.0269],[744.58,5131.38,314,5410],1490,36,1910861],
 ["SUNSONE UK","so_926407","UK","UK",[10252.84,10427.91,7476.43],[510,572,446],[803,889,837],[0.0202,0.0210,None],[884.07,4832.34,434,5612],1138,33,1707855],
 ["Huettenlampen DE","huettenlampen","Germany","DE",[11408.15,10289.56,9667.73],[488,475,448],[729,727,656],[0.0320,0.0300,None],[904.83,6239.27,355,4636],535,19,537264],
 ["LEDSONE DE","ledsonede","Germany","DE",[5715.68,8391.54,6742.58],[259,420,275],[376,585,480],[0.0194,0.0259,None],[652.91,2937.36,209,3811],604,9,824341],
 ["Coventry Lights UK","coventrylights","UK","UK",[7330.82,8149.76,3974.38],[337,426,240],[495,713,362],[0.0233,0.0253,None],None,523,31,1133408],
 ["Vintage Interior UK","vintageinterior","UK","UK",[3052.92,3383.36,4382.34],[180,215,207],[316,412,359],[0.0231,0.0283,None],None,467,14,970293],
 ["SUNSONE UK","so_926407","Germany","DE",[1864.10,1815.18,2112.85],[82,77,120],[107,114,164],[0.0221,0.0225,None],[226.18,1079.83,59,1308],293,0,320423],
 ["DC Transformer UK","dctransformer","UK","UK",[1804.58,1801.32,2841.82],[142,130,209],[249,223,331],[0.0251,0.0261,None],None,459,0,727781],
 ["Electricalsone UK","electricalsone","Germany","DE",[1474.31,3138.43,3204.66],[79,192,166],[114,293,294],[0.0215,0.0330,0.0252],[127.79,527.19,40,775],485,0,493928],
 ["RE6865 UK","re6865","UK","UK",[1129.70,1648.04,2715.95],[55,52,168],[87,91,243],[0.0180,0.0162,None],None,394,0,811460],
 ["Lighting Sone UK","lighting_sone","UK","UK",[689.24,1054.08,667.21],[50,58,35],[63,85,47],[0.0240,0.0202,None],None,243,7,642464],
 ["Homin GmbH DE","homin_gmbh","Germany","DE",[460.53,280.22,257.38],[19,12,13],[26,15,21],[0.0124,0.0082,None],None,147,27,222349],
 ["Electricalsone UK","electricalsone","US","US",[463.59,843.21,402.10],[10,25,4],[17,29,9],[0.0111,0.0148,0.0085],None,378,0,420445],
 ["led_sone","led_sone","France","FR",[255.15,156.12,86.68],[3,2,2],[9,5,4],[0.0056,0.0021,0.0000],[10.62,115.92,3,62],364,0,569768],
 ["electricalsone","electricalsone","Canada","CA",[231.84,138.57,None],[2,2,None],[3,3,None],[None,None,None],[3.95,97.62,1,15],154,0,287756],
 ["Neighbour Market US","neighbourmarket","US","US",[203.29,434.64,121.45],[4,8,2],[9,13,3],[None,None,None],None,338,0,416518],
 ["led_sone","led_sone","US","US",[167.10,1197.31,477.56],[4,12,9],[5,44,11],[0.0044,0.0093,0.0056],[32.47,95.73,3,145],390,0,539024],
 ["led_sone","led_sone","Italy","IT",[128.83,272.97,108.84],[2,1,2],[4,12,3],[None,None,None],None,136,0,349400],
 ["electricalsone","electricalsone","France","FR",[62.14,201.96,None],[1,4,None],[2,8,None],[0.0030,0.0106,0.0000],[7.31,0,0,48],165,0,101772],
 ["huettenlampen","huettenlampen","Italy","IT",[10.52,None,None],[1,None,None],[2,None,None],[None,None,None],None,2,0,178],
]
keys=["name","store","mkt","mkc","rev","ord","units","conv","ad","active","newl","stock"]
ROWS=[dict(zip(keys,r)) for r in R]

MKTS=["UK","Germany","France","Italy","Ireland","US","Canada"]
MLAB={"UK":"UK","Germany":"DE","France":"FR","Italy":"IT","Ireland":"IE","US":"US","Canada":"CA"}
DASH='<span class="na">&mdash;</span>'

# ---------- formatting helpers (mirror the earlier JS exactly) ----------
def _jr(n):  return math.floor(n+0.5)
def gbp(n):  return "&mdash;" if n is None else "&pound;"+format(_jr(n),",")
def gbp2(n): return "&mdash;" if n is None else "&pound;"+("%.2f"%n)
def num(n):  return "&mdash;" if n is None else format(_jr(n),",")
def pct(n):  return "&mdash;" if n is None else ("%.2f%%"%(n*100))
def aov(r,o):return (r/o) if o else None
def cCls(c): return "" if c is None else ("g" if c>0.045 else ("y" if c>=0.03 else "rr"))
def aCls(a): return "g" if a<0.12 else ("y" if a<=0.18 else "rr")
def rCls(r): return "g" if r>8 else ("y" if r>=5 else "rr")
def gCls(g): return "g" if g>0.10 else ("y" if g>=0 else "rr")
def rankBadge(n):
    if not n: return DASH
    c="rk1" if n==1 else "rk2" if n==2 else "rk3" if n==3 else "rkn"
    return '<span class="rk %s">%d</span>'%(c,n)
def arrow(c,p):
    if p in (None,0) or c is None: return ""
    g=(c-p)/p
    cl="up" if g>0.001 else "down" if g<-0.001 else "flat"
    a="&#9650;" if g>0.001 else "&#9660;" if g<-0.001 else "&ndash;"
    return '<span class="delta %s">%s %.0f%%</span>'%(cl,a,abs(g)*100)

def _dicts(rows): return [dict(zip(keys,r)) for r in rows]

# ---------- one view (KPIs + main tbody + marketplace tbody + row count) ----------
def render_view(rows):
    D=_dicts(rows); n=len(D)
    order=sorted(range(n), key=lambda i:-(D[i]['rev'][0] or 0))
    salesRank={i:k+1 for k,i in enumerate(order)}
    ppc=[i for i in range(n) if D[i]['ad']]; ppc.sort(key=lambda i:-(D[i]['ad'][0] or 0))
    ppcRank={i:k+1 for k,i in enumerate(ppc)}
    T=dict(rev=0,ordv=0,units=0,sp=0,sa=0,active=0,newl=0,stock=0,ad=False)
    for d in D:
        T['rev']+=d['rev'][0] or 0; T['ordv']+=d['ord'][0] or 0; T['units']+=d['units'][0] or 0
        if d['ad']: T['sp']+=d['ad'][0]; T['sa']+=d['ad'][1]; T['ad']=True
        T['active']+=d['active'] or 0; T['newl']+=d['newl'] or 0; T['stock']+=d['stock'] or 0
    nacc=len({d['store'] for d in D})
    tAov=T['rev']/T['ordv'] if T['ordv'] else 0
    tTac=T['sp']/T['rev'] if T['rev'] else 0
    tRet=T['rev']/T['sp'] if T['sp'] else 0
    def fmt(k,v): return gbp(v) if k=='gbp' else num(v) if k=='num' else gbp2(v) if k=='gbp2' else pct(v) if k=='pct' else ("%.2f"%v) if k=='dec' else str(_jr(v))
    KP=[["&#128183;","Total Revenue",T['rev'],"gbp","","order_total, completed"],
        ["&#129534;","Total Orders",T['ordv'],"num","",num(T['units'])+" units"],
        ["&#127919;","Overall AOV",tAov,"gbp2","",""],
        ["&#127978;","Rows (acct&times;mkt)",n,"int","","%d accounts &middot; 7 markets"%nacc],
        ["&#128227;","Ad Spend",T['sp'],"gbp","","TACOS "+pct(tTac)],
        ["&#128201;","Overall TACOS",tTac,"pct",("g" if tTac<0.12 else "a"),"spend&divide;total revenue"],
        ["&#128200;","Total Return",tRet,"dec",("g" if tRet>8 else "a"),"revenue&divide;ad spend"],
        ["&#127991;&#65039;","Active Listings",T['active'],"num","","new "+num(T['newl'])]]
    kpis="".join('<div class="kpi %s">%s<div class="ic">%s</div><div class="lbl">%s</div><div class="val">%s</div><div class="sub">%s</div></div>'%(
        (k[4] or ""),('<span class="rib">%s</span>'%("GOOD" if k[4]=="g" else "WATCH") if k[4] else ""),k[0],k[1],fmt(k[3],k[2]),k[5]) for k in KP)
    tb=[]
    for i in order:
        d=D[i]
        AOV=[aov(d['rev'][j],d['ord'][j]) for j in range(3)]
        tacos=d['ad'][0]/d['rev'][0] if d['ad'] and d['rev'][0] else None
        ret=d['rev'][0]/d['ad'][0] if d['ad'] and d['ad'][0] else None
        grow=(d['rev'][0]-d['rev'][1])/d['rev'][1] if (len(d['rev'])>1 and d['rev'][1] not in (None,0)) else None
        revC=('<span class="pill %s">%s</span>%s'%(gCls(grow),gbp(d['rev'][0]),arrow(d['rev'][0],d['rev'][1]))) if grow is not None else '<b>%s</b>'%gbp(d['rev'][0])
        conv=d['conv'] if d['conv'] else [None,None,None]
        tb.append('<tr>'
          '<td class="acc"><span class="flag">%s</span> <span class="aname">%s</span><div class="store">%s%s</div></td>'%(MLAB.get(d['mkt'],d['mkt']),d['name'],d['store'],('' if d['ad'] else ' <span class="noads">No ads</span>'))+
          '<td class="sep p-jun">%s</td><td class="p-lm">%s</td><td class="p-ly">%s</td>'%(revC,gbp(d['rev'][1] if len(d['rev'])>1 else None),gbp(d['rev'][2] if len(d['rev'])>2 else None))+
          '<td class="sep p-jun">%s%s</td><td class="p-lm">%s</td><td class="p-ly">%s</td>'%(num(d['ord'][0]),arrow(d['ord'][0],d['ord'][1] if len(d['ord'])>1 else None),num(d['ord'][1] if len(d['ord'])>1 else None),num(d['ord'][2] if len(d['ord'])>2 else None))+
          '<td class="sep p-jun">%s</td><td class="p-lm">%s</td><td class="p-ly">%s</td>'%(num(d['units'][0]),num(d['units'][1] if len(d['units'])>1 else None),num(d['units'][2] if len(d['units'])>2 else None))+
          '<td class="sep p-jun">%s</td><td class="p-lm">%s</td><td class="p-ly">%s</td>'%(gbp2(AOV[0]),gbp2(AOV[1]),gbp2(AOV[2]))+
          '<td class="sep p-jun">%s</td><td class="p-lm">%s</td><td class="p-ly">%s</td>'%((DASH if conv[0] is None else '<span class="pill %s">%s</span>'%(cCls(conv[0]),pct(conv[0]))),pct(conv[1]),pct(conv[2]))+
          '<td class="sep p-jun">%s</td><td class="p-jun">%s</td>'%(gbp(d['ad'][0] if d['ad'] else None),gbp(d['ad'][1] if d['ad'] else None))+
          '<td class="p-jun">%s</td><td class="p-jun">%s</td><td class="p-jun">%s</td>'%((DASH if tacos is None else '<span class="pill %s">%s</span>'%(aCls(tacos),pct(tacos))),(DASH if ret is None else '<span class="pill %s">%.2f</span>'%(rCls(ret),ret)),rankBadge(ppcRank.get(i)))+
          '<td class="sep p-jun">%s</td><td class="p-jun">%s</td><td class="p-jun">%s</td><td class="p-jun">%s</td></tr>'%(num(d['active']),(num(d['newl']) if d['newl'] else '<span class="na">0</span>'),rankBadge(salesRank.get(i)),num(d['stock'])))
    xa=T['rev']/T['ordv'] if T['ordv'] else 0
    tb.append('<tr class="tot"><td class="acc">TOTAL &mdash; %d rows</td>'%n+
      '<td class="sep">%s</td><td>&mdash;</td><td>&mdash;</td><td class="sep">%s</td><td>&mdash;</td><td>&mdash;</td><td class="sep">%s</td><td>&mdash;</td><td>&mdash;</td>'%(gbp(T['rev']),num(T['ordv']),num(T['units']))+
      '<td class="sep">%s</td><td>&mdash;</td><td>&mdash;</td><td class="sep">&mdash;</td><td>&mdash;</td><td>&mdash;</td>'%gbp2(xa)+
      '<td class="sep">%s</td><td>%s</td><td>%s</td><td>%s</td><td>&mdash;</td>'%((gbp(T['sp']) if T['ad'] else DASH),(gbp(T['sa']) if T['ad'] else DASH),(pct(tTac) if T['sp'] else DASH),("%.2f"%tRet if T['sp'] else DASH))+
      '<td class="sep">%s</td><td>%s</td><td>&mdash;</td><td>%s</td></tr>'%(num(T['active']),num(T['newl']),num(T['stock'])))
    # marketplace summary
    MS={m:dict(rev=0,ordv=0,units=0,sp=0,sa=0,n=0) for m in MKTS}
    for d in D:
        m=MS.get(d['mkt'])
        if not m: continue
        m['rev']+=d['rev'][0] or 0; m['ordv']+=d['ord'][0] or 0; m['units']+=d['units'][0] or 0
        if d['ad']: m['sp']+=d['ad'][0]; m['sa']+=d['ad'][1]
        m['n']+=1
    ms=[]
    for m in MKTS:
        s=MS[m]; ac=s['sp']/s['rev'] if s['sp'] and s['rev'] else None; ro=s['rev']/s['sp'] if s['sp'] else None
        dim=' style="opacity:.5"' if s['rev']==0 else ''
        ms.append('<tr%s><td class="mk"><span class="flag">%s</span> %s</td><td style="text-align:right">%s</td><td style="text-align:right">%s</td><td style="text-align:right">%s</td><td style="text-align:right">%s</td><td style="text-align:right">%s</td><td style="text-align:right">%s</td><td style="text-align:right">%d</td></tr>'%(
            dim,MLAB[m],m,gbp(s['rev']),num(s['ordv']),num(s['units']),(gbp(s['sp']) if s['sp'] else "&mdash;"),
            ('<span class="pill %s">%s</span>'%(aCls(ac),pct(ac)) if ac is not None else "&mdash;"),
            ('<span class="pill %s">%.2f</span>'%(rCls(ro),ro) if ro is not None else "&mdash;"),s['n']))
    return {"kpis":kpis,"tb":"".join(tb),"ms":"".join(ms),"rc":"%d rows"%n}

# static reference blocks (range-independent)
THR='<tr><th>KPI</th><th>&#128994; Green</th><th>&#128993; Yellow</th><th>&#128308; Red</th></tr>'+"".join(
    '<tr><td>%s</td><td><span class="pill g">%s</span></td><td><span class="pill y">%s</span></td><td><span class="pill rr">%s</span></td></tr>'%(t[0],t[1],t[2],t[3])
    for t in [["Revenue Growth (MoM)","&gt;10%","0-10%","&lt;0%"],["Conversion Rate","&gt;4.5%","3-4.5%","&lt;3%"],["TACOS (ad&divide;total sales)","&lt;12%","12-18%","&gt;18%"],["Total Return","&gt;8","5-8","&lt;5"],["Stock","&gt;30 Days","15-30 Days","&lt;15 Days"],["Active Listings","Increasing","Stable","Decreasing"]])
AUTO='<tr><th>Process</th><th>Before</th><th>After</th><th>Saved</th></tr>'+"".join(
    '<tr><td>%s</td><td class="rt">%dm</td><td class="rt">%dm</td><td class="rt up"><b>%dm</b></td></tr>'%(a[0],a[1],a[2],a[1]-a[2])
    for a in [["Account Health Check",15,2],["Sales Report",25,3],["PPC Performance Review",30,5],["Listing Performance Analysis",90,8],["Stock Monitoring",50,4],["Return Analysis",40,3],["SKU Performance Report",70,5]])

# ---------- aggregate a row-set into a sub-period from embedded daily data ----------
def aggregate_range(rows, daily, a, b):
    """rows = full-shape lists; daily[(store,mkt)] = dict of per-day arrays (idx0=day1). Days a..b inclusive."""
    out=[]
    for r in rows:
        store,mkt=r[1],r[2]
        dd=daily.get((store,mkt))
        if not dd:
            sr=list(r); sr[4]=[0,None,None]; sr[5]=[0,None,None]; sr[6]=[0,None,None]; sr[7]=[None,None,None]; sr[8]=None
            out.append(sr); continue
        sl=lambda k: dd.get(k,[])[a-1:b]
        rev=sum(sl("rev")); od=sum(sl("ord")); un=sum(sl("units"))
        sp=sum(sl("sp")); sa=sum(sl("sa")); aod=sum(sl("aod")); ack=sum(sl("ack"))
        cv=sum(sl("conv")); ck=sum(sl("click")); nl=sum(sl("newl"))
        ad=[round(sp,2),round(sa,2),int(aod),int(ack)] if sp>0 else None
        conv=[(cv/ck if ck>0 else None),None,None]
        sr=[r[0],store,mkt,r[3],[round(rev,2),None,None],[int(od),None,None],[int(un),None,None],conv,ad,r[9],int(nl),r[11]]
        out.append(sr)
    return out

# ---------- assemble the full standalone HTML ----------
def build(rows, month_label="June 2026", daily=None, ndays=None):
    full=render_view(rows)
    views=[("full","Full month",full,None)]
    if daily and ndays:
        presets=[("h1","1st half",1,15),("h2","2nd half",16,ndays),
                 ("w1","Week 1",1,7),("w2","Week 2",8,14),("w3","Week 3",15,21),("w4","Week 4",22,ndays)]
        for key,label,a,b in presets:
            v=render_view(aggregate_range(rows,daily,a,b))
            views.append((key,label,v,(a,b)))
    mlab=month_label.split()[0][:3]  # e.g. "Jun"
    # radios (before .wrap so the CSS sibling selector can reach the views)
    radios="".join('<input type="radio" name="ebrange" id="r-%s" class="rsel"%s>'%(k," checked" if i==0 else "") for i,(k,_,_,_) in enumerate(views))
    # toggle CSS
    css_rules=[".view{display:none}"]
    for k,_,_,_ in views:
        css_rules.append("#r-%s:checked ~ .wrap .view-%s{display:block}"%(k,k))
        css_rules.append("#r-%s:checked ~ .wrap label[for=r-%s]{background:var(--teal);color:#fff;border-color:var(--teal)}"%(k,k))
    toggle_css="<style>"+ "".join(css_rules) +"</style>"
    # range button bar
    def rng_note(rr):
        if rr is None: return "all %d days"%(ndays or 0) if ndays else "whole month"
        return "%s %d &ndash; %s %d"%(mlab,rr[0],mlab,rr[1])
    bar='<div class="rangebar"><span class="rblbl">&#128197; Date range:</span>'+"".join(
        '<label for="r-%s" class="rbtn">%s</label>'%(k,label) for k,label,_,_ in views)+'</div>'
    # view blocks
    blocks=[]
    for k,label,v,rr in views:
        note = ('Showing <b>%s</b>'%label)+(' &middot; '+rng_note(rr) if rr else ' &middot; whole reporting month')
        note += ' &middot; Sales/Ads/Conversion/New are for this range; <b>Active Listings &amp; Stock are current snapshots</b> (no per-day history).'
        lmly = '' if k=='full' else '<div class="snote">LM/LY comparison columns apply to the full month only &mdash; blank for sub-ranges.</div>'
        blocks.append(
          '<div class="view view-%s">'%k+
          '<div class="rnote">%s</div>'%note+
          '<div class="kpis">%s</div>'%v['kpis']+
          '<div class="shead"><h2><span class="d"></span> Account &times; Marketplace Performance <span class="count">%s</span></h2></div>'%v['rc']+
          '<div class="tcard"><div class="snote">&#8596; Scroll for all columns &middot; Account + Market pinned &middot; headers fixed. Sales = order_total (product + postage actually paid), completed orders.</div>%s'%lmly+
          '<div class="scroll mainscroll"><table class="main">'+MAIN_THEAD+'<tbody>%s</tbody></table></div></div>'%v['tb']+
          '<div class="shead"><h2><span class="d"></span> By Marketplace &mdash; all accounts combined <span class="count">7 markets</span></h2></div>'+
          '<div class="tcard"><div class="scroll"><table class="mkt">'+MKT_THEAD+'<tbody>%s</tbody></table></div></div>'%v['ms']+
          '</div>')
    body=('<div class="wrap">'+bar+"".join(blocks)+
          '<div class="grid2"><div class="panel"><h3>&#127919; KPI Thresholds</h3><table class="mini">%s</table></div>'%THR+
          '<div class="panel"><h3>&#9889; Automation Impact</h3><table class="mini">%s</table></div></div>'%AUTO+
          DEFINITIONS+
          '<div class="foot">EBPD &middot; REQ-13-D01 &middot; per-marketplace view &middot; sales = order_total &middot; read-only reporting from live warehouse.</div>'+
          '</div>')
    html=HEAD+CSS+toggle_css+"</head><body>"+radios+body+"</body></html>"
    html=html.replace("June 2026", month_label)
    return html

HEAD='<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>eBay Account Performance &mdash; June 2026</title>'

CSS=r'''<style>
:root{--bg:#eef1f5;--bg2:#e7ebf1;--card:#fff;--ink:#111a2b;--ink2:#28344a;--muted:#5b6a86;--faint:#8592a8;
--line:#e3e8ef;--line2:#eef1f6;--slate:#1e293b;--slate2:#334155;--teal:#0d9488;--teal2:#14b8a6;--tealbg:#d6f2ee;--teald:#0b7d72;
--green:#15803d;--greenbg:#dcf5e4;--amber:#b45309;--amberbg:#fceccb;--red:#dc2626;--redbg:#fce1e1;--gold:#d99e00;
--sh-sm:0 1px 2px rgba(17,26,43,.07);--sh:0 10px 28px -14px rgba(30,41,59,.32);--r:16px;}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;min-height:100vh;color:var(--ink);background:linear-gradient(180deg,var(--bg),var(--bg2));
font-family:"Segoe UI",-apple-system,BlinkMacSystemFont,Roboto,Arial,sans-serif;font-size:14.5px;line-height:1.5;-webkit-font-smoothing:antialiased}
.rsel{position:absolute;opacity:0;pointer-events:none;width:0;height:0}
.wrap{width:100%;max-width:100%;padding:16px clamp(12px,2.2vw,34px) 60px}
.rangebar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:4px 0 14px;padding:11px 13px;background:var(--card);border:1px solid var(--line);border-radius:13px;box-shadow:var(--sh-sm)}
.rangebar .rblbl{font-size:12.5px;font-weight:800;color:var(--slate2);margin-right:4px}
.rbtn{cursor:pointer;font-size:12.5px;font-weight:700;color:var(--slate2);background:#f3f6fa;border:1px solid var(--line);border-radius:8px;padding:6px 13px;user-select:none;transition:.12s}
.rbtn:hover{border-color:var(--teal2);color:var(--teald)}
.rnote{font-size:12px;color:var(--muted);background:var(--tealbg);border:1px solid #bfe8e2;border-radius:9px;padding:8px 13px;margin:0 0 12px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:11px;margin:4px 0}
.kpi{position:relative;background:var(--card);border:1px solid var(--line);border-radius:13px;padding:12px 13px;box-shadow:var(--sh-sm);overflow:hidden}
.kpi .ic{width:30px;height:30px;border-radius:9px;display:grid;place-items:center;font-size:15px;background:var(--tealbg);margin-bottom:8px}
.kpi.g .ic{background:var(--greenbg)}.kpi.a .ic{background:var(--amberbg)}.kpi.r .ic{background:var(--redbg)}
.kpi .lbl{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;font-weight:700}
.kpi .val{font-size:20px;font-weight:800;margin-top:3px;color:var(--ink)}
.kpi .sub{font-size:10.5px;color:var(--faint);margin-top:2px}
.kpi .rib{position:absolute;top:0;right:0;padding:2px 9px;border-bottom-left-radius:10px;font-size:9px;font-weight:800}
.kpi.g .rib{background:var(--greenbg);color:var(--green)}.kpi.a .rib{background:var(--amberbg);color:var(--amber)}
.shead{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin:18px 0 8px}
.shead h2{font-size:15.5px;margin:0;display:flex;align-items:center;gap:9px;font-weight:700}
.shead h2 .d{width:9px;height:9px;border-radius:2px;background:var(--teal);transform:rotate(45deg)}
.count{font-size:12px;font-weight:700;color:var(--teal);background:var(--tealbg);padding:3px 10px;border-radius:20px}
.tcard{background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh);overflow:hidden}
.snote{font-size:11.5px;color:var(--faint);padding:9px 16px 0}
.scroll{overflow-x:auto}
.mainscroll{overflow:auto;max-height:calc(100vh - 24px)}
table{border-collapse:separate;border-spacing:0;width:100%;font-variant-numeric:tabular-nums}
table.main{min-width:1720px;font-size:13px}
thead th{background:var(--slate2);color:#fff;font-weight:600;padding:10px 11px;white-space:nowrap;position:sticky;top:0;z-index:2;font-size:11.5px;vertical-align:middle}
thead tr.grp th{background:var(--slate);font-size:11px;text-transform:uppercase;letter-spacing:.9px;text-align:center;border-left:2px solid rgba(255,255,255,.14);padding:8px 10px}
thead tr.grp th.tealh{background:var(--teal)}
thead tr.cols th{top:35px;text-align:right;border-left:1px solid rgba(255,255,255,.08)}
th.acc,td.acc{position:sticky;left:0;text-align:left;min-width:210px}
thead th.acc{z-index:5;background:var(--slate2)}
tbody td.acc{background:var(--card);z-index:1}
tbody td{padding:10px 11px;text-align:right;white-space:nowrap;border-bottom:1px solid var(--line2);color:var(--ink2)}
tbody tr:hover td{background:#f2fbf9}tbody tr:hover td.acc{background:#e9f7f4}
.sep{border-left:2px solid #dbe2ec}
.p-jun{background:#fbfdfc}.p-lm{background:#f6f9fb;color:#495569}.p-ly{background:#f8fafc;color:#66728a}
tbody tr:hover .p-jun,tbody tr:hover .p-lm,tbody tr:hover .p-ly{background:#f2fbf9}
.aname{font-weight:700;font-size:13px;color:var(--ink)}.store{font-size:10px;color:var(--faint);font-weight:600}
.flag{display:inline-block;min-width:30px;text-align:center;font-weight:800;color:#fff;background:var(--teal);border-radius:6px;padding:2px 7px;font-size:11px}
.pill{display:inline-block;padding:3px 9px;border-radius:7px;font-weight:800;font-size:12px}
.g{background:var(--greenbg);color:var(--green)}.y{background:var(--amberbg);color:var(--amber)}.rr{background:var(--redbg);color:var(--red)}
.delta{font-size:10px;font-weight:700;display:block;margin-top:2px}.up{color:var(--green)}.down{color:var(--red)}.flat{color:var(--faint)}
.na{color:var(--faint);font-style:italic;font-weight:600}
.rk{display:inline-grid;place-items:center;width:24px;height:24px;border-radius:50%;font-weight:800;font-size:11px;color:#fff}
.rk1{background:linear-gradient(145deg,#f3ca3e,#d99e00)}.rk2{background:linear-gradient(145deg,#c4cfdd,#94a3b8)}.rk3{background:linear-gradient(145deg,#e0a366,#c07b3a)}.rkn{background:#e4e9f0;color:#67728a}
.noads{display:inline-block;font-size:9px;font-weight:800;color:#7c8aa2;background:#eef1f6;border:1px solid #e0e6ef;border-radius:5px;padding:1px 6px;margin-left:6px}
tr.tot td{background:#eef4f3!important;font-weight:800;border-top:2px solid var(--teal);border-bottom:none;font-size:13px;color:var(--ink)}
tr.tot td.acc{background:#eef4f3!important}
table.mkt{min-width:760px;font-size:12.8px}table.mkt td.mk{text-align:left;font-weight:700;color:var(--slate2)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:24px}@media(max-width:900px){.grid2{grid-template-columns:1fr}}
.panel{background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh-sm);overflow:hidden}
.panel h3{margin:0;padding:14px 18px;font-size:13.5px;background:var(--tealbg);color:#0b5f57;border-bottom:1px solid var(--line)}
.mini{width:100%;border-collapse:collapse;font-size:12.6px}.mini td,.mini th{padding:9px 14px;text-align:left;border-bottom:1px solid var(--line2)}
.mini th{color:var(--muted);font-weight:700;font-size:11px;text-transform:uppercase}.mini td.rt{text-align:right}
details.notes{margin-top:22px;background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh-sm);overflow:hidden}
details.notes summary{cursor:pointer;padding:15px 18px;font-weight:700;color:#0b5f57;background:var(--tealbg)}
details.notes .nb{padding:14px 22px;font-size:12.8px}details.notes ul{margin:0;padding-left:18px}details.notes li{margin:6px 0}
.foot{margin-top:26px;text-align:center;font-size:11.5px;color:var(--faint)}
@media print{.rangebar{display:none}.mainscroll{max-height:none;overflow:visible}table.main{min-width:0;font-size:9px}thead th{position:static}}
</style>'''

MAIN_THEAD=r'''<thead><tr class="grp"><th class="acc" rowspan="2">Account &amp; Marketplace</th><th colspan="15">Sales</th><th colspan="5" class="tealh">Advertising</th><th colspan="4">Listings &amp; Stock</th></tr><tr class="cols"><th class="sep">Revenue</th><th>LM</th><th>LY</th><th class="sep">Orders</th><th>LM</th><th>LY</th><th class="sep">Units</th><th>LM</th><th>LY</th><th class="sep">AOV</th><th>LM</th><th>LY</th><th class="sep">Conv.</th><th>LM</th><th>LY</th><th class="sep">Ad Spend</th><th>Ad Sales</th><th>TACOS</th><th>Return</th><th>PPC Rk</th><th class="sep">Active</th><th>New</th><th>Sales Rk</th><th>Stock</th></tr></thead>'''
MKT_THEAD=r'''<thead><tr><th class="acc" style="min-width:150px">Marketplace</th><th style="text-align:right">Revenue</th><th style="text-align:right">Orders</th><th style="text-align:right">Units</th><th style="text-align:right">Ad Spend</th><th style="text-align:right">TACOS</th><th style="text-align:right">Return</th><th style="text-align:right">Rows</th></tr></thead>'''

DEFINITIONS=r'''<details class="notes"><summary>Definitions, data sources &amp; notes</summary><div class="nb"><ul>
<li><b>Date range presets</b> re-scope Sales, Orders, Units, Ad Spend/Sales, Conversion and New Listings to the chosen part of the month. <b>Active Listings &amp; Stock</b> are always current snapshots (no per-day history). LM/LY comparison columns apply to the full month only.</li>
<li><b>Rows = account &times; marketplace.</b> "LEDSONE UK &middot; UK" = led_sone sold to UK buyers; its German/FR/US/IT sales are their own rows. Nothing aggregated, nothing double-counted.</li>
<li><b>Sales = SUM(order_total)</b> &mdash; eBay's actual order value (product + postage actually paid), completed orders only.</li>
<li><b>Ad Spend / Ad Sales</b> = eBay Promoted Listings <b>Priority / ON_SITE</b> campaigns only (record_subtype=ON_SITE; Standard COST_PER_SALE excluded per Thinesh). <b>TACOS</b> = Ad Spend &divide; total revenue &middot; <b>Return</b> = total revenue &divide; Ad Spend &middot; <b>PPC Rank</b> = by spend.</li>
<li><b>Conversion</b> = account conversions &divide; page-views (whole-account traffic, per marketplace) &middot; <b>Active</b> = distinct eBay listings on that site &middot; <b>New</b> = listings created in range (ledsone listings.ebay_listings.created_at) &middot; <b>Sales Rank</b> = rows ranked by revenue.</li>
<li><b>Stock</b> = warehouse units for that site's SKUs &mdash; physical stock is shared across sites, so it overlaps between rows.</li>
</ul></div></details>'''

if __name__=="__main__":
    out_html=build(R, "June 2026")   # no daily -> Full view only (standalone smoke test)
    out=r"C:\Users\digit\Downloads\eBay Account Performance Dashboard - June 2026 - FINAL.html"
    open(out,"w",encoding="utf-8").write(out_html)
    tot_rev=sum(d['rev'][0] for d in ROWS); tot_ord=sum(d['ord'][0] for d in ROWS); tot_new=sum(d['newl'] for d in ROWS)
    print("FULL view rows:",len(ROWS),"| June revenue:",round(tot_rev,2),"| orders:",tot_ord,"| new listings:",tot_new)
