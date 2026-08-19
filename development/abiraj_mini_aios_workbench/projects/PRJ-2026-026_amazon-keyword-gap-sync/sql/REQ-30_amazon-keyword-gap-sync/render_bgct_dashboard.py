#!/usr/bin/env python3
"""
REQ-30-D02 - BGCT Keyword Gap review dashboard - renderer
PRJ-2026-026 (bgct)

Reads bgct_payload.json (written by build_bgct_d01.py) and emits a single self-contained HTML
file. No network calls, no external assets, no database access - the payload is the only input,
so the dashboard always matches the Excel it was built alongside.

Implements source section 2.6 (pre-computed review dashboard) and section 2.7 (the two buttons).

SCOPE BOUNDARY: the buttons record state in the browser only. Neither one writes to Amazon.
Section 2.7's automatic SP-API push is out of workbench scope - `add_target` tells a person where
the keyword should go; a person puts it there.
"""
import os, json, html, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, "..", ".."))
PAYLOAD = os.path.join(HERE, "bgct_payload.json")
OUT = os.path.join(PROJECT, "evidence", "final_outputs", "REQ-30_amazon-keyword-gap-sync",
                   "REQ-30-D02_keyword_gap_dashboard.html")

BRANDS = {"dcvoltage_uk": "DCVOLTAGE UK", "ledsone_uk": "LEDSone UK"}
E = lambda s: html.escape(str(s if s is not None else ""))


def main():
    p = json.load(open(PAYLOAD, encoding="utf-8"))
    per, rules = p["period"], p["rules"]
    pa, pb, pc = p["part_a"], p["part_b"], p.get("part_c", [])

    pairs = {}
    for r in pb:
        pairs.setdefault((r["brand"], r["top_asin"], r["duplicate_asin"]), []).append(r)
    for v in pairs.values():
        v.sort(key=lambda r: -r["search_query_volume"])

    gaps = sum(1 for r in pb if r["status"] == "gap")
    nmonths = len(per["months"])
    req = rules["top_moving_months_required"]
    tm_rule = (f"units &gt; {rules['top_moving_units_gt']} in "
               + ("all " if req >= nmonths else f"at least {req} of ") + f"{nmonths} months")
    tiles = [("Top-Moving ASINs", len(p["top_moving"]), tm_rule),
             ("Underperforming listings", len(pa) + len(pairs), "no sales 6mo, or falling 3mo"),
             ("Listings needing rewrite", len(pa), "Part A — no content to check"),
             ("Real keyword gaps", gaps, f"Part B — across {len(pairs)} listings"),
             ("Wrong SKU — rejected", len(pc), "Part C — wattage or fitting differs")]

    def badge(v, yes="✓", no="✗"):
        return f'<span class="b {"y" if v else "n"}">{yes if v else no}</span>'

    TARGET = {"backend": "Add to backend", "bullet": "Add to bullets",
              "backend_and_bullet": "Add to backend + bullets", "none": "—"}

    body = []
    for brand in ("dcvoltage_uk", "ledsone_uk"):
        bp = {k: v for k, v in pairs.items() if k[0] == brand}
        ba = [r for r in pa if r["brand"] == brand]
        bc = [r for r in pc if r["brand"] == brand]
        if not bp and not ba and not bc:
            continue
        body.append(f'<section class="acct"><h2>{E(BRANDS[brand])}</h2>'
                    f'<p class="sub">{len(ba)} listing(s) needing a rewrite · {len(bp)} listing(s) with keyword gaps '
                    f'· accounts are reported independently and never merged</p>')

        if ba:
            body.append('<h3 class="pa">Part A — listing has no content ('
                        f'{len(ba)})</h3><p class="note">Every keyword would read as “missing” because there is '
                        'nothing on the listing to search. These need a rewrite, not keyword edits.</p>'
                        '<table class="t"><thead><tr><th>Dead ASIN</th><th>SKU</th><th>Base SKU</th>'
                        '<th>Why flagged</th><th>What is missing</th><th>Proven terms ready</th>'
                        '<th>Top-Moving twin</th></tr></thead><tbody>')
            for r in sorted(ba, key=lambda x: x["base_sku"]):
                body.append(f'<tr><td class="m">{E(r["duplicate_asin"])}</td><td class="m s">{E(r["duplicate_sku"])}</td>'
                            f'<td class="m">{E(r["base_sku"])}</td><td>{E(r["duplicate_status"])}</td>'
                            f'<td class="warn">{E(r["issue"])}</td><td class="c">{r["terms_available"]}</td>'
                            f'<td class="m">{E(r["top_asin"])}</td></tr>')
            body.append("</tbody></table>")

        if bc:
            body.append(f'<h3 class="pc">Part C — wrong SKU, pair rejected ({len(bc)})</h3>'
                        '<p class="note">These two listings share a base SKU but state <b>different '
                        'wattage or a different cap fitting</b>, so they are not the same bulb — the stored '
                        'SKU is wrong. '
                        'No keywords were checked. Fix the SKU first.</p>'
                        '<table class="t"><thead><tr><th>Good seller</th><th>Its wattage</th>'
                        '<th>Listing with the wrong SKU</th><th>Its spec</th><th>Wrong SKU</th>'
                        '<th>Base SKU</th><th>Title</th></tr></thead><tbody>')
            for r in sorted(bc, key=lambda x: x["base_sku"]):
                body.append(f'<tr><td class="m">{E(r["top_asin"])}</td><td class="c n">{r["top_watts"]}W</td>'
                            f'<td class="m">{E(r["duplicate_asin"])}</td>'
                            f'<td class="c n warn"><b>{E(r["duplicate_watts"])}</b></td>'
                            f'<td class="m warn">{E(r["duplicate_sku"])}</td>'
                            f'<td class="m">{E(r["base_sku"])}</td>'
                            f'<td class="s">{E(r["title"][:90])}</td></tr>')
            body.append("</tbody></table>")

        if bp:
            body.append(f'<h3 class="pb">Part B — keyword gaps ({len(bp)} listings)</h3>')
            for (br, top, dup), rows in sorted(bp.items(), key=lambda kv: -sum(
                    1 for r in kv[1] if r["status"] == "gap")):
                g = sum(1 for r in rows if r["status"] == "gap")
                allp = g == 0
                body.append(
                    f'<div class="pair" data-search="{E((top + " " + dup + " " + rows[0]["base_sku"]).lower())}">'
                    f'<div class="ph"><div><span class="tag">Top-Moving</span> <b class="m">{E(top)}</b>'
                    f' <span class="arrow">→</span> <span class="tag dead">{E(rows[0]["duplicate_status"])}</span>'
                    f' <b class="m">{E(dup)}</b><div class="sk">base SKU {E(rows[0]["base_sku"])}</div></div>'
                    f'<div class="acts">'
                    + (f'<button class="btn ok" onclick="mark(this)">All keywords present · Mark reviewed</button>'
                       if allp else
                       f'<button class="btn add" onclick="mark(this)">Add missing keywords ({g})</button>')
                    + '</div></div>'
                    '<table class="t"><thead><tr><th>Keyword</th><th class="c">Volume</th>'
                    '<th class="c">Title / bullets / desc</th><th class="c">Backend</th>'
                    '<th>Status</th><th>Where to add it</th></tr></thead><tbody>')
                for r in rows:
                    cls = "" if r["status"] == "present" else " gap"
                    body.append(f'<tr class="{cls.strip()}"><td>{E(r["keyword"])}</td>'
                                f'<td class="c n">{r["search_query_volume"]:,}</td>'
                                f'<td class="c">{badge(r["in_frontend"])}</td>'
                                f'<td class="c">{badge(r["in_backend"])}</td>'
                                f'<td>{E(r["status"])}</td>'
                                f'<td class="tgt">{E(TARGET[r["add_target"]])}</td></tr>')
                body.append("</tbody></table></div>")
        body.append("</section>")

    qa = " · ".join(f'{k.split("_",1)[1].replace("_"," ")} <b class="{"y" if v else "n"}">'
                    f'{"PASS" if v else "FAIL"}</b>' for k, v in p["qa"].items())

    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BGCT Keyword Gap Report — REQ-30-D02</title><style>
