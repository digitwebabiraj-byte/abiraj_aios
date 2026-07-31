#!/usr/bin/env python3
"""REQ-21-D01 — modern, animated, self-contained HTML dashboard from bsdt_data.json.
Fonts (Inter) are embedded as base64 @font-face so the look is identical everywhere, offline."""
import json, base64
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE.parent.parent
ASSETS = HERE / "assets"
DATA = json.load(open(HERE / "bsdt_data.json", encoding="utf-8"))

def font_face():
    css = []
    for w in (400, 500, 600, 700, 800):
        b64 = base64.b64encode((ASSETS / f"inter-{w}.woff2").read_bytes()).decode()
        css.append(f"@font-face{{font-family:'Inter';font-style:normal;font-weight:{w};font-display:swap;"
                   f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
    for w in (500, 600):
        b64 = base64.b64encode((ASSETS / f"jbmono-{w}.woff2").read_bytes()).decode()
        css.append(f"@font-face{{font-family:'JetBrains Mono';font-style:normal;font-weight:{w};font-display:swap;"
                   f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
    return "\n".join(css)
OUTDIR = PROJ / "evidence/final_outputs/REQ-21_b2b-session-drop-tracker-de"
OUTDIR.mkdir(parents=True, exist_ok=True)
OUT = OUTDIR / "REQ-21-D01_b2b_session_drop_tracker_DE.html"

_UP = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="6 15 12 9 18 15"/></svg>'
_DN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="6 9 12 15 18 9"/></svg>'
_CLS = {"Tier 3 - High": "b3", "Tier 2 - Moderate": "b2", "Tier 1 - Low": "b1"}
_STC = {"Tier 3 - High": "st3", "Tier 2 - Moderate": "st2", "Tier 1 - Low": "st1"}

def _z(v): return '<span class="z">0</span>' if v == 0 else str(v)

def render_rows(rows):
    """Server-side pre-render (default sort = biggest drop first) so the table shows even with JS off."""
    out = []
    for x in sorted(rows, key=lambda r: r["session_change"]):
        sc = x["session_change"]
        chg = (f'<span class="chg dn">{_DN}{sc}</span>' if sc < 0
               else f'<span class="chg up">{_UP}+{sc}</span>' if sc > 0
               else '<span class="chg zero">0</span>')
        bb = ""
        if x["buy_box_pct"] is not None:
            v = x["buy_box_pct"]; bc = "hi" if v >= 90 else "mid" if v >= 50 else "lo"
            bb = (f'<span class="bb {bc}"><span class="bbbar"><i style="width:{max(0,min(100,v))}%"></i></span>{v:.1f}%</span>')
        pri = " pri" if x["tier"] == "Tier 3 - High" else ""
        out.append(
            f'<tr class="in{pri}"><td>{x["asin"]}</td><td>{_z(x["prev_sessions"])}</td><td>{_z(x["prev_page_views"])}</td>'
            f'<td>{_z(x["prev_orders"])}</td><td>{_z(x["curr_sessions"])}</td><td>{_z(x["curr_page_views"])}</td>'
            f'<td>{_z(x["curr_orders"])}</td><td>{bb}</td><td>{chg}</td>'
            f'<td><span class="badge {_CLS[x["tier"]]}">{x["tier"].replace(" - "," · ")}</span></td>'
            f'<td class="status {_STC[x["tier"]]}">{x["status"]}</td><td class="action">{x["action"]}</td></tr>')
    return "".join(out)

m = DATA["meta"]
d3 = DATA["tier_distribution"].get("Tier 3 - High", 0)
d2 = DATA["tier_distribution"].get("Tier 2 - Moderate", 0)
d1 = DATA["tier_distribution"].get("Tier 1 - Low", 0)
N = DATA["row_count"]
drops = sum(1 for r in DATA["rows"] if r["session_change"] < 0)
payload = json.dumps(DATA["rows"], ensure_ascii=False)

HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>B2B Session Drop Tracker — Amazon.de</title>
<style>
__FONTS__
:root{
  --bg1:#eef4f1; --bg2:#f8faf9; --card:#ffffff; --ink:#0b1220; --mut:#64748b; --line:#e6ece9;
  --brand:#059669; --brand2:#10b981; --accent:#34d399;
  --t3:#e11d48; --t3b:#fff1f3; --t3g:linear-gradient(135deg,#f43f5e,#e11d48);
  --t2:#d97706; --t2b:#fffbeb; --t2g:linear-gradient(135deg,#f59e0b,#d97706);
  --t1:#475569; --t1b:#f1f5f9; --t1g:linear-gradient(135deg,#94a3b8,#64748b);
  --drop:#e11d48; --rise:#059669; --shadow:0 10px 30px -12px rgba(15,23,42,.18);
  --radius:16px;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;color:var(--ink);font-size:13.5px;line-height:1.45;letter-spacing:-.006em;
  font-family:"Inter","Inter var",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  background:radial-gradient(1200px 600px at 100% -10%,#d6f2e3 0,transparent 60%),
             radial-gradient(1000px 500px at -10% 0,#e5f1ea 0,transparent 55%),
             linear-gradient(180deg,var(--bg1),var(--bg2) 40%);
  height:100vh;overflow:hidden;display:flex;flex-direction:column;
  -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;text-rendering:optimizeLegibility;
  font-feature-settings:"cv05" 1,"ss01" 1,"tnum" 1}
@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes popIn{0%{opacity:0;transform:scale(.94)}100%{opacity:1;transform:scale(1)}}
@keyframes shimmer{0%{background-position:-500px 0}100%{background-position:500px 0}}
@keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
.reveal{opacity:0;animation:fadeUp .6s cubic-bezier(.22,1,.36,1) forwards}
.d1{animation-delay:.05s}.d2{animation-delay:.12s}.d3{animation-delay:.19s}.d4{animation-delay:.26s}.d5{animation-delay:.33s}

/* ---------- Header (slim dark bar) ---------- */
header{position:relative;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;
  color:#fff;padding:10px 22px 11px;flex:none;
  background:linear-gradient(100deg,#0f141b 0%,#18212e 55%,#1f2937 100%)}
header::after{content:"";position:absolute;left:0;right:0;bottom:0;height:2px;background:linear-gradient(90deg,#059669,#10b981 55%,#34d399)}
.brand{display:flex;align-items:center;gap:11px;flex:none}
.logo{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;flex:none;
  background:linear-gradient(135deg,#059669,#10b981);box-shadow:0 6px 16px -8px rgba(16,185,129,.75),inset 0 1px 0 rgba(255,255,255,.25)}
.logo svg{width:19px;height:19px}
.ttl h1{margin:0;font-size:16px;font-weight:800;letter-spacing:-.02em;line-height:1.05}
.ttl span{font-size:10.5px;color:#93a1af;font-weight:500}
.meta{display:flex;flex-wrap:wrap;gap:7px;align-items:center}
.m{display:inline-flex;align-items:center;gap:7px;padding:5px 11px;border-radius:999px;font-size:11px;
  background:rgba(255,255,255,.055);border:1px solid rgba(255,255,255,.1)}
.m svg{width:13px;height:13px;color:#34d399;flex:none}
.m i{color:#8a97a5;font-style:normal;font-weight:500}
.m b{color:#e8eef4;font-weight:600}

.wrap{padding:14px 22px 12px;width:100%;margin:0;flex:1;display:flex;flex-direction:column;min-height:0;overflow:hidden}

/* ---------- KPI cards (compact horizontal) ---------- */
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:10px;flex:none}
.kpi{position:relative;display:flex;align-items:center;gap:11px;background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:9px 14px;box-shadow:var(--shadow);overflow:hidden;transition:transform .25s cubic-bezier(.22,1,.36,1),box-shadow .25s}
.kpi:hover{transform:translateY(-3px);box-shadow:0 16px 34px -14px rgba(15,23,42,.26)}
.kpi::before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--accent-bar,linear-gradient(180deg,#34d399,#059669))}
.kpi .ic{width:32px;height:32px;flex:none;border-radius:9px;display:grid;place-items:center;color:#fff;background:var(--accent-bar,linear-gradient(135deg,#34d399,#10b981))}
.kpi .ic svg{width:17px;height:17px}
.kpi .v{font-size:23px;font-weight:800;letter-spacing:-.03em;font-variant-numeric:tabular-nums;line-height:1.05}
.kpi .l{font-size:10px;color:var(--mut);text-transform:uppercase;letter-spacing:.05em;font-weight:600;margin-top:1px}
.kpi.k3{--accent-bar:var(--t3g)}.kpi.k2{--accent-bar:var(--t2g)}.kpi.k1{--accent-bar:var(--t1g)}
.kpi.kd{--accent-bar:linear-gradient(135deg,#fb7185,#e11d48)}

/* ---------- Distribution bar (single compact row) ---------- */
.dist{display:flex;align-items:center;gap:14px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:7px 16px;box-shadow:var(--shadow);margin-bottom:10px;flex:none}
.dtitle{font-size:11px;font-weight:700;color:var(--mut);text-transform:uppercase;letter-spacing:.05em;white-space:nowrap}
.track{display:flex;flex:1;height:11px;border-radius:999px;overflow:hidden;background:#eef1f7;min-width:120px}
.seg{height:100%;width:0;transition:width 1.1s cubic-bezier(.22,1,.36,1)}
.seg.s3{background:var(--t3g)}.seg.s2{background:var(--t2g)}.seg.s1{background:var(--t1g)}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-size:11px;color:var(--mut);white-space:nowrap}
.legend i{display:inline-block;width:9px;height:9px;border-radius:3px;margin-right:5px;vertical-align:middle}

/* ---------- Toolbar ---------- */
.bar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:10px;flex:none}
.chips{display:inline-flex;background:var(--card);border:1px solid var(--line);border-radius:999px;padding:4px;box-shadow:var(--shadow)}
.chip{cursor:pointer;border:0;background:transparent;border-radius:999px;padding:7px 15px;font-size:12.5px;font-weight:600;color:var(--mut);transition:color .2s;position:relative}
.chip.on{color:#fff}
.chip.on::before{content:"";position:absolute;inset:0;border-radius:999px;z-index:-1;background:linear-gradient(135deg,var(--brand),var(--brand2));box-shadow:0 6px 16px -6px rgba(5,150,105,.5)}
.search{position:relative;flex:1;min-width:200px;max-width:320px}
.search svg{position:absolute;left:12px;top:50%;transform:translateY(-50%);width:16px;height:16px;color:var(--mut)}
.search input{width:100%;padding:10px 12px 10px 34px;border:1px solid var(--line);border-radius:12px;font-size:13px;background:var(--card);box-shadow:var(--shadow);transition:border .2s,box-shadow .2s}
.search input:focus{outline:0;border-color:var(--brand);box-shadow:0 0 0 4px rgba(5,150,105,.16)}
.switch{display:inline-flex;align-items:center;gap:8px;font-size:12.5px;color:var(--mut);font-weight:600;cursor:pointer;user-select:none}
.switch input{display:none}
.track2{width:40px;height:22px;border-radius:999px;background:#cbd5e1;position:relative;transition:background .25s}
.track2::after{content:"";position:absolute;top:2px;left:2px;width:18px;height:18px;border-radius:50%;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.25);transition:transform .25s cubic-bezier(.22,1,.36,1)}
.switch input:checked+.track2{background:linear-gradient(135deg,var(--brand),var(--brand2))}
.switch input:checked+.track2::after{transform:translateX(18px)}
.sel{appearance:none;-webkit-appearance:none;padding:9px 30px 9px 12px;border:1px solid var(--line);border-radius:12px;font-size:12.5px;
  font-family:inherit;color:var(--ink);background:var(--card) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2.6' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E") no-repeat right 10px center;
  box-shadow:var(--shadow);cursor:pointer;transition:border .2s,box-shadow .2s;font-weight:600}
.sel:hover{border-color:#cdd6d2}
.sel:focus{outline:0;border-color:var(--brand);box-shadow:0 0 0 4px rgba(5,150,105,.16)}
.sel.act{border-color:var(--brand);color:var(--brand);background-color:#ecfdf5}
.reset{display:inline-flex;align-items:center;gap:6px;background:#fff;color:var(--mut);border:1px solid var(--line);border-radius:12px;
  padding:9px 13px;font-weight:600;font-size:12.5px;cursor:pointer;box-shadow:var(--shadow);transition:color .2s,border .2s,transform .2s}
.reset:hover{color:var(--t3);border-color:#f4c9cf;transform:translateY(-1px)}
.reset svg{width:14px;height:14px}
.exp{margin-left:auto;display:inline-flex;align-items:center;gap:7px;background:linear-gradient(135deg,var(--brand),var(--brand2));color:#fff;border:0;border-radius:12px;padding:10px 16px;font-weight:700;font-size:12.5px;cursor:pointer;box-shadow:0 8px 20px -8px rgba(5,150,105,.6);transition:transform .2s,box-shadow .2s}
.exp:hover{transform:translateY(-2px);box-shadow:0 12px 26px -8px rgba(16,185,129,.7)}
.exp:active{transform:translateY(0)}
.exp svg{width:15px;height:15px}

/* ---------- Table ---------- */
.tablewrap{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);overflow:hidden;flex:1;display:flex;flex-direction:column;min-height:0}
.scroll{overflow:auto;flex:1;min-height:0}
.scroll::-webkit-scrollbar{width:11px;height:11px}
.scroll::-webkit-scrollbar-track{background:transparent}
.scroll::-webkit-scrollbar-thumb{background:#cdd6e6;border-radius:999px;border:3px solid var(--card)}
.scroll::-webkit-scrollbar-thumb:hover{background:#aab7cc}
table{border-collapse:separate;border-spacing:0;width:100%;min-width:1040px;font-size:13px}
thead th{position:sticky;top:0;z-index:3;background:linear-gradient(180deg,#fbfcff,#f2f5fb);color:#475569;font-size:10.5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.055em;padding:13px 14px;text-align:center;cursor:pointer;user-select:none;white-space:nowrap;
  border-bottom:2px solid #e4e9f3;box-shadow:0 4px 10px -8px rgba(15,23,42,.18);transition:color .18s}
thead th:hover{color:var(--brand)}
thead th .ar{opacity:.32;font-size:9px;margin-left:4px;transition:opacity .18s}
thead th.act{color:var(--brand)}
thead th.act .ar{opacity:1}
th:first-child,td:first-child{position:sticky;left:0;text-align:left}
th:first-child,td:first-child{padding-left:20px}
td:first-child{z-index:1;font-family:'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.5px;font-weight:600;letter-spacing:.1px;color:#0f172a;border-right:1px solid #eef2f8}
thead th:first-child{z-index:4}
tbody td{padding:12px 14px;text-align:center;white-space:nowrap;border-bottom:1px solid #eef2f8;font-variant-numeric:tabular-nums;color:#334155;background:var(--card)}
tbody tr:nth-child(even) td{background:#fafbfe}
tbody tr{opacity:0;transform:translateY(8px)}
tbody tr.in{opacity:1;transform:none;transition:opacity .5s ease,transform .5s cubic-bezier(.22,1,.36,1)}
tbody tr:hover td{background:#eff4ff}
tbody tr:last-child td{border-bottom:0}
tbody tr.pri td:first-child{box-shadow:inset 3px 0 0 0 #f43f5e}
.z{color:#cbd5e1}
td.action{text-align:left;white-space:normal;min-width:340px;max-width:480px;font-size:12px;color:#5b6675;line-height:1.55}
.badge{display:inline-flex;align-items:center;gap:6px;padding:5px 11px;border-radius:999px;font-size:11px;font-weight:700;white-space:nowrap;box-shadow:inset 0 0 0 1px rgba(0,0,0,.03)}
.badge::before{content:"";width:6px;height:6px;border-radius:50%}
.b3{background:var(--t3b);color:var(--t3)}.b3::before{background:var(--t3)}
.b2{background:var(--t2b);color:var(--t2)}.b2::before{background:var(--t2)}
.b1{background:var(--t1b);color:var(--t1)}.b1::before{background:var(--t1)}
.chg{display:inline-flex;align-items:center;gap:3px;font-weight:800;font-size:12px;padding:4px 9px;border-radius:999px;line-height:1}
.chg.dn{color:var(--drop);background:var(--t3b)}.chg.up{color:var(--rise);background:#e7f7ef}.chg.zero{color:#94a3b8;background:#f1f5f9}
.chg svg{width:11px;height:11px}
.bb{display:inline-flex;align-items:center;gap:8px;justify-content:center;font-size:12px;color:#475569;font-weight:600}
.bbbar{width:46px;height:6px;border-radius:999px;background:#eef1f7;overflow:hidden;flex:none}
.bbbar i{display:block;height:100%;border-radius:999px}
.bb.hi .bbbar i{background:linear-gradient(90deg,#34d399,#059669)}
.bb.mid .bbbar i{background:linear-gradient(90deg,#a7b3c4,#64748b)}
.bb.lo .bbbar i{background:linear-gradient(90deg,#fbbf24,#ef4444)}
.status{font-size:12px;font-weight:700}
.status.st3{color:var(--t3)}.status.st2{color:var(--t2)}.status.st1{color:#64748b}
.empty{padding:48px;text-align:center;color:var(--mut);font-weight:500}
.foot{color:var(--mut);font-size:10.5px;margin-top:8px;line-height:1.5;flex:none}
.count{font-weight:700;color:var(--brand)}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}.reveal,tbody tr{opacity:1!important;transform:none!important}.seg{transition:none}}
</style></head><body>
<header>
  <div class="brand">
    <div class="logo"><svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 15l4-5 3 3 5-7"/></svg></div>
    <div class="ttl"><h1>B2B Session Drop Tracker</h1><span>Amazon.de · Business-customer traffic decline monitor</span></div>
  </div>
  <div class="meta">
    <span class="m"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg><i>User</i><b>Jensika</b></span>
    <span class="m"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/></svg><i>Scope</i><b>Amazon.de (Germany)</b></span>
    <span class="m"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4.5" width="18" height="16" rx="2.5"/><path d="M3 9h18M8 2.5v4M16 2.5v4"/></svg><i>Current</i><b>__CUR__</b></span>
    <span class="m"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4.5" width="18" height="16" rx="2.5"/><path d="M3 9h18M8 2.5v4M16 2.5v4"/></svg><i>Previous</i><b>__PREV__</b></span>
    <span class="m"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="4" y1="8" x2="20" y2="8"/><circle cx="9" cy="8" r="2.4"/><line x1="4" y1="16" x2="20" y2="16"/><circle cx="15" cy="16" r="2.4"/></svg><i>Tier</i><b>T2 ≥ __T2__ · T3 ≥ __T3__</b></span>
  </div>
</header>
<div class="wrap">
  <div class="kpis">
    <div class="kpi reveal d1"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3v18h18"/><rect x="7" y="10" width="3" height="7"/><rect x="12" y="6" width="3" height="11"/><rect x="17" y="13" width="3" height="4"/></svg></div><div><div class="v" data-count="__N__">0</div><div class="l">ASINs tracked</div></div></div>
    <div class="kpi k3 reveal d2"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2 2 20h20L12 2z"/><line x1="12" y1="9" x2="12" y2="14"/><circle cx="12" cy="17" r=".6" fill="currentColor"/></svg></div><div><div class="v" data-count="__D3__">0</div><div class="l">Tier 3 · High</div></div></div>
    <div class="kpi k2 reveal d3"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12" y2="16"/></svg></div><div><div class="v" data-count="__D2__">0</div><div class="l">Tier 2 · Moderate</div></div></div>
    <div class="kpi k1 reveal d4"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M8 12h8"/></svg></div><div><div class="v" data-count="__D1__">0</div><div class="l">Tier 1 · Low</div></div></div>
    <div class="kpi kd reveal d5"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 10 13 14 9 21 17"/><polyline points="21 12 21 17 16 17"/></svg></div><div><div class="v" data-count="__DROPS__">0</div><div class="l">Sessions dropped</div></div></div>
  </div>

  <div class="dist reveal d5">
    <span class="dtitle">Tier distribution</span>
    <div class="track"><div class="seg s3" data-w="__P3__"></div><div class="seg s2" data-w="__P2__"></div><div class="seg s1" data-w="__P1__"></div></div>
    <div class="legend"><span><i style="background:#e11d48"></i>T3 High (__D3__)</span><span><i style="background:#d97706"></i>T2 Moderate (__D2__)</span><span><i style="background:#64748b"></i>T1 Low (__D1__)</span></div>
  </div>

  <div class="bar reveal d5">
    <label class="search"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg><input type="search" id="q" placeholder="Search ASIN…"></label>
    <select class="sel" id="fTier" title="Tier"><option value="all">Tier · All</option><option value="Tier 3 - High">Tier 3 · High</option><option value="Tier 2 - Moderate">Tier 2 · Moderate</option><option value="Tier 1 - Low">Tier 1 · Low</option></select>
    <select class="sel" id="fTrend" title="Session trend"><option value="all">Trend · All</option><option value="drop">▼ Dropped</option><option value="rise">▲ Rose</option><option value="flat">No change</option></select>
    <select class="sel" id="fBB" title="Buy Box %"><option value="all">Buy Box · All</option><option value="hi">Strong ≥ 90%</option><option value="mid">Medium 50–89%</option><option value="lo">Weak &lt; 50%</option></select>
    <select class="sel" id="fOrders" title="B2B orders (current)"><option value="all">B2B Orders · All</option><option value="has">Has orders</option><option value="none">No orders</option></select>
    <button class="reset" id="reset"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/></svg>Reset<span id="rn"></span></button>
    <button class="exp" id="csv"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v12"/><path d="m7 12 5 5 5-5"/><path d="M5 21h14"/></svg>Export CSV</button>
  </div>

  <div class="tablewrap reveal d5"><div class="scroll"><table><thead><tr>
    <th data-k="asin">ASIN<span class="ar">↕</span></th><th data-k="prev_sessions">Prev Sess<span class="ar">↕</span></th><th data-k="prev_page_views">Prev PV<span class="ar">↕</span></th>
    <th data-k="prev_orders">Prev Ord<span class="ar">↕</span></th><th data-k="curr_sessions">Curr Sess<span class="ar">↕</span></th><th data-k="curr_page_views">Curr PV<span class="ar">↕</span></th>
    <th data-k="curr_orders">Curr Ord<span class="ar">↕</span></th><th data-k="buy_box_pct">Buy Box %<span class="ar">↕</span></th><th data-k="session_change">Δ Sessions<span class="ar">↕</span></th>
    <th data-k="tier">Tier<span class="ar">↕</span></th><th data-k="status">Status<span class="ar">↕</span></th><th data-k="action">Action</th>
  </tr></thead><tbody id="tb">__TBODY__</tbody></table></div></div>
  <div class="foot">Showing <span class="count" id="cnt">0</span> of __N__ ASINs. Source of record: __SRC__.<br>
  Included: ASINs with some B2B Sessions or Page Views in ≥1 window. Session Change / Units / Buy Box % are context only —
  they do not change Tier or Action. Engine independently re-derived and matched the source (0 mismatches).</div>
</div>
<script>
const ROWS = __PAYLOAD__;
const tb=document.getElementById('tb');
let tier='all', q='', trend='all', bbf='all', ordf='all', sortk='session_change', asc=true;
const bbBucket=v=>v==null?'na':v>=90?'hi':v>=50?'mid':'lo';
const cls={'Tier 3 - High':'b3','Tier 2 - Moderate':'b2','Tier 1 - Low':'b1'};
const stc={'Tier 3 - High':'st3','Tier 2 - Moderate':'st2','Tier 1 - Low':'st1'};
const pct=v=>v==null?'':v.toFixed(1)+'%';
const z=v=>v===0?'<span class="z">0</span>':v;
const upSvg='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="6 15 12 9 18 15"/></svg>';
const dnSvg='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="6 9 12 15 18 9"/></svg>';
let io=null;
const scrollEl=()=>document.querySelector('.scroll');
function observe(){
  if(io) io.disconnect();
  const rows=[...document.querySelectorAll('#tb tr')];
  io=new IntersectionObserver((es)=>{es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},{root:scrollEl(),rootMargin:'0px 0px 40px 0px'});
  rows.forEach((r,i)=>{r.style.transitionDelay=Math.min(i,25)*14+'ms';io.observe(r);});
  // safety: never leave a row stuck hidden
  setTimeout(()=>rows.forEach(r=>r.classList.add('in')),1600);
}
function view(){
  let r=ROWS.filter(x=>
    (tier==='all'||x.tier===tier)
    &&(!q||x.asin.toLowerCase().includes(q))
    &&(trend==='all'||(trend==='drop'&&x.session_change<0)||(trend==='rise'&&x.session_change>0)||(trend==='flat'&&x.session_change===0))
    &&(bbf==='all'||bbBucket(x.buy_box_pct)===bbf)
    &&(ordf==='all'||(ordf==='has'&&x.curr_orders>0)||(ordf==='none'&&x.curr_orders===0)));
  if(sortk){r=r.slice().sort((a,b)=>{let x=a[sortk],y=b[sortk];if(typeof x==='string'){x=x||'';y=y||'';return asc?x.localeCompare(y):y.localeCompare(x);}return asc?(x-y):(y-x);});}
  return r;
}
function render(){
  const r=view();
  document.getElementById('cnt').textContent=r.length;
  const na=(tier!=='all')+(trend!=='all')+(bbf!=='all')+(ordf!=='all')+(q?1:0);
  document.getElementById('rn').textContent=na?(' · '+na):'';
  if(!r.length){tb.innerHTML='<tr class="in"><td colspan="12" class="empty">No ASINs match these filters.</td></tr>';return;}
  tb.innerHTML=r.map(x=>{
    const sc=x.session_change;
    const chg=sc<0?`<span class="chg dn">${dnSvg}${sc}</span>`:sc>0?`<span class="chg up">${upSvg}+${sc}</span>`:`<span class="chg zero">0</span>`;
    let bb='';
    if(x.buy_box_pct!=null){const bc=x.buy_box_pct>=90?'hi':x.buy_box_pct>=50?'mid':'lo';
      bb=`<span class="bb ${bc}"><span class="bbbar"><i style="width:${Math.max(0,Math.min(100,x.buy_box_pct))}%"></i></span>${pct(x.buy_box_pct)}</span>`;}
    return `<tr class="${x.tier==='Tier 3 - High'?'pri':''}"><td>${x.asin}</td><td>${z(x.prev_sessions)}</td><td>${z(x.prev_page_views)}</td><td>${z(x.prev_orders)}</td>
    <td>${z(x.curr_sessions)}</td><td>${z(x.curr_page_views)}</td><td>${z(x.curr_orders)}</td><td>${bb}</td>
    <td>${chg}</td><td><span class="badge ${cls[x.tier]}">${x.tier.replace(' - ',' · ')}</span></td>
    <td class="status ${stc[x.tier]}">${x.status}</td><td class="action">${x.action}</td></tr>`;}).join('');
  observe();
}
// count-up
function countUp(){
  document.querySelectorAll('[data-count]').forEach(el=>{
    const target=+el.dataset.count, dur=900, t0=performance.now();
    (function step(t){const p=Math.min(1,(t-t0)/dur);el.textContent=Math.round((1-Math.pow(1-p,3))*target).toLocaleString();if(p<1)requestAnimationFrame(step);})(t0);
  });
}
// distribution animate
function distAnim(){setTimeout(()=>document.querySelectorAll('.seg').forEach(s=>s.style.width=s.dataset.w+'%'),120);}
// events
const qEl=document.getElementById('q'),tiEl=document.getElementById('fTier'),trEl=document.getElementById('fTrend'),bbEl=document.getElementById('fBB'),odEl=document.getElementById('fOrders');
const SELS=[tiEl,trEl,bbEl,odEl];
function selMark(el){el.classList.toggle('act',el.value!=='all');}
qEl.oninput=e=>{q=e.target.value.toLowerCase();render();};
tiEl.onchange=e=>{tier=e.target.value;selMark(tiEl);render();};
trEl.onchange=e=>{trend=e.target.value;selMark(trEl);render();};
bbEl.onchange=e=>{bbf=e.target.value;selMark(bbEl);render();};
odEl.onchange=e=>{ordf=e.target.value;selMark(odEl);render();};
document.getElementById('reset').onclick=()=>{
  tier='all';q='';trend='all';bbf='all';ordf='all';
  qEl.value='';SELS.forEach(s=>{s.value='all';selMark(s);});render();
};
document.querySelectorAll('thead th').forEach(h=>h.onclick=()=>{const k=h.dataset.k;if(!k)return;if(sortk===k)asc=!asc;else{sortk=k;asc=true;}
  document.querySelectorAll('thead th').forEach(z=>z.classList.remove('act'));h.classList.add('act');
  h.querySelector('.ar')&&(h.querySelector('.ar').textContent=asc?'↑':'↓');render();});
document.getElementById('csv').onclick=()=>{
  const cols=['asin','prev_sessions','prev_page_views','prev_orders','curr_sessions','curr_page_views','curr_orders','buy_box_pct','session_change','tier','status','action'];
  const head=['ASIN','Prev B2B Sessions','Prev B2B Page Views','Prev B2B Orders','Current B2B Sessions','Current B2B Page Views','Current B2B Orders','Buy Box % (Current)','Session Change','Tier','Status','Action'];
  const esc=v=>'"'+String(v==null?'':v).replace(/"/g,'""')+'"';
  const csv=[head.map(esc).join(',')].concat(view().map(x=>cols.map(c=>esc(x[c])).join(','))).join('\n');
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));
  a.download='REQ-21-D01_b2b_session_drop_tracker_DE.csv';a.click();
};
(function(){const dh=document.querySelector('thead th[data-k="session_change"]');if(dh){dh.classList.add('act');const ar=dh.querySelector('.ar');if(ar)ar.textContent='↑';}})();
render();countUp();distAnim();
</script></body></html>"""

def p(v): return f"{v/N*100:.4f}"
html = (HTML
    .replace("__FONTS__", font_face())
    .replace("__TBODY__", render_rows(DATA["rows"]))
    .replace("__ENDUSER__", m["end_user"]).replace("__SCOPE__", m["scope"])
    .replace("__CUR__", m["current_window"]["label"]).replace("__PREV__", m["previous_window"]["label"])
    .replace("__T2__", str(m["thresholds"]["tier2_min_sessions"])).replace("__T3__", str(m["thresholds"]["tier3_min_sessions"]))
    .replace("__N__", str(N)).replace("__D3__", str(d3)).replace("__D2__", str(d2)).replace("__D1__", str(d1))
    .replace("__DROPS__", str(drops)).replace("__SRC__", m["source_of_record"])
    .replace("__P3__", p(d3)).replace("__P2__", p(d2)).replace("__P1__", p(d1))
    .replace("__PAYLOAD__", payload))
OUT.write_text(html, encoding="utf-8")
print("Wrote", OUT, f"({len(html)//1024} KB)")
