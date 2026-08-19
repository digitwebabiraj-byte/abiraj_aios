#!/usr/bin/env python3
"""
REQ-30-D01 - BGCT Phase 1 SQP keyword dashboard - renderer
PRJ-2026-026 (bgct)

Reads bgct_payload.json (written by build_bgct_d01.py) and emits ONE self-contained, full-screen
HTML file for the Phase 1 output: the proven search terms behind every Top-Moving ASIN.

Same design language, filters and interaction model as the D02 dashboard, so both deliverables
behave identically for the person using them.

Implements the source's Phase 1 Step 8 export contract plus its "What to Look For in SQP Data"
interpretation guide, exposed as filterable pattern flags.

READ-ONLY: no network calls, no external assets, no database access. The payload is the only input.
"""
import os, json, html, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, "..", ".."))
PAYLOAD = os.path.join(HERE, "bgct_payload.json")
OUT = os.path.join(PROJECT, "evidence", "final_outputs", "REQ-30_amazon-keyword-gap-sync",
                   "REQ-30-D01_sqp_top_terms_dashboard.html")

BRANDS = {"dcvoltage_uk": "DCVOLTAGE UK", "ledsone_uk": "LEDSone UK"}


def main():
    p = json.load(open(PAYLOAD, encoding="utf-8"))
    per, rules = p["period"], p["rules"]
    terms, tm = p["phase1"], p["top_moving"]

    nmonths = len(per["months"])
    req = rules["top_moving_months_required"]
    tm_rule = (f"more than {rules['top_moving_units_gt']} units in "
               + ("all " if req >= nmonths else f"at least {req} of ") + f"{nmonths} months")

    # ---- the source's "What to Look For" patterns, as flags -------------------------------------
    # The document names five patterns but states NO numeric cut-offs (open item #10), so the two
    # that need one are split on the MEDIAN of this run and labelled as such on screen. Nothing here
    # invents a business threshold - it is a documented, reproducible split of the actual data.
    vols = [t["search_query_volume"] for t in terms] or [0]
    shares = [t["asin_share"] for t in terms if t["asin_share"] is not None] or [0]
    mv, ms = st.median(vols), st.median(shares)

    rows = []
    for t in terms:
        v, sh = t["search_query_volume"], t["asin_share"]
        rows.append({
            "mo": t["month"], "br": t["brand"], "a": t["top_asin"], "kw": t["search_term"],
            "sc": t["search_query_score"], "v": v,
            "tc": t["total_count"], "ac": t["asin_count"],
            "sh": round(sh * 100, 2) if sh is not None else None,
            "cr": round(t["click_rate"] * 100, 2) if t["click_rate"] is not None else None,
            "cs": round(t["asin_click_share"] * 100, 2) if t["asin_click_share"] is not None else None,
            "pu": t["purchases"], "lt": 1 if t["is_long_tail"] else 0,
            # "High Volume + Low ASIN Share - you appear in results but lose clicks"
            "op": 1 if (v >= mv and sh is not None and sh < ms) else 0,
        })

    tm_rows = [{"br": r["brand"], "a": r["asin"], "u": r["units"], "n": r["terms"]} for r in tm]
    with_terms = sum(1 for r in tm if r["terms"] > 0)
    data = json.dumps({"t": rows, "m": tm_rows}, separators=(",", ":"))
    E = html.escape

    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BGCT Phase 1 — SQP Top Search Terms — REQ-30-D01</title><style>
:root{{
 --bg:#eef1f5; --panel:#fff; --ink:#14202c; --mut:#5c6b7a; --line:#dde3ea; --line2:#eef1f5;
 --nv:#1b3a5c; --nv2:#25507d; --ok:#177245; --warn:#a86a12; --opp:#0b6f8f; --lt:#6b3fa0;
 --chip:#e8eef7;
}}
*{{box-sizing:border-box}} html,body{{height:100%}}
body{{margin:0;background:var(--bg);color:var(--ink);
 font:14px/1.45 -apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}}
