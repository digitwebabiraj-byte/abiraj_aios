"""
REQ-29-D01 — dashboard renderer.

Reads the SAME avm_payload.json the Excel is built from, so the two files cannot drift.
Reproduces the layout the requester drew on the source Dashboard sheet: 4 KPI tiles,
the Merge Status Overview, the Business/Technical summary and the ROI panel — plus a
searchable, sortable, filterable candidate table for the operator.

Self-contained: no external CSS, JS, fonts or images.
"""
import json, sys
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAYLOAD = HERE / "avm_payload.json"
OUT = (HERE.parent.parent / "evidence" / "final_outputs" /
       "REQ-29_amazon-asin-variation-merge" / "REQ-29-D01_asin_variation_merge.html")

CSS = """
:root{--bg:#f5f6f8;--card:#fff;--ink:#1a1d23;--muted:#6b7280;--line:#e3e6ea;
--brand:#1f3864;--ok:#0f7b3e;--okbg:#e7f5ec;--warn:#b45309;--warnbg:#fef3e2;
--bad:#b42318;--badbg:#fdeaea;--accent:#ff9900}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:1560px;margin:0 auto;padding:22px 26px 60px}
header{background:linear-gradient(100deg,#1f3864,#2d5090);color:#fff;border-radius:12px;
padding:20px 26px;margin-bottom:18px}
header h1{margin:0;font-size:21px;letter-spacing:.2px}
header p{margin:6px 0 0;opacity:.86;font-size:13px}
.banner{background:var(--warnbg);border:1px solid #f2d5a8;border-left:4px solid var(--warn);
color:#7c4a06;padding:12px 16px;border-radius:8px;margin-bottom:18px;font-size:13px}
.banner b{color:#5c3704}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin-bottom:18px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:11px;padding:16px 18px}
.kpi .lab{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);font-weight:600}
.kpi .val{font-size:31px;font-weight:680;margin-top:6px;line-height:1.1}
.kpi.ok .val{color:var(--ok)} .kpi.warn .val{color:var(--warn)} .kpi.accent .val{color:var(--brand)}
.grid{display:grid;grid-template-columns:minmax(300px,1fr) minmax(420px,1.9fr);gap:14px;margin-bottom:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:11px;padding:16px 18px}
.card h2{margin:0 0 12px;font-size:12px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted)}
.card table{width:100%;border-collapse:collapse}
.card td{padding:7px 0;border-bottom:1px solid #f0f2f4;vertical-align:top}
.card tr:last-child td{border-bottom:0}
.card td:first-child{color:var(--muted);padding-right:14px;white-space:nowrap}
.card td.n{text-align:right;font-variant-numeric:tabular-nums;font-weight:650;white-space:nowrap}
ul.roi{margin:0;padding-left:18px} ul.roi li{margin:5px 0}
.toolbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:12px}
input[type=search]{flex:1;min-width:240px;padding:9px 13px;border:1px solid var(--line);
border-radius:8px;font-size:14px;background:var(--card)}
.chip{padding:7px 14px;border:1px solid var(--line);background:var(--card);border-radius:20px;
cursor:pointer;font-size:13px;font-weight:600;color:var(--muted)}
.chip.on{background:var(--brand);color:#fff;border-color:var(--brand)}
.count{color:var(--muted);font-size:13px}
.tablecard{background:var(--card);border:1px solid var(--line);border-radius:11px;overflow:hidden}
.scroll{overflow-x:auto}
table.data{width:100%;border-collapse:collapse;font-size:13px}
table.data th{background:#f0f2f5;text-align:left;padding:10px 11px;font-size:11px;
letter-spacing:.05em;text-transform:uppercase;color:#4b5563;border-bottom:1px solid var(--line);
cursor:pointer;white-space:nowrap;position:sticky;top:0}
table.data th:hover{background:#e6e9ee}
table.data td{padding:10px 11px;border-bottom:1px solid #f2f4f6;vertical-align:top}
table.data tr.blocked{background:#fffaf8}
table.data tr:hover{background:#f7f9fc}
.pill{display:inline-block;padding:2px 9px;border-radius:11px;font-size:11.5px;font-weight:650;white-space:nowrap}
.p-ok{background:var(--okbg);color:var(--ok)} .p-warn{background:var(--warnbg);color:var(--warn)}
.p-bad{background:var(--badbg);color:var(--bad)}
.mono{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:12.5px}
a.asin{color:var(--brand);text-decoration:none;border-bottom:1px dotted #9aa8bd}
a.asin:hover{border-bottom-style:solid}
.sub{color:var(--muted);font-size:12px;display:block;margin-top:2px}
.blank{display:inline-block;min-width:52px;border-bottom:1px dashed #c7ccd4;color:#c7ccd4}
footer{margin-top:22px;color:var(--muted);font-size:12px;line-height:1.7}
@media(max-width:1000px){.grid{grid-template-columns:1fr}}
"""

