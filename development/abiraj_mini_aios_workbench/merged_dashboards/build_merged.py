# -*- coding: utf-8 -*-
"""
Registry-driven merged dashboard builder — INDEPENDENT-TAB model.
Each task keeps its OWN rows, columns and row count. The page is tabs: click a task
-> see that task's own rows + count + columns. No cross-task row join (so tasks may
cover different listings / different counts — that's expected and correct).

Reads registry.json + each task's standard <code>_merge.json (per MERGE_DATA_SPEC.md).
Adding a task = its emitter output + one registry line. Sources are never touched.
"""
import json, os, sys, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
REG_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "registry.json")
REG = json.load(open(REG_PATH, encoding="utf-8"))
OUT = os.path.join(HERE, REG.get("output", "ebay_listings_eppr_esnm/merged_eppr_esnm_dashboard.html"))

def num(x):
    try: return float(x)
    except (TypeError, ValueError): return None

tasks = []
for t in REG["tasks"]:
    d = json.load(open(os.path.join(HERE, t["file"]), encoding="utf-8"))
    if not d["rows"]:
        raise SystemExit(f"ABORT: task {d['task']} has 0 rows")
    headline = set(t.get("headline", []))

    id_cols  = [c for c in d["columns"] if c["role"] == "id"]
    met_cols = [c for c in d["columns"] if c["role"] == "metric"]
    ordered  = id_cols + met_cols
    cols = [{"key": c["key"], "name": c["name"], "group": ("ID" if c["role"] == "id" else d["task"]),
             "type": c["type"], "pin": c["key"] in ("image", "sku"),
             "agg": c.get("agg"), "big": c["key"] in headline} for c in ordered]

    # rows aligned to this task's own column order
    ckeys = [c["key"] for c in ordered]
    rows = [[r.get(k) for k in ckeys] for r in d["rows"]]

    # default sort: first money metric desc (nice ordering), else leave as-is
    sort_key = next((c["key"] for c in met_cols if c["type"] == "money"), None)
    if sort_key:
        si = ckeys.index(sort_key)
        rows.sort(key=lambda r: (num(r[si]) if num(r[si]) is not None else -1), reverse=True)

    # slim summary line: only genuinely-useful TOTALS (num/money headline metrics).
    # deliberately drops text "N set" counts and weak per-row averages.
    summary = []
    for c in met_cols:
        if c["key"] not in headline or c["type"] not in ("num", "money") or c.get("agg") == "avg":
            continue
        ci = ckeys.index(c["key"])
        vals = [num(r[ci]) for r in rows]; vals = [v for v in vals if v is not None]
        disp = f"{sum(vals):,.0f}" if c["type"] == "num" else f"{sum(vals):,.2f}"
        summary.append({"name": c["name"], "disp": disp})
    summary = summary[:3]

    # filter dropdowns: registry lists column keys; keep those present in this task
    have = {c["key"]: c["name"] for c in cols}
    tfilters = [{"key": k, "name": have[k]} for k in t.get("filters", []) if k in have]

    tasks.append({"code": d["task"], "label": d.get("label", d["task"]),
                  "owner": d.get("owner", ""), "as_of": d.get("as_of", ""),
                  "count": len(rows), "cols": cols, "summary": summary,
                  "filters": tfilters, "rows": rows})
    print(f"loaded {d['task']}: {len(rows):,} rows, {len(cols)} cols, as_of {d.get('as_of')}")

meta = {"title": REG.get("title", "Unified Dashboard"),
        "colors": REG.get("colors", {}), "currency": REG.get("currency", "£"), "tasks": tasks}

