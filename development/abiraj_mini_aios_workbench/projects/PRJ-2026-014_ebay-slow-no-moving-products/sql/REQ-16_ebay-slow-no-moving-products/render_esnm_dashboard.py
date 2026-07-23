# -*- coding: utf-8 -*-
"""
REQ-16-D01 — eBay Slow Moving & No Moving Products, reviewer dashboard.

Renders a single self-contained full-screen HTML console showing the report in the exact
20-column format of the requirement sheet, with date + dimension filters above the table.

Reuses build_esnm_d01.fetch()/assemble() so the dashboard and the workbook can never drift.
Row virtualisation keeps 11,156 rows scrolling smoothly; dictionary encoding keeps the file small.
"""
import os, sys, json, io
from datetime import timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import build_esnm_d01 as B

PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
FINAL = os.path.join(PROJ, "evidence", "final_outputs", "REQ-16_ebay-slow-no-moving-products")
OUT_HTML = os.path.join(FINAL, "REQ-16-D01_esnm_dashboard.html")
OUT_JSON = os.path.join(FINAL, "esnm_d01_data.json")

PRIO_ORDER = ["Critical", "High", "Medium", "Low", ""]


def encode(rows, cov):
    """Dictionary-encode repeating strings; emit compact row arrays."""
    dicts = {k: [] for k in ("account", "brand", "category", "status", "action", "site")}
    index = {k: {} for k in dicts}

    def idx(kind, val):
        val = val or ""
        m = index[kind]
        if val not in m:
            m[val] = len(dicts[kind])
            dicts[kind].append(val)
        return m[val]

    out = []
    for r in rows:
        last_sale = None
        if not r["idle_is_proxy"] and r["idle_days"] is not None:
            last_sale = (B.ANCHOR - timedelta(days=int(r["idle_days"]))).isoformat()
        out.append([
            r["img_only"] or "",                           # 0  real image URL (thumbnail)
            idx("account", r["account"]),                  # 1
            idx("brand", r["brand"]),                      # 2
            r["sku"] or "",                                # 3
            r["item_id"],                                  # 4
            r["title"] or "",                              # 5
            idx("category", r["category"]),                # 6
            round(r["price"], 2) if r["price"] is not None else None,   # 7
            r["currency"],                                 # 8
            r["stock"] or 0,                               # 9
            r["s7"], r["s30"], r["s90"], r["s90_ly"],      # 10-13
            (round(r["trend"], 4) if r["trend"] is not None else None), # 14
            r["idle_days"],                                # 15
            (r["views"] if r["has_traffic"] else None),    # 16
            None,                                          # 17 watchers - no source
            (round(r["cvr"], 5) if (r["has_traffic"] and r["cvr"] is not None) else None), # 18
            idx("status", r["status"]),                    # 19
            idx("action", r["action"]),                    # 20
            PRIO_ORDER.index(r["priority"]),               # 21
            r["rule_no"],                                  # 22
            last_sale,                                     # 23
            idx("site", r["site"]),                        # 24
            1 if r["idle_is_proxy"] else 0,                # 25 never sold
            r["s30_ly"],                                   # 26 same period last year, 30 days
        ])

    counts = {}
    for r in rows:
        counts[r["rule_no"]] = counts.get(r["rule_no"], 0) + 1

    gbp = sum((r["stock"] or 0) * (r["price"] or 0) for r in rows
              if r["rule_no"] == 1 and r["currency"] == "GBP")
    eur = sum((r["stock"] or 0) * (r["price"] or 0) for r in rows
              if r["rule_no"] == 1 and r["currency"] == "EUR")
    dead_units = sum((r["stock"] or 0) for r in rows if r["s90"] <= 0)

    return dict(
        anchor=B.ANCHOR.isoformat(),
        rows=out, dicts=dicts,
        actions={str(k): v for k, v in sorted(counts.items())},
        kpi=dict(total=len(rows),
                 critical=counts.get(1, 0),
                 dead_units=int(dead_units),
                 gbp_at_risk=round(gbp, 2), eur_at_risk=round(eur, 2),
                 accounts=len({r["account"] for r in rows}),
                 no_traffic=sum(1 for r in rows if not r["has_traffic"])),
        cov=cov,
        windows=dict(w7=[ (B.ANCHOR - timedelta(days=6)).isoformat(), B.ANCHOR.isoformat() ],
                     w30=[ B.W30_A.isoformat(), B.ANCHOR.isoformat() ],
                     w90=[ B.W90_A.isoformat(), B.ANCHOR.isoformat() ],
                     ly=[ B.LY_A.isoformat(), B.LY_B.isoformat() ]),
        rules=[dict(n=n, action=B.ACTIONS[n][0], prio=B.ACTIONS[n][1]) for n in sorted(B.ACTIONS)],
    )


