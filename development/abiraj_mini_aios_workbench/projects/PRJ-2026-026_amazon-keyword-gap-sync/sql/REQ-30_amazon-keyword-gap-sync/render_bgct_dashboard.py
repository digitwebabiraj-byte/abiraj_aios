#!/usr/bin/env python3
"""
BGCT Keyword Workflow dashboard - renderer (ONE file, both phases)
PRJ-2026-026 / REQ-30 (bgct)

Reads bgct_payload.json (written by build_bgct_d01.py) and emits a SINGLE self-contained,
full-screen HTML file covering both deliverables as two tabs:

  Phase 1 - Proven keywords  (REQ-30-D01)  the SQP top search terms per Top-Moving ASIN
  Phase 2 - Gaps to fix      (REQ-30-D02)  Part A rewrites / Part B keyword gaps
                                          Part C (wrong SKU) is intentionally NOT rendered - it is a
                                          SKU-data fix, not a keyword job, and it confused the reader.
                                          It stays in REQ-30-D02.xlsx and on the decision sheet (Q4),
                                          and its ASINs get the 'sku_check' bucket on the bulbs tab.

ONE file on purpose: the person receiving this should have one thing to open, not a folder of HTML.
This renderer also DELETES the two superseded single-phase HTML files, so only one dashboard ever
ships. The two Excel workbooks stay separate - they are the two named deliverables.

Implements source section 2.6 (pre-computed per-pair review) and section 2.7 (the two buttons).

SCOPE BOUNDARY: the review buttons record state in the browser only. Neither writes to Amazon.
Section 2.7's automatic SP-API push is out of workbench scope - `add_target` tells a person where the
keyword should go; a person puts it there.

READ-ONLY: no network calls, no external assets, no database access. The payload is the only input.
"""
import os, json, html, statistics as stat

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, "..", ".."))
PAYLOAD = os.path.join(HERE, "bgct_payload.json")
OUTDIR = os.path.join(PROJECT, "evidence", "final_outputs", "REQ-30_amazon-keyword-gap-sync")
OUT = os.path.join(OUTDIR, "REQ-30_bgct_keyword_dashboard.html")
SUPERSEDED = ["REQ-30-D01_sqp_top_terms_dashboard.html", "REQ-30-D02_keyword_gap_dashboard.html"]

BRANDS = {"dcvoltage_uk": "DCVOLTAGE UK", "ledsone_uk": "LEDSone UK"}
STATUS = {"zero_sales_6mo": "No sales 6 months", "sales_drop_3mo": "Sales falling 3 months"}
TARGET = {"backend": "Add to backend", "bullet": "Add to bullets",
          "backend_and_bullet": "Add to backend + bullets", "none": "Nothing to do"}


def main():
    p = json.load(open(PAYLOAD, encoding="utf-8"))
    per, rules, qa = p["period"], p["rules"], p["qa"]
    pa, pb, pc = p["part_a"], p["part_b"], p.get("part_c", [])
    cov = p.get("coverage", {})
    # Amazon delivers each account's search data on its own schedule. When one account's month is
    # assembled from fewer weeks than another's, its keyword volumes are NOT comparable - and nothing
    # in a row admits that. Say it on the face of the report rather than let her infer equal footing.
    sqpc = p.get("sqp_coverage", {})
    BRN = {"dcvoltage_uk": "DCVOLTAGE UK", "ledsone_uk": "LEDSone UK"}
    thin = []
    for b, c in sorted(sqpc.items()):
        wk = c.get("weeks_by_month", {})
        if wk and min(wk.values()) < 4:
            det = ", ".join(f"{m[:7]}&nbsp;{n}wk" for m, n in sorted(wk.items()))
            thin.append(f"<b>{BRN.get(b, b)}</b> {det}")
    freshness = ("" if not thin else
        '<div class="fresh"><b>Search-data coverage.</b> Amazon sends each account its own search '
        'data, and one of yours arrived thinner than the other. A month built from fewer weeks has '
        'lower keyword volumes than a full one, so <b>do not compare volumes across the two accounts</b> '
        '&mdash; compare within an account. ' + " &middot; ".join(thin) + ' (4wk = complete).</div>')
    cat = p.get("catalogue", [])
    rows_g = [{"a": r["asin"], "sk": r["sku"], "bs": r["base_sku"], "ac": r["accounts"],
               "u": r["units_by_month"], "u3": r["units_3mo"], "u6": r["units_6mo"],
               "ma": r["months_above"], "b": r["bucket"], "st": r["status"],
               "ti": r["title"]} for r in cat]
    terms, tm = p["phase1"], p["top_moving"]

    pairsB = sorted({(r["brand"], r["top_asin"], r["duplicate_asin"]) for r in pb})
    gaps = [r for r in pb if r["status"] == "gap"]
    nmonths = len(per["months"])
    req = rules["top_moving_months_required"]
    tm_rule = (f"more than {rules['top_moving_units_gt']} units in "
               + ("all " if req >= nmonths else f"at least {req} of ") + f"{nmonths} months")

    # ---- Phase 1 rows + the source's "What to Look For" pattern flags ---------------------------
    # The document names five patterns but gives NO numeric cut-off (open item #10), so the one that
    # needs one is a MEDIAN SPLIT of this run, labelled as such on screen. No threshold is invented.
    vols = [t["search_query_volume"] for t in terms] or [0]
    shares = [t["asin_share"] for t in terms if t["asin_share"] is not None] or [0]
    mv, ms = stat.median(vols), stat.median(shares)
    rows_t = [{"mo": t["month"], "br": t["brand"], "a": t["top_asin"], "kw": t["search_term"],
               "sc": t["search_query_score"], "v": t["search_query_volume"],
               "sh": round(t["asin_share"] * 100, 2) if t["asin_share"] is not None else None,
               "cr": round(t["click_rate"] * 100, 2) if t["click_rate"] is not None else None,
               "pu": t["purchases"], "lt": 1 if t["is_long_tail"] else 0,
               "op": 1 if (t["search_query_volume"] >= mv and t["asin_share"] is not None
                           and t["asin_share"] < ms) else 0} for t in terms]
    rows_m = [{"br": r["brand"], "a": r["asin"], "u": r["units"], "n": r["terms"]} for r in tm]
    with_terms = sum(1 for r in tm if r["terms"] > 0)

    # ---- Phase 2 rows --------------------------------------------------------------------------
    rows_b = [{"br": r["brand"], "ta": r["top_asin"], "da": r["duplicate_asin"], "sk": r["base_sku"],
               "ds": r["duplicate_status"], "kw": r["keyword"], "v": r["search_query_volume"],
               "f": 1 if r["in_frontend"] else 0, "b": 1 if r["in_backend"] else 0,
               "mf": r.get("missing_words_frontend", ""),
               "mb": r.get("missing_words_backend", ""),
               "t": r["add_target"]} for r in pb]
    rows_a = [{"br": r["brand"], "ta": r["top_asin"], "da": r["duplicate_asin"],
               "sku": r["duplicate_sku"], "sk": r["base_sku"], "ds": r["duplicate_status"],
               "is": r["issue"], "n": r["keywords_ready_to_use"], "ti": r["title"]} for r in pa]
    # part_c is deliberately NOT sent to the page - see the header note. It stays in the Excel.
    _unused_rows_c = [{"br": r["brand"], "ta": r["top_asin"], "da": r["duplicate_asin"],
               "sku": r["duplicate_sku"], "sk": r["base_sku"], "tw": r["top_watts"],
               "dw": r["duplicate_watts"], "is": r["issue"], "ti": r["title"]} for r in pc]

    data = json.dumps({"t": rows_t, "m": rows_m, "a": rows_a, "b": rows_b,
                       "g": rows_g}, separators=(",", ":"))
    qa_line = " · ".join(f'{k.split("_",1)[1].replace("_"," ")} '
                         f'<b class="{"y" if v else "n"}">{"PASS" if v else "FAIL"}</b>'
                         for k, v in qa.items())
    E = html.escape

    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BGCT Keyword Workflow — REQ-30</title><style>