PAGE = r"""<!doctype html><html data-theme="light"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--bg:#eef1f7;--panel:#fff;--ink:#0f1b2d;--muted:#64748b;--line:#e6eaf1;--head:#0f1b3a;
 --accent:#2563eb;--chip:#eef2ff;--chipink:#3730a3;--pos:#059669;--neg:#dc2626;--stick:#fff;
 --sh:0 1px 2px rgba(16,27,61,.04),0 8px 24px rgba(16,27,61,.06);--zebra:#fafbfe;}
*{box-sizing:border-box}
html,body{height:100%}
body{margin:0;background:radial-gradient(1200px 400px at 15% -10%,#e9edfb,transparent),var(--bg);color:var(--ink);font:14px/1.45 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}
.wrap{padding:16px 18px;display:flex;flex-direction:column;height:100vh;min-height:0}
.top{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
h1{font-size:19px;margin:0;font-weight:750;letter-spacing:-.01em}.sub{color:var(--muted);font-size:12.5px;margin-top:2px}
.hint{color:var(--muted);font-size:12.5px;margin:10px 0 4px}
.btn{border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:10px;padding:8px 14px;font-size:12.5px;font-weight:600;cursor:pointer;box-shadow:var(--sh);transition:.15s}
.btn:hover{border-color:var(--accent);color:var(--accent)}
.bar{display:flex;justify-content:space-between;align-items:center;gap:10px 16px;flex-wrap:wrap;margin:12px 0 10px}
.filt{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.tabs{display:inline-flex;flex-wrap:wrap;gap:5px;margin:0;background:var(--panel);padding:5px;border-radius:14px;box-shadow:var(--sh)}
.tab{display:inline-flex;align-items:center;gap:8px;border:0;background:transparent;
 border-radius:10px;padding:8px 14px;font-size:13px;font-weight:600;cursor:pointer;color:var(--muted);transition:.15s ease}
.tab:hover{background:var(--zebra);color:var(--ink)}
.tab.active{color:#fff;box-shadow:0 2px 8px rgba(16,27,61,.18)}
.tab .tnote{font-weight:400;opacity:.75;font-size:11px}
.tab .tcount{font-weight:700;font-size:11px;padding:1px 8px;border-radius:999px;background:var(--chip);color:var(--chipink)}
.tab.active .tcount{background:rgba(255,255,255,.22);color:#fff}
.tdot{width:9px;height:9px;border-radius:50%;flex:none}
.tab.active .tdot{background:#fff!important}
.tab.active{box-shadow:0 0 0 2px color-mix(in srgb,var(--accent) 26%,transparent);border-color:var(--accent)}
.summary{margin:12px 0 8px;color:var(--muted);font-size:12.5px}
.summary b.tot{color:var(--ink)}.summary .sep{color:var(--line);margin:0 5px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:16px;overflow:hidden;margin-top:0;
 flex:1 1 auto;display:flex;flex-direction:column;min-height:0;box-shadow:var(--sh)}
@media (max-width:760px), (max-height:900px){
 .wrap{padding:7px} .hint{display:none} #sub{display:none}
 h1{font-size:14px} .top{margin-bottom:0} .bar{margin:6px 0}
 .tab{padding:5px 11px;font-size:12.5px} .tdot{width:8px;height:8px}
 .inp{padding:5px 9px} th,td{padding:5px 9px} tbody td{height:34px} thead th{font-size:12px}
}
.controls{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.inp{border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:9px;padding:7px 11px;font-size:12.5px;box-shadow:var(--sh);transition:.15s}
.inp:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 18%,transparent)}
#q{min-width:230px}
thead th{cursor:pointer;user-select:none}
thead th.fix{cursor:pointer}
thead th .ar{font-size:9px;margin-left:4px;opacity:.9}
.ptop{display:flex;justify-content:space-between;align-items:center;padding:12px 14px;border-bottom:1px solid var(--line);gap:10px;flex-wrap:wrap}
.scroll{overflow:auto;flex:1 1 auto;min-height:120px}
table{border-collapse:separate;border-spacing:0;width:max-content;min-width:100%}
th,td{padding:9px 12px;font-size:12.5px;white-space:nowrap;border-bottom:1px solid var(--line);text-align:left;
 max-width:170px;overflow:hidden;text-overflow:ellipsis}
tbody td{height:42px}tr.spacer td{padding:0;border:0;height:0;max-width:none}
th.title,td.title{max-width:260px}
th.imgc,td.imgc{max-width:52px;width:52px;text-align:center;overflow:visible}
th.num,td.num,th.money,td.money,th.pct,td.pct{max-width:120px}
thead th{position:sticky;top:0;background:linear-gradient(var(--head),#16244a);color:#e2e8f6;z-index:3;font-weight:600;letter-spacing:.02em;text-transform:uppercase;font-size:11px}
tbody td.num,tbody td.money,tbody td.pct,thead th.num,thead th.money,thead th.pct{text-align:right;font-variant-numeric:tabular-nums}
td.fix,th.fix{position:sticky;background:var(--stick);z-index:2}thead th.fix{z-index:4;background:var(--head)}
tbody tr:nth-child(even) td{background:var(--zebra)}tbody tr:nth-child(even) td.fix{background:var(--zebra)}
tbody tr:hover td{background:color-mix(in srgb,var(--accent) 9%,var(--panel))!important}
.title{max-width:270px;overflow:hidden;text-overflow:ellipsis}
td.empty{padding:26px 14px;text-align:center;color:var(--muted);font-size:13px}
img.thumb{width:34px;height:34px;object-fit:contain;border-radius:6px;background:#fff;border:1px solid var(--line)}
.chip{display:inline-block;padding:2px 8px;border-radius:999px;background:var(--chip);color:var(--chipink);font-size:11px}
.pos{color:var(--pos)}.neg{color:var(--neg)}
</style></head><body><div class="wrap">
<div class="top"><div><h1 id="h1"></h1><div class="sub" id="sub"></div></div>
 <div style="display:flex;gap:8px"><button class="btn" id="csv">Export CSV</button></div></div>
<div class="hint"><b>Pick a task tab.</b> Each tab shows that task's own listings and its own count — a task may cover more or fewer rows than another, that's normal. The left identity columns stay pinned; the right side is that task's data.</div>
<div class="bar">
  <div class="tabs" id="tabs"></div>
  <div class="filt">
    <input id="q" class="inp" type="search" placeholder="Search SKU or title…">
    <span id="filters" class="controls"></span>
    <span class="sub" id="count"></span>
  </div>
</div>
<div class="panel">
 <div class="scroll"><table><thead><tr id="hrow"></tr></thead><tbody id="body"></tbody></table></div></div></div>
<script>
const DATA=__DATA__, COLORS=DATA.colors, TASKS=DATA.tasks;
let active=0;
const ui={q:'',f:{},sortCol:null,sortDir:-1};
let view=[];
function T(){return TASKS[active];}
function colIdx(pred){return T().cols.findIndex(pred);}
function computeView(){
 const cols=T().cols, rows=T().rows;
 const skuI=colIdx(c=>c.key==='sku'), titI=colIdx(c=>c.key==='title'||c.name==='Product Title');
 let v=rows;
 if(ui.q){const q=ui.q.toLowerCase();
  v=v.filter(r=>(skuI>=0&&(''+(r[skuI]??'')).toLowerCase().includes(q))||(titI>=0&&(''+(r[titI]??'')).toLowerCase().includes(q)));}
 T().filters.forEach(f=>{const val=ui.f[f.key];if(!val)return;const ci=colIdx(c=>c.key===f.key);
  if(ci>=0)v=v.filter(r=>(''+(r[ci]??''))===val);});
 if(ui.sortCol!=null){const ci=ui.sortCol,dir=ui.sortDir,typ=cols[ci].type;
  v=v.slice().sort((a,b)=>{let x=a[ci],y=b[ci];
   if(typ==='num'||typ==='money'||typ==='pct'){x=Number(x);y=Number(y);const xn=isNaN(x),yn=isNaN(y);
    if(xn&&yn)return 0;if(xn)return 1;if(yn)return -1;return (x-y)*dir;}
   x=(x==null?'':''+x).toLowerCase();y=(y==null?'':''+y).toLowerCase();return x<y?-dir:x>y?dir:0;});}
 view=v;
}
function updateCount(){const t=T().count,n=view.length;
 const base=(n===t?`${t.toLocaleString()} listings`:`showing <b>${n.toLocaleString()}</b> of ${t.toLocaleString()}`);
 document.getElementById('count').innerHTML=base+` · as of <b>${T().as_of||'?'}</b>`;}
function updateArrows(){document.querySelectorAll('#hrow th').forEach((th,i)=>{const a=th.querySelector('.ar');
 if(a)a.textContent=(ui.sortCol===i?(ui.sortDir<0?'▼':'▲'):'');});}
function applyView(){SCROLLER.scrollTop=0;computeView();paint();updateCount();updateArrows();}
function fmt(v,t){if(v===null||v===undefined||v==='')return'';
 if(t==='money'){const n=Number(v);return isNaN(n)?v:n.toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2});}
 if(t==='num'){const n=Number(v);return isNaN(n)?v:n.toLocaleString();}
 if(t==='pct'){const n=Number(v);return isNaN(n)?v:n.toFixed(2)+'%';}return v;}
function cls(c){return c.type==='money'?'money':c.type==='num'?'num':c.type==='pct'?'pct':'';}
function col(code){return COLORS[code]||'#2563eb';}
function renderTabs(){const host=document.getElementById('tabs');host.innerHTML='';
 TASKS.forEach((t,idx)=>{const b=document.createElement('button');b.className='tab'+(active===idx?' active':'');
  b.style.background=active===idx?col(t.code):'';
  b.innerHTML=`<span class="tdot" style="background:${col(t.code)}"></span>${t.label}<span class="tcount">${t.count.toLocaleString()}</span><span class="tnote">${t.owner||''}</span>`;
  b.onclick=()=>{active=idx;renderTabs();renderTable();};host.appendChild(b);});}
let ROWH=42;const BUF=10;const SCROLLER=document.querySelector('.scroll');let stickyOffs=[];
function measureOffsets(){const hs=[...document.querySelectorAll('#hrow th')];let o=0;stickyOffs=[];
 hs.forEach(th=>{if(th.classList.contains('fix')){stickyOffs.push(o);o+=th.getBoundingClientRect().width;}else stickyOffs.push(null);});}
function applyOffsets(){const hs=[...document.querySelectorAll('#hrow th')];
 hs.forEach((th,i)=>{if(stickyOffs[i]!=null)th.style.left=stickyOffs[i]+'px';});
 document.querySelectorAll('#body tr').forEach(tr=>{[...tr.children].forEach((td,i)=>{
  if(td.classList.contains('fix')&&stickyOffs[i]!=null)td.style.left=stickyOffs[i]+'px';});});}
function buildHeader(){const cols=T().cols;const hrow=document.getElementById('hrow');hrow.innerHTML='';
 stickyOffs=[];                                   // clear stale offsets from the previous tab
 cols.forEach((c,i)=>{const th=document.createElement('th');
  th.innerHTML=(c.type==='img'?'':c.name)+'<span class="ar"></span>';
  th.className=(c.pin?'fix ':'')+(c.type==='img'?'imgc ':'')+cls(c);if(c.group!=='ID')th.style.background=col(T().code);
  th.onclick=()=>{if(ui.sortCol===i){ui.sortDir=-ui.sortDir;}else{ui.sortCol=i;ui.sortDir=(c.type==='text'||c.type==='img'?1:-1);}applyView();};
  hrow.appendChild(th);});
 computeView();paint();                            // render rows FIRST so columns reach final width
 requestAnimationFrame(()=>{measureOffsets();applyOffsets();updateArrows();
  const s=document.querySelector('#body tr:not(.spacer)');
  if(s){const h=s.getBoundingClientRect().height;if(h>1&&Math.abs(h-ROWH)>0.5){ROWH=h;paint();applyOffsets();}}});}
let ccyMI=-1,ccyAI=-1;
function rowCurrency(r){
 if(ccyMI>=0){const m=(''+(r[ccyMI]??'')).toLowerCase();if(m.includes('german'))return '€';if(m.includes('uk')||m.includes('gb'))return '£';}
 if(ccyAI>=0){const a=(''+(r[ccyAI]??'')).toLowerCase();if(a.includes('german')||/\bde\b/.test(a))return '€';if(a.includes('uk'))return '£';}
 return DATA.currency||'£';}
function makeCell(c,val,cur){const td=document.createElement('td');td.className=(c.pin?'fix ':'')+cls(c);
 if(c.type==='img'){td.className+=' imgc';td.innerHTML=val?`<img class="thumb" src="${val}" loading="lazy">`:'';}
 else if(c.key==='title'||c.name==='Product Title'){td.className+=' title';const t=val||'—';td.textContent=t;td.title=t;}
 else{let s;
  if(c.type==='money'&&val!=null&&val!==''&&!isNaN(Number(val))){const n=Number(val);
   s=(n<0?'-':'')+(cur||'')+Math.abs(n).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2});}
  else s=fmt(val,c.type);
  if(s===''||s===null||s===undefined){s='—';td.style.color='var(--muted)';}
  td.textContent=s;td.title=s;
  if(c.group!=='ID'&&c.type==='money'){const n=Number(val);if(!isNaN(n)&&val!==null&&val!=='')td.classList.add(n<0?'neg':'pos');}}
 return td;}
function paint(){const cols=T().cols,ROWS=view;const body=document.getElementById('body');const nCol=cols.length;
 if(ROWS.length===0){body.innerHTML=`<tr><td class="empty" colspan="${nCol}">No listings match your search or filter.</td></tr>`;return;}
 const st=SCROLLER.scrollTop,vh=SCROLLER.clientHeight;
 const start=Math.max(0,Math.floor(st/ROWH)-BUF),end=Math.min(ROWS.length,start+Math.ceil(vh/ROWH)+BUF*2);
 body.innerHTML='';
 const top=document.createElement('tr');top.className='spacer';top.innerHTML=`<td colspan="${nCol}" style="height:${start*ROWH}px"></td>`;body.appendChild(top);
 const frag=document.createDocumentFragment();
 for(let ri=start;ri<end;ri++){const r=ROWS[ri];const cur=rowCurrency(r);const tr=document.createElement('tr');
  cols.forEach((c,i)=>{const td=makeCell(c,r[i],cur);if(c.pin&&stickyOffs[i]!=null)td.style.left=stickyOffs[i]+'px';tr.appendChild(td);});frag.appendChild(tr);}
 body.appendChild(frag);const bot=document.createElement('tr');bot.className='spacer';
 bot.innerHTML=`<td colspan="${nCol}" style="height:${(ROWS.length-end)*ROWH}px"></td>`;body.appendChild(bot);}
function buildFilters(){const host=document.getElementById('filters');host.innerHTML='';
 T().filters.forEach(f=>{const ci=colIdx(c=>c.key===f.key);if(ci<0)return;
  const vals=[...new Set(T().rows.map(r=>(''+(r[ci]??'')).trim()).filter(Boolean))].sort();
  if(!vals.length)return;
  const sel=document.createElement('select');sel.className='inp';
  sel.innerHTML=`<option value="">All ${f.name}</option>`+vals.map(v=>`<option value="${v.replace(/"/g,'&quot;')}">${v}</option>`).join('');
  sel.onchange=()=>{ui.f[f.key]=sel.value;applyView();};host.appendChild(sel);});}
function renderTable(){
 ui.q='';ui.f={};ui.sortCol=null;ui.sortDir=-1;document.getElementById('q').value='';
 ccyMI=colIdx(c=>c.key==='market'||c.name==='Marketplace');ccyAI=colIdx(c=>c.key==='account');
 buildFilters();buildHeader();updateCount();}
let ticking=false;SCROLLER.addEventListener('scroll',()=>{if(!ticking){ticking=true;requestAnimationFrame(()=>{paint();ticking=false;});}});
document.getElementById('q').addEventListener('input',e=>{ui.q=e.target.value;applyView();});
document.getElementById('csv').onclick=()=>{const cols=T().cols;
 const head=cols.map(c=>c.name).join(',');
 const lines=view.map(r=>cols.map((c,i)=>{let v=r[i]??'';v=(''+v).replace(/"/g,'""');return /[",\n]/.test(v)?`"${v}"`:v;}).join(','));
 const blob=new Blob([head+'\n'+lines.join('\n')],{type:'text/csv'});const a=document.createElement('a');
 a.href=URL.createObjectURL(blob);a.download=T().code.toLowerCase()+'_listings.csv';a.click();};
document.getElementById('h1').innerHTML=DATA.title+' <span class="chip">'+TASKS.map(t=>t.code).join(' · ')+'</span>';
document.getElementById('sub').textContent=TASKS.length+' tasks · search, sort by clicking a column, filter by account';
renderTabs();renderTable();
</script></body></html>"""

html = PAGE.replace("__TITLE__", meta["title"]).replace("__DATA__", json.dumps(meta))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write(html)
print("wrote", OUT, f"| {len(html):,} bytes | md5 {hashlib.md5(html.encode()).hexdigest()[:10]}")
print("tabs:", [f"{t['code']}({t['count']})" for t in tasks])