HTML = r"""<!doctype html>
<!-- data-theme="light" is set deliberately: the light palette is the specified default and must
     NOT follow the viewer's OS dark-mode preference. Dark remains available via the toggle. -->
<html lang="en" data-theme="light"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>eBay Slow Moving &amp; No Moving Products — REQ-16-D01</title>
<style>
*,*::before,*::after{box-sizing:border-box}
:root{
  --bg:#f2f6fd; --bg2:#e9eff9; --card:#fff; --card2:#fbfcff;
  --ink:#111827; --ink2:#374151; --muted:#6b7280; --faint:#9ca3af;
  --line:#e4eaf4; --line2:#eef2f9;
  --accent:#4f46e5; --accent2:#0ea5e9; --accent-soft:#eef2ff; --accent-bd:#c7d2fe;
  --crit:#dc2626; --critbg:#fef2f2; --critbd:#fecaca;
  --high:#ea580c; --highbg:#fff7ed; --highbd:#fed7aa;
  --med:#b45309;  --medbg:#fffbeb;  --medbd:#fde68a;
  --low:#059669;  --lowbg:#ecfdf5;  --lowbd:#a7f3d0;
  --none:#64748b; --nonebg:#f8fafc; --nonebd:#e2e8f0;
  --sh-xs:0 1px 2px rgba(17,24,39,.04);
  --sh:0 2px 8px rgba(17,24,39,.06),0 1px 2px rgba(17,24,39,.04);
  --sh-md:0 8px 22px rgba(17,24,39,.09),0 2px 6px rgba(17,24,39,.05);
  --sh-lg:0 18px 44px rgba(17,24,39,.14);
  --rowh:48px; --r:14px; --ease:cubic-bezier(.22,.9,.3,1);
}
:root[data-theme=dark]{
  --bg:#0d1424; --bg2:#0a101d; --card:#141c2e; --card2:#182135;
  --ink:#eef3fb; --ink2:#cbd5e1; --muted:#94a3b8; --faint:#64748b;
  --line:#243149; --line2:#1c2740;
  --accent:#818cf8; --accent2:#38bdf8; --accent-soft:#1e254a; --accent-bd:#3b4794;
  --crit:#fca5a5; --critbg:#2c1416; --critbd:#7f1d1d;
  --high:#fdba74; --highbg:#2a1a0e; --highbd:#7c2d12;
  --med:#fcd34d;  --medbg:#271f0c;  --medbd:#78350f;
  --low:#6ee7b7;  --lowbg:#06251c;  --lowbd:#065f46;
  --none:#94a3b8; --nonebg:#151d2f; --nonebd:#2b3852;
  --sh:0 2px 8px rgba(0,0,0,.45); --sh-md:0 8px 22px rgba(0,0,0,.5);
  --sh-lg:0 18px 44px rgba(0,0,0,.6); --sh-xs:0 1px 2px rgba(0,0,0,.4);
}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){
  --bg:#0d1424; --bg2:#0a101d; --card:#141c2e; --card2:#182135;
  --ink:#eef3fb; --ink2:#cbd5e1; --muted:#94a3b8; --faint:#64748b;
  --line:#243149; --line2:#1c2740;
  --accent:#818cf8; --accent2:#38bdf8; --accent-soft:#1e254a; --accent-bd:#3b4794;
  --crit:#fca5a5; --critbg:#2c1416; --critbd:#7f1d1d;
  --high:#fdba74; --highbg:#2a1a0e; --highbd:#7c2d12;
  --med:#fcd34d;  --medbg:#271f0c;  --medbd:#78350f;
  --low:#6ee7b7;  --lowbg:#06251c;  --lowbd:#065f46;
  --none:#94a3b8; --nonebg:#151d2f; --nonebd:#2b3852;
  --sh:0 2px 8px rgba(0,0,0,.45); --sh-md:0 8px 22px rgba(0,0,0,.5);
  --sh-lg:0 18px 44px rgba(0,0,0,.6); --sh-xs:0 1px 2px rgba(0,0,0,.4);
}}

html,body{height:100%}
body{margin:0;color:var(--ink);
  background:linear-gradient(180deg,var(--bg) 0%,var(--bg2) 100%) fixed;
  font:13px/1.45 "Inter","Segoe UI",system-ui,-apple-system,Arial,sans-serif;
  -webkit-font-smoothing:antialiased;display:flex;flex-direction:column;overflow:hidden;
  /* EMBEDDED-SAFE. Inside the ph_task panel the host container can be only a few hundred px
     tall, which collapses the flex table to ~2 rows (reported 2026-07-22).
     This floor is deliberately a FIXED px value, NOT min(...,100vh): in an iframe 100vh
     resolves to the iframe's own short height, so a vh-based floor evaluates to the very
     height we are trying to escape and does nothing. A flat floor makes the host scroll
     instead, which is what gives the table real estate. In a normal browser window
     height:100% is larger and wins, so the single-view layout is unchanged. */
  min-height:560px;}
body:fullscreen, body:-webkit-full-screen{min-height:100%}
.num{font-variant-numeric:tabular-nums;font-feature-settings:"tnum" 1}

@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes sheen{from{background-position:-180% 0}to{background-position:280% 0}}
@media (prefers-reduced-motion:reduce){*{animation:none !important;transition:none !important}}

/* ================= header ================= */
header{flex:none;padding:13px 22px 0;position:relative;
  background:linear-gradient(180deg,var(--card) 0%,var(--card) 62%,transparent 100%)}
header::before{content:"";position:absolute;inset:0 0 auto 0;height:3px;
  background:linear-gradient(90deg,var(--accent),var(--accent2),var(--low));
  background-size:220% 100%;animation:sheen 9s linear infinite}
.htop{display:flex;align-items:flex-start;gap:18px;flex-wrap:wrap;animation:rise .5s var(--ease) both}
.brand{display:flex;align-items:center;gap:11px}
/* eBay wordmark — drawn from text in the four brand colours so the file stays fully
   self-contained (no external image request, works offline). Nominative use: it labels which
   marketplace the data came from; it does not imply eBay produced this report. */
.logo{height:38px;padding:0 13px;border-radius:11px;flex:none;display:flex;align-items:center;
  background:#fff;border:1px solid var(--line);box-shadow:var(--sh);
  font-family:"Market Sans","Helvetica Neue",Helvetica,Arial,sans-serif;
  font-size:23px;font-weight:800;letter-spacing:-.055em;line-height:1;
  transition:transform .25s var(--ease),box-shadow .25s var(--ease)}
.logo:hover{transform:translateY(-1px) scale(1.03);box-shadow:var(--sh-md)}
.logo i{font-style:normal}
.logo .e{color:#e53238}.logo .b{color:#0064d2}
.logo .a{color:#f5af02}.logo .y{color:#86b817}
.logo .mk{font-size:9px;font-weight:700;color:var(--muted);letter-spacing:.6px;
  text-transform:uppercase;margin-left:9px;padding-left:9px;border-left:1px solid var(--line)}
h1{margin:0;font-size:18px;font-weight:680;letter-spacing:-.02em;color:var(--ink)}
.sub{color:var(--muted);font-size:11.5px;margin-top:2px}
.sub b{color:var(--ink2);font-weight:620}
.spacer{flex:1}
.themebtn{background:var(--card);border:1px solid var(--line);color:var(--ink2);
  border-radius:10px;padding:8px 13px;cursor:pointer;font:inherit;font-size:12px;font-weight:600;
  box-shadow:var(--sh-xs);transition:.22s var(--ease)}
.themebtn:hover{border-color:var(--accent);color:var(--accent);
  box-shadow:0 4px 12px rgba(79,70,229,.16);transform:translateY(-1px)}

/* ================= KPI cards ================= */
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(172px,1fr));gap:9px;margin:11px 0 0}
.kpi{position:relative;background:linear-gradient(160deg,var(--card) 0%,var(--card2) 100%);
  border:1px solid var(--line);border-radius:var(--r);padding:13px 15px 12px;
  box-shadow:var(--sh);overflow:hidden;cursor:default;
  animation:rise .5s var(--ease) both;animation-delay:calc(var(--i) * 65ms);
  transition:transform .25s var(--ease),box-shadow .25s var(--ease),border-color .25s var(--ease)}
.kpi:hover{transform:translateY(-3px);box-shadow:var(--sh-md);border-color:var(--accent-bd)}
.kpi::before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;
  background:var(--tone,var(--accent));opacity:.95}
.kpi::after{content:"";position:absolute;right:-28px;top:-28px;width:86px;height:86px;
  border-radius:50%;background:var(--tone,var(--accent));opacity:.07;transition:transform .3s var(--ease)}
.kpi:hover::after{transform:scale(1.35)}
.kpi .top{display:flex;align-items:center;gap:7px;margin-bottom:5px}
.kpi .ic{width:22px;height:22px;border-radius:7px;display:grid;place-items:center;font-size:12px;
  background:color-mix(in srgb,var(--tone,var(--accent)) 14%,transparent);color:var(--tone,var(--accent))}
.kpi .l{font-size:9.5px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.6px}
.kpi .v{font-size:22px;font-weight:720;letter-spacing:-.03em;color:var(--ink);line-height:1.12}
.kpi .v small{font-size:12px;font-weight:600;color:var(--muted);letter-spacing:0}
.kpis.filtered .kpi{border-color:var(--accent-bd)}
.kpis.filtered .kpi::before{opacity:.55}
.kpi .v small{transition:opacity .2s}
.kpi.t-crit{--tone:var(--crit)} .kpi.t-high{--tone:var(--high)}
.kpi.t-ok{--tone:var(--low)}    .kpi.t-info{--tone:var(--accent2)}

/* ================= filters ================= */
.filters{margin:11px 22px 0;background:var(--card);border:1px solid var(--line);
  border-radius:var(--r);padding:0;flex:none;box-shadow:var(--sh);z-index:5;overflow:visible;
  animation:rise .5s var(--ease) both;animation-delay:.14s}
.frow{display:flex;gap:16px;align-items:flex-end;flex-wrap:wrap;padding:11px 15px}
.frow + .frow{border-top:1px solid var(--line2)}
.fg{display:flex;flex-direction:column;gap:5px;min-width:0}
.fg.grow{flex:1 1 210px}
.fg > label{font-size:9.5px;font-weight:700;color:var(--muted);text-transform:uppercase;
  letter-spacing:.6px;white-space:nowrap;height:12px;display:flex;align-items:center}

/* every control is exactly 36px tall so labels and boxes line up across both rows */
.ctl,.fg select,.dategrp,.seg,.searchwrap,.reset{height:36px}
.fg select{background:var(--card);border:1px solid var(--line);color:var(--ink);border-radius:10px;
  padding:0 30px 0 11px;font:inherit;font-size:12.5px;cursor:pointer;min-width:150px;
  appearance:none;-webkit-appearance:none;
  background-image:linear-gradient(45deg,transparent 50%,var(--muted) 50%),
                   linear-gradient(135deg,var(--muted) 50%,transparent 50%);
  background-position:calc(100% - 16px) 15px,calc(100% - 11px) 15px;
  background-size:5px 5px,5px 5px;background-repeat:no-repeat;
  transition:border-color .18s,box-shadow .18s}
.fg select:hover{border-color:var(--accent-bd)}
.fg select:focus{outline:none;border-color:var(--accent);
  box-shadow:0 0 0 3.5px color-mix(in srgb,var(--accent) 15%,transparent)}

/* --- joined date range: reads as ONE control, not two loose boxes --- */
.dategrp{display:inline-flex;align-items:center;border:1px solid var(--line);border-radius:10px;
  background:var(--card);padding:0 4px 0 0;transition:border-color .18s,box-shadow .18s}
.dategrp:hover{border-color:var(--accent-bd)}
.dategrp:focus-within{border-color:var(--accent);
  box-shadow:0 0 0 3.5px color-mix(in srgb,var(--accent) 15%,transparent)}
.dategrp input[type=date]{border:0;background:transparent;color:var(--ink);font:inherit;
  font-size:12.5px;padding:0 8px;height:34px;width:132px;outline:none;
  font-variant-numeric:tabular-nums}
.dategrp input[type=date]::-webkit-calendar-picker-indicator{cursor:pointer;opacity:.5}
.dategrp input[type=date]:hover::-webkit-calendar-picker-indicator{opacity:1}
.dategrp .sep{color:var(--faint);font-size:12px;flex:none;padding:0 1px}
.dclear{border:0;background:transparent;color:var(--faint);cursor:pointer;font-size:16px;
  line-height:1;width:24px;height:24px;border-radius:6px;flex:none;
  display:grid;place-items:center;transition:.18s;opacity:0;pointer-events:none}
.dategrp.has .dclear{opacity:1;pointer-events:auto}
.dclear:hover{background:var(--critbg);color:var(--crit)}

/* --- chip groups sit in an inset track so they read as one segmented control --- */
.seg{display:inline-flex;align-items:center;gap:4px;background:var(--line2);
  border:1px solid var(--line);border-radius:11px;padding:0 4px}
.chip{border:1px solid transparent;background:transparent;color:var(--muted);border-radius:8px;
  padding:0 11px;height:26px;font:inherit;font-size:11.5px;cursor:pointer;font-weight:620;
  white-space:nowrap;display:inline-flex;align-items:center;transition:.18s var(--ease)}
.chip:hover{background:var(--card);color:var(--accent);box-shadow:var(--sh-xs)}
.chip.on{background:var(--accent);color:#fff;box-shadow:0 2px 7px rgba(79,70,229,.34)}
.chip.crit.on{background:var(--crit);box-shadow:0 2px 7px rgba(220,38,38,.34)}
.chip.high.on{background:var(--high);box-shadow:0 2px 7px rgba(234,88,12,.34)}
.chip.med.on {background:var(--med); box-shadow:0 2px 7px rgba(180,83,9,.34)}
.chip.low.on {background:var(--low); box-shadow:0 2px 7px rgba(5,150,105,.34)}

/* --- search with a clear affordance --- */
.searchwrap{position:relative;display:flex;align-items:center;width:100%}
.searchwrap .ico{position:absolute;left:11px;color:var(--faint);font-size:12.5px;pointer-events:none}
.searchwrap input{width:100%;height:36px;background:var(--card);border:1px solid var(--line);
  color:var(--ink);border-radius:10px;padding:0 30px 0 30px;font:inherit;font-size:12.5px;
  transition:border-color .18s,box-shadow .18s}
.searchwrap input::placeholder{color:var(--faint)}
.searchwrap input:hover{border-color:var(--accent-bd)}
.searchwrap input:focus{outline:none;border-color:var(--accent);
  box-shadow:0 0 0 3.5px color-mix(in srgb,var(--accent) 15%,transparent)}
.sclear{position:absolute;right:7px;border:0;background:transparent;color:var(--faint);
  cursor:pointer;font-size:16px;line-height:1;width:22px;height:22px;border-radius:6px;
  display:grid;place-items:center;transition:.18s;opacity:0;pointer-events:none}
.searchwrap.has .sclear{opacity:1;pointer-events:auto}
.sclear:hover{background:var(--critbg);color:var(--crit)}

/* --- reset, with a live count of how many filters are active --- */
.reset{margin-left:auto;align-self:flex-end;background:var(--card);border:1px solid var(--line);
  color:var(--muted);border-radius:10px;padding:0 14px;cursor:pointer;font:inherit;font-size:12px;
  font-weight:620;display:inline-flex;align-items:center;gap:8px;white-space:nowrap;
  transition:.2s var(--ease)}
.reset:hover{border-color:var(--crit);color:var(--crit);background:var(--critbg)}
.reset[disabled]{opacity:.45;cursor:default}
.reset[disabled]:hover{border-color:var(--line);color:var(--muted);background:var(--card)}
.fcount{min-width:18px;height:18px;padding:0 5px;border-radius:999px;background:var(--accent);
  color:#fff;font-size:10px;font-weight:750;display:none;place-items:center;
  font-variant-numeric:tabular-nums}
.reset.active .fcount{display:grid}
.reset.active{border-color:var(--accent-bd);color:var(--accent)}


/* ================= table ================= */
.wrap{flex:1;min-height:240px;margin:13px 22px 0;background:var(--card);border:1px solid var(--line);
  border-radius:var(--r) var(--r) 0 0;overflow:hidden;display:flex;flex-direction:column;
  box-shadow:var(--sh-md);animation:rise .5s var(--ease) both;animation-delay:.22s}
.scroller{flex:1;overflow:auto;position:relative;scrollbar-width:thin}
.scroller::-webkit-scrollbar{width:11px;height:11px}
.scroller::-webkit-scrollbar-track{background:var(--line2)}
.scroller::-webkit-scrollbar-thumb{background:#c3cddf;border-radius:99px;border:3px solid var(--line2)}
.scroller::-webkit-scrollbar-thumb:hover{background:var(--accent)}
/* table-layout:fixed makes the <th> widths authoritative. Without it the browser sizes
   columns from content, so long titles/categories stretched the table to 2,616px against
   1,880px of declared widths and pushed two thirds of it off-screen. */
table{border-collapse:separate;border-spacing:0;table-layout:fixed;
  /* width:max-content defeats table-layout:fixed - the browser still sizes to content
     (measured 2,787px against 1,880px of declared widths). width:100% + a min-width equal
     to the declared total means: fill the pane when it is wide, and scroll by the minimum
     when it is narrow. */
  width:100%;min-width:1880px}
thead th{position:sticky;top:0;z-index:3;text-align:left;color:var(--ink2);
  background:linear-gradient(180deg,#fdfefe 0%,#eef2f9 100%);
  font-size:9.5px;font-weight:750;text-transform:uppercase;letter-spacing:.55px;
  padding:11px 10px;border-bottom:2px solid var(--accent-bd);
  border-right:1px solid var(--line2);white-space:nowrap;cursor:pointer;user-select:none;
  transition:background .18s,color .18s}
:root[data-theme=dark] thead th{background:linear-gradient(180deg,#1b2540 0%,#141c2e 100%)}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]) thead th{
  background:linear-gradient(180deg,#1b2540 0%,#141c2e 100%)}}
thead th:hover{color:var(--accent);background:var(--accent-soft)}
thead th .ar{opacity:.3;margin-left:5px;font-size:9px}
thead th.sorted{color:var(--accent);background:var(--accent-soft)}
thead th.sorted .ar{opacity:1}
tbody td{padding:0 10px;height:var(--rowh);border-bottom:1px solid var(--line2);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  background:var(--card);color:var(--ink2);transition:background .13s}
tbody tr:nth-child(even) td{background:var(--card2)}
tbody tr:hover td{background:var(--accent-soft)}
td.r{text-align:right}
td.c{text-align:center}
td.num{color:var(--ink);font-weight:560}
.title-cell{max-width:330px;color:var(--ink);font-weight:520}
.zero{color:var(--faint)}
.dn{color:var(--crit);font-weight:700}
.up{color:var(--low);font-weight:700}
.flat{color:var(--faint)}
.na{color:var(--faint);font-style:italic;font-size:11.5px}

/* --- frozen identity columns: with 20 columns you lose the product when you scroll
       right, so Image + Account stay pinned to the left edge ------------------- */
tbody td.stick,thead th.stick{position:sticky;z-index:2}
thead th.stick{z-index:4}
tbody td.s0,thead th.s0{left:0}
tbody td.s1,thead th.s1{left:var(--stick1,64px)}  /* set from COLS[0].w at init */
tbody td.s1{border-right:1px solid var(--line)}
thead th.s1{border-right:1px solid var(--accent-bd)}
.scroller.scrolled td.s1,.scroller.scrolled th.s1{box-shadow:6px 0 12px -6px rgba(17,24,39,.22)}

/* --- priority edge bar: instant triage down the left margin ------------------ */
tbody td.s0{box-shadow:inset 4px 0 0 var(--pc,transparent)}
tr.pr0{--pc:var(--crit)}tr.pr1{--pc:var(--high)}tr.pr2{--pc:var(--med)}
tr.pr3{--pc:var(--low)}tr.pr4{--pc:var(--nonebd)}

/* --- column-group separators: identity | commercial | sales | traffic | action */
tbody td.gsep,thead th.gsep{border-right:2px solid var(--line)}
thead th.gsep{border-right:2px solid var(--accent-bd)}

/* --- inline magnitude bar behind Stock so scale reads at a glance ------------ */
td.bar{position:relative}
td.bar::before{content:"";position:absolute;left:0;top:6px;bottom:6px;width:var(--w,0);
  background:linear-gradient(90deg,color-mix(in srgb,var(--high) 22%,transparent),
                                   color-mix(in srgb,var(--high) 6%,transparent));
  border-radius:0 3px 3px 0;pointer-events:none}
td.bar > span{position:relative}

/* --- header lifts once the body scrolls ------------------------------------- */
.scroller.scrolledY thead th{box-shadow:0 4px 10px -6px rgba(17,24,39,.3)}

/* --- compact density --------------------------------------------------------- */
body.compact{--rowh:34px}
body.compact a.thumb,body.compact .noimg{width:28px;height:28px;border-radius:7px}
body.compact td.imgcell{padding:2px 4px}
body.compact .pill{padding:2px 9px;font-size:10.5px}
body.compact tbody td{font-size:12px}

/* --- sort affordance --------------------------------------------------------- */
thead th .ar{opacity:.28;margin-left:5px;font-size:9px;transition:opacity .15s}
thead th:hover .ar{opacity:.65}
thead th.sorted .ar{opacity:1}

/* thumbnails */
td.imgcell{padding:3px 5px}
a.thumb{position:relative;display:block;width:42px;height:42px;border-radius:9px;overflow:hidden;
  border:1px solid var(--line);background:#fff;margin:0 auto;box-shadow:var(--sh-xs);
  transition:transform .22s var(--ease),box-shadow .22s var(--ease),border-color .22s}
a.thumb img{width:100%;height:100%;object-fit:contain;display:block;background:#fff}
a.thumb:hover{transform:scale(1.12);border-color:var(--accent);
  box-shadow:0 6px 18px rgba(79,70,229,.3);z-index:6}
.noimg{display:flex;align-items:center;justify-content:center;width:42px;height:42px;
  border-radius:9px;border:1.5px dashed var(--line);color:var(--faint);font-size:15px;margin:0 auto}
a.thumb .zoom{display:none;position:fixed;z-index:99;width:240px;height:240px;background:#fff;
  border:1px solid var(--line);border-radius:14px;box-shadow:var(--sh-lg);padding:8px;
  animation:fade .16s ease both}
a.thumb .zoom img{width:100%;height:100%;object-fit:contain}
a.thumb:hover .zoom{display:block}

/* action pills */
.pill{display:inline-flex;align-items:center;padding:4px 11px;border-radius:999px;font-size:11px;
  font-weight:680;line-height:1.35;max-width:100%;overflow:hidden;text-overflow:ellipsis;
  border:1px solid transparent;white-space:nowrap;transition:.2s var(--ease)}
tbody tr:hover .pill{transform:translateX(2px)}
.p0{background:var(--critbg);color:var(--crit);border-color:var(--critbd)}
.p1{background:var(--highbg);color:var(--high);border-color:var(--highbd)}
.p2{background:var(--medbg); color:var(--med); border-color:var(--medbd)}
.p3{background:var(--lowbg); color:var(--low); border-color:var(--lowbd)}
.p4{background:var(--nonebg);color:var(--none);border-color:var(--nonebd)}
.dot{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:7px;flex:none}
.d0{background:var(--crit)}.d1{background:var(--high)}.d2{background:var(--med)}
.d3{background:var(--low)}.d4{background:var(--none)}

/* ================= footer ================= */
footer{flex:none;padding:9px 22px 11px;color:var(--muted);font-size:11.5px;
  display:flex;gap:18px;align-items:center;flex-wrap:wrap}
footer b{color:var(--ink);font-weight:680}
.warn{color:var(--crit);font-weight:620;background:var(--critbg);border:1px solid var(--critbd);
  padding:4px 11px;border-radius:8px}
.warn b{color:var(--crit)}
.empty{padding:56px;text-align:center;color:var(--muted);animation:fade .3s both}
/* ============ SHORT-VIEWPORT MODE ==========================================================
   The ph_task panel gives the report only a few hundred px. Rather than force the host to
   scroll, reclaim the height from the chrome: smaller logo/heading, single-line KPI tiles,
   tighter filter rows, shorter table rows. Roughly doubles the rows visible without scrolling.
   Triggered on viewport HEIGHT, so a normal desktop window is untouched. */
@media (max-height:880px){
  :root{--rowh:40px}
  header{padding:8px 10px 0}
  header::before{height:2px}
  h1{font-size:15px}
  .sub{font-size:10.5px;margin-top:1px}
  .logo{height:30px;padding:0 10px;font-size:18px;border-radius:9px}
  .logo .mk{font-size:8px;margin-left:7px;padding-left:7px}
  .themebtn{padding:6px 10px;font-size:11.5px;border-radius:8px}

  /* KPI tiles collapse to one compact line: label above, figure beside the accent bar */
  .kpis{gap:7px;margin:9px 0 0;grid-template-columns:repeat(auto-fit,minmax(150px,1fr))}
  .kpi{padding:7px 11px 6px;border-radius:11px}
  .kpi::after{display:none}
  .kpi .top{gap:5px;margin-bottom:1px}
  .kpi .ic{width:17px;height:17px;border-radius:5px;font-size:10px}
  .kpi .l{font-size:8.5px;letter-spacing:.45px}
  .kpi .v{font-size:16px}
  .kpi .v small{font-size:10px}

  .filters{margin:8px 10px 0;border-radius:11px}
  .frow{padding:7px 12px;gap:12px}
  .fg>label{font-size:8.5px;height:10px}
  .ctl,.fg select,.dategrp,.seg,.searchwrap,.reset{height:31px}
  .dategrp input[type=date]{height:29px;width:118px;font-size:11.5px}
  .chip{height:23px;padding:0 9px;font-size:10.5px}
  .searchwrap input,.fg select{font-size:11.5px}
  #search{min-width:190px}

  .wrap{margin:8px 10px 0;border-radius:11px 11px 0 0}
  thead th{padding:8px 9px;font-size:9px}
  tbody td{font-size:11.5px}
  a.thumb,.noimg{width:34px;height:34px;border-radius:7px}
  td.imgcell{padding:2px 4px}
  .pill{padding:3px 8px;font-size:10px}
  tbody td{padding:0 7px}
  thead th{padding:8px 7px}
  footer{padding:4px 10px 6px;font-size:10.5px;gap:12px;flex-wrap:nowrap;
    white-space:nowrap;overflow:hidden}
  /* the caveat banner is the single biggest chrome consumer when it wraps (133px measured);
     one line + ellipsis, full text still available on hover */
  .warn{padding:3px 9px;max-width:46vw;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  #src{display:none}
  #selsum{overflow:hidden;text-overflow:ellipsis}
}
/* very short hosts: drop the sub-line entirely, it is the least load-bearing element */
@media (max-height:700px){
  .sub{display:none}
  .kpis{margin:7px 0 0}
}

/* collapsible chrome - trade controls for rows in a short panel */
body.nofilters .filters{display:none}
body.nokpis .kpis{display:none}
.themebtn.on{background:var(--accent);border-color:var(--accent);color:#fff}
</style></head><body>

<header>
  <div class="htop">
    <div class="brand">
      <div class="logo" title="eBay marketplace data — UK + Germany">
        <i class="e">e</i><i class="b">b</i><i class="a">a</i><i class="y">y</i>
        <span class="mk">UK · DE</span>
      </div>
      <div>
      <h1>eBay Slow Moving &amp; No Moving Products</h1>
      <div class="sub">REQ-16-D01 &middot; LEDSone group &middot; UK + Germany &middot;
        anchor <b id="anchor"></b> &middot; sales windows 7 / 30 / 90 days &middot;
        year-on-year vs <b id="lywin"></b></div>
      </div>
    </div>
    <div class="spacer"></div>
    <button class="themebtn" id="hidef" title="Hide the filter bar to show more rows">⌃ Filters</button>
    <button class="themebtn" id="hidek" title="Hide the KPI cards to show more rows">⌃ Cards</button>
    <button class="themebtn" id="fs">⛶ Full screen</button>
    <button class="themebtn" id="density">▤ Compact</button>
    <button class="themebtn" id="theme">◐ Dark</button>
  </div>
  <div class="kpis" id="kpis"></div>
</header>

<div class="filters">
  <div class="frow">
    <div class="fg">
      <label>Last sale date</label>
      <div class="dategrp" id="dategrp">
        <input type="date" id="dfrom" aria-label="Last sale date from">
        <span class="sep">&rarr;</span>
        <input type="date" id="dto" aria-label="Last sale date to">
        <button class="dclear" id="dclear" title="Clear dates" aria-label="Clear dates">&times;</button>
      </div>
    </div>
    <div class="fg">
      <label>Quick range</label>
      <div class="seg" id="datepresets">
        <button class="chip" data-d="all">All time</button>
        <button class="chip" data-d="30">Sold &le;30d</button>
        <button class="chip" data-d="90">Sold &le;90d</button>
        <button class="chip" data-d="old">No sale &gt;90d</button>
        <button class="chip" data-d="never">Never sold</button>
      </div>
    </div>
    <div class="fg">
      <label>Priority</label>
      <div class="seg" id="prio">
        <button class="chip crit" data-p="0">Critical</button>
        <button class="chip high" data-p="1">High</button>
        <button class="chip med"  data-p="2">Medium</button>
        <button class="chip low"  data-p="3">Low</button>
        <button class="chip"      data-p="4">Monitor</button>
      </div>
    </div>
  </div>
  <div class="frow">
    <div class="fg"><label>Account</label><select id="acct"></select></div>
    <div class="fg"><label>Marketplace</label><select id="site"></select></div>
    <div class="fg"><label>Action required</label><select id="action"></select></div>
    <div class="fg grow">
      <label>Search title / SKU / item ID</label>
      <div class="searchwrap" id="searchwrap">
        <span class="ico">&#9906;</span>
        <input type="text" id="search" placeholder="e.g. pendant, LED-001, 1647...">
        <button class="sclear" id="sclear" title="Clear search" aria-label="Clear search">&times;</button>
      </div>
    </div>
    <button class="reset" id="reset" disabled>Reset filters <span class="fcount" id="fcount">0</span></button>
  </div>
</div>

<div class="wrap">
  <div class="scroller" id="scroller">
    <table id="tbl">
      <thead><tr id="hrow"></tr></thead>
      <tbody id="tb"></tbody>
    </table>
    <div class="empty" id="empty" style="display:none">No listings match these filters.</div>
  </div>
</div>

<footer>
  <span>Showing <b id="shown">0</b> of <b id="tot">0</b> listings</span>
  <span id="selsum"></span>
  <span class="warn" id="gapnote"></span>
  <span style="margin-left:auto" id="src"></span>
</footer>

<script id="payload" type="application/json">__DATA__</script>
<script>
const D = JSON.parse(document.getElementById('payload').textContent);
const R = D.rows, DI = D.dicts;
const PRIO = ['Critical','High','Medium','Low','Monitor'];

// column definitions - EXACTLY the 20 columns of the requirement sheet, in order
const COLS = [
 // widths trimmed 2026-07-22: 20 columns previously totalled 3,104px against ~1,650px of
 // usable space inside the ph_task panel, so two thirds of the report sat off-screen.
 {t:'Image',                 w:52,  a:'c'},
 {t:'Account',               w:118},
 {t:'Brand',                 w:86},
 {t:'SKU',                   w:120},
 {t:'Item ID',               w:94},
 {t:'Product Title',         w:228},
 {t:'Category',              w:150},
 {t:'Current Price',         w:78,  a:'r'},
 {t:'Stock',                 w:64,  a:'r', tip:'eBay published quantity — not physical warehouse inventory'},
 {t:'7d Sales',              w:64,  a:'r', tip:'Units sold in the last 7 days'},
 {t:'30d Sales',             w:68,  a:'r', tip:'Units sold in the last 30 days'},
 {t:'90d Sales',             w:68,  a:'r', tip:'Units sold in the last 90 days'},
 {t:'LY 30d',                w:68,  a:'r', tip:'Units sold in the SAME 30-day window one year ago — compare against 30d Sales'},
 {t:'LY 90d',                w:68,  a:'r', tip:'Units sold in the SAME 90-day window one year ago — compare against 90d Sales. This is the comparator Sales Trend and Rule 4 use.'},
 {t:'Sales Trend',           w:84,  a:'r'},
 {t:'Days Since Sale',       w:78,  a:'r'},
 {t:'Views 30d',             w:70,  a:'r'},
 {t:'Conv Rate',             w:74,  a:'r'},
 {t:'Status',                w:72,  a:'c'},
 {t:'Action Required',       w:176}
];
// map column index -> row-array index / accessor
// Watchers (row slot 17) is intentionally absent - it has no data source in either DB.
// col 12 -> row slot 26 (same 30 days last year), col 13 -> slot 13 (same 90 days last year)
const IDX = [0,1,2,3,4,5,6,7,9,10,11,12,26,13,14,15,16,18,19,20];

const $ = s => document.querySelector(s);
// keep the second frozen column flush against the first - a hardcoded offset drifted
// the moment the Image column width changed, tearing a gap in the frozen pair
document.documentElement.style.setProperty('--stick1', COLS[0].w + 'px');
const fmtInt = n => (n==null?'':Number(n).toLocaleString('en-GB'));
const money = (v,c) => v==null?'':(c==='EUR'?'€':'£')+v.toFixed(2);

/* ---------- header ---------- */
$('#anchor').textContent = D.anchor;
$('#lywin').textContent  = D.windows.ly[0]+' → '+D.windows.ly[1];
$('#src').textContent = 'Sources: ledsone (listings · sales · PPC) + warehouse traffic_data (views · conversion)';

// Cards are built ONCE with a stable DOM (so the entrance animation does not replay on
// every keystroke), then their values are recomputed from the FILTERED view on each refresh.
// Showing frozen totals next to a filtered table is actively misleading.
const QTIP = 'eBay PUBLISHED quantity x listing price - NOT physical inventory. '
           + 'Use for relative ranking only, never as a stock valuation.';
const CARDS = [
  {id:'k-total', l:'Listings assessed',      tone:'t-info', ic:'\u25A4', tip:''},
  {id:'k-crit',  l:'Critical \u00B7 end listing', tone:'t-crit', ic:'\u25CF',
   tip:'Rule 1 \u2014 zero sales in the last 90 days.'},
  {id:'k-zero',  l:'Zero sales in 90 days',  tone:'t-crit', ic:'\u25D1',
   tip:'Rule 1 is exactly "90-day sales = 0" and runs first, so these two match by definition.'},
  {id:'k-qty',   l:'Listed qty \u00B7 dead \u273B',   tone:'t-high', ic:'\u25A6', tip:QTIP},
  {id:'k-val',   l:'Listed value \u00B7 dead \u273B', tone:'t-high', ic:'\u00A3', tip:QTIP},
  {id:'k-acct',  l:'Account \u00D7 marketplace', tone:'t-ok', ic:'\u25C8', tip:''}
];
$('#kpis').innerHTML = CARDS.map((c,n)=>
  `<div class="kpi ${c.tone}" style="--i:${n}"${c.tip?` title="${c.tip}"`:''}>`
  +`<div class="top"><span class="ic">${c.ic}</span><span class="l">${c.l}</span></div>`
  +`<div class="v num" id="${c.id}">&mdash;</div></div>`).join('');

function updateKpis(rows, filtered){
  let crit=0, zero=0, qty=0, gbp=0, eur=0; const accts=new Set();
  for(const r of rows){
    accts.add(r[1]);
    if(r[22]===1){ crit++; const v=(r[9]||0)*(r[7]||0); if(r[8]==='EUR') eur+=v; else gbp+=v; }
    if(r[12]<=0){ zero++; qty += (r[9]||0); }
  }
  const n = rows.length;
  const of = t => filtered ? ` <small>of ${fmtInt(t)}</small>` : '';
  $('#k-total').innerHTML = fmtInt(n) + of(D.kpi.total);
  $('#k-crit').innerHTML  = fmtInt(crit) + (n ? ` <small>(${(crit/n*100).toFixed(1)}%)</small>` : '');
  $('#k-zero').innerHTML  = fmtInt(zero);
  $('#k-qty').innerHTML   = fmtInt(qty);
  $('#k-val').innerHTML   = '\u00A3'+fmtInt(Math.round(gbp))+' <small>+ \u20AC'+fmtInt(Math.round(eur))+'</small>';
  $('#k-acct').innerHTML  = fmtInt(accts.size) + of(D.kpi.accounts);
  $('#kpis').classList.toggle('filtered', !!filtered);
}

$('#gapnote').title = 'Listed qty/value = eBay published quantity x listing price - not physical inventory, ranking aid only. Watchers column removed - no source in either database, so Rule 6 never fires. Views understated - only ' + D.cov.days30 + ' of 30 traffic days ingested. Last-year columns: compare 30d vs 30d and 90d vs 90d; Sales Trend uses the 90-day pair.';
$('#gapnote').innerHTML =
  '✻ Listed qty/value = eBay <b>published</b> quantity × listing price — <b>not physical inventory</b>; '
  + 'ranking aid only. &nbsp;·&nbsp; <b>Watchers column removed</b> — no source in either database, so Rule 6 never fires. &nbsp;·&nbsp; '
  + 'Views understated — only <b>' + D.cov.days30 + ' of 30</b> traffic days ingested. &nbsp;·&nbsp; '
  + 'Last-year columns: compare <b>30d vs 30d</b> and <b>90d vs 90d</b> — Sales Trend uses the 90-day pair.';

/* ---------- table head ---------- */
// group boundaries: identity(0-6) | commercial(7-8) | sales(9-14) | traffic(15-17) | action
const GSEP = new Set([6,8,15,17]);
const stickCls = i => i===0 ? ' stick s0' : i===1 ? ' stick s1' : '';
$('#hrow').innerHTML = COLS.map((c,i)=>
  `<th data-i="${i}" class="${(GSEP.has(i)?'gsep':'')+stickCls(i)}" `
  +`style="width:${c.w}px;min-width:${c.w}px"${c.tip?` title="${c.tip}"`:''}>`
  +`${c.t}${c.tip?' ✻':''}<span class="ar">▴▾</span></th>`).join('');

/* ---------- filter controls ---------- */
function fill(sel, list, label){
  sel.innerHTML = `<option value="-1">${label}</option>` +
    list.map((v,i)=>`<option value="${i}">${v}</option>`).join('');
}
fill($('#acct'),  DI.account, 'All accounts');
fill($('#site'),  DI.site,    'All marketplaces');
fill($('#action'),DI.action,  'All actions');

let F = {prio:new Set(), acct:-1, site:-1, action:-1, q:'', from:null, to:null, never:null};
let sortCol = null, sortDir = 1, view = R;

function passes(r){
  if(F.prio.size && !F.prio.has(r[21])) return false;
  if(F.acct  >=0 && r[1]!==F.acct)   return false;
  if(F.site  >=0 && r[24]!==F.site)  return false;
  if(F.action>=0 && r[20]!==F.action)return false;
  if(F.never===1 && r[25]!==1) return false;
  if(F.never===0 && r[25]===1) return false;
  if(F.from || F.to){
    const d = r[23];
    if(!d) return false;                      // never-sold has no date
    if(F.from && d < F.from) return false;
    if(F.to   && d > F.to)   return false;
  }
  if(F.q){
    const q = F.q;
    if(!(r[5].toLowerCase().includes(q) || r[3].toLowerCase().includes(q) || r[4].includes(q)))
      return false;
  }
  return true;
}

function applySort(a){
  if(sortCol===null) return a;
  const ri = IDX[sortCol];
  const txt = [1,2,6,18,19].includes(sortCol);
  const dictName = {1:'account',2:'brand',6:'category',18:'status',19:'action'}[sortCol];
  return a.slice().sort((x,y)=>{
    let u = x[ri], v = y[ri];
    if(txt){ u = DI[dictName][u]||''; v = DI[dictName][v]||''; return sortDir*u.localeCompare(v); }
    if(sortCol===3||sortCol===4||sortCol===5){ u=String(u); v=String(v); return sortDir*u.localeCompare(v); }
    u = (u==null?-Infinity:u); v = (v==null?-Infinity:v);
    return sortDir*(u<v?-1:u>v?1:0);
  });
}

function syncChrome(){
  // how many filters are actually narrowing the view
  let n = F.prio.size ? 1 : 0;
  if(F.acct>=0) n++; if(F.site>=0) n++; if(F.action>=0) n++;
  if(F.q) n++; if(F.from||F.to||F.never!==null) n++;
  const rb=$('#reset'), fc=$('#fcount');
  fc.textContent=n; rb.classList.toggle('active', n>0); rb.disabled = n===0;
  $('#dategrp').classList.toggle('has', !!($('#dfrom').value || $('#dto').value));
  $('#searchwrap').classList.toggle('has', !!$('#search').value);
}

function refresh(){
  syncChrome();
  view = applySort(R.filter(passes));
  updateKpis(view, view.length !== R.length);
  $('#shown').textContent = fmtInt(view.length);
  $('#tot').textContent   = fmtInt(R.length);
  let s7=0,s30=0,s90=0,st=0;
  for(const r of view){ s7+=r[10]; s30+=r[11]; s90+=r[12]; st+=r[9]; }
  $('#selsum').innerHTML = view.length
    ? `Selected: <b>${fmtInt(st)}</b> units in stock · sales <b>${fmtInt(s7)}</b> / <b>${fmtInt(s30)}</b> / <b>${fmtInt(s90)}</b> (7 / 30 / 90d)`
    : '';
  $('#empty').style.display = view.length ? 'none' : 'block';
  $('#tbl').style.display   = view.length ? '' : 'none';
  sc.scrollTop = 0;
  render();
}

/* ---------- virtualised rows ---------- */
const sc = $('#scroller'), tb = $('#tb');
let ROWH = (window.innerHeight <= 880 ? 40 : 48); const BUF = 10;

function cell(r, ci){
  const ri = IDX[ci], v = r[ri];
  switch(ci){
    case 0: {
      // real product thumbnail, linked to the live eBay listing, with hover zoom
      const site = DI.site[r[24]];
      const dom = site==='Germany' ? 'www.ebay.de' : 'www.ebay.co.uk';
      const href = `https://${dom}/itm/${r[4]}`;
      if(!v) return `<span class="noimg" title="no image on this listing">▢</span>`;
      // eBay CDN size variants: the stored URL is s-l1600 (up to ~385 KB). A 42px thumbnail
      // only needs s-l225 (~17 KB, 23x smaller); the hover zoom uses s-l400.
      const s  = v.replace(/"/g,'&quot;');
      const th = s.replace(/s-l\d+\.(jpg|jpeg|png|webp)/i, 's-l225.$1');
      const zm = s.replace(/s-l\d+\.(jpg|jpeg|png|webp)/i, 's-l400.$1');
      // NOT loading="lazy": virtualisation already keeps only ~25 rows in the DOM, so every
      // thumbnail is on-screen by construction. Lazy-loading on top of that is redundant and
      // measurably delays them (an IntersectionObserver round-trip per image, per scroll
      // re-render). The zoom image stays lazy - it is hidden until hover.
      return `<a class="thumb" href="${href}" target="_blank" rel="noopener" title="Open listing on eBay">`
           + `<img decoding="async" src="${th}" alt="" `
           + `onerror="this.onerror=null;this.src='${s}'">`
           + `<span class="zoom"><img loading="lazy" decoding="async" src="${zm}" alt=""></span></a>`;
    }
    case 1: return DI.account[v];
    case 2: return DI.brand[v];
    case 6: return DI.category[v] || '<span class="na">—</span>';
    case 7: return money(v, r[8]);
    case 8: return '<span>'+fmtInt(v)+'</span>';
    case 9: case 10: case 11: case 12: case 13:
      return v ? fmtInt(v) : '<span class="zero">0</span>';
    case 14: {
      // No sales last year => the ratio is undefined. Two very different situations hide here:
      //   both windows zero  -> genuinely no change, show 0%
      //   zero last year but sales this year -> it GREW from nothing; 0% would read as flat
      //                                          and understate a growing listing, so show NEW
      if(v==null) return r[12] > 0
        ? '<span class="up" title="no sales in the same window last year - grew from zero">▲ NEW</span>'
        : '<span class="flat">→ 0%</span>';
      const p = Math.round(v*100);
      if(p<=-1) return `<span class="dn">▼ ${p}%</span>`;
      if(p>=1)  return `<span class="up">▲ +${p}%</span>`;
      return `<span class="flat">→ 0%</span>`;
    }
    case 15: return r[25]===1 ? `<span class="na" title="never sold — listing age shown">${fmtInt(v)}*</span>` : fmtInt(v);
    case 16: return v==null ? '<span class="na">no data</span>' : fmtInt(v);
    case 17: return v==null ? '<span class="na">—</span>' : (v*100).toFixed(1)+'%';
    case 18: return DI.status[v];
    case 19: {
      const p = r[21];
      return `<span class="pill p${p}" title="${DI.action[v]}"><span class="dot d${p}"></span>${DI.action[v]}</span>`;
    }
    default: return String(v==null?'':v);
  }
}

function render(){
  const total = view.length;
  const vh = sc.clientHeight;
  let start = Math.max(0, Math.floor(sc.scrollTop/ROWH) - BUF);
  let end   = Math.min(total, Math.ceil((sc.scrollTop+vh)/ROWH) + BUF);
  const padTop = start*ROWH, padBot = Math.max(0,(total-end)*ROWH);
  const nc = COLS.length;
  let h = padTop ? `<tr style="height:${padTop}px"><td colspan="${nc}" style="padding:0;border:0"></td></tr>` : '';
  for(let i=start;i<end;i++){
    const r = view[i];
    h += `<tr class="pr${r[21]}">`;
    for(let c=0;c<nc;c++){
      const al = COLS[c].a ? ' '+COLS[c].a : '';
      const isNum = [7,8,9,10,11,12,13,14,15,16,17].includes(c);
      let cls = (c===0?'imgcell':c===5?'title-cell':'') + al + (isNum?' num':'')
              + (GSEP.has(c)?' gsep':'') + stickCls(c);
      const raw = (c===5? r[5] : c===3? r[3] : '');
      let style = '';
      if(c===8){                              // Stock: magnitude bar behind the figure
        // sqrt scale - stock spans 0..9,555 with a median of 96, so a linear bar would be
        // invisible on almost every row
        const w = Math.min(1, Math.sqrt((r[9]||0)/2600));
        if(w>0.02){ cls += ' bar'; style = ` style="--w:${(w*100).toFixed(1)}%"`; }
      }
      h += `<td class="${cls}"${style}${raw?` title="${raw.replace(/"/g,'&quot;')}"`:''}>${cell(r,c)}</td>`;
    }
    h += '</tr>';
  }
  if(padBot) h += `<tr style="height:${padBot}px"><td colspan="${nc}" style="padding:0;border:0"></td></tr>`;
  tb.innerHTML = h;
}
sc.addEventListener('scroll', ()=>{
  sc.classList.toggle('scrolled',  sc.scrollLeft > 2);
  sc.classList.toggle('scrolledY', sc.scrollTop  > 2);
  render();
}, {passive:true});
window.addEventListener('resize', render);

/* ---------- events ---------- */
document.getElementById('hrow').addEventListener('click', e=>{
  const th = e.target.closest('th'); if(!th) return;
  const i = +th.dataset.i;
  if(sortCol===i) sortDir = -sortDir; else { sortCol = i; sortDir = 1; }
  [...document.querySelectorAll('#hrow th')].forEach(x=>x.classList.remove('sorted'));
  th.classList.add('sorted');
  th.querySelector('.ar').textContent = sortDir>0 ? '▴' : '▾';
  refresh();
});
$('#prio').addEventListener('click', e=>{
  const b = e.target.closest('.chip'); if(!b) return;
  const p = +b.dataset.p;
  if(F.prio.has(p)){F.prio.delete(p); b.classList.remove('on');}
  else {F.prio.add(p); b.classList.add('on');}
  refresh();
});
$('#datepresets').addEventListener('click', e=>{
  const b = e.target.closest('.chip'); if(!b) return;
  [...document.querySelectorAll('#datepresets .chip')].forEach(x=>x.classList.remove('on'));
  b.classList.add('on');
  const d = b.dataset.d, A = new Date(D.anchor);
  const iso = n => new Date(A.getTime()-n*864e5).toISOString().slice(0,10);
  F.from=F.to=null; F.never=null;
  if(d==='30'){ F.from=iso(30); F.to=D.anchor; F.never=0; }
  else if(d==='90'){ F.from=iso(90); F.to=D.anchor; F.never=0; }
  else if(d==='old'){ F.from='2000-01-01'; F.to=iso(90); F.never=0; }
  else if(d==='never'){ F.never=1; }
  else { b.classList.remove('on'); }
  $('#dfrom').value = (F.from && F.from!=='2000-01-01') ? F.from : '';
  $('#dto').value   = F.to || '';
  refresh();
});
$('#dfrom').addEventListener('change', e=>{ F.from = e.target.value||null;
  [...document.querySelectorAll('#datepresets .chip')].forEach(x=>x.classList.remove('on')); refresh(); });
$('#dto').addEventListener('change', e=>{ F.to = e.target.value||null;
  [...document.querySelectorAll('#datepresets .chip')].forEach(x=>x.classList.remove('on')); refresh(); });
$('#acct').addEventListener('change', e=>{F.acct=+e.target.value; refresh();});
$('#site').addEventListener('change', e=>{F.site=+e.target.value; refresh();});
$('#action').addEventListener('change', e=>{F.action=+e.target.value; refresh();});
let qt; $('#search').addEventListener('input', e=>{
  clearTimeout(qt); qt=setTimeout(()=>{F.q=e.target.value.trim().toLowerCase(); refresh();},160);
});
$('#reset').addEventListener('click', ()=>{
  F = {prio:new Set(), acct:-1, site:-1, action:-1, q:'', from:null, to:null, never:null};
  document.querySelectorAll('.chip').forEach(c=>c.classList.remove('on'));
  $('#acct').value=$('#site').value=$('#action').value='-1';
  $('#search').value=''; $('#dfrom').value=''; $('#dto').value='';
  sortCol=null; sortDir=1;
  [...document.querySelectorAll('#hrow th')].forEach(x=>{x.classList.remove('sorted');
    x.querySelector('.ar').textContent='▴▾';});
  refresh();
});
$('#hidef').addEventListener('click', ()=>{
  const on = document.body.classList.toggle('nofilters');
  $('#hidef').classList.toggle('on', on);
  $('#hidef').textContent = on ? '⌄ Filters' : '⌃ Filters';
  render();
});
$('#hidek').addEventListener('click', ()=>{
  const on = document.body.classList.toggle('nokpis');
  $('#hidek').classList.toggle('on', on);
  $('#hidek').textContent = on ? '⌄ Cards' : '⌃ Cards';
  render();
});
$('#fs').addEventListener('click', ()=>{
  const d=document, el=d.documentElement;
  const on = d.fullscreenElement || d.webkitFullscreenElement;
  if(on){ (d.exitFullscreen||d.webkitExitFullscreen).call(d); }
  else  { (el.requestFullscreen||el.webkitRequestFullscreen).call(el); }
});
document.addEventListener('fullscreenchange', ()=>{
  $('#fs').textContent = document.fullscreenElement ? '⤡ Exit full screen' : '⛶ Full screen';
  render();
});
function baseRowH(){ return window.innerHeight <= 880 ? 40 : 48; }
window.addEventListener('resize', ()=>{
  if(!document.body.classList.contains('compact')){ ROWH = baseRowH(); render(); }
});
$('#density').addEventListener('click', ()=>{
  const on = document.body.classList.toggle('compact');
  ROWH = on ? 34 : baseRowH();                      // keep virtualisation in step with the CSS
  $('#density').textContent = on ? '\u25A5 Comfortable' : '\u25A4 Compact';
  render();
});
$('#dclear').addEventListener('click', ()=>{
  F.from=F.to=null; F.never=null;
  $('#dfrom').value=''; $('#dto').value='';
  document.querySelectorAll('#datepresets .chip').forEach(c=>c.classList.remove('on'));
  refresh();
});
$('#sclear').addEventListener('click', ()=>{
  F.q=''; $('#search').value=''; $('#search').focus(); refresh();
});
$('#theme').addEventListener('click', ()=>{
  // starts on light (set on <html>); this only ever flips between the two explicit themes
  const now = document.documentElement.getAttribute('data-theme')==='dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', now);
  $('#theme').textContent = now==='dark' ? '☀ Light' : '◐ Dark';
});

refresh();
</script>
</body></html>
"""


def main():
    data = B.fetch()
    rows = B.assemble(data)
    payload = encode(rows, data["cov"])
    if not os.path.isdir(FINAL):
        os.makedirs(FINAL)
    with io.open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, separators=(",", ":"))
    js = json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")
    html = HTML.replace("__DATA__", js)
    with io.open(OUT_HTML, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("rows      :", len(rows))
    print("json      : %s (%.2f MB)" % (OUT_JSON, os.path.getsize(OUT_JSON) / 1048576.0))
    print("dashboard : %s (%.2f MB)" % (OUT_HTML, os.path.getsize(OUT_HTML) / 1048576.0))


if __name__ == "__main__":
    main()