header{{background:linear-gradient(180deg,var(--nv2),var(--nv));color:#fff;padding:14px 22px 12px}}
header h1{{margin:0;font-size:18px;letter-spacing:.2px}}
header .meta{{opacity:.9;font-size:12px;margin-top:3px}}
header .meta b{{color:#ffe9b0;font-weight:600}}
.note{{background:#eef6fb;border-top:1px solid #cde2ef;border-bottom:1px solid #cde2ef;
 padding:9px 22px;font-size:12.5px;color:#0d4a63}} .note b{{color:#08384c}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;padding:14px 22px 4px}}
.kpi{{background:var(--panel);border:1px solid var(--line);border-radius:9px;padding:11px 13px;
 border-left:4px solid var(--nv2)}}
.kpi.clk{{cursor:pointer;transition:.12s}} .kpi.clk:hover{{border-color:var(--nv2);box-shadow:0 2px 8px rgba(20,32,44,.09)}}
.kpi.on{{background:#f5f9ff;box-shadow:inset 0 0 0 1px var(--nv2)}}
.kpi.o{{border-left-color:var(--opp)}} .kpi.l{{border-left-color:var(--lt)}}
.kpi .v{{font-size:26px;font-weight:700;line-height:1.05;font-variant-numeric:tabular-nums}}
.kpi .k{{font-size:12px;color:var(--mut);margin-top:3px}}
.bar{{position:sticky;top:0;z-index:20;background:rgba(238,241,245,.96);backdrop-filter:blur(6px);
 border-bottom:1px solid var(--line);padding:10px 22px;display:flex;gap:9px;align-items:center;flex-wrap:wrap}}
.bar input,.bar select{{font:13px inherit;color:var(--ink);background:#fff;border:1px solid #c9d3de;
 border-radius:7px;padding:7px 9px;outline:none}}
.bar input[type=search]{{flex:1 1 250px;min-width:190px}}
.bar input[type=number]{{width:96px}}
.bar input:focus,.bar select:focus{{border-color:var(--nv2);box-shadow:0 0 0 3px rgba(37,80,125,.13)}}
.bar label{{font-size:11px;color:var(--mut);display:flex;flex-direction:column;gap:3px}}
.bar label.chk{{flex-direction:row;align-items:center;gap:6px;font-size:12.5px;color:var(--ink);
 background:#fff;border:1px solid #c9d3de;border-radius:7px;padding:7px 10px;cursor:pointer}}
.bar label.chk:hover{{border-color:var(--nv2)}} .bar label.chk input{{margin:0;cursor:pointer}}
.count{{margin-left:auto;font-size:12.5px;color:var(--mut);white-space:nowrap}}
.count b{{color:var(--ink);font-variant-numeric:tabular-nums}}
.btn{{border:1px solid #c9d3de;background:#fff;border-radius:7px;padding:7px 11px;font-size:12.5px;
 cursor:pointer;color:var(--ink)}} .btn:hover{{border-color:var(--nv2);color:var(--nv2)}}
main{{padding:4px 22px 70px}} section{{margin-top:20px}}
h2{{font-size:14.5px;margin:0 0 3px;padding-left:10px;border-left:4px solid var(--nv2)}}
h2 .n{{color:var(--mut);font-weight:500}}
.sub{{color:var(--mut);font-size:12.5px;margin:0 0 9px;padding-left:14px}}
.wrap{{background:var(--panel);border:1px solid var(--line);border-radius:9px;overflow:auto}}
table{{width:100%;border-collapse:separate;border-spacing:0;font-size:13px}}
th{{position:sticky;top:0;z-index:5;background:#f2f5f9;text-align:left;padding:8px 10px;font-size:11.5px;
 font-weight:600;color:#3c4c5d;border-bottom:1px solid var(--line);white-space:nowrap;cursor:pointer;user-select:none}}
th:hover{{background:#e8eef7;color:var(--nv2)}}
th.na{{cursor:default}} th.na:hover{{background:#f2f5f9;color:#3c4c5d}}
th .ar{{opacity:.35;font-size:9px;margin-left:3px}} th.sorted .ar{{opacity:1;color:var(--nv2)}}
td{{padding:7px 10px;border-bottom:1px solid var(--line2);vertical-align:top}}
tbody tr:hover td{{background:#f7fafd}}
.c{{text-align:center}} .r{{text-align:right;font-variant-numeric:tabular-nums}}
.m{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:12px;white-space:nowrap}}
.s{{color:var(--mut);font-size:11.5px}} .kw{{font-weight:600}}
.pill{{display:inline-block;padding:2px 8px;border-radius:11px;font-size:11px;font-weight:600;white-space:nowrap}}
.pill.acc{{background:var(--chip);color:var(--nv)}}
.pill.op{{background:#e2f2f8;color:var(--opp)}} .pill.lt{{background:#f0e9f8;color:var(--lt)}}
.empty{{padding:26px;text-align:center;color:var(--mut);font-size:13px}}
footer{{color:var(--mut);font-size:11.5px;padding:16px 22px 40px;border-top:1px solid var(--line);margin-top:26px}}
kbd{{background:#fff;border:1px solid #c9d3de;border-bottom-width:2px;border-radius:4px;padding:0 4px;
 font-size:11px;font-family:inherit}}
@media (max-width:820px){{ .bar,main,header,.note,.kpis{{padding-left:12px;padding-right:12px}} }}
</style></head><body>

<header>
  <h1>BGCT Phase 1 — Proven Search Terms per Top-Moving ASIN</h1>
  <div class="meta">REQ-30-D01 · Amazon UK · DCVOLTAGE UK + LEDSone UK (reported separately, never
  merged) · Amazon Search Query Performance, <b>{E(per['start'])} → {E(per['end'])}</b> ·
  generated {E(p['generated_at'])}</div>
</header>

<div class="note"><b>These are the words real customers typed</b> to find your best-selling bulbs —
Amazon's own first-party data, not an estimate. They are the input to the gap report (D02).</div>

<div class="kpis">
  <div class="kpi"><div class="v">{len(tm)}</div>
    <div class="k">Top-Moving ASINs<br><span class="s">{tm_rule}</span></div></div>
  <div class="kpi"><div class="v">{with_terms}</div>
    <div class="k">…with proven terms<br><span class="s">the rest had none that converted</span></div></div>
  <div class="kpi"><div class="v">{len(terms)}</div>
    <div class="k">Search terms<br><span class="s">top {rules['terms_per_asin']} per ASIN</span></div></div>
  <div class="kpi o clk" data-f="op"><div class="v">{sum(r['op'] for r in rows)}</div>
    <div class="k">Opportunity terms<br><span class="s">high volume, low share of it</span></div></div>
  <div class="kpi l clk" data-f="lt"><div class="v">{sum(r['lt'] for r in rows)}</div>
    <div class="k">Long-tail terms<br><span class="s">3–6 words, 50–500 / mo</span></div></div>
</div>

<div class="bar">
  <input type="search" id="q" placeholder="Search a keyword or ASIN…   (press / )">
  <label>Account<select id="fbr"><option value="">All accounts</option>
    <option value="dcvoltage_uk">DCVOLTAGE UK</option><option value="ledsone_uk">LEDSone UK</option>
  </select></label>
  <label>Month<select id="fmo"><option value="">All 3 months</option></select></label>
  <label>ASIN<select id="fa"><option value="">All Top-Moving ASINs</option></select></label>
  <label>Min searches<input type="number" id="fv" min="0" step="50" placeholder="0"></label>
  <label class="chk"><input type="checkbox" id="fop"> Opportunity only</label>
  <label class="chk"><input type="checkbox" id="flt"> Long-tail only</label>
  <button class="btn" id="reset">Reset</button>
  <span class="count" id="count"></span>
</div>

<main>
  <section>
    <h2>Search terms <span class="n" id="nT"></span></h2>
    <p class="sub">Sorted by monthly searches. Click any heading to re-sort. <b>Opportunity</b> =
    at or above the median volume but below the median share of it — the source's
    “high volume + low ASIN share” pattern. <b>Long-tail</b> = 3–6 words, 50–500 searches a month.</p>
    <div class="wrap"><table id="tT"><thead><tr>
      <th data-k="mo">Month<span class="ar">▾</span></th>
      <th data-k="br">Account<span class="ar">▾</span></th>
      <th data-k="kw">Search term<span class="ar">▾</span></th>
      <th data-k="v" class="r">Searches / mo<span class="ar">▾</span></th>
      <th data-k="sh" class="r">Your share<span class="ar">▾</span></th>
      <th data-k="cr" class="r">Click rate<span class="ar">▾</span></th>
      <th data-k="pu" class="r">Purchases<span class="ar">▾</span></th>
      <th data-k="sc" class="r">Query score<span class="ar">▾</span></th>
      <th data-k="op" class="c">Pattern<span class="ar">▾</span></th>
      <th data-k="a">From ASIN<span class="ar">▾</span></th>
      </tr></thead><tbody></tbody></table>
      <div class="empty" hidden>Nothing matches these filters.</div></div>
  </section>

  <section>
    <h2>Top-Moving ASINs <span class="n" id="nM"></span></h2>
    <p class="sub">The best sellers these keywords came from. Units are shown month by month, as the
    source requires — never combined into one range.</p>
    <div class="wrap"><table id="tM"><thead><tr>
      <th data-k="br">Account<span class="ar">▾</span></th>
      <th data-k="a">ASIN<span class="ar">▾</span></th>
      <th class="na">Units per month ({E(' · '.join(m[:7] for m in per['months']))})</th>
      <th data-k="n" class="r">Proven terms<span class="ar">▾</span></th>
      </tr></thead><tbody></tbody></table>
      <div class="empty" hidden>Nothing matches these filters.</div></div>
  </section>
</main>

<footer>
<b>How this is built.</b> Source = Amazon <b>Search Query Performance</b>
(<code>business_reports.amz_search_query_performance</code>), the ASIN-level view the document
requires · window {E(per['start'])} → {E(per['end'])}, the last {nmonths} complete months, assembled
from Amazon's weekly rows with rates recomputed from their numerator and denominator, never averaged ·
Top-Moving = {tm_rule}, within the requester's own “Bulbs” category ·
top {rules['terms_per_asin']} terms per ASIN by volume, terms with no purchases dropped (source Step 6) ·
long-tail = 3–6 words and 50–500 searches a month (source Step 7).<br>
<b>Opportunity</b> is a median split of this run: the source names the “high volume + low ASIN share”
pattern but gives no numeric cut-off, so no threshold has been invented.<br>
Source: BGCT_Keyword_Workflow_Phase1_Phase2_v2.1.pdf · PRJ-2026-026 / REQ-30 (bgct) ·
<b>not yet signed off</b>. Shortcuts: <kbd>/</kbd> search, <kbd>Esc</kbd> clear.
</footer>

<script>
const D = {data};
const BR = {json.dumps(BRANDS)};
const $ = s => document.querySelector(s);
const esc = s => String(s==null?'':s).replace(/[&<>"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));
const sort = {{T:{{k:'v',d:-1}}, M:{{k:'n',d:-1}}}};
const num = x => x==null ? '<span class="s">—</span>' : x.toLocaleString();
const pct = x => x==null ? '<span class="s">—</span>' : x.toFixed(2)+'%';

// ASIN dropdown, ordered by how many terms each one contributes
const byAsin = {{}}; D.t.forEach(r=>byAsin[r.a]=(byAsin[r.a]||0)+1);
$('#fmo').insertAdjacentHTML('beforeend',
  [...new Set(D.t.map(r=>r.mo))].sort().map(m=>`<option value="${{m}}">${{m}}</option>`).join(''));
$('#fa').insertAdjacentHTML('beforeend', Object.keys(byAsin)
  .sort((x,y)=>byAsin[y]-byAsin[x])
  .map(a=>`<option value="${{a}}">${{a}} (${{byAsin[a]}})</option>`).join(''));

function F(){{ return {{
  q:$('#q').value.trim().toLowerCase(), br:$('#fbr').value, a:$('#fa').value,
  mo:$('#fmo').value,
  v:parseInt($('#fv').value||'0',10)||0, op:$('#fop').checked, lt:$('#flt').checked }}; }}

function keepT(r,f){{
  if(f.mo && r.mo!==f.mo) return false;
  if(f.br && r.br!==f.br) return false;
  if(f.a && r.a!==f.a) return false;
  if(r.v < f.v) return false;
  if(f.op && !r.op) return false;
  if(f.lt && !r.lt) return false;
  if(f.q && !(r.kw+' '+r.a).toLowerCase().includes(f.q)) return false;
  return true;
}}
function keepM(r,f){{
  if(f.br && r.br!==f.br) return false;
  if(f.a && r.a!==f.a) return false;
  if(f.q && !r.a.toLowerCase().includes(f.q)) return false;
  return true;
}}
function order(rows,k,d){{
  return rows.slice().sort((a,b)=>{{
    let x=a[k], y=b[k];
    if(x==null) x = (typeof y==='number') ? -1 : '';
    if(y==null) y = (typeof x==='number') ? -1 : '';
    if(typeof x==='number'||typeof y==='number') return ((x||0)-(y||0))*d;
    return String(x).localeCompare(String(y))*d;
  }});
}}

function draw(){{
  const f=F();
  const T=order(D.t.filter(r=>keepT(r,f)),sort.T.k,sort.T.d);
  const M=order(D.m.filter(r=>keepM(r,f)),sort.M.k,sort.M.d);

  $('#tT tbody').innerHTML = T.map(r=>`<tr>
    <td class="m">${{esc(r.mo)}}</td>
    <td><span class="pill acc">${{esc(BR[r.br])}}</span></td>
    <td class="kw">${{esc(r.kw)}}</td>
    <td class="r">${{num(r.v)}}</td><td class="r">${{pct(r.sh)}}</td>
    <td class="r">${{pct(r.cr)}}</td><td class="r">${{num(r.pu)}}</td>
    <td class="r">${{num(r.sc)}}</td>
    <td class="c">${{r.op?'<span class="pill op">Opportunity</span> ':''}}${{r.lt?'<span class="pill lt">Long-tail</span>':''}}${{(!r.op&&!r.lt)?'<span class="s">—</span>':''}}</td>
    <td class="m s">${{esc(r.a)}}</td></tr>`).join('');

  $('#tM tbody').innerHTML = M.map(r=>`<tr>
    <td><span class="pill acc">${{esc(BR[r.br])}}</span></td>
    <td class="m">${{esc(r.a)}}</td>
    <td class="m">${{r.u.join('  ·  ')}}</td>
    <td class="r">${{r.n}}</td></tr>`).join('');

  $('#nT').textContent = T.length===D.t.length ? `(${{D.t.length}})` : `(${{T.length}} of ${{D.t.length}})`;
  $('#nM').textContent = M.length===D.m.length ? `(${{D.m.length}})` : `(${{M.length}} of ${{D.m.length}})`;
  [['T',T],['M',M]].forEach(([s,rows])=>{{
    $('#t'+s).hidden = rows.length===0;
    $('#t'+s).closest('.wrap').querySelector('.empty').hidden = rows.length!==0;
  }});
  $('#count').innerHTML = `Showing <b>${{T.length}}</b> term${{T.length===1?'':'s'}}`
    + (T.length!==D.t.length?` of ${{D.t.length}}`:'')
    + ` · <b>${{new Set(T.map(r=>r.a)).size}}</b> ASIN${{new Set(T.map(r=>r.a)).size===1?'':'s'}}`;
  $('.kpi.o').classList.toggle('on',f.op); $('.kpi.l').classList.toggle('on',f.lt);
  document.querySelectorAll('th[data-k]').forEach(th=>{{
    const t=th.closest('table').id.slice(1), on=sort[t].k===th.dataset.k;
    th.classList.toggle('sorted',on);
    th.querySelector('.ar').textContent = on ? (sort[t].d>0?'▲':'▼') : '▾';
  }});
}}

['q','fbr','fmo','fa','fv','fop','flt'].forEach(id=>{{
  $('#'+id).addEventListener('input',draw); $('#'+id).addEventListener('change',draw); }});
document.querySelectorAll('.kpi.clk').forEach(k=>k.addEventListener('click',()=>{{
  const b=$('#f'+k.dataset.f); b.checked=!b.checked; draw(); }}));
$('#reset').addEventListener('click',()=>{{
  ['q','fbr','fmo','fa','fv'].forEach(id=>$('#'+id).value='');
  $('#fop').checked=false; $('#flt').checked=false;
  sort.T={{k:'v',d:-1}}; sort.M={{k:'n',d:-1}}; draw(); }});
document.querySelectorAll('th[data-k]').forEach(th=>th.addEventListener('click',()=>{{
  const t=th.closest('table').id.slice(1), k=th.dataset.k;
  if(sort[t].k===k) sort[t].d*=-1; else sort[t]={{k:k,d:(typeof (D[t==='T'?'t':'m'][0]||{{}})[k]==='number'?-1:1)}};
  draw(); }}));
addEventListener('keydown',e=>{{
  if(e.key==='/' && e.target.tagName!=='INPUT'){{ e.preventDefault(); $('#q').focus(); }}
  if(e.key==='Escape'){{ $('#q').value=''; draw(); }} }});
draw();
</script></body></html>"""

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(doc)
    print(f"dashboard -> {OUT}\n{len(terms)} terms · {with_terms}/{len(tm)} ASINs with terms · "
          f"{sum(r['op'] for r in rows)} opportunity · {sum(r['lt'] for r in rows)} long-tail · "
          f"{len(doc):,} bytes")


if __name__ == "__main__":
    main()