:root{{--bg:#f6f7f9;--card:#fff;--ink:#16202c;--mut:#5d6b7a;--line:#e2e6ec;--nv:#1f3864;
--gap:#c0392b;--ok:#1e8449;--warn:#b7791f;}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);
font:14px/1.5 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif}}
header{{background:var(--nv);color:#fff;padding:22px 26px}}
header h1{{margin:0 0 4px;font-size:20px}} header .meta{{opacity:.85;font-size:12.5px}}
.wrap{{max-width:1500px;margin:0 auto;padding:20px 26px 60px}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin:18px 0}}
.tile{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px}}
.tile .v{{font-size:30px;font-weight:700;line-height:1.1}} .tile .k{{color:var(--mut);font-size:12.5px;margin-top:4px}}
.tile .h{{color:var(--mut);font-size:11.5px;margin-top:6px;font-style:italic}}
.bar{{background:#fff4e5;border:1px solid #f0d3a3;border-left:4px solid var(--warn);
padding:12px 16px;border-radius:8px;margin:16px 0;font-size:13px}}
.bar b{{color:#8a5a00}}
section.acct{{margin:30px 0}} section.acct h2{{margin:0 0 2px;font-size:17px}}
.sub{{color:var(--mut);margin:0 0 14px;font-size:12.5px}}
h3.pa,h3.pb{{font-size:14px;margin:22px 0 4px;padding-left:9px;border-left:4px solid var(--warn)}}
h3.pb{{border-color:var(--gap)}} h3.pc{{border-color:#7d3c98}}
.note{{color:var(--mut);font-size:12.5px;margin:0 0 10px}}
table.t{{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);
border-radius:8px;overflow:hidden;margin-bottom:16px}}
.t th{{background:#eef1f5;text-align:left;padding:8px 10px;font-size:12px;color:#3a4a5c;
border-bottom:1px solid var(--line);white-space:nowrap}}
.t td{{padding:7px 10px;border-bottom:1px solid #f0f2f5;vertical-align:top}}
.t tr:last-child td{{border-bottom:none}} .t tr.gap td{{background:#fdf6f5}}
.c{{text-align:center}} .n{{font-variant-numeric:tabular-nums;text-align:right}}
.m{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:12.5px}}
.s{{color:var(--mut);font-size:11.5px}} .warn{{color:var(--warn)}} .tgt{{font-weight:600}}
.b{{display:inline-block;width:20px;height:20px;line-height:20px;border-radius:50%;font-size:12px;color:#fff}}
.b.y{{background:var(--ok)}} .b.n{{background:var(--gap)}}
.pair{{background:var(--card);border:1px solid var(--line);border-radius:10px;margin-bottom:14px;overflow:hidden}}
.ph{{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;
padding:12px 14px;background:#f9fafc;border-bottom:1px solid var(--line);flex-wrap:wrap}}
.tag{{background:#e7edf6;color:var(--nv);border-radius:4px;padding:2px 7px;font-size:11px;font-weight:600}}
.tag.dead{{background:#fbe6e4;color:var(--gap)}} .arrow{{color:var(--mut);margin:0 4px}}
.sk{{color:var(--mut);font-size:11.5px;margin-top:4px}}
.pair table.t{{border:none;border-radius:0;margin:0}}
.btn{{border:0;border-radius:7px;padding:8px 14px;font-size:12.5px;font-weight:600;cursor:pointer;color:#fff}}
.btn.ok{{background:var(--ok)}} .btn.add{{background:var(--gap)}} .btn.done{{background:#7b8794}}
#q{{width:100%;max-width:420px;padding:9px 12px;border:1px solid var(--line);border-radius:8px;font-size:13px}}
footer{{color:var(--mut);font-size:11.5px;margin-top:34px;border-top:1px solid var(--line);padding-top:14px}}
b.y{{color:var(--ok)}} b.n{{color:var(--gap)}}
</style></head><body>
<header><h1>BGCT — Keyword Collection &amp; Cross-ASIN Gap Sync</h1>
<div class="meta">REQ-30-D02 · Amazon UK · DCVOLTAGE UK + LEDSone UK (never merged) ·
period {E(per['start'])} → {E(per['end'])} · zero-sales window from {E(per['zero_sales_from'])} ·
generated {E(p['generated_at'])}</div></header>
<div class="wrap">
<div class="bar"><b>This report does not change anything on Amazon.</b> It shows where each proven
keyword should go. The buttons below record your review in this page only — a person applies the
keywords. (Source section 2.7's automatic SP-API push is deliberately out of scope.)</div>
<div class="tiles">{''.join(f'<div class="tile"><div class="v">{v:,}</div><div class="k">{k}</div><div class="h">{h}</div></div>' for k,v,h in tiles)}</div>
<input id="q" placeholder="Filter by ASIN or base SKU…" oninput="flt(this.value)">
{''.join(body)}
<footer>
Rules — Top-Moving: {tm_rule} ·
base SKU: pack size, trailing letters and account suffixes stripped, bundles kept whole ·
underperformer: 0 units in {rules['zero_sales_window_months']} months (catalogue-anchored) or strictly falling across the period ·
keyword match: all words present anywhere, any order, case and punctuation ignored ·
top {rules['terms_per_asin']} terms per ASIN, zero-conversion terms dropped (source Step 6).<br>
QA (source 2.10) — {qa}.<br>
Source: BGCT_Keyword_Workflow_Phase1_Phase2_v2.1.pdf · PRJ-2026-026 / REQ-30 (bgct, provisional) ·
rules confirmed by Abiraj 2026-08-19, business confirmation from Thuwaraga outstanding ·
DRAFT — not validated, not published, not automated.
</footer></div>
<script>
function mark(b){{b.classList.add('done');b.classList.remove('ok','add');b.textContent='Reviewed ✓';b.disabled=true;}}
function flt(v){{v=v.trim().toLowerCase();
 document.querySelectorAll('.pair').forEach(function(el){{
  el.style.display = !v || el.dataset.search.indexOf(v)>-1 ? '' : 'none';}});}}
</script></body></html>"""

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(doc)
    print(f"dashboard -> {OUT}\n{len(pa)} Part A · {len(pairs)} Part B listings · {gaps} gaps · {len(doc):,} bytes")


if __name__ == "__main__":
    main()