JS = """
const rows=[...document.querySelectorAll('#tb tr')];
let filter='all';
function apply(){
  const q=document.getElementById('q').value.toLowerCase();
  let n=0;
  rows.forEach(r=>{
    const okF = filter==='all'
      || (filter==='merge' && r.dataset.blocked==='0')
      || (filter==='review' && r.dataset.blocked==='1')
      || (filter==='dup' && r.dataset.dup==='Yes')
      || (filter==='oos' && r.dataset.stock==='Out of Stock');
    const okQ = !q || r.textContent.toLowerCase().includes(q);
    const show = okF && okQ;
    r.style.display = show?'':'none';
    if(show) n++;
  });
  document.getElementById('cnt').textContent = n+' of '+rows.length+' candidates shown';
}
document.getElementById('q').addEventListener('input',apply);
document.querySelectorAll('.chip').forEach(c=>c.addEventListener('click',()=>{
  document.querySelectorAll('.chip').forEach(x=>x.classList.remove('on'));
  c.classList.add('on'); filter=c.dataset.f; apply();
}));
document.querySelectorAll('table.data th').forEach((th,i)=>{
  let asc=true;
  th.addEventListener('click',()=>{
    const tb=document.getElementById('tb');
    [...tb.querySelectorAll('tr')].sort((a,b)=>{
      const x=a.cells[i].innerText.trim(), y=b.cells[i].innerText.trim();
      const nx=parseFloat(x), ny=parseFloat(y);
      const c=(!isNaN(nx)&&!isNaN(ny))?nx-ny:x.localeCompare(y);
      return asc?c:-c;
    }).forEach(r=>tb.appendChild(r));
    asc=!asc; apply();
  });
});
apply();
"""


def render():
    p = json.loads(PAYLOAD.read_text())
    k, so, cov, ru = p["kpi"], p["status_overview"], p["coverage"], p["rules"]
    e = escape

    trs = []
    for r in p["rows"]:
        stock_pill = ('<span class="pill p-ok">In Stock</span>' if r["stock_status"] == "In Stock"
                      else '<span class="pill p-bad">Out of Stock</span>')
        dup_pill = ('<span class="pill p-bad">Yes</span>' if r["duplicate_warning"] == "Yes"
                    else '<span class="pill p-ok">No</span>')
        reason_pill = ('<span class="pill p-warn">No reviews</span>'
                       if r["merge_reason"].startswith("No reviews")
                       else '<span class="pill p-warn">Low rating</span>')
        child_asin, child_sku = r["child_asin_sku"].split(" / ", 1)
        trs.append(f"""<tr data-blocked="{1 if r['_blocked'] else 0}"
 data-dup="{e(r['duplicate_warning'])}" data-stock="{e(r['stock_status'])}">
<td class="mono">{e(r['base_sku'])}</td>
<td><a class="asin mono" href="https://www.amazon.co.uk/dp/{e(r['parent_asin'])}"
 target="_blank" rel="noopener">{e(r['parent_asin'])}</a>
<span class="sub">{e(r['parent_title'])}</span></td>
<td><b>{e(r['parent_rating_reviews'])}</b></td>
<td><a class="asin mono" href="https://www.amazon.co.uk/dp/{e(child_asin)}"
 target="_blank" rel="noopener">{e(child_asin)}</a>
<span class="sub mono">{e(child_sku)}</span></td>
<td>{e(r['child_colour_rating'])}<span class="sub">{r['child_reviews']} review(s)</span></td>
<td>{reason_pill}</td>
<td>{stock_pill}</td>
<td>{dup_pill}</td>
<td><span class="blank">&nbsp;</span></td>
<td><span class="blank">&nbsp;</span></td></tr>""")

    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ASIN Rating Analysis &amp; Variation Merging — REQ-29-D01</title>
<style>{CSS}</style></head><body><div class="wrap">

<header>
<h1>ASIN Rating Analysis &amp; Variation Merging</h1>
<p>Amazon {e(p['scope']['site'])} · {e(', '.join(p['scope']['accounts']))} · generated {e(p['generated_at'])}
· REQ-29-D01 · PRJ-2026-025</p>
</header>

<div class="banner">
<b>PILOT / DRAFT — provisional rules pending Prasath's confirmation.</b>
Ratings collected for <b>{cov['asins_rating_collected']}</b> ASINs across
<b>{cov['families_examined']}</b> variation families
({cov['asins_rating_failed']} could not be collected and are excluded, never assumed).
The full Amazon UK catalogue is 16,963 ASINs / 1,761 multi-child families.
Star ratings and review counts exist in <b>neither company database</b> — they are collected from the
public Amazon product page. Every threshold below is a documented default, not agreed business logic.
<b>No merge executes without operator approval.</b>
</div>

