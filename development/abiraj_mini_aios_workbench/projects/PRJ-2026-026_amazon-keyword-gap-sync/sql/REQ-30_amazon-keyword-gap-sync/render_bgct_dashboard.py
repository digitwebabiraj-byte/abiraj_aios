#!/usr/bin/env python3
"""
REQ-30-D02 - BGCT Keyword Gap review dashboard - renderer
PRJ-2026-026 (bgct)

Reads bgct_payload.json (written by build_bgct_d01.py) and emits ONE self-contained, full-screen
HTML file. No network calls, no external assets, no database access - the payload is the only input,
so the dashboard always matches the Excel it was built alongside.

Implements source section 2.6 (pre-computed review dashboard) and section 2.7 (the two buttons).

Design: full-viewport working tool, not a report page.
  - sticky toolbar that stays put while scrolling: text search + 5 filters + live "showing X of Y"
  - clickable KPI tiles that act as one-click filters
  - flat, sortable tables (click any header) so a person can scan and prioritise by volume
  - every row carries its own account / pair / SKU, so any filtered view is still self-explanatory
  - keyboard: "/" focuses search, Esc clears it

SCOPE BOUNDARY: the review buttons record state in the browser only. Neither writes to Amazon.
Section 2.7's automatic SP-API push is out of workbench scope - `add_target` tells a person where the
keyword should go; a person puts it there.
"""
import os, json, html

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, "..", ".."))
PAYLOAD = os.path.join(HERE, "bgct_payload.json")
OUT = os.path.join(PROJECT, "evidence", "final_outputs", "REQ-30_amazon-keyword-gap-sync",
                   "REQ-30-D02_keyword_gap_dashboard.html")

BRANDS = {"dcvoltage_uk": "DCVOLTAGE UK", "ledsone_uk": "LEDSone UK"}
STATUS = {"zero_sales_6mo": "No sales 6 months", "sales_drop_3mo": "Sales falling 3 months"}
TARGET = {"backend": "Add to backend", "bullet": "Add to bullets",
          "backend_and_bullet": "Add to backend + bullets", "none": "Nothing to do"}


def main():
    p = json.load(open(PAYLOAD, encoding="utf-8"))
    per, rules, qa = p["period"], p["rules"], p["qa"]
    pa, pb, pc = p["part_a"], p["part_b"], p.get("part_c", [])

    pairsB = sorted({(r["brand"], r["top_asin"], r["duplicate_asin"]) for r in pb})
    gaps = [r for r in pb if r["status"] == "gap"]

    nmonths = len(per["months"])
    req = rules["top_moving_months_required"]
    tm_rule = (f"more than {rules['top_moving_units_gt']} units in "
               + ("all " if req >= nmonths else f"at least {req} of ") + f"{nmonths} months")

    # ---- data handed to the page (kept small and flat: the page does all filtering client-side) ---
    rows_b = [{"br": r["brand"], "ta": r["top_asin"], "da": r["duplicate_asin"],
               "sk": r["base_sku"], "ds": r["duplicate_status"], "kw": r["keyword"],
               "v": r["search_query_volume"], "f": 1 if r["in_frontend"] else 0,
               "b": 1 if r["in_backend"] else 0, "t": r["add_target"]} for r in pb]
    rows_a = [{"br": r["brand"], "ta": r["top_asin"], "da": r["duplicate_asin"],
               "sku": r["duplicate_sku"], "sk": r["base_sku"], "ds": r["duplicate_status"],
               "is": r["issue"], "n": r["terms_available"], "ti": r["title"]} for r in pa]
    rows_c = [{"br": r["brand"], "ta": r["top_asin"], "da": r["duplicate_asin"],
               "sku": r["duplicate_sku"], "sk": r["base_sku"], "tw": r["top_watts"],
               "dw": r["duplicate_watts"], "is": r["issue"], "ti": r["title"]} for r in pc]

    data = json.dumps({"a": rows_a, "b": rows_b, "c": rows_c}, separators=(",", ":"))
    qa_line = " · ".join(f'{k.split("_",1)[1].replace("_"," ")} '
                         f'<b class="{"y" if v else "n"}">{"PASS" if v else "FAIL"}</b>'
                         for k, v in qa.items())
    E = html.escape

    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BGCT Keyword Gap Report — REQ-30-D02</title><style>
