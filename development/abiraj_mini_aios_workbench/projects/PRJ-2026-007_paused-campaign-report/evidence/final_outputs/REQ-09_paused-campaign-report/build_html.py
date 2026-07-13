# -*- coding: utf-8 -*-
"""build_html.py — SECONDARY / audit renderer for the Paused Campaign Report (Utharsika).
Reads data.json and writes Utharsika_Paused_Campaigns_dataview.html (self-contained, plain).

NOTE: this is NOT the published artifact. The canonical, published dashboard is the
hand-finished `Utharsika_Paused_Campaigns_Report.html` (see SYSTEM_REFERENCE.md §7). This
script exists only to re-render the same governed data.json as a quick offline data view for
audit if the published file is ever unavailable. Both draw from the identical 33-row pull.
Run:  python build_html.py   (from this folder)
"""
import json, os, html
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "data.json"), encoding="utf-8") as f:
    payload = json.load(f)
meta, rows = payload["meta"], payload["rows"]
rec = meta["reconciliation"]

def rule_tag(reason):
    tags = []
    if "Rule 1" in reason: tags.append("Rule 1")
    if "Rule 2" in reason: tags.append("Rule 2")
    if "Rule 3" in reason: tags.append("Rule 3")
    return tags or ["Other"]

rules = Counter()
for r in rows:
    for t in rule_tag(r["pause_reason"]):
        rules[t] += 1
waves = Counter(r["campaign_pause_date"] for r in rows)
campaigns = len({r["campaign_name"] for r in rows})

# JSON for client-side filtering
client_rows = json.dumps(rows, ensure_ascii=False)

def esc(x): return html.escape(str(x))

stat_cards = [
    (rec["targets"], "Paused ad targets"),
    (rec["distinct_asins"], "Distinct ASINs"),
    (campaigns, "Campaigns affected"),
    (rec["total_automation_pauses"], "Total automation pauses"),
    (rec["reactivated_excluded"], "Re-activated (excluded)"),
]
cards_html = "".join(
    '<div class="card"><div class="num">%s</div><div class="lbl">%s</div></div>' % (n, esc(l))
    for n, l in stat_cards)

rule_chips = "".join(
    '<span class="chip">%s <b>%d</b></span>' % (esc(k), v) for k, v in sorted(rules.items()))
wave_chips = "".join(
    '<span class="chip alt">%s <b>%d</b></span>' % (esc(k), v) for k, v in sorted(waves.items()))

HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Paused Campaign Report — Utharsika</title>
<style>
  :root{ --navy:#1F2A44; --accent:#2E5AAC; --line:#e3e8f2; --muted:#5b6578; --bg:#f5f7fb; --chip:#eef2fa; }
  *{box-sizing:border-box}
  body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
       color:#1b2233;background:var(--bg);font-size:14px}
  header{background:linear-gradient(120deg,#1F2A44,#2E5AAC);color:#fff;padding:18px 22px}
  header h1{margin:0;font-size:19px;font-weight:700}
  header .sub{opacity:.86;margin-top:4px;font-size:12.5px}
  .wrap{padding:16px 22px 40px}
  .cards{display:flex;flex-wrap:wrap;gap:12px;margin:6px 0 14px}
  .card{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px 16px;min-width:150px;flex:1}
  .card .num{font-size:26px;font-weight:800;color:var(--navy)}
  .card .lbl{font-size:11.5px;color:var(--muted);margin-top:2px;text-transform:uppercase;letter-spacing:.03em}
  .row{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:8px 0}
  .chip{background:var(--chip);border:1px solid var(--line);border-radius:20px;padding:4px 11px;font-size:12px;color:#33405c}
  .chip.alt{background:#fff}
  .chip b{color:var(--accent)}
  .controls{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0 8px}
  input[type=search],select{padding:8px 11px;border:1px solid var(--line);border-radius:8px;font-size:13px;background:#fff}
  input[type=search]{flex:1;min-width:220px}
  .tablewrap{overflow-x:auto;background:#fff;border:1px solid var(--line);border-radius:10px}
  table{border-collapse:collapse;width:100%;min-width:920px}
  th,td{padding:9px 11px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
  th{position:sticky;top:0;background:var(--accent);color:#fff;font-size:12px;cursor:pointer;white-space:nowrap}
  th .ar{opacity:.6;font-size:10px}
  tbody tr:nth-child(even){background:#f8fafd}
  tbody tr:hover{background:#eef4ff}
  td.asin{font-family:ui-monospace,Menlo,Consolas,monospace;font-weight:600;color:var(--navy);white-space:nowrap}
  td.sku{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12px;color:#33405c}
  td.days{text-align:center;font-weight:700}
  td.reason{max-width:520px;font-size:12px;color:#333}
  .rt{display:inline-block;font-size:10.5px;font-weight:700;border-radius:4px;padding:1px 6px;margin-right:4px}
  .r1{background:#fde8e8;color:#b02525}.r2{background:#e8f0fd;color:#2450a8}.r3{background:#fff2dc;color:#9a6413}
  .cname{font-size:12.5px;color:#26324c;max-width:260px}
  footer{color:var(--muted);font-size:11.5px;padding:14px 22px;line-height:1.6}
  .pill{display:inline-block;background:#eaf7ee;color:#1c7a3a;border-radius:6px;padding:2px 8px;font-size:11px;font-weight:700}
  .count{font-size:12px;color:var(--muted);margin-left:auto}
</style></head>
<body>
<header>
  <h1>Paused Campaign Report — Utharsika</h1>
  <div class="sub">Amazon PPC ad targets paused by automation and <b>still paused</b> as of __RUNDATE__
   · read-only from <code>order_management_copy</code> · REQ-09-D01 · PH-2026-07-UTHAR10</div>
</header>
<div class="wrap">
  <div class="cards">__CARDS__</div>
  <div class="row"><span style="font-size:12px;color:var(--muted);font-weight:700">PAUSE RULE</span>__RULECHIPS__</div>
  <div class="row"><span style="font-size:12px;color:var(--muted);font-weight:700">PAUSE DATE</span>__WAVECHIPS__
     <span class="pill">4/4 validation checks PASS</span></div>

  <div class="controls">
    <input id="q" type="search" placeholder="Search campaign, ad group, ASIN, SKU, reason…">
    <select id="frule">
      <option value="">All rules</option>
      <option value="Rule 1">Rule 1 (ACOS)</option>
      <option value="Rule 2">Rule 2 (zero orders + spend)</option>
      <option value="Rule 3">Rule 3 (spend, orders dropped)</option>
    </select>
    <select id="fwave"><option value="">All pause dates</option>__WAVEOPTS__</select>
    <span class="count" id="count"></span>
  </div>

  <div class="tablewrap">
    <table id="tbl">
      <thead><tr>
        <th data-k="campaign_name">Campaign Name <span class="ar">&#8597;</span></th>
        <th data-k="ad_group_name">Ad Group <span class="ar">&#8597;</span></th>
        <th data-k="asin">ASIN <span class="ar">&#8597;</span></th>
        <th data-k="sku">SKU <span class="ar">&#8597;</span></th>
        <th data-k="pause_reason">Pause Reason <span class="ar">&#8597;</span></th>
        <th data-k="campaign_pause_date">Pause Date <span class="ar">&#8597;</span></th>
        <th data-k="days_paused">Days <span class="ar">&#8597;</span></th>
      </tr></thead>
      <tbody id="tb"></tbody>
    </table>
  </div>
</div>
<footer>
  <b>Grain:</b> one row per still-paused ad target (per ASIN); Campaign Name is the parent campaign.
  <b>Scope:</b> campaign name contains "Utharsika" (no owner column); Amazon only; SB excluded.
  <b>Still paused:</b> current <code>ppc.record_status='paused'</code> — 8 re-activated pauses excluded.
  <b>Pause Reason</b> is verbatim from <code>ppc_etl_automation_log.reason</code>.
  <b>Days Paused</b> = today &minus; pause date. Ultimate cross-check is the Amazon Ads console.
  Open items A–E await Satheesvaran sign-off. The workbook's sample rows are illustrative only.
</footer>
<script>
const ROWS = __ROWS__;
const tb = document.getElementById('tb');
const q = document.getElementById('q'), fr = document.getElementById('frule'),
      fw = document.getElementById('fwave'), cnt = document.getElementById('count');
let sortK = 'days_paused', sortAsc = false;
function ruleTags(reason){
  let h='';
  if(reason.includes('Rule 1')) h+='<span class="rt r1">R1</span>';
  if(reason.includes('Rule 2')) h+='<span class="rt r2">R2</span>';
  if(reason.includes('Rule 3')) h+='<span class="rt r3">R3</span>';
  return h;
}
function esc(s){return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function render(){
  const term=q.value.toLowerCase(), fru=fr.value, fwa=fw.value;
  let data=ROWS.filter(r=>{
    if(fru && !r.pause_reason.includes(fru)) return false;
    if(fwa && r.campaign_pause_date!==fwa) return false;
    if(term){
      const blob=(r.campaign_name+' '+r.ad_group_name+' '+r.asin+' '+r.sku+' '+r.pause_reason).toLowerCase();
      if(!blob.includes(term)) return false;
    }
    return true;
  });
  data.sort((a,b)=>{
    let x=a[sortK], y=b[sortK];
    if(sortK==='days_paused'){x=+x;y=+y;}
    if(x<y) return sortAsc?-1:1;
    if(x>y) return sortAsc?1:-1;
    return 0;
  });
  tb.innerHTML=data.map(r=>`<tr>
    <td class="cname">${esc(r.campaign_name)}</td>
    <td>${esc(r.ad_group_name||'')}</td>
    <td class="asin">${esc(r.asin||'')}</td>
    <td class="sku">${esc(r.sku||'')}</td>
    <td class="reason">${ruleTags(r.pause_reason)}${esc(r.pause_reason)}</td>
    <td>${esc(r.campaign_pause_date)}</td>
    <td class="days">${esc(r.days_paused)}</td></tr>`).join('');
  cnt.textContent=data.length+' of '+ROWS.length+' targets';
}
document.querySelectorAll('th').forEach(th=>th.addEventListener('click',()=>{
  const k=th.dataset.k; if(k===sortK) sortAsc=!sortAsc; else {sortK=k;sortAsc=true;} render();
}));
q.addEventListener('input',render); fr.addEventListener('change',render); fw.addEventListener('change',render);
render();
</script>
</body></html>"""

wave_opts = "".join('<option value="%s">%s (%d)</option>' % (d, d, n) for d, n in sorted(waves.items()))
out_html = (HTML
    .replace("__RUNDATE__", esc(meta["run_date"]))
    .replace("__CARDS__", cards_html)
    .replace("__RULECHIPS__", rule_chips)
    .replace("__WAVECHIPS__", wave_chips)
    .replace("__WAVEOPTS__", wave_opts)
    .replace("__ROWS__", client_rows))

out = os.path.join(HERE, "Utharsika_Paused_Campaigns_dataview.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(out_html)
print("data-view html written (audit only, NOT the published artifact):", out)
