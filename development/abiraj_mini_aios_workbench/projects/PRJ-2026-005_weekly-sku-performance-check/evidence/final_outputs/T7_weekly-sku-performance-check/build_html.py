#!/usr/bin/env python3
"""
Table 7 - Weekly SKU Performance Check | Thuwaraga (PH-2026-07-THUW07)
Renders the governed dataset (data.json) into a standalone, self-contained
interactive HTML dashboard.

Structure follows the approved Table 7 template (sheet "PH-2026-07-THUW07"):
  Purple  SKU SUMMARY row  (group = resolved base SKU)  ->  followed by its
  Blue    ASIN detail rows (one per listing / ref_id)

Colour semantics (from the template legend):
  Purple = SKU summary | Blue = ASIN detail | Green = performing (orders>0)
  Red = NOT performing (0 orders this week) | Orange = partial family (0<X<Y)

Data rules are LOCKED in HANDOFF.md / SYSTEM_REFERENCE.md. This script does no
DB access and invents no figures - it only shapes and renders data.json.

Usage:  python build_html.py
"""
import json, os, html, collections

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data.json")
OUT  = os.path.join(HERE, "Table7_Weekly_SKU_Performance_Thuwaraga.html")

PLATFORM_KEY = {"AMAZON": "amazon", "EBAY": "ebay", "B&Q": "bq"}


def load():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


# Pack-size / multipack suffixes appended to a base product SKU (e.g. LDMG80B224 -> LDMG80B2243PK).
# A suffix is only stripped when the resulting base is ITSELF a real SKU in Thuwaraga's universe,
# so nothing is over-merged and no product relationship is invented (governance: anchored + reversible).
_PACK_SUFFIXES = (
    ["APK"]
    + [f"{n}PK" for n in range(1, 25)]      # 1PK .. 24PK
    + [f"{n}PCK" for n in range(1, 25)]     # 1PCK .. 24PCK
    + [f"PCK{n}" for n in range(1, 25)]     # PCK1 .. PCK24
    + [f"PACK{n}" for n in range(1, 25)] + [f"{n}PACK" for n in range(1, 25)]
)
# shortest suffix first => remove the smallest token that yields a real base SKU (most conservative)
_PACK_SUFFIXES.sort(key=len)


def product_family(sku, uni_upper):
    """Resolve a listing SKU to its product family by stripping a pack suffix,
    but only when the stripped base is a real SKU in the universe."""
    su = sku.upper()
    for suf in _PACK_SUFFIXES:
        if su.endswith(suf) and len(su) > len(suf):
            base = sku[: len(sku) - len(suf)]
            if base and base.upper() in uni_upper:
                return base
    return sku


def build_groups(data):
    """Group listing rows into product families (base SKU + its pack variants) ->
    purple summary + blue ASIN/listing rows, matching the Table 7 template."""
    names = data["names"]
    uni_upper = {r["s"].upper() for r in data["rows"]}

    groups = collections.OrderedDict()
    for r in data["rows"]:
        fam = product_family(r["s"], uni_upper)
        groups.setdefault(fam, []).append(r)

    out = []
    for base, listings in groups.items():
        # representative product name: prefer the base SKU's own title, else first non-empty
        pname = names.get(base, "")
        if not pname:
            for r in listings:
                pname = names.get(r["s"], "") or pname
                if pname:
                    break
        y = len(listings)
        x = sum(1 for r in listings if r["o"] > 0)
        plat = {"amazon": 0, "ebay": 0, "bq": 0}
        for r in listings:
            plat[PLATFORM_KEY[r["p"]]] += r["o"]
        total = sum(plat.values())
        distinct_skus = {r["s"] for r in listings}
        merged_flag = len(distinct_skus) > 1   # family rolls up >1 distinct SKU (verify)

        if y > 0 and x == y:
            perf, state = "All performing ✅", "green"
        elif x == 0:
            perf, state = f"0/{y} performing \U0001f534", "red"
        else:
            perf, state = f"{x}/{y} performing ⚠️", "orange"
        action = "See ASIN rows below ↓" if x < y else "—"

        blue = []
        for r in sorted(listings, key=lambda z: (-z["o"], z["p"])):
            pk = PLATFORM_KEY[r["p"]]
            row_orders = {"amazon": 0, "ebay": 0, "bq": 0}
            row_orders[pk] = r["o"]
            performing = r["o"] > 0
            blue.append({
                "sku": r["s"],
                "ref": r["r"] or ("B&Q SKU" if r["p"] == "B&Q" else "—"),
                "name": names.get(r["s"], "") or pname or "—",
                "platform": r["p"],
                "account": r["a"] or "—",
                "amazon": row_orders["amazon"], "ebay": row_orders["ebay"],
                "bq": row_orders["bq"], "total": r["o"],
                "performing": performing,
                "action": "—" if performing else "Investigate & fix listing",
                "variant": r["s"] != base,   # a pack-size / variant SKU under this family
            })

        out.append({
            "base": base, "name": pname or "—", "x": x, "y": y,
            "skus": len(distinct_skus),
            "amazon": plat["amazon"], "ebay": plat["ebay"], "bq": plat["bq"],
            "total": total, "perf": perf, "state": state, "action": action,
            "merged": merged_flag, "active": total > 0, "rows": blue,
        })
    # active families first, then by total orders desc, then base sku
    out.sort(key=lambda g: (not g["active"], -g["total"], g["base"]))
    return out