:root{{
 --bg:#eef1f5; --panel:#fff; --ink:#14202c; --mut:#5c6b7a; --line:#dde3ea; --line2:#eef1f5;
 --nv:#1b3a5c; --nv2:#25507d; --gap:#c0392b; --gapbg:#fdf4f3; --ok:#177245; --warn:#a86a12;
 --purple:#6b3fa0; --chip:#e8eef7;
}}
*{{box-sizing:border-box}}
html,body{{height:100%}}
body{{margin:0;background:var(--bg);color:var(--ink);
 font:14px/1.45 -apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
 -webkit-font-smoothing:antialiased}}

/* ---------- header ---------- */
header{{background:linear-gradient(180deg,var(--nv2),var(--nv));color:#fff;padding:14px 22px 12px}}
header h1{{margin:0;font-size:18px;letter-spacing:.2px}}
header .meta{{opacity:.9;font-size:12px;margin-top:3px}}
header .meta b{{color:#ffe9b0;font-weight:600}}

.note{{background:#fff8e8;border-top:1px solid #f0dcae;border-bottom:1px solid #f0dcae;
 padding:9px 22px;font-size:12.5px;color:#6b4a05}}
.note b{{color:#8a5a00}}

/* ---------- KPI tiles ---------- */
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;padding:14px 22px 4px}}
.kpi{{background:var(--panel);border:1px solid var(--line);border-radius:9px;padding:11px 13px;
 cursor:pointer;transition:.12s;border-left:4px solid var(--line)}}
.kpi:hover{{border-color:var(--nv2);box-shadow:0 2px 8px rgba(20,32,44,.09)}}
.kpi.on{{border-color:var(--nv2);background:#f5f9ff;box-shadow:inset 0 0 0 1px var(--nv2)}}
.kpi .v{{font-size:26px;font-weight:700;line-height:1.05;font-variant-numeric:tabular-nums}}
.kpi .k{{font-size:12px;color:var(--mut);margin-top:3px}}
.kpi.a{{border-left-color:var(--warn)}} .kpi.b{{border-left-color:var(--gap)}}
.kpi.c{{border-left-color:var(--purple)}} .kpi.t{{border-left-color:var(--nv2)}}

/* ---------- sticky toolbar ---------- */
.bar{{position:sticky;top:0;z-index:20;background:rgba(238,241,245,.96);backdrop-filter:blur(6px);
 border-bottom:1px solid var(--line);padding:10px 22px;display:flex;gap:9px;align-items:center;
 flex-wrap:wrap}}
.bar input[type=search],.bar select,.bar input[type=number]{{font:13px inherit;color:var(--ink);
 background:#fff;border:1px solid #c9d3de;border-radius:7px;padding:7px 9px;outline:none}}
.bar input[type=search]{{flex:1 1 260px;min-width:200px}}
.bar input[type=search]:focus,.bar select:focus,.bar input[type=number]:focus{{border-color:var(--nv2);
 box-shadow:0 0 0 3px rgba(37,80,125,.13)}}
.bar input[type=number]{{width:96px}}
.bar label{{font-size:11px;color:var(--mut);display:flex;flex-direction:column;gap:3px}}
.bar label.chk{{flex-direction:row;align-items:center;gap:6px;font-size:12.5px;color:var(--ink);
 background:#fff;border:1px solid #c9d3de;border-radius:7px;padding:7px 10px;cursor:pointer}}
.bar label.chk:hover{{border-color:var(--nv2)}}
.bar label.chk span:first-child{{display:none}}
.bar label.chk input{{margin:0;cursor:pointer}}
.count{{margin-left:auto;font-size:12.5px;color:var(--mut);white-space:nowrap}}
.count b{{color:var(--ink);font-variant-numeric:tabular-nums}}
.btn{{border:1px solid #c9d3de;background:#fff;border-radius:7px;padding:7px 11px;font-size:12.5px;
 cursor:pointer;color:var(--ink)}}
.btn:hover{{border-color:var(--nv2);color:var(--nv2)}}

/* ---------- sections ---------- */
main{{padding:4px 22px 70px}}
section{{margin-top:20px}}
h2{{font-size:14.5px;margin:0 0 3px;padding-left:10px;border-left:4px solid var(--line)}}
h2 .n{{color:var(--mut);font-weight:500}}
section.A h2{{border-left-color:var(--warn)}}
section.B h2{{border-left-color:var(--gap)}}
section.C h2{{border-left-color:var(--purple)}}
.sub{{color:var(--mut);font-size:12.5px;margin:0 0 9px;padding-left:14px}}

/* ---------- tables ---------- */
.wrap{{background:var(--panel);border:1px solid var(--line);border-radius:9px;overflow:auto;
 max-height:none}}
table{{width:100%;border-collapse:separate;border-spacing:0;font-size:13px}}
th{{position:sticky;top:0;z-index:5;background:#f2f5f9;text-align:left;padding:8px 10px;
 font-size:11.5px;font-weight:600;color:#3c4c5d;border-bottom:1px solid var(--line);
 white-space:nowrap;cursor:pointer;user-select:none}}
th:hover{{background:#e8eef7;color:var(--nv2)}}
th.na{{cursor:default}} th.na:hover{{background:#f2f5f9;color:#3c4c5d}}
th .ar{{opacity:.35;font-size:9px;margin-left:3px}}
th.sorted .ar{{opacity:1;color:var(--nv2)}}
td{{padding:7px 10px;border-bottom:1px solid var(--line2);vertical-align:top}}
tbody tr:hover td{{background:#f7fafd}}
tbody tr.gap td{{background:var(--gapbg)}}
tbody tr.gap:hover td{{background:#fbeceb}}
.c{{text-align:center}} .r{{text-align:right;font-variant-numeric:tabular-nums}}
.m{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:12px;white-space:nowrap}}
.s{{color:var(--mut);font-size:11.5px}}
.kw{{font-weight:600}}
.tick{{display:inline-block;width:19px;height:19px;line-height:19px;border-radius:50%;
 font-size:11px;color:#fff;text-align:center}}
.tick.y{{background:var(--ok)}} .tick.n{{background:var(--gap)}}
.pill{{display:inline-block;padding:2px 8px;border-radius:11px;font-size:11px;font-weight:600;
 white-space:nowrap}}
.pill.both{{background:#fbe9e7;color:var(--gap)}}
.pill.be{{background:#fff3e0;color:var(--warn)}}
.pill.bu{{background:#e8f0fe;color:var(--nv2)}}
.pill.no{{background:#e7f4ea;color:var(--ok)}}
.pill.acc{{background:var(--chip);color:var(--nv)}}
.warnt{{color:var(--warn)}}
.empty{{padding:26px;text-align:center;color:var(--mut);font-size:13px}}
footer{{color:var(--mut);font-size:11.5px;padding:16px 22px 40px;border-top:1px solid var(--line);
 margin-top:26px}}
b.y{{color:var(--ok)}} b.n{{color:var(--gap)}}
kbd{{background:#fff;border:1px solid #c9d3de;border-bottom-width:2px;border-radius:4px;
 padding:0 4px;font-size:11px;font-family:inherit}}
@media (max-width:820px){{ .bar{{padding:9px 12px}} main{{padding:4px 12px 60px}}
 header,.note,.kpis{{padding-left:12px;padding-right:12px}} }}
</style></head><body>

<header>
  <h1>BGCT — Keyword Collection &amp; Cross-ASIN Gap Sync</h1>
  <div class="meta">REQ-30-D02 · Amazon UK · DCVOLTAGE UK + LEDSone UK (reported separately, never
  merged) · keywords from <b>{E(per['start'])} → {E(per['end'])}</b> · no-sales window from
  <b>{E(per['zero_sales_from'])}</b> · generated {E(p['generated_at'])}</div>
</header>

<div class="note"><b>This report changes nothing on Amazon.</b> It shows where each proven keyword
should go — a person adds it. (The source document's automatic push is deliberately out of scope.)</div>

<div class="kpis">
  <div class="kpi t" data-f="all"><div class="v">{len(p['top_moving'])}</div>
    <div class="k">Top-Moving ASINs<br><span class="s">{tm_rule}</span></div></div>
  <div class="kpi a" data-f="A"><div class="v">{len(pa)}</div>
    <div class="k">Need a rewrite<br><span class="s">Part A — nothing on the listing</span></div></div>
  <div class="kpi b" data-f="B"><div class="v">{len(gaps)}</div>
    <div class="k">Keyword gaps<br><span class="s">Part B — across {len(pairsB)} listings</span></div></div>
  <div class="kpi c" data-f="C"><div class="v">{len(pc)}</div>
    <div class="k">Wrong SKU<br><span class="s">Part C — rejected, not the same bulb</span></div></div>
</div>

<div class="bar">
  <input type="search" id="q" placeholder="Search ASIN, SKU or keyword…   (press / )">
  <label>Account<select id="fbr"><option value="">All accounts</option>
    <option value="dcvoltage_uk">DCVOLTAGE UK</option><option value="ledsone_uk">LEDSone UK</option>
  </select></label>
  <label>Show<select id="fsec"><option value="">Everything</option>
    <option value="A">A — needs rewrite</option><option value="B">B — keyword gaps</option>
    <option value="C">C — wrong SKU</option></select></label>
  <label>What to do<select id="ftg"><option value="">Any action</option>
    <option value="backend_and_bullet">Add to backend + bullets</option>
    <option value="backend">Add to backend</option>
    <option value="bullet">Add to bullets</option>
    <option value="none">Nothing to do</option></select></label>
  <label>Why flagged<select id="fds"><option value="">Any reason</option>
    <option value="zero_sales_6mo">No sales 6 months</option>
    <option value="sales_drop_3mo">Sales falling 3 months</option></select></label>
  <label>Min searches<input type="number" id="fv" min="0" step="10" placeholder="0"></label>
  <label class="chk"><span>&nbsp;</span><span><input type="checkbox" id="fgap" checked>
    Only rows needing action</span></label>
  <button class="btn" id="reset">Reset</button>
  <span class="count" id="count"></span>
</div>

<main>
  <section class="A" id="secA">
    <h2>Part A — listing has no content <span class="n" id="nA"></span></h2>
    <p class="sub">Every keyword would read as “missing” because there is nothing on the listing to
    search. These need writing, not keyword edits.</p>
    <div class="wrap"><table id="tA"><thead><tr>
      <th data-k="br">Account<span class="ar">▾</span></th>
      <th data-k="da">Dead listing<span class="ar">▾</span></th>
      <th data-k="sku">Its SKU<span class="ar">▾</span></th>
      <th data-k="sk">Base SKU<span class="ar">▾</span></th>
      <th data-k="ds">Why flagged<span class="ar">▾</span></th>
      <th data-k="is">What is missing<span class="ar">▾</span></th>
      <th data-k="n" class="r">Terms ready<span class="ar">▾</span></th>
      <th data-k="ta">Good twin<span class="ar">▾</span></th>
      <th class="na">Title</th></tr></thead><tbody></tbody></table>
      <div class="empty" hidden>Nothing matches these filters.</div></div>
  </section>

  <section class="C" id="secC">
    <h2>Part C — wrong SKU, pair rejected <span class="n" id="nC"></span></h2>
    <p class="sub">These share a base SKU but are <b>not the same bulb</b> — the wattage or the cap
    fitting differs, so the stored SKU is wrong. No keywords were checked. Fix the SKU first.</p>
    <div class="wrap"><table id="tC"><thead><tr>
      <th data-k="br">Account<span class="ar">▾</span></th>
      <th data-k="ta">Good seller<span class="ar">▾</span></th>
      <th data-k="tw" class="c">Its spec<span class="ar">▾</span></th>
      <th data-k="da">Listing with wrong SKU<span class="ar">▾</span></th>
      <th data-k="dw" class="c">Its spec<span class="ar">▾</span></th>
      <th data-k="sku">Wrong SKU<span class="ar">▾</span></th>
      <th data-k="sk">Base SKU<span class="ar">▾</span></th>
      <th class="na">Title</th></tr></thead><tbody></tbody></table>
      <div class="empty" hidden>Nothing matches these filters.</div></div>
  </section>

  <section class="B" id="secB">
    <h2>Part B — keyword gaps <span class="n" id="nB"></span></h2>
    <p class="sub">One row per keyword. <b>Sorted by monthly searches</b> — work down from the top.
    Click any column heading to re-sort.</p>
    <div class="wrap"><table id="tB"><thead><tr>
      <th data-k="br">Account<span class="ar">▾</span></th>
      <th data-k="kw">Keyword<span class="ar">▾</span></th>
      <th data-k="v" class="r">Searches / mo<span class="ar">▾</span></th>
      <th data-k="f" class="c">In text<span class="ar">▾</span></th>
      <th data-k="b" class="c">In backend<span class="ar">▾</span></th>
      <th data-k="t">What to do<span class="ar">▾</span></th>
      <th data-k="da">Listing to fix<span class="ar">▾</span></th>
      <th data-k="ds">Why flagged<span class="ar">▾</span></th>
      <th data-k="sk">Base SKU<span class="ar">▾</span></th>
      <th data-k="ta">Keyword came from<span class="ar">▾</span></th>
      </tr></thead><tbody></tbody></table>
      <div class="empty" hidden>Nothing matches these filters.</div></div>
  </section>
</main>

<footer>
<b>How each figure is decided.</b>
Top-Moving = {tm_rule}, in the requester's own “Bulbs” category ·
base SKU = pack size, trailing markers and account suffixes stripped, using the SKU mapping table
(<code>mapped_sku</code>); bundles kept whole ·
underperforming = no sales in {rules['zero_sales_window_months']} months (counted from the product
list, so listings absent from the sales report still count) or falling every month ·
a keyword counts as present if <b>all its words appear anywhere</b> in the text, any order, ignoring
capitals and punctuation ·
top {rules['terms_per_asin']} terms per ASIN, terms with no purchases dropped ·
a pair is rejected when the two listings state a different wattage or cap fitting.<br>
<b>Self-checks:</b> {qa_line}.<br>
Source: BGCT_Keyword_Workflow_Phase1_Phase2_v2.1.pdf · PRJ-2026-026 / REQ-30 (bgct) ·
independently validated 10/10 · <b>not yet signed off</b>. Shortcuts: <kbd>/</kbd> search,
<kbd>Esc</kbd> clear.
</footer>

<script>
const D = {data};
const BR = {json.dumps(BRANDS)}, ST = {json.dumps(STATUS)}, TG = {json.dumps(TARGET)};
const PILL = {{backend_and_bullet:'both',backend:'be',bullet:'bu',none:'no'}};
const $ = s => document.querySelector(s);
const esc = s => String(s==null?'':s).replace(/[&<>"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));
const sort = {{A:{{k:'sk',d:1}}, B:{{k:'v',d:-1}}, C:{{k:'sk',d:1}}}};
let sec = '';

function F(){{ return {{
  q:  $('#q').value.trim().toLowerCase(),
  br: $('#fbr').value, tg: $('#ftg').value, ds: $('#fds').value,
  v:  parseInt($('#fv').value||'0',10) || 0,
  g:  $('#fgap').checked }}; }}

function keep(r,f,kind){{
  if(f.br && r.br!==f.br) return false;
  if(f.ds && r.ds && r.ds!==f.ds) return false;
  if(kind==='B'){{
    if(f.g && r.t==='none') return false;            // hide keywords already in both places
    if(f.tg && r.t!==f.tg) return false;
    if(r.v < f.v) return false;
  }}
  else if(f.tg || f.v) return false;                 // action / volume only exist in Part B
  if(f.q){{
    const hay = [r.da,r.ta,r.sk,r.sku,r.kw,r.ti].filter(Boolean).join(' ').toLowerCase();
    if(!hay.includes(f.q)) return false;
  }}
  return true;
}}

function order(rows,k,d){{
  return rows.slice().sort((a,b)=>{{
    let x=a[k], y=b[k];
    if(typeof x==='number'||typeof y==='number') return ((x||0)-(y||0))*d;
    return String(x||'').localeCompare(String(y||''))*d;
  }});
}}

function draw(){{
  const f=F();
  const A = (sec&&sec!=='A')?[]:order(D.a.filter(r=>keep(r,f,'A')),sort.A.k,sort.A.d);
  const B = (sec&&sec!=='B')?[]:order(D.b.filter(r=>keep(r,f,'B')),sort.B.k,sort.B.d);
  const C = (sec&&sec!=='C')?[]:order(D.c.filter(r=>keep(r,f,'C')),sort.C.k,sort.C.d);

  $('#tA tbody').innerHTML = A.map(r=>`<tr>
    <td><span class="pill acc">${{esc(BR[r.br])}}</span></td>
    <td class="m">${{esc(r.da)}}</td><td class="m s">${{esc(r.sku)}}</td><td class="m">${{esc(r.sk)}}</td>
    <td>${{esc(ST[r.ds]||r.ds)}}</td><td class="warnt">${{esc(r.is)}}</td>
    <td class="r">${{r.n}}</td><td class="m">${{esc(r.ta)}}</td>
    <td class="s">${{esc((r.ti||'').slice(0,80))}}</td></tr>`).join('');

  $('#tC tbody').innerHTML = C.map(r=>`<tr>
    <td><span class="pill acc">${{esc(BR[r.br])}}</span></td>
    <td class="m">${{esc(r.ta)}}</td><td class="c m">${{esc(r.tw)}}</td>
    <td class="m">${{esc(r.da)}}</td><td class="c m warnt"><b>${{esc(r.dw)}}</b></td>
    <td class="m warnt">${{esc(r.sku)}}</td><td class="m">${{esc(r.sk)}}</td>
    <td class="s">${{esc((r.ti||'').slice(0,80))}}</td></tr>`).join('');

  $('#tB tbody').innerHTML = B.map(r=>`<tr class="${{r.t==='none'?'':'gap'}}">
    <td><span class="pill acc">${{esc(BR[r.br])}}</span></td>
    <td class="kw">${{esc(r.kw)}}</td>
    <td class="r">${{r.v.toLocaleString()}}</td>
    <td class="c"><span class="tick ${{r.f?'y':'n'}}">${{r.f?'✓':'✗'}}</span></td>
    <td class="c"><span class="tick ${{r.b?'y':'n'}}">${{r.b?'✓':'✗'}}</span></td>
    <td><span class="pill ${{PILL[r.t]}}">${{esc(TG[r.t])}}</span></td>
    <td class="m">${{esc(r.da)}}</td><td>${{esc(ST[r.ds]||r.ds)}}</td>
    <td class="m">${{esc(r.sk)}}</td><td class="m s">${{esc(r.ta)}}</td></tr>`).join('');

  const set=(id,n,tot)=>{{ $(id).textContent = n===tot ? `(${{tot}})` : `(${{n}} of ${{tot}})`; }};
  set('#nA',A.length,D.a.length); set('#nB',B.length,D.b.length); set('#nC',C.length,D.c.length);
  ['A','B','C'].forEach(s=>{{
    const rows={{A:A,B:B,C:C}}[s];
    $('#sec'+s).hidden = !!(sec && sec!==s);
    $('#t'+s).hidden = rows.length===0;
    $('#sec'+s+' .empty').hidden = rows.length!==0;
  }});
  const shown=A.length+B.length+C.length, tot=D.a.length+D.b.length+D.c.length;
  const g=B.filter(r=>r.t!=='none').length;
  $('#count').innerHTML = `Showing <b>${{shown}}</b> row${{shown===1?'':'s'}}` +
    (f.g?` · <b>${{D.b.filter(r=>r.t!=='none').length}}</b> gaps in total`
        :` of ${{tot}}`);
  document.querySelectorAll('.kpi').forEach(k=>k.classList.toggle('on',(k.dataset.f==='all'?'':k.dataset.f)===sec));
  document.querySelectorAll('th[data-k]').forEach(th=>{{
    const t=th.closest('table').id.slice(1), on=sort[t].k===th.dataset.k;
    th.classList.toggle('sorted',on);
    th.querySelector('.ar').textContent = on ? (sort[t].d>0?'▲':'▼') : '▾';
  }});
}}

['q','fbr','ftg','fds','fv'].forEach(id=>{{
  $('#'+id).addEventListener('input',draw); $('#'+id).addEventListener('change',draw); }});
$('#fsec').addEventListener('change',e=>{{ sec=e.target.value; draw(); }});
$('#ftg').addEventListener('change',e=>{{                 // asking for 'Nothing to do' un-hides them
  if(e.target.value==='none') $('#fgap').checked=false; draw(); }});
$('#fgap').addEventListener('change',draw);
document.querySelectorAll('.kpi').forEach(k=>k.addEventListener('click',()=>{{
  const f=k.dataset.f==='all'?'':k.dataset.f; sec = (sec===f)?'':f; $('#fsec').value=sec; draw(); }}));
$('#reset').addEventListener('click',()=>{{
  ['q','fbr','ftg','fds','fv'].forEach(id=>$('#'+id).value='');
  $('#fgap').checked=true; sec=''; $('#fsec').value=''; draw(); }});
document.querySelectorAll('th[data-k]').forEach(th=>th.addEventListener('click',()=>{{
  const t=th.closest('table').id.slice(1), k=th.dataset.k;
  if(sort[t].k===k) sort[t].d*=-1; else sort[t]={{k:k,d:(k==='v'?-1:1)}};
  draw(); }}));
addEventListener('keydown',e=>{{
  if(e.key==='/' && e.target.tagName!=='INPUT'){{ e.preventDefault(); $('#q').focus(); }}
  if(e.key==='Escape'){{ $('#q').value=''; draw(); }} }});
draw();
</script></body></html>"""

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(doc)
    print(f"dashboard -> {OUT}\n{len(pa)} Part A · {len(pairsB)} Part B listings · {len(gaps)} gaps · "
          f"{len(pc)} Part C · {len(doc):,} bytes")


if __name__ == "__main__":
    main()