<div class="kpis">
<div class="kpi accent"><div class="lab">Total ASINs</div><div class="val">{k['total_asins']:,}</div></div>
<div class="kpi warn"><div class="lab">No-Review / Low-Rated</div><div class="val">{k['no_review_or_low_rated']:,}</div></div>
<div class="kpi ok"><div class="lab">Recommend Merge</div><div class="val">{k['recommend_merge']:,}</div></div>
<div class="kpi warn"><div class="lab">Needs Review</div><div class="val">{k['needs_review']:,}</div></div>
</div>

<div class="grid">
<div class="card"><h2>Merge Status Overview</h2><table>
<tr><td>Recommend merge</td><td class="n">{so['recommend_merge']:,}</td></tr>
<tr><td>Needs review</td><td class="n">{so['needs_review']:,}</td></tr>
<tr><td>Duplicate warnings</td><td class="n">{so['duplicate_warnings']:,}</td></tr>
<tr><td>Out of stock</td><td class="n">{so['out_of_stock']:,}</td></tr>
<tr><td>Families examined</td><td class="n">{cov['families_examined']:,}</td></tr>
<tr><td>Families with no qualifying parent</td><td class="n">{cov['families_no_qualifying_parent']:,}</td></tr>
</table></div>

<div class="card"><h2>Business / Technical Summary</h2><table>
<tr><td>Automation Objective</td><td>Identify low/no-rating ASINs and recommend stronger variation parents.</td></tr>
<tr><td>Approval Control</td><td><b>No merge executes without PH/operator approval.</b></td></tr>
<tr><td>Key Validation</td><td>Duplicate variation attributes are checked before merging
({e(ru['duplicate_match'])} matching on {e(', '.join(ru['duplicate_attributes']))}).</td></tr>
<tr><td>Execution</td><td>Approved merges use the required Amazon Seller Central flat-file process —
a manual step outside this system.</td></tr>
<tr><td>Candidate rule <i>(provisional)</i></td><td>reviews &le; {ru['no_reviews_at_or_below']}
or rating &lt; {ru['low_rating_below']}.</td></tr>
<tr><td>Parent rule <i>(provisional)</i></td><td>&ge; {ru['parent_min_reviews']} reviews and rating
&ge; {ru['parent_min_rating']}; strongest = most reviews, then highest rating.</td></tr>
<tr><td>Out of stock <i>(provisional)</i></td><td>{e(ru['out_of_stock'])}</td></tr>
<tr><td>Open Dependency</td><td>PH team input required for the flat-file template, a sample file
and the variation field list.</td></tr>
</table></div>
</div>

<div class="card" style="margin-bottom:18px"><h2>Expected Business Value / ROI</h2>
<ul class="roi">
<li>Reduce manual ASIN rating and variation analysis time.</li>
<li>Consolidate customer reviews across eligible variations.</li>
<li>Improve listing credibility where a stronger review history is shared.</li>
<li>Reduce manual errors through systematic parent selection and duplicate checks.</li>
<li>Create measurable automation outputs and execution logs for follow-up.</li>
</ul></div>

<div class="toolbar">
<input id="q" type="search" placeholder="Search SKU, ASIN, colour, reason…">
<button class="chip on" data-f="all">All</button>
<button class="chip" data-f="merge">Recommend merge</button>
<button class="chip" data-f="review">Needs review</button>
<button class="chip" data-f="dup">Duplicate warning</button>
<button class="chip" data-f="oos">Out of stock</button>
<span class="count" id="cnt"></span>
</div>

<div class="tablecard"><div class="scroll"><table class="data">
<thead><tr>
<th>Base SKU</th><th>Parent ASIN</th><th>Parent rating / reviews</th>
<th>Child ASIN / SKU</th><th>Child colour / rating</th><th>Merge reason</th>
<th>Stock</th><th>Duplicate</th><th>Approved (Y/N)</th><th>Operator notes</th>
</tr></thead><tbody id="tb">
{''.join(trs) if trs else '<tr><td colspan="10" style="padding:26px;text-align:center;color:#6b7280">No merge candidates found under the current provisional rules.</td></tr>'}
</tbody></table></div></div>

<footer>
<b>Approved (Y/N)</b> and <b>Operator notes</b> are deliberately blank — they are the operator's decision
and are never pre-filled. Print or export this page, or use the Excel workbook, to record approvals.<br>
Catalogue data: <span class="mono">listings.amazon_listings</span> (live, read-only).
Ratings: public Amazon UK product pages — no database source exists for them (owner-confirmed 2026-08-18).<br>
PRJ-2026-025 · REQ-29-D01 · user Prasath · assigned by HR · developer Abiraj.
</footer>

</div><script>{JS}</script></body></html>"""

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"html   -> {OUT}  ({len(html):,} chars, {len(p['rows'])} rows)", flush=True)


if __name__ == "__main__":
    sys.exit(render())