:root{{--bg:#eef1f5;--panel:#fff;--ink:#14202c;--mut:#5c6b7a;--line:#dde3ea;--line2:#eef1f5;
 --nv:#1b3a5c;--nv2:#25507d;--gap:#c0392b;--gapbg:#fdf4f3;--ok:#177245;--warn:#a86a12;
 --purple:#6b3fa0;--opp:#0b6f8f;--chip:#e8eef7;}}
*{{box-sizing:border-box}} html,body{{height:100%}}
body{{margin:0;background:var(--bg);color:var(--ink);
 font:14px/1.45 -apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}}
header{{background:linear-gradient(180deg,var(--nv2),var(--nv));color:#fff;padding:14px 22px 0}}
header h1{{margin:0;font-size:18px;letter-spacing:.2px}}
header .meta{{opacity:.9;font-size:12px;margin-top:3px}}
header .meta b{{color:#ffe9b0;font-weight:600}}
.tabs{{display:flex;gap:4px;margin-top:12px}}
.tab{{background:rgba(255,255,255,.12);color:#dbe7f3;border:0;border-radius:8px 8px 0 0;
 padding:10px 18px;font:600 13px inherit;cursor:pointer}}
.tab:hover{{background:rgba(255,255,255,.2);color:#fff}}
.tab.on{{background:var(--bg);color:var(--nv)}}
.tab .c{{opacity:.75;font-weight:500;margin-left:5px}}
.help{{background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--nv2);
 border-radius:9px;margin:14px 22px 0;padding:14px 18px}}
.help>summary{{cursor:pointer;font-size:14px;font-weight:700;color:var(--nv);list-style:none;
 display:flex;align-items:center;gap:7px}}
.help>summary::-webkit-details-marker{{display:none}}
/* the show/hide affordance is a pseudo-element, so it is styled to LOOK like the button it is -
   the whole summary row is the click target, and it highlights on hover of any part of it */
.covt{{width:100%;border-collapse:collapse;font-size:13px}}
.covt td{{padding:6px 8px;border-bottom:1px solid var(--line2);vertical-align:top}}
.covt td.n{{width:64px;text-align:right;font-weight:700;font-size:16px;
 font-variant-numeric:tabular-nums;color:var(--nv2)}}
.covt tr.hi td{{background:#f2f8f4}} .covt tr.hi td.n{{color:var(--ok)}}
.covt tr.warnrow td{{background:#fff8ec}} .covt tr.warnrow td.n{{color:var(--warn)}}
.help.cov{{border-left-color:var(--opp)}}
.help>summary::after{{content:"Hide ▴";margin-left:auto;flex:none;
 font-size:12px;font-weight:600;color:var(--nv2);background:#f2f6fb;
 border:1px solid #c9d9ea;border-bottom-width:2px;border-radius:7px;padding:4px 11px;
 transition:.12s}}
.help:not([open])>summary::after{{content:"Show ▾"}}
.help>summary:hover::after{{background:var(--nv2);color:#fff;border-color:var(--nv)}}
.help>summary:active::after{{transform:translateY(1px);border-bottom-width:1px}}
.help>summary:focus-visible{{outline:none}}
.help>summary:focus-visible::after{{box-shadow:0 0 0 3px rgba(37,80,125,.25)}}
.help:not([open]){{padding:11px 18px}}
.help[open]>summary{{margin-bottom:9px;padding-bottom:8px;border-bottom:1px solid var(--line2)}}
.help ol{{margin:0;padding-left:20px}} .help li{{margin:6px 0;font-size:13px}}
.help .tip{{margin-top:10px;padding-top:9px;border-top:1px dashed var(--line);font-size:12.5px;
 color:var(--mut)}}
.help b{{color:var(--ink)}}
.help .lg{{display:inline-block;width:15px;height:15px;border-radius:4px;vertical-align:-2px;margin-right:4px}}
.note{{padding:9px 22px;font-size:12.5px;border-bottom:1px solid var(--line)}}
.note.p1{{background:#eef6fb;border-top:1px solid #cde2ef;color:#0d4a63}} .note.p1 b{{color:#08384c}}
.note.p2{{background:#fff8e8;border-top:1px solid #f0dcae;color:#6b4a05}} .note.p2 b{{color:#8a5a00}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;padding:14px 22px 4px}}
.kpi{{background:var(--panel);border:1px solid var(--line);border-radius:9px;padding:11px 13px;
 border-left:4px solid var(--nv2)}}
.kpi.clk{{cursor:pointer;transition:.12s}}
.kpi.clk:hover{{border-color:var(--nv2);box-shadow:0 2px 8px rgba(20,32,44,.09)}}
.kpi.on{{background:#f5f9ff;box-shadow:inset 0 0 0 1px var(--nv2)}}
.kpi .v{{font-size:26px;font-weight:700;line-height:1.05;font-variant-numeric:tabular-nums}}
.kpi .k{{font-size:12px;color:var(--mut);margin-top:3px}}
.kpi.a{{border-left-color:var(--warn)}} .kpi.b{{border-left-color:var(--gap)}}
.kpi.c{{border-left-color:var(--purple)}} .kpi.o{{border-left-color:var(--opp)}}
.kpi.l{{border-left-color:var(--purple)}}
.bar{{position:sticky;top:0;z-index:20;background:rgba(238,241,245,.96);backdrop-filter:blur(6px);
 border-bottom:1px solid var(--line);padding:10px 22px;display:flex;gap:9px;align-items:center;flex-wrap:wrap}}
.bar input,.bar select{{font:13px inherit;color:var(--ink);background:#fff;border:1px solid #c9d3de;
 border-radius:7px;padding:7px 9px;outline:none}}
.bar input[type=search]{{flex:1 1 240px;min-width:180px}}
.bar input[type=number]{{width:92px}}
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
section.A h2{{border-left-color:var(--warn)}} section.B h2{{border-left-color:var(--gap)}}
section.C h2{{border-left-color:var(--purple)}}
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
tbody tr.gap td{{background:var(--gapbg)}} tbody tr.gap:hover td{{background:#fbeceb}}
.c{{text-align:center}} .r{{text-align:right;font-variant-numeric:tabular-nums}}
.m{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:12px;white-space:nowrap}}
.asin{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:12px;white-space:nowrap;
 background:#eaf2fb;color:#123a63;border:1px solid #cfe0f2;border-radius:4px;padding:1px 5px}}
th b{{color:var(--nv2)}}
.s{{color:var(--mut);font-size:11.5px}} .kw{{font-weight:600}} .warnt{{color:var(--warn)}}
/* free-text columns are capped and ellipsised, with the full value on hover, so one long title
   cannot turn a table row into a seven-line block on a narrow window */
.clip{{max-width:320px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.clip.wide{{max-width:420px}}
/* Amazon itself reports a click rate above 100% when one search yields several clicks - up to
   5900% in this data. The figure is faithful, so it is shown, but marked so it does not read as a
   fault. Hovering explains it. */
.odd{{color:var(--warn);border-bottom:1px dotted var(--warn);cursor:help}}
.tick{{display:inline-block;width:19px;height:19px;line-height:19px;border-radius:50%;font-size:11px;
 color:#fff;text-align:center}} .tick.y{{background:var(--ok)}} .tick.n{{background:var(--gap)}}
.pill{{display:inline-block;padding:2px 8px;border-radius:11px;font-size:11px;font-weight:600;white-space:nowrap}}
.pill.acc{{background:var(--chip);color:var(--nv)}} .pill.both{{background:#fbe9e7;color:var(--gap)}}
.pill.be{{background:#fff3e0;color:var(--warn)}} .pill.bu{{background:#e8f0fe;color:var(--nv2)}}
.pill.no{{background:#e7f4ea;color:var(--ok)}} .pill.op{{background:#e2f2f8;color:var(--opp)}}
.pill.lt{{background:#f0e9f8;color:var(--purple)}}
.pill.bk{{background:#fbe9e7;color:var(--gap)}} .pill.wn{{background:#f0e9f8;color:var(--purple)}}
.pill.am{{background:#fff3e0;color:var(--warn)}} .pill.ok{{background:#e7f4ea;color:var(--ok)}}
.pill.tm{{background:#e2f2f8;color:var(--opp)}}
/* The ASIN column is what she actually hunts for - keep it visible however far she scrolls right.
   Each state below repeats a colour the plain cells already have; a transparent sticky cell would
   let the scrolling columns slide visibly underneath it. */
tbody td.pin{{position:sticky;left:0;z-index:3;background:var(--panel);
  box-shadow:1px 0 0 var(--line),4px 0 7px -4px rgba(0,0,0,.16)}}
thead th.pin{{position:sticky;left:0;top:0;z-index:6;background:#f2f5f9;
  box-shadow:1px 0 0 var(--line),4px 0 7px -4px rgba(0,0,0,.16)}}
tbody tr:hover td.pin{{background:#f7fafd}}
tbody tr.gap td.pin{{background:var(--gapbg)}}
tbody tr.gap:hover td.pin{{background:#fbeceb}}
.fresh{{background:#fff8e6;border:1px solid #f0dcae;border-left:4px solid var(--warn);
 color:#5a4413;border-radius:0 7px 7px 0;padding:9px 13px;margin:10px 22px 0;font-size:12.5px;
 line-height:1.5}}
.fresh b{{color:#7a5a12}}
.wd{{display:inline-block;font-weight:700;font-size:12px;border-radius:5px;padding:1px 7px;
 margin:1px 2px 1px 0;white-space:nowrap}}
.wd.be{{background:#fff3e0;color:var(--warn);border:1px solid #f0d9b0}}
.wd.bu{{background:#e8f0fe;color:var(--nv2);border:1px solid #c9d9ea}}
/* each month shown with a tick or cross, so the Top-Moving rule reads off the row itself */
.mth{{display:inline-block;font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:11.5px;
 border-radius:5px;padding:2px 7px;margin-right:5px;white-space:nowrap}}
.mth.ok{{background:#e7f4ea;color:var(--ok);border:1px solid #bfe0c8}}
.mth.no{{background:#f4f5f7;color:var(--mut);border:1px solid var(--line)}}
.pair{{background:var(--panel);border:1px solid var(--line);border-radius:9px;margin-bottom:12px;overflow:hidden}}
.ph{{display:flex;justify-content:space-between;align-items:flex-start;gap:14px;padding:11px 13px;
 background:#f6f9fc;border-bottom:1px solid var(--line);flex-wrap:wrap}}
.ph .sk{{color:var(--mut);font-size:11.5px;margin-top:3px}}
.tag{{background:var(--chip);color:var(--nv);border-radius:4px;padding:2px 7px;font-size:11px;font-weight:600}}
.tag.dead{{background:#fbe9e7;color:var(--gap)}} .arrow{{color:var(--mut);margin:0 5px}}
.act{{border:0;border-radius:7px;padding:8px 13px;font-size:12.5px;font-weight:600;cursor:pointer;
 color:#fff;white-space:nowrap}} .act.ok{{background:var(--ok)}} .act.add{{background:var(--gap)}}
.act.done{{background:#78868f;cursor:default}} .state{{font-size:11.5px;color:var(--mut);margin-left:9px}}
.pair .wrap{{border:0;border-radius:0}}
.empty{{padding:26px;text-align:center;color:var(--mut);font-size:13px}}
footer{{color:var(--mut);font-size:11.5px;padding:16px 22px 40px;border-top:1px solid var(--line);margin-top:26px}}
b.y{{color:var(--ok)}} b.n{{color:var(--gap)}}
kbd{{background:#fff;border:1px solid #c9d3de;border-bottom-width:2px;border-radius:4px;padding:0 4px;
 font-size:11px;font-family:inherit}}
[hidden]{{display:none !important}}
@media (max-width:820px){{header,.note,.kpis,.bar,main,footer{{padding-left:12px;padding-right:12px}}}}
</style></head><body>

<header>
  <h1>BGCT — Keyword Collection &amp; Cross-ASIN Gap Sync</h1>
  <div class="meta">REQ-30 · Amazon UK · DCVOLTAGE UK + LEDSone UK (reported separately, never merged)
  · keywords from <b>{E(per['start'])} → {E(per['end'])}</b> · no-sales window from
  <b>{E(per['zero_sales_from'])}</b> · generated {E(p['generated_at'])}</div>
  {freshness}
  <div class="tabs">
    <button class="tab on" data-t="1">Phase 1 — Proven keywords<span class="c">{len(terms)}</span></button>
    <button class="tab" data-t="2">Phase 2 — Gaps to fix<span class="c">{len(gaps)}</span></button>
    <button class="tab" data-t="3">All my bulbs<span class="c">{cov.get('total',0)}</span></button>
  </div>
</header>

<div id="p1">
<details class="help" id="h1" open>
  <summary>How to use this tab</summary>
  <ol>
    <li>This is the list of words <b>customers really typed into Amazon</b> before buying your
      best-selling bulbs. It is Amazon's own data, not a guess.</li>
    <li>Look for <span class="pill op">Opportunity</span> — it means <b>many people search this word,
      but your bulb hardly ever shows up for it</b>. Those are your best chances.</li>
    <li><span class="pill lt">Long-tail</span> means a longer, more exact phrase (3–6 words). Fewer
      searches, but the customer knows what they want, so they buy more often.</li>
    <li>The <b>Top-Moving ASINs</b> table lower down shows the bulbs these words came from. Each month
      is marked ✓ if it sold more than {rules['top_moving_units_gt']}, and the
      <b>Months above {rules['top_moving_units_gt']}</b> column counts the ticks — a bulb is included
      when it has <b>{rules['top_moving_months_required']} or more</b> out of
      {len(per['months'])}.</li>
    <li>Use <b>Month</b> to see one month at a time, and <b>ASIN</b> to see the words for one product.</li>
    <li>Click <b>Searches / mo</b> at the top of the column to sort biggest first.</li>
    <li><b>Looking a product up in the Listing tool?</b> The blue boxed codes are
      <b>ASINs</b> (like <span class="asin">B08G4YZDH5</span>) — paste those into the tool's
      <b>ASIN</b> box. Plain codes like <span class="m">LDMG125E278_VDS</span> are <b>SKUs</b> — paste
      those into the <b>SKU</b> box. Putting a SKU in the ASIN box finds nothing.</li>
  </ol>
  <div class="tip">Use this tab when you are <b>writing or improving a listing</b> and need to know
    which words to include. To see which listings are <b>missing</b> these words, go to
    <b>Phase 2</b>.</div>
</details>
<div class="note p1"><b>These are the words real customers typed</b> to find your best-selling bulbs —
Amazon's own first-party data, not an estimate. They are the input to Phase 2.</div>
<div class="kpis">
  <div class="kpi"><div class="v">{len(tm)}</div><div class="k">Top-Moving ASINs<br>
    <span class="s">{tm_rule}</span></div></div>
  <div class="kpi"><div class="v">{with_terms}</div><div class="k">…with proven keywords<br>
    <span class="s">the rest had none that converted</span></div></div>
  <div class="kpi"><div class="v">{len(terms)}</div><div class="k">Keyword rows<br>
    <span class="s">one per ASIN per month</span></div></div>
  <div class="kpi o clk" data-f="op1"><div class="v">{sum(r['op'] for r in rows_t)}</div>
    <div class="k">Opportunity<br><span class="s">high demand, low share of it</span></div></div>
  <div class="kpi l clk" data-f="lt1"><div class="v">{sum(r['lt'] for r in rows_t)}</div>
    <div class="k">Long-tail<br><span class="s">3–6 words, 50–500 / mo</span></div></div>
</div>
<div class="bar">
  <input type="search" id="q1" placeholder="Search a keyword or ASIN…   (press / )">
  <label>Account<select id="br1"><option value="">All accounts</option>
    <option value="dcvoltage_uk">DCVOLTAGE UK</option><option value="ledsone_uk">LEDSone UK</option></select></label>
  <label>Month<select id="mo1"><option value="">All {nmonths} months</option></select></label>
  <label>ASIN<select id="a1"><option value="">All Top-Moving ASINs</option></select></label>
  <label>Min searches<input type="number" id="v1" min="0" step="50" placeholder="0"></label>
  <label class="chk"><input type="checkbox" id="op1"> Opportunity only</label>
  <label class="chk"><input type="checkbox" id="lt1"> Long-tail only</label>
  <button class="btn" id="rs1">Reset</button><span class="count" id="ct1"></span>
</div>
<main>
  <section><h2>Search terms <span class="n" id="nT"></span></h2>
  <p class="sub">One row per ASIN <b>per month</b> — the source requires the months checked separately,
  never combined. <b>Opportunity</b> = at or above the median demand but below the median share of it
  (the source names this pattern but gives no cut-off, so it is a median split of this run).
  <b>Long-tail</b> = 3–6 words, 50–500 searches a month.</p>
  <div class="wrap"><table id="tT"><thead><tr>
    <th data-k="mo">Month<span class="ar">▾</span></th>
    <th data-k="br">Account<span class="ar">▾</span></th>
    <th data-k="kw">Search term<span class="ar">▾</span></th>
    <th data-k="v" class="r">Searches / mo<span class="ar">▾</span></th>
    <th data-k="sh" class="r">Your share<span class="ar">▾</span></th>
    <th data-k="cr" class="r">Click rate<span class="ar">▾</span></th>
    <th data-k="pu" class="r">Purchases<span class="ar">▾</span></th>
    <th data-k="op" class="c">Pattern<span class="ar">▾</span></th>
    <th data-k="a">From <b>ASIN</b><span class="ar">▾</span></th></tr></thead><tbody></tbody></table>
    <div class="empty" hidden>Nothing matches these filters.</div></div></section>

  <section><h2>Top-Moving ASINs <span class="n" id="nM"></span></h2>
  <p class="sub">The best sellers these keywords came from. Units month by month, never combined.</p>
  <div class="wrap"><table id="tM"><thead><tr>
    <th data-k="br">Account<span class="ar">▾</span></th>
    <th data-k="a"><b>ASIN</b><span class="ar">▾</span></th>
    <th class="na">Units sold each month — ✓ means more than {rules['top_moving_units_gt']}</th>
    <th class="na c">Months above {rules['top_moving_units_gt']}</th>
    <th data-k="n" class="r">Proven keywords<span class="ar">▾</span></th></tr></thead><tbody></tbody></table>
    <div class="empty" hidden>Nothing matches these filters.</div></div></section>
</main>
</div>

<div id="p2" hidden>
<details class="help" id="h2" open>
  <summary>How to use this tab — your monthly to-do list</summary>
  <ol>
    <li>You sell the <b>same bulb</b> twice. One listing sells; the other sells nothing. Often the dead
      one is simply <b>missing the words</b> customers search for. This tab lists those words.</li>
    <li>There are <b>two jobs</b>, and they are different:
      <br><b>Part A</b> — the listing is <b>empty</b> (no bullet points, no keywords). It needs
      <b>writing</b>. The column <b>Keywords ready to use</b> tells you how many proven words are
      already waiting from the good twin.
      <br><b>Part B</b> — the listing has text, but <b>specific words are missing</b>. Each row tells
      you the word and exactly <b>where to put it</b>.
</li>
    <li><b>Only add the words shown in “Words to actually add”</b> — not the whole phrase. If the
      keyword is <i>e27 screw bulb</i> and the listing already has “e27” and “bulb”, the only thing
      missing is <b>screw</b>. The backend keyword box has a size limit, and Amazon says not to repeat
      words that are already there.</li>
    <li>In Part B, read the <b>What to do</b> column and follow it exactly:
      <br><span class="pill be">Add to backend</span> put it only in the backend keyword box
      <br><span class="pill bu">Add to bullets</span> put it only in the bullet points
      <br><span class="pill both">Add to backend + bullets</span> put it in both</li>
    <li><b>Work in batches.</b> Set <b>What to do</b> to “Add to backend”, do all of those in Seller
      Central in one go, then switch to the next one. Much faster than going listing by listing.</li>
    <li>Start with the <b>biggest numbers</b>. The list is already sorted by monthly searches, so the
      top rows are worth the most. Words fewer than
      <b>{rules['min_search_volume_for_gaps']} people</b> searched are left out — they are not worth
      your time. You can still see every word on the <b>Phase 1</b> tab.</li>
    <li>When you have finished a listing, set <b>View</b> to <b>“By listing”</b> and click its button
      to mark it done.</li>
    <li><b>Looking a listing up in the Listing tool?</b> The blue boxed codes are <b>ASINs</b>
      (like <span class="asin">B08G4YZDH5</span>) — paste those into the tool's <b>ASIN</b> box. Plain
      codes like <span class="m">LDMG125E278_VDS</span> are <b>SKUs</b> — paste those into the
      <b>SKU</b> box. Putting a SKU in the ASIN box finds nothing.</li>
  </ol>
  <div class="tip"><b>Two things to know.</b> Nothing here touches Amazon — you make the changes
    yourself, so nothing can go wrong by accident. And <b>if a word does not suit the bulb, do not add
    it</b> — the report finds words that work, but only you can judge whether a word really describes
    that product. Amazon does not like keywords that do not match.</div>
</details>
<div class="note p2"><b>This report changes nothing on Amazon.</b> It shows where each proven keyword
should go — a person adds it. (The source document's automatic push is deliberately out of scope.)</div>
<details class="help cov" open>
  <summary>Where did all {cov.get('total',0)} of your bulbs go?</summary>
  <p class="sub" style="padding-left:0;margin:0 0 10px">Every bulb in your “Bulbs” category is listed
  below, so nothing is silently left out.</p>
  <table class="covt">
    <tr><td class="n">{cov.get('top_moving',0)}</td><td><b>Your best sellers</b> — these supplied the
      proven keywords. Nothing to fix on them.</td></tr>
    <tr class="hi"><td class="n">{cov.get('in_report',0)}</td><td><b>In this report</b> — a listing
      below needs work. This is the list you act on.</td></tr>
    <tr><td class="n">{cov.get('selling_ok',0)}</td><td><b>Selling normally</b> — not a best seller,
      but not dying either. Nothing to fix.</td></tr>
    <tr><td class="n">{cov.get('under_no_gap',0)}</td><td><b>Struggling, but already have the words</b>
      — we checked them and found no missing keyword. Their problem is something else (price, stock,
      photos, reviews).</td></tr>
    <tr class="warnrow"><td class="n">{cov.get('under_no_twin',0)}</td><td><b>Struggling, but this
      report cannot help them</b> — there is no best-selling version of the same product to copy
      proven words from. <b>This is the biggest group.</b> They need keyword research of their own,
      not a copy.</td></tr>
  </table>
  <div class="tip">So this report acts on <b>{cov.get('in_report',0)}</b> bulbs. The
  <b>{cov.get('under_no_twin',0)}</b> in the last row are the real gap in coverage — worth discussing
  as separate work.</div>
</details>
<div class="kpis">
  <div class="kpi clk" data-f="secall"><div class="v">{len(pa)+len(pairsB)}</div>
    <div class="k">Underperforming listings<br><span class="s">no sales 6mo, or falling 3mo</span></div></div>
  <div class="kpi a clk" data-f="secA"><div class="v">{len(pa)}</div>
    <div class="k">Need a rewrite<br><span class="s">Part A — nothing on the listing</span></div></div>
  <div class="kpi b clk" data-f="secB"><div class="v">{len(gaps)}</div>
    <div class="k">Keyword gaps<br><span class="s">Part B — across {len(pairsB)} listings</span></div></div>
</div>
<div class="bar">
  <input type="search" id="q2" placeholder="Search ASIN, SKU or keyword…   (press / )">
  <label>Account<select id="br2"><option value="">All accounts</option>
    <option value="dcvoltage_uk">DCVOLTAGE UK</option><option value="ledsone_uk">LEDSone UK</option></select></label>
  <label>Show<select id="sec2"><option value="">Everything</option>
    <option value="A">A — needs rewrite</option>
    <option value="B">B — keyword gaps</option></select></label>
  <label>View<select id="vw2"><option value="flat">All keywords — one list</option>
    <option value="pair">By listing — with review buttons</option></select></label>
  <label>What to do<select id="tg2"><option value="">Any action</option>
    <option value="backend_and_bullet">Add to backend + bullets</option>
    <option value="backend">Add to backend</option><option value="bullet">Add to bullets</option>
    <option value="none">Nothing to do</option></select></label>
  <label>Why flagged<select id="ds2"><option value="">Any reason</option>
    <option value="zero_sales_6mo">No sales 6 months</option>
    <option value="sales_drop_3mo">Sales falling 3 months</option></select></label>
  <label>Min searches<input type="number" id="v2" min="0" step="10" placeholder="0"
    title="The report already excludes keywords under {rules['min_search_volume_for_gaps']} searches a month. Raise this to focus further."></label>
  <label class="chk"><input type="checkbox" id="gap2" checked> Only rows needing action</label>
  <button class="btn" id="rs2">Reset</button><span class="count" id="ct2"></span>
</div>
<main>
  <section class="A" id="secA"><h2>Part A — listing has no content <span class="n" id="nA"></span></h2>
  <p class="sub">Every keyword would read as “missing” because there is nothing on the listing to
  search. These need <b>writing</b>, not keyword edits. <b>Keywords ready to use</b> = how many proven
  search terms already exist on the good-selling twin, so whoever rewrites it does not start from a
  blank page. <b>0 — none</b> means the twin has no proven terms either.</p>
  <div class="wrap"><table id="tA"><thead><tr>
    <th data-k="da" class="pin">Dead listing — <b>ASIN</b><span class="ar">▾</span></th>
    <th data-k="br">Account<span class="ar">▾</span></th>
    <th data-k="sku">Its <b>SKU</b><span class="ar">▾</span></th>
    <th data-k="sk">Base SKU<span class="ar">▾</span></th>
    <th data-k="ds">Why flagged<span class="ar">▾</span></th>
    <th data-k="is">What is missing<span class="ar">▾</span></th>
    <th data-k="n" class="r">Keywords ready to use<span class="ar">▾</span></th>
    <th data-k="ta">Good twin — <b>ASIN</b><span class="ar">▾</span></th>
    <th class="na">Title</th></tr></thead><tbody></tbody></table>
    <div class="empty" hidden>Nothing matches these filters.</div></div></section>

  <section class="B" id="secB"><h2>Part B — keyword gaps <span class="n" id="nB"></span></h2>
  <p class="sub">Sorted by monthly searches — work down from the top. Switch <b>View</b> to
  “By listing” for the per-pair review buttons.</p>
  <div class="wrap"><table id="tB"><thead><tr>
    <th data-k="da" class="pin">Listing to fix — <b>ASIN</b><span class="ar">▾</span></th>
    <th data-k="kw">Keyword<span class="ar">▾</span></th>
    <th data-k="v" class="r">Searches / mo<span class="ar">▾</span></th>
    <th data-k="f" class="c">In text<span class="ar">▾</span></th>
    <th data-k="b" class="c">In backend<span class="ar">▾</span></th>
    <th data-k="t">What to do<span class="ar">▾</span></th>
    <th class="na">Words to actually add</th>
    <th data-k="br">Account<span class="ar">▾</span></th>
    <th data-k="ds">Why flagged<span class="ar">▾</span></th>
    <th data-k="sk">Base SKU<span class="ar">▾</span></th>
    <th data-k="ta">Keyword came from — <b>ASIN</b><span class="ar">▾</span></th></tr></thead><tbody></tbody></table>
    <div class="empty" hidden>Nothing matches these filters.</div></div>
  <div id="pairs" hidden></div></section>
</main>
</div>

<div id="p3" hidden>
<div class="note p1"><b>Every bulb in your category</b>, whether this report acts on it or not — with
its sales over the last 3 months and the last 6, and why it is or is not in the report.</div>
<div class="kpis">
  <div class="kpi clk" data-f="gb-"><div class="v">{cov.get('total',0)}</div>
    <div class="k">All your bulbs<br><span class="s">click a tile to filter</span></div></div>
  <div class="kpi b clk" data-f="gb-in_report"><div class="v">{cov.get('in_report',0)}</div>
    <div class="k">In this report<br><span class="s">needs work now</span></div></div>
  <div class="kpi c clk" data-f="gb-under_no_twin"><div class="v">{cov.get('under_no_twin',0)}</div>
    <div class="k">Struggling, no twin<br><span class="s">this report cannot help</span></div></div>
  <div class="kpi a clk" data-f="gb-under_no_gap"><div class="v">{cov.get('under_no_gap',0)}</div>
    <div class="k">Struggling, words OK<br><span class="s">problem is something else</span></div></div>
  <div class="kpi o clk" data-f="gb-selling_ok"><div class="v">{cov.get('selling_ok',0)}</div>
    <div class="k">Selling normally<br><span class="s">nothing to fix</span></div></div>
  <div class="kpi clk" data-f="gb-top_moving"><div class="v">{cov.get('top_moving',0)}</div>
    <div class="k">Best sellers<br><span class="s">gave the keywords</span></div></div>
</div>
<div class="bar">
  <input type="search" id="q3" placeholder="Search ASIN, SKU or product name…   (press / )">
  <label>Account<select id="br3"><option value="">All accounts</option>
    <option value="dcvoltage_uk">DCVOLTAGE UK</option>
    <option value="ledsone_uk">LEDSone UK</option></select></label>
  <label>What is happening<select id="bk3"><option value="">Everything</option>
    <option value="in_report">In this report — needs work</option>
    <option value="under_no_twin">Struggling — no twin to copy from</option>
    <option value="under_no_gap">Struggling — words already there</option>
    <option value="selling_ok">Selling normally</option>
    <option value="top_moving">Best seller — gave the keywords</option>
    <option value="sku_check">SKU code needs checking</option></select></label>
  <label>Sales<select id="sl3"><option value="">Any</option>
    <option value="none6">No sales in 6 months</option>
    <option value="none3">No sales in the 3 months</option>
    <option value="drop">Falling every month</option>
    <option value="some">Sold something</option></select></label>
  <button class="btn" id="rs3">Reset</button><span class="count" id="ct3"></span>
</div>
<main><section><h2>All bulbs <span class="n" id="nG"></span></h2>
  <p class="sub">One row per bulb. <b>Months above {rules['top_moving_units_gt']}</b> counts how many
  of the 3 months sold more than {rules['top_moving_units_gt']}. Click any heading to sort.</p>
  <div class="wrap"><table id="tG"><thead><tr>
    <th data-k="a"><b>ASIN</b><span class="ar">▾</span></th>
    <th data-k="sk">Its <b>SKU</b><span class="ar">▾</span></th>
    <th data-k="ac">Account<span class="ar">▾</span></th>
    <th class="na">Units each month</th>
    <th data-k="ma" class="c">Months above {rules['top_moving_units_gt']}<span class="ar">▾</span></th>
    <th data-k="u3" class="r">3-month sales<span class="ar">▾</span></th>
    <th data-k="u6" class="r">6-month sales<span class="ar">▾</span></th>
    <th data-k="st">What is happening<span class="ar">▾</span></th>
    <th class="na">Product</th></tr></thead><tbody></tbody></table>
    <div class="empty" hidden>Nothing matches these filters.</div></div></section></main>
</div>

<footer>
<b>How each figure is decided.</b> Keywords come from Amazon <b>Search Query Performance</b>, the
ASIN-level view the source requires, for {E(per['start'])} → {E(per['end'])} — the last {nmonths}
complete months, assembled from Amazon's weekly rows with rates recomputed from their numerator and
denominator, never averaged, and the months kept separate as the source insists ·
Top-Moving = {tm_rule}, within the requester's own “Bulbs” category ·
top {rules['terms_per_asin']} keywords per ASIN per month, terms with no purchases dropped ·
<b>a keyword only reaches the Part B list if at least {rules['min_search_volume_for_gaps']} people
searched it in a month</b> (Phase 1 is unfiltered, so the full set is still there) ·
base SKU = pack size, trailing markers and account suffixes stripped, using the SKU mapping table
(<code>mapped_sku</code>); bundles kept whole ·
underperforming = no sales in {rules['zero_sales_window_months']} months (counted from the product
list, so listings absent from the sales report still count) or falling every month ·
a keyword counts as present if <b>all its words appear anywhere</b> in the text, any order, ignoring
capitals and punctuation · a pair is rejected when the two listings state a different wattage or cap
fitting.<br>
A click rate shown in <span class="odd">amber</span> is above 100% — Amazon's own figure, which happens
when one search produces several clicks on a term whose recorded volume is very low. Hover any long
title or note to read it in full.<br>
<b>Self-checks:</b> {qa_line}.<br>
Source: BGCT_Keyword_Workflow_Phase1_Phase2_v2.1.pdf · PRJ-2026-026 / REQ-30 (bgct) ·
independently validated 10/10 · <b>not yet signed off</b>. Shortcuts: <kbd>/</kbd> search,
<kbd>Esc</kbd> clear.
</footer>

<script>
const D = {data};
const BR = {json.dumps(BRANDS)}, ST = {json.dumps(STATUS)}, TG = {json.dumps(TARGET)};
const PILL = {{backend_and_bullet:'both',backend:'be',bullet:'bu',none:'no'}};
// Only the words that are genuinely absent - never the whole phrase. The backend keyword field is a
// bag of words with a byte limit, so repeating words already there wastes it.
function words(r){{
  const chip=(w,cls)=>`<span class="wd ${{cls}}">${{esc(w)}}</span>`;
  const out=[];
  if(r.t==='none') return '<span class="s">—</span>';
  if(r.mb && (r.t==='backend'||r.t==='backend_and_bullet'))
    out.push('<span class="s">backend:</span> '+r.mb.split(' ').map(w=>chip(w,'be')).join(' '));
  if(r.mf && (r.t==='bullet'||r.t==='backend_and_bullet'))
    out.push('<span class="s">bullets:</span> '+r.mf.split(' ').map(w=>chip(w,'bu')).join(' '));
  return out.join('<br>') || '<span class="s">—</span>';
}}
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const esc = s => String(s==null?'':s).replace(/[&<>"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));
const num = x => x==null ? '<span class="s">—</span>' : x.toLocaleString();
const pct = x => x==null ? '<span class="s">—</span>' : x.toFixed(2)+'%';
// Amazon reports >100% when a single search produces several clicks; show it, but flag it
const rate = x => x==null ? '<span class="s">—</span>'
  : (x>100 ? `<span class="odd" title="Amazon reports more than one click per search for this term - its recorded search volume is very low, so treat this figure with care">${{x.toFixed(0)}}%</span>`
           : x.toFixed(2)+'%');
const sort = {{T:{{k:'v',d:-1}},M:{{k:'n',d:-1}},A:{{k:'sk',d:1}},B:{{k:'v',d:-1}},
  G:{{k:'u6',d:-1}}}};
const UNITS_GT = {rules['top_moving_units_gt']}, MONTHS = {json.dumps([m[:7] for m in per['months']])};
const REVIEWED = {{}};        // 2.9 action_state - in-page only, never sent to Amazon
let tab='1', sec='';

function order(rows,k,d){{
  return rows.slice().sort((a,b)=>{{
    let x=a[k], y=b[k];
    if(x==null) x = (typeof y==='number')?-1:'';
    if(y==null) y = (typeof x==='number')?-1:'';
    if(typeof x==='number'||typeof y==='number') return ((x||0)-(y||0))*d;
    return String(x).localeCompare(String(y))*d;
  }});
}}
function arrows(){{ $$('th[data-k]').forEach(th=>{{
  const t=th.closest('table').id.slice(1), on=sort[t] && sort[t].k===th.dataset.k;
  th.classList.toggle('sorted',!!on);
  th.querySelector('.ar').textContent = on ? (sort[t].d>0?'▲':'▼') : '▾';
}}); }}

/* ---------------- PHASE 1 ---------------- */
$('#mo1').insertAdjacentHTML('beforeend',
  [...new Set(D.t.map(r=>r.mo))].sort().map(m=>`<option value="${{m}}">${{m}}</option>`).join(''));
const byAsin={{}}; D.t.forEach(r=>byAsin[r.a]=(byAsin[r.a]||0)+1);
$('#a1').insertAdjacentHTML('beforeend', Object.keys(byAsin).sort((x,y)=>byAsin[y]-byAsin[x])
  .map(a=>`<option value="${{a}}">${{a}} (${{byAsin[a]}})</option>`).join(''));

function draw1(){{
  const f={{q:$('#q1').value.trim().toLowerCase(),br:$('#br1').value,mo:$('#mo1').value,
            a:$('#a1').value,v:parseInt($('#v1').value||'0',10)||0,
            op:$('#op1').checked,lt:$('#lt1').checked}};
  const T=order(D.t.filter(r=>
    (!f.mo||r.mo===f.mo)&&(!f.br||r.br===f.br)&&(!f.a||r.a===f.a)&&r.v>=f.v&&
    (!f.op||r.op)&&(!f.lt||r.lt)&&(!f.q||(r.kw+' '+r.a).toLowerCase().includes(f.q))),sort.T.k,sort.T.d);
  const M=order(D.m.filter(r=>
    (!f.br||r.br===f.br)&&(!f.a||r.a===f.a)&&(!f.q||r.a.toLowerCase().includes(f.q))),sort.M.k,sort.M.d);

  $('#tT tbody').innerHTML=T.map(r=>`<tr><td class="m">${{esc(r.mo)}}</td>
    <td><span class="pill acc">${{esc(BR[r.br])}}</span></td><td class="kw">${{esc(r.kw)}}</td>
    <td class="r">${{num(r.v)}}</td><td class="r">${{pct(r.sh)}}</td><td class="r">${{rate(r.cr)}}</td>
    <td class="r">${{num(r.pu)}}</td>
    <td class="c">${{r.op?'<span class="pill op">Opportunity</span> ':''}}${{r.lt?'<span class="pill lt">Long-tail</span>':''}}${{(!r.op&&!r.lt)?'<span class="s">—</span>':''}}</td>
    <td><span class="asin">${{esc(r.a)}}</span></td></tr>`).join('');
  $('#tM tbody').innerHTML=M.map(r=>{{
    const cells = r.u.map((v,i)=>{{
      const ok = v > UNITS_GT;
      return `<span class="mth ${{ok?'ok':'no'}}" title="${{MONTHS[i]}}: ${{v}} units">`
           + `${{MONTHS[i].slice(5)}} <b>${{v}}</b> ${{ok?'✓':'✗'}}</span>`;
    }}).join('');
    const n = r.u.filter(v=>v>UNITS_GT).length;
    return `<tr><td><span class="pill acc">${{esc(BR[r.br])}}</span></td>
    <td><span class="asin">${{esc(r.a)}}</span></td><td>${{cells}}</td>
    <td class="c"><b>${{n}} of ${{r.u.length}}</b></td>
    <td class="r">${{r.n}}</td></tr>`;}}).join('');
  $('#nT').textContent = T.length===D.t.length?`(${{D.t.length}})`:`(${{T.length}} of ${{D.t.length}})`;
  $('#nM').textContent = M.length===D.m.length?`(${{D.m.length}})`:`(${{M.length}} of ${{D.m.length}})`;
  [['T',T],['M',M]].forEach(([s,rows])=>{{ $('#t'+s).hidden=rows.length===0;
    $('#t'+s).closest('.wrap').querySelector('.empty').hidden=rows.length!==0; }});
  $('#ct1').innerHTML=`Showing <b>${{T.length}}</b> keyword row${{T.length===1?'':'s'}}`
    +(T.length!==D.t.length?` of ${{D.t.length}}`:'')
    +` · <b>${{new Set(T.map(r=>r.a)).size}}</b> ASINs`;
  $('.kpi.o').classList.toggle('on',f.op); $('.kpi.l').classList.toggle('on',f.lt);
  arrows();
}}

/* ---------------- PHASE 2 ---------------- */
function F2(){{ return {{q:$('#q2').value.trim().toLowerCase(),br:$('#br2').value,
  tg:$('#tg2').value,ds:$('#ds2').value,v:parseInt($('#v2').value||'0',10)||0,g:$('#gap2').checked}}; }}
function keep2(r,f,kind){{
  if(f.br && r.br!==f.br) return false;
  if(f.ds && r.ds && r.ds!==f.ds) return false;
  if(kind==='B'){{ if(f.g && r.t==='none') return false;
    if(f.tg && r.t!==f.tg) return false; if(r.v<f.v) return false; }}
  else if(f.tg||f.v) return false;
  if(f.q){{ const h=[r.da,r.ta,r.sk,r.sku,r.kw,r.ti].filter(Boolean).join(' ').toLowerCase();
    if(!h.includes(f.q)) return false; }}
  return true;
}}
function draw2(){{
  const f=F2();
  const A=(sec&&sec!=='A')?[]:order(D.a.filter(r=>keep2(r,f,'A')),sort.A.k,sort.A.d);
  const B=(sec&&sec!=='B')?[]:order(D.b.filter(r=>keep2(r,f,'B')),sort.B.k,sort.B.d);

  $('#tA tbody').innerHTML=A.map(r=>`<tr>
    <td class="pin"><span class="asin">${{esc(r.da)}}</span></td>
    <td><span class="pill acc">${{esc(BR[r.br])}}</span></td><td class="m s">${{esc(r.sku)}}</td>
    <td class="m">${{esc(r.sk)}}</td>
    <td>${{esc(ST[r.ds]||r.ds)}}</td>
    <td class="warnt clip" title="${{esc(r.is)}}">${{esc(r.is)}}</td>
    <td class="r">${{r.n?r.n:'<span class="warnt">0 — none</span>'}}</td>
    <td><span class="asin">${{esc(r.ta)}}</span></td>
    <td class="s clip wide" title="${{esc(r.ti)}}">${{esc(r.ti)}}</td></tr>`).join('');
  $('#tB tbody').innerHTML=B.map(r=>`<tr class="${{r.t==='none'?'':'gap'}}">
    <td class="pin"><span class="asin">${{esc(r.da)}}</span></td>
    <td class="kw">${{esc(r.kw)}}</td>
    <td class="r">${{r.v.toLocaleString()}}</td>
    <td class="c"><span class="tick ${{r.f?'y':'n'}}">${{r.f?'✓':'✗'}}</span></td>
    <td class="c"><span class="tick ${{r.b?'y':'n'}}">${{r.b?'✓':'✗'}}</span></td>
    <td><span class="pill ${{PILL[r.t]}}">${{esc(TG[r.t])}}</span></td>
    <td>${{words(r)}}</td>
    <td><span class="pill acc">${{esc(BR[r.br])}}</span></td>
    <td>${{esc(ST[r.ds]||r.ds)}}</td>
    <td class="m">${{esc(r.sk)}}</td><td><span class="asin">${{esc(r.ta)}}</span></td></tr>`).join('');

  /* grouped view - source 2.6 (per-pair status) + 2.7 (the two buttons) */
  const grouped=$('#vw2').value==='pair';
  $('#tB').closest('.wrap').hidden = grouped||B.length===0;
  $('#pairs').hidden = !grouped;
  if(grouped){{
    const g={{}}; B.forEach(r=>{{const k=r.br+'|'+r.ta+'|'+r.da;(g[k]=g[k]||[]).push(r);}});
    const keys=Object.keys(g).sort((x,y)=>
      g[y].filter(r=>r.t!=='none').length-g[x].filter(r=>r.t!=='none').length);
    $('#pairs').innerHTML=keys.map(k=>{{
      const rs=g[k],r0=rs[0],nG=rs.filter(r=>r.t!=='none').length;
      const btn = (nG===0 && !f.g)
        ? `<button class="act ok" data-p="${{k}}">All keywords present · Mark reviewed</button>`
        : `<button class="act add" data-p="${{k}}">Add missing keywords (${{nG}})</button>`;
      return `<div class="pair"><div class="ph"><div><span class="tag">Top-Moving</span>
        <b class="m">${{esc(r0.ta)}}</b><span class="arrow">→</span>
        <span class="tag dead">${{esc(ST[r0.ds]||r0.ds)}}</span> <b class="m">${{esc(r0.da)}}</b>
        <span class="pill acc">${{esc(BR[r0.br])}}</span>
        <div class="sk">base SKU ${{esc(r0.sk)}} · ${{rs.length}} keyword${{rs.length===1?'':'s'}} shown
          · action_state <b>${{nG?'pending_add':'reviewed'}}</b></div></div>
        <div>${{btn}}<span class="state"></span></div></div>
        <div class="wrap"><table><thead><tr><th class="na">Keyword</th><th class="na r">Searches / mo</th>
        <th class="na c">In text</th><th class="na c">In backend</th><th class="na">What to do</th>
        <th class="na">Words to actually add</th></tr></thead><tbody>${{rs.map(r=>`<tr class="${{r.t==='none'?'':'gap'}}">
          <td class="kw">${{esc(r.kw)}}</td><td class="r">${{r.v.toLocaleString()}}</td>
          <td class="c"><span class="tick ${{r.f?'y':'n'}}">${{r.f?'✓':'✗'}}</span></td>
          <td class="c"><span class="tick ${{r.b?'y':'n'}}">${{r.b?'✓':'✗'}}</span></td>
          <td><span class="pill ${{PILL[r.t]}}">${{esc(TG[r.t])}}</span></td>
          <td>${{words(r)}}</td></tr>`).join('')}}
        </tbody></table></div></div>`;
    }}).join('') || '<div class="empty">Nothing matches these filters.</div>';
    $$('#pairs .act').forEach(b=>b.addEventListener('click',()=>{{
      const st = REVIEWED[b.dataset.p] = b.classList.contains('ok')?'reviewed':'added';
      b.className='act done'; b.textContent = st==='reviewed'?'Reviewed ✓':'Marked as added ✓';
      b.nextElementSibling.textContent='recorded in this page only — nothing was sent to Amazon';
    }}));
  }}

  const set=(id,n,t)=>{{ $(id).textContent = n===t?`(${{t}})`:`(${{n}} of ${{t}})`; }};
  set('#nA',A.length,D.a.length); set('#nB',B.length,D.b.length);
  ['A','B'].forEach(s=>{{ const rows={{A:A,B:B}}[s];
    $('#sec'+s).hidden = !!(sec&&sec!==s);
    if(s!=='B') $('#t'+s).hidden = rows.length===0;
    $('#sec'+s+' .empty').hidden = rows.length!==0; }});
  const shown=A.length+B.length, tot=D.a.length+D.b.length;
  $('#ct2').innerHTML=`Showing <b>${{shown}}</b> row${{shown===1?'':'s'}}`
    +(f.g?` · <b>${{D.b.filter(r=>r.t!=='none').length}}</b> gaps in total`:` of ${{tot}}`);
  $$('#p2 .kpi').forEach(k=>k.classList.toggle('on',
    k.dataset.f==='secall' ? sec==='' : k.dataset.f==='sec'+sec));
  arrows();
}}

/* ---------------- ALL BULBS ---------------- */
const BK={{in_report:'bk',under_no_twin:'wn',under_no_gap:'am',selling_ok:'ok',top_moving:'tm',
  sku_check:'lt'}};
function draw3(){{
  const q=$('#q3').value.trim().toLowerCase(), br=$('#br3').value,
        bk=$('#bk3').value, sl=$('#sl3').value;
  const G=order(D.g.filter(r=>{{
    if(bk && r.b!==bk) return false;
    if(br && r.ac.indexOf(br)<0) return false;
    if(sl==='none6' && r.u6!==0) return false;
    if(sl==='none3' && r.u3!==0) return false;
    if(sl==='some'  && r.u3===0) return false;
    if(sl==='drop'){{ const u=r.u; if(!(u[0]>u[1] && u[1]>u[2] && u[0]>0)) return false; }}
    if(q && (r.a+' '+r.sk+' '+r.bs+' '+r.ti).toLowerCase().indexOf(q)<0) return false;
    return true;
  }}),sort.G.k,sort.G.d);
  $('#tG tbody').innerHTML=G.map(r=>{{
    const cells=r.u.map((v,i)=>`<span class="mth ${{v>UNITS_GT?'ok':'no'}}" title="${{MONTHS[i]}}: ${{v}}">`
      +`${{MONTHS[i].slice(5)}} <b>${{v}}</b></span>`).join('');
    return `<tr><td><span class="asin">${{esc(r.a)}}</span></td><td class="m s">${{esc(r.sk)}}</td>
      <td class="s">${{esc(r.ac)}}</td><td>${{cells}}</td>
      <td class="c"><b>${{r.ma}}</b></td>
      <td class="r">${{r.u3?r.u3.toLocaleString():'<span class="s">0</span>'}}</td>
      <td class="r">${{r.u6?r.u6.toLocaleString():'<span class="s">0</span>'}}</td>
      <td><span class="pill ${{BK[r.b]||''}}">${{esc(r.st)}}</span></td>
      <td class="s clip wide" title="${{esc(r.ti)}}">${{esc(r.ti)}}</td></tr>`;}}).join('');
  $('#nG').textContent = G.length===D.g.length?`(${{D.g.length}})`:`(${{G.length}} of ${{D.g.length}})`;
  $('#tG').hidden=G.length===0;
  $('#tG').closest('.wrap').querySelector('.empty').hidden=G.length!==0;
  const noSale=G.filter(r=>r.u6===0).length;
  $('#ct3').innerHTML=`Showing <b>${{G.length}}</b> bulb${{G.length===1?'':'s'}}`
    +(G.length!==D.g.length?` of ${{D.g.length}}`:'')
    +` · <b>${{noSale}}</b> with no sales in 6 months`;
  $$('#p3 .kpi').forEach(k=>k.classList.toggle('on',k.dataset.f==='gb-'+bk));
  arrows();
}}

/* ---------------- wiring ---------------- */
function tabTo(t){{ tab=t;
  $('#p1').hidden=t!=='1'; $('#p2').hidden=t!=='2'; $('#p3').hidden=t!=='3';
  $$('.tab').forEach(b=>b.classList.toggle('on',b.dataset.t===t));
  (t==='1'?draw1:t==='2'?draw2:draw3)(); }}
$$('.tab').forEach(b=>b.addEventListener('click',()=>tabTo(b.dataset.t)));
// The instructions collapse via the browser's own <details> element - no script, no storage, so
// there is nothing here that can fail or block the tables from drawing.

['q1','br1','mo1','a1','v1','op1','lt1'].forEach(id=>{{
  $('#'+id).addEventListener('input',draw1); $('#'+id).addEventListener('change',draw1); }});
['q2','br2','tg2','ds2','v2','gap2','vw2'].forEach(id=>{{
  $('#'+id).addEventListener('input',draw2); $('#'+id).addEventListener('change',draw2); }});
$('#sec2').addEventListener('change',e=>{{ sec=e.target.value; draw2(); }});
['q3','br3','bk3','sl3'].forEach(id=>{{
  $('#'+id).addEventListener('input',draw3); $('#'+id).addEventListener('change',draw3); }});
$$('#p3 .kpi.clk').forEach(k=>k.addEventListener('click',()=>{{
  const want=k.dataset.f.slice(3);
  $('#bk3').value = ($('#bk3').value===want?'':want); draw3(); }}));
$('#rs3').addEventListener('click',()=>{{
  ['q3','br3','bk3','sl3'].forEach(i=>$('#'+i).value='');
  sort.G={{k:'u6',d:-1}}; draw3(); }});
$('#tg2').addEventListener('change',e=>{{ if(e.target.value==='none') $('#gap2').checked=false; draw2(); }});
$$('#p1 .kpi.clk').forEach(k=>k.addEventListener('click',()=>{{
  const b=$('#'+k.dataset.f); b.checked=!b.checked; draw1(); }}));
$$('#p2 .kpi.clk').forEach(k=>k.addEventListener('click',()=>{{
  const want = k.dataset.f==='secall' ? '' : k.dataset.f.slice(3);
  sec = (sec===want) ? '' : want; $('#sec2').value=sec; draw2(); }}));
$('#rs1').addEventListener('click',()=>{{ ['q1','br1','mo1','a1','v1'].forEach(i=>$('#'+i).value='');
  $('#op1').checked=false; $('#lt1').checked=false; sort.T={{k:'v',d:-1}}; sort.M={{k:'n',d:-1}}; draw1(); }});
$('#rs2').addEventListener('click',()=>{{ ['q2','br2','tg2','ds2','v2'].forEach(i=>$('#'+i).value='');
  $('#gap2').checked=true; $('#vw2').value='flat'; sec=''; $('#sec2').value=''; draw2(); }});
$$('th[data-k]').forEach(th=>th.addEventListener('click',()=>{{
  const t=th.closest('table').id.slice(1), k=th.dataset.k;
  if(!sort[t]) return;
  if(sort[t].k===k) sort[t].d*=-1;
  else sort[t]={{k:k,d:(k==='v'||k==='n'||k==='pu'||k==='sh'||k==='cr')?-1:1}};
  (tab==='1'?draw1:tab==='2'?draw2:draw3)(); }}));
addEventListener('keydown',e=>{{
  if(e.key==='/' && e.target.tagName!=='INPUT'){{ e.preventDefault();
    $(tab==='1'?'#q1':tab==='2'?'#q2':'#q3').focus(); }}
  if(e.key==='Escape'){{ $(tab==='1'?'#q1':tab==='2'?'#q2':'#q3').value='';
    (tab==='1'?draw1:tab==='2'?draw2:draw3)(); }} }});
draw1();
</script></body></html>"""

    os.makedirs(OUTDIR, exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(doc)
    removed = []
    for f in SUPERSEDED:
        old = os.path.join(OUTDIR, f)
        if os.path.exists(old):
            os.remove(old); removed.append(f)
    print(f"dashboard -> {OUT}")
    print(f"Phase 1: {len(terms)} keyword rows, {with_terms}/{len(tm)} ASINs with terms | "
          f"Phase 2: {len(pa)} Part A, {len(pairsB)} Part B listings, {len(gaps)} gaps, {len(pc)} Part C")
    print(f"{len(doc):,} bytes" + (f" | removed superseded: {', '.join(removed)}" if removed else ""))


if __name__ == "__main__":
    main()