def esc(s):
    return html.escape(str(s), quote=True)


def render(data, groups):
    m = data["meta"]
    n_families = len(groups)
    n_listings = sum(g["y"] for g in groups)
    n_perf = sum(sum(1 for r in g["rows"] if r["performing"]) for g in groups)
    n_zero = n_listings - n_perf
    tot_orders = sum(g["total"] for g in groups)
    amz = sum(g["amazon"] for g in groups)
    eby = sum(g["ebay"] for g in groups)
    bq = sum(g["bq"] for g in groups)
    active_fams = sum(1 for g in groups if g["active"])
    dead_fams = n_families - active_fams
    need_fix = [g for g in groups if g["x"] < g["y"]]

    # payload for client-side filtering/search
    payload = json.dumps(groups, ensure_ascii=False)

    need_fix_count = len(need_fix)
    n_merged = sum(1 for g in groups if g["merged"])
    perf_pct = round(100 * n_perf / n_listings) if n_listings else 0
    tot = tot_orders or 1
    aw = round(100 * amz / tot)
    ew = round(100 * eby / tot)
    bw = max(0, 100 - aw - ew)

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Table 7 - Weekly SKU Performance Check - Thuwaraga</title>
<style>
:root{{
--bg:#dfe4ee;--panel:#ffffff;--panel2:#eaeef6;--ink:#0a0f1c;--ink2:#26324a;
--mut:#4a586f;--faint:#74819a;--line:#c4cddd;--line2:#d7deec;
--brand:#4338ca;--brand-ink:#3730a3;
--purple:#6d28d9;--purple-bg:#e6dafb;--purple-line:#c4abf1;
--blue:#1d4ed8;--blue-bg:#d8e6fe;
--green:#047857;--green-bg:#c3efda;--red:#dc2626;--red-bg:#fbd7d7;
--orange:#b45309;--orange-bg:#fae2ba;
--amazon:#dd7a09;--ebay:#2563eb;--bq:#0d9488;
--shadow:0 1px 2px rgba(15,23,42,.07),0 12px 28px -14px rgba(15,23,42,.28);
--radius:14px;}}
*{{box-sizing:border-box}}
html{{-webkit-text-size-adjust:100%}}
body{{margin:0;font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
background:var(--bg);color:var(--ink);font-size:13px;line-height:1.45;
-webkit-font-smoothing:antialiased;color-scheme:light;}}
.wrap{{max-width:none;width:100%;margin:0;padding:24px clamp(16px,3vw,44px) 72px;}}
code{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.92em;
background:var(--panel2);padding:1px 5px;border-radius:5px;border:1px solid var(--line2);}}
/* ---- header ---- */
.hero{{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);
box-shadow:var(--shadow);padding:20px 22px;position:relative;overflow:hidden;}}
.hero::before{{content:"";position:absolute;inset:0 0 auto 0;height:4px;
background:linear-gradient(90deg,var(--amazon),var(--ebay) 55%,var(--bq));}}
.hero-top{{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;align-items:flex-start;}}
.eyebrow{{font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;
color:var(--brand-ink);margin-bottom:4px;}}
h1{{margin:0 0 8px;font-size:23px;font-weight:800;letter-spacing:-.02em;}}
.chips{{display:flex;flex-wrap:wrap;gap:7px;margin-top:2px;}}
.chip{{display:inline-flex;align-items:center;gap:6px;background:var(--panel2);
border:1px solid var(--line);border-radius:999px;padding:4px 11px;font-size:11.5px;
font-weight:600;color:var(--ink2);}}
.chip b{{color:var(--ink)}}
.chip i{{width:7px;height:7px;border-radius:50%;display:inline-block}}
.win{{text-align:right;min-width:210px;}}
.win .wlabel{{font-size:10.5px;text-transform:uppercase;letter-spacing:.08em;color:var(--faint);}}
.win .wval{{font-size:15px;font-weight:800;letter-spacing:-.01em;margin-top:2px;white-space:nowrap;}}
.win .wsub{{font-size:11px;color:var(--mut);margin-top:5px;line-height:1.4;max-width:260px;margin-left:auto;}}
/* ---- KPIs ---- */
.kpis{{display:grid;grid-template-columns:1.5fr repeat(4,1fr);gap:12px;margin:16px 0;}}
@media(max-width:960px){{.kpis{{grid-template-columns:repeat(2,1fr)}}.hero-top{{flex-direction:column}}.win{{text-align:left}}.win .wsub{{margin-left:0}}}}
@media(max-width:560px){{.kpis{{grid-template-columns:1fr}}}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);
box-shadow:var(--shadow);padding:15px 16px;display:flex;flex-direction:column;gap:2px;}}
.card:not(.hero-card){{justify-content:center}}
.card .cl{{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.05em;color:var(--mut);}}
.card .cv{{font-size:27px;font-weight:800;letter-spacing:-.02em;line-height:1.1;font-variant-numeric:tabular-nums;}}
.card .cs{{font-size:11.5px;color:var(--faint);margin-top:2px;}}
.card.ok .cv{{color:var(--green)}}.card.warn .cv{{color:var(--orange)}}.card.bad .cv{{color:var(--red)}}
.card.hero-card{{gap:8px}}
.bar{{display:flex;height:12px;border-radius:6px;overflow:hidden;background:var(--line2);margin-top:4px;}}
.bar span{{display:block;height:100%}}
.barleg{{display:flex;flex-wrap:wrap;gap:12px;margin-top:8px;font-size:11.5px;color:var(--ink2);font-weight:600;}}
.barleg span{{display:inline-flex;align-items:center;gap:6px}}
.barleg i{{width:9px;height:9px;border-radius:3px;display:inline-block}}
.barleg b{{font-variant-numeric:tabular-nums}}
.prog{{height:6px;border-radius:99px;background:var(--line2);overflow:hidden;margin-top:8px}}
.prog span{{display:block;height:100%;background:var(--green);border-radius:99px}}
/* ---- toolbar ---- */
.toolbar{{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:18px 0 10px;}}
.search{{flex:1;min-width:220px;position:relative;}}
.search svg{{position:absolute;left:11px;top:50%;transform:translateY(-50%);color:var(--faint);}}
.search input{{width:100%;padding:9px 12px 9px 34px;border:1px solid var(--line);border-radius:10px;
font-size:13px;background:var(--panel);color:var(--ink);outline:none;transition:.15s;}}
.search input:focus{{border-color:var(--brand);box-shadow:0 0 0 3px rgba(79,70,229,.15);}}
.seg{{display:inline-flex;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:3px;gap:2px;}}
.seg button{{border:0;background:transparent;padding:7px 13px;cursor:pointer;font-size:12px;
font-weight:600;color:var(--mut);border-radius:7px;transition:.15s;white-space:nowrap;}}
.seg button:hover{{color:var(--ink)}}
.seg button.on{{background:var(--brand);color:#fff;box-shadow:0 1px 3px rgba(79,70,229,.4);}}
.legend{{font-size:11.5px;color:var(--mut);margin:2px 2px 12px;display:flex;flex-wrap:wrap;gap:8px 18px;align-items:center;}}
.legend span{{display:inline-flex;align-items:center;gap:6px}}
.dot{{width:10px;height:10px;border-radius:3px;display:inline-block}}
.count{{color:var(--mut);font-size:12px;margin:0 2px 10px;font-weight:500;}}
.count b{{color:var(--ink)}}
/* ---- table ---- */
.tablewrap{{overflow:auto;background:var(--panel);border:1px solid var(--line);
border-radius:var(--radius);box-shadow:var(--shadow);
max-height:max(78vh,640px);}}
table{{border-collapse:separate;border-spacing:0;width:100%;min-width:980px;}}
th,td{{padding:8px 9px;text-align:left;white-space:nowrap;border-bottom:1px solid var(--line2);
vertical-align:middle;}}
thead th{{position:sticky;top:0;background:var(--panel2);color:var(--ink2);font-size:10.5px;
font-weight:700;text-transform:uppercase;letter-spacing:.04em;z-index:3;
border-bottom:2px solid var(--line);}}
thead th:first-child{{padding-left:30px;}}
th.num,td.num{{text-align:right;font-variant-numeric:tabular-nums;}}
td.name{{white-space:normal;max-width:330px;color:var(--ink2);line-height:1.35;}}
tbody tr:last-child td{{border-bottom:0}}
/* product (summary) row */
tr.sku{{cursor:pointer;background:var(--purple-bg);transition:background .12s;}}
tr.sku:hover{{filter:brightness(.99)}}
tr.sku td{{font-weight:700;border-top:1px solid var(--purple-line);border-bottom:1px solid var(--purple-line);}}
tr.sku td:first-child{{position:relative;padding-left:30px;}}
tr.sku td:first-child::before{{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--purple)}}
tr.sku.st-green td:first-child::before{{background:var(--green)}}
tr.sku.st-red td:first-child::before{{background:var(--red)}}
tr.sku.st-orange td:first-child::before{{background:var(--orange)}}
.caret{{position:absolute;left:11px;top:50%;transform:translateY(-50%);color:var(--mut);
font-size:9px;transition:transform .15s;display:inline-block;width:10px;}}
tr.sku.op .caret{{transform:translateY(-50%) rotate(90deg)}}
/* listing (detail) row */
tr.asin td{{color:var(--ink2)}}
tr.asin td:first-child{{padding-left:30px;position:relative;font-weight:600;}}
tr.asin td:first-child::before{{content:"";position:absolute;left:14px;top:0;bottom:0;width:2px;background:var(--line)}}
tr.asin:hover td{{background:var(--panel2)}}
tr.asin.zero td:first-child::before{{background:var(--red)}}
/* pills & tags */
.pill{{display:inline-block;padding:3px 9px;border-radius:999px;font-size:11px;font-weight:700;white-space:nowrap;}}
.pill.green{{background:var(--green-bg);color:var(--green)}}
.pill.red{{background:var(--red-bg);color:var(--red)}}
.pill.orange{{background:var(--orange-bg);color:var(--orange)}}
.pill.purple{{background:var(--purple-bg);color:var(--purple);border:1px solid var(--purple-line)}}
.pf{{display:inline-flex;align-items:center;gap:6px;font-weight:600;font-size:12px}}
.pf i{{width:7px;height:7px;border-radius:50%;display:inline-block}}
.pf.amazon i{{background:var(--amazon)}}.pf.ebay i{{background:var(--ebay)}}.pf.bq i{{background:var(--bq)}}
.flag{{display:inline-block;margin-left:7px;background:var(--orange-bg);color:var(--orange);
border:1px solid var(--orange);font-size:9.5px;font-weight:700;padding:1px 6px;border-radius:5px;
vertical-align:middle;}}
.z{{color:var(--faint)}}
.act{{color:var(--red);font-weight:600;}}
.foot{{color:var(--mut);font-size:11.5px;margin-top:18px;line-height:1.7;max-width:1000px;}}
.foot b{{color:var(--ink2)}}
</style></head><body><div class="wrap">
<section class="hero">
<div class="hero-top">
<div>
<div class="eyebrow">Table 7 &middot; Weekly Report</div>
<h1>Weekly SKU Performance Check</h1>
<div class="chips">
<span class="chip"><i style="background:var(--amazon)"></i>Amazon UK</span>
<span class="chip"><i style="background:var(--ebay)"></i>eBay UK</span>
<span class="chip"><i style="background:var(--bq)"></i>B&amp;Q UK</span>
<span class="chip">Portfolio Holder: <b>Thuwaraga</b></span>
<span class="chip">{esc(m['project_code'])}</span>
</div>
</div>
<div class="win">
<div class="wlabel">Report window &middot; run {esc(m['run_date'])}</div>
<div class="wval">{esc(m['week_start'])} &rarr; {esc(m['week_end'])}</div>
<div class="wsub">Rolling 7 days (Thursday). Data snapshot as of
<b>{esc(m.get('snapshot_at','n/a'))}</b> &mdash; live DB, counts settle ~1&ndash;2 days.</div>
</div>
</div>
</section>

<div class="kpis">
<div class="card hero-card">
<div class="cl">Orders this week</div>
<div class="cv">{tot_orders:,}</div>
<div class="bar">
<span style="width:{aw}%;background:var(--amazon)"></span>
<span style="width:{ew}%;background:var(--ebay)"></span>
<span style="width:{bw}%;background:var(--bq)"></span>
</div>
<div class="barleg">
<span><i style="background:var(--amazon)"></i>Amazon <b>{amz}</b></span>
<span><i style="background:var(--ebay)"></i>eBay <b>{eby}</b></span>
<span><i style="background:var(--bq)"></i>B&amp;Q <b>{bq}</b></span>
</div>
</div>
<div class="card"><div class="cl">Product families</div><div class="cv">{n_families:,}</div>
<div class="cs">{active_fams} active &middot; {dead_fams} idle</div></div>
<div class="card"><div class="cl">Listings (ASINs)</div><div class="cv">{n_listings:,}</div>
<div class="cs">across all accounts</div></div>
<div class="card ok"><div class="cl">Performing</div><div class="cv">{n_perf:,}</div>
<div class="prog"><span style="width:{perf_pct}%"></span></div>
<div class="cs">{perf_pct}% of listings &middot; {n_zero:,} at zero</div></div>
<div class="card bad"><div class="cl">Zero-order products</div><div class="cv">{dead_fams:,}</div>
<div class="cs">no sales on any listing this week</div></div>
</div>

<div class="toolbar">
<div class="search">
<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
<input id="q" placeholder="Search SKU, ASIN / item id, product name or account&hellip;">
</div>
<div class="seg" id="seg">
<button data-f="active" class="on">Active</button>
<button data-f="all">All</button>
<button data-f="dead">Zero-order</button>
<button data-f="merged">Merged</button>
</div>
</div>
<div class="legend">
<span><i class="dot" style="background:var(--purple)"></i>Product family</span>
<span><i class="dot" style="background:var(--blue)"></i>Listing detail</span>
<span><i class="dot" style="background:var(--green)"></i>Performing</span>
<span><i class="dot" style="background:var(--red)"></i>Zero orders</span>
<span><i class="dot" style="background:var(--orange)"></i>Partial family</span>
<span><span class="flag" style="margin-left:0">+N&nbsp;SKUs</span>&nbsp;pack variants merged &mdash; verify</span>
</div>
<div class="count" id="count"></div>
<div class="tablewrap"><table>
<thead><tr>
<th>SKU / ASIN</th><th>Type</th><th>Product Name</th><th>Platform</th>
<th>Account</th>
<th class="num">Amz</th><th class="num">eBay</th><th class="num">B&amp;Q</th>
<th class="num">Total</th><th>Performing?</th><th>Action</th>
</tr></thead><tbody id="body"></tbody>
</table></div>
<div class="foot">
Generated by <code>build_html.py</code> from <code>data.json</code> (governed, read-only pull from DB
<code>{esc(m['database'])}</code>; orders = <code>COUNT(DISTINCT order_item_info)</code> where
<code>order_status='Completed'</code>). Excludes {m['excluded_amzn_gr_group_ids']} Amazon internal
group-id pseudo-SKUs (<code>amzn.gr.*</code>, all zero-order). &ldquo;Not performing&rdquo; = zero
Completed orders in the window &mdash; many are idle cross-listings, not necessarily a fault.
<b>Product family</b> = base SKU with its pack-size variants (e.g. <code>LDMG80B224</code> +
<code>&hellip;2PK/&hellip;3PK/&hellip;APK</code>) rolled up; a suffix merges only when the stripped
base is itself a real SKU. Families tagged <span class="flag" style="margin-left:0">+N&nbsp;SKUs</span>
merge more than one SKU and should be human-verified. <code>mapped_sku</code> is not used for grouping.
</div>
</div>
<script>
const WS={json.dumps(m['week_start'])}, WE={json.dumps(m['week_end'])};
const GROUPS={payload};
const body=document.getElementById('body');
const q=document.getElementById('q');
const countEl=document.getElementById('count');
let filter='active';
const open=new Set();
function esc(s){{return String(s).replace(/[&<>"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));}}
function plat(p){{const k={{'AMAZON':'amazon','EBAY':'ebay','B&Q':'bq'}}[p]||'amazon';
  const lbl={{'AMAZON':'Amazon','EBAY':'eBay','B&Q':'B&Q'}}[p]||p;
  return '<span class="pf '+k+'"><i></i>'+esc(lbl)+'</span>';}}
function num(n){{return n?('<b>'+n+'</b>'):'<span class="z">0</span>';}}
function matches(g,term){{
  if(!term)return true;
  if(g.base.toLowerCase().includes(term)||g.name.toLowerCase().includes(term))return true;
  return g.rows.some(r=>r.sku.toLowerCase().includes(term)||String(r.ref).toLowerCase().includes(term)||r.name.toLowerCase().includes(term)||r.account.toLowerCase().includes(term));
}}
function pass(g){{
  if(filter==='active')return g.active;
  if(filter==='dead')return !g.active;
  if(filter==='merged')return g.merged;
  return true;
}}
function render(){{
  const term=q.value.trim().toLowerCase();
  let html='',shown=0,listings=0;
  for(const g of GROUPS){{
    if(!pass(g)||!matches(g,term))continue;
    shown++;listings+=g.y;
    const isOpen=open.has(g.base)||term.length>0;
    html+=`<tr class="sku st-${{g.state}} ${{isOpen?'op':''}}" data-b="${{esc(g.base)}}">
      <td><span class="caret">▶</span>${{esc(g.base)}}${{g.merged?'<span class=flag>+'+(g.skus-1)+' SKUs</span>':''}}</td>
      <td><span class="pill purple">SKU SUMMARY</span></td>
      <td class="name" title="${{esc(g.name)}}">Bulb</td>
      <td><span style="color:var(--mut);font-weight:600">All platforms</span></td>
      <td class="z">&mdash;</td>
      <td class="num">${{num(g.amazon)}}</td><td class="num">${{num(g.ebay)}}</td>
      <td class="num">${{num(g.bq)}}</td><td class="num">${{num(g.total)}}</td>
      <td><span class="pill ${{g.state}}">${{esc(g.perf)}}</span></td>
      <td class="${{g.x<g.y?'act':'z'}}">${{esc(g.action)}}</td></tr>`;
    if(isOpen){{
      for(const r of g.rows){{
        html+=`<tr class="asin ${{r.performing?'':'zero'}}">
          <td>${{esc(r.sku)}}${{r.variant?'<span class=flag>variant</span>':''}}</td>
          <td>${{esc(r.ref)}}</td><td class="name" title="${{esc(r.name)}}">Bulb</td>
          <td>${{plat(r.platform)}}</td><td>${{esc(r.account)}}</td>
          <td class="num">${{num(r.amazon)}}</td><td class="num">${{num(r.ebay)}}</td>
          <td class="num">${{num(r.bq)}}</td><td class="num">${{num(r.total)}}</td>
          <td><span class="pill ${{r.performing?'green':'red'}}">${{r.performing?'YES ✓':'NO ✕'}}</span></td>
          <td class="${{r.performing?'z':'act'}}">${{esc(r.action)}}</td></tr>`;
      }}
    }}
  }}
  body.innerHTML=html||'<tr><td colspan=11 style="padding:28px;text-align:center;color:var(--mut)">No matching products.</td></tr>';
  countEl.innerHTML=`Showing <b>${{shown}}</b> famil${{shown===1?'y':'ies'}} &middot; <b>${{listings}}</b> listings`;
}}
body.addEventListener('click',e=>{{
  const tr=e.target.closest('tr.sku');if(!tr)return;
  const b=tr.getAttribute('data-b');
  if(open.has(b))open.delete(b);else open.add(b);
  render();
}});
q.addEventListener('input',render);
document.querySelectorAll('#seg button').forEach(b=>b.addEventListener('click',()=>{{
  document.querySelectorAll('#seg button').forEach(x=>x.classList.remove('on'));
  b.classList.add('on');filter=b.getAttribute('data-f');open.clear();render();
}}));
render();
</script>
</body></html>"""


def main():
    data = load()
    groups = build_groups(data)
    out = render(data, groups)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(out)
    print("wrote", OUT, os.path.getsize(OUT), "bytes;", len(groups), "SKU families")


if __name__ == "__main__":
    main()
