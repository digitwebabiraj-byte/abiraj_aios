"""
REQ-15-D01 — full-screen eBay PPC Pause Automation console.
Renders eppa_d01_data.json into a single self-contained HTML app (no external assets).

Design system
-------------
Typography  : platform-native variable stacks (Segoe UI Variable / SF / Inter) with a real modular
              scale, tabular figures on every number, and optical letter-spacing on micro-labels.
              No webfont is loaded — the page must render identically offline and inside a viewer
              that blocks external requests.
Colour      : a single, carefully-tuned LIGHT theme — semantic tokens, four surface levels for real
              depth, every text pair measured at >=4.5:1 (WCAG AA for small text). No dark mode:
              this report is read in a bright office and embedded in a light portal, and one
              well-tuned palette beats two half-tuned ones.
Layout      : 4px spacing rhythm, app shell at 100dvh, one scroll region.
Motion      : 120–160ms ease, fully disabled under prefers-reduced-motion.
A11y        : visible focus rings, aria-pressed/selected state, keyboard shortcuts, generous hit
              areas on controls, semantic table with scope, skip link.

UX          : density toggle · sticky campaign column · live search · filter chips · sortable
              columns · expandable decision trace · staff decision + note (persisted) ·
              CSV export of the current view · toast feedback.
"""
import json, os, re, html
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
FINAL = os.path.abspath(os.path.join(HERE, "..", "..", "evidence", "final_outputs",
                                     "REQ-15_ebay-ppc-product-pause-automation"))
D = json.load(open(os.path.join(FINAL, "eppa_d01_data.json"), encoding="utf-8"))
rows, K, TH, ANCHOR = D["rows"], D["kpis"], D["thresholds"], D["anchor"]
e = html.escape
m = lambda v: "£" + format(v, ",.2f")

# ---------------------------------------------------------------- date windows
# The SQL predicate is `date > anchor - N`, so each window is the N days ENDING on the anchor,
# inclusive of it. Derived here rather than written by hand so the ranges stay correct on every
# Monday refresh — a hardcoded date is the classic way a rebuilt report starts lying.
_A = datetime.strptime(ANCHOR, "%Y-%m-%d").date()


def _range(n):
    """Return (start, end) for the n-day window ending on the anchor."""
    return _A - timedelta(days=n - 1), _A


def _fmt(n):
    st, en = _range(n)
    if (st.year, st.month) == (en.year, en.month):          # 8–21 Jul 2026
        return "%d–%d %s %d" % (st.day, en.day, en.strftime("%b"), en.year)
    if st.year == en.year:                                   # 22 Jun – 21 Jul 2026
        return "%d %s – %d %s %d" % (st.day, st.strftime("%b"), en.day,
                                     en.strftime("%b"), en.year)
    return "%d %s %d – %d %s %d" % (st.day, st.strftime("%b"), st.year,
                                    en.day, en.strftime("%b"), en.year)


W30, W14, W7 = _fmt(30), _fmt(14), _fmt(7)
ANCHOR_LONG = _A.strftime("%d %b %Y").lstrip("0")
RULE_KEY = {"Stock": "stock", "Rule 1": "r1", "Rule 2": "r2"}

# ---------------------------------------------------------------- KPI strip
def card(v, l, sub="", filt="", tone=""):
    return ('<button class="kpi%s" data-filter="%s"%s>'
            '<span class="kpi-v">%s</span><span class="kpi-l">%s</span>%s</button>'
            % (" t-" + tone if tone else "", filt,
               ' title="Filter the log to: %s"' % filt if filt else "",
               v, l, '<span class="kpi-s">%s</span>' % sub if sub else ""))

kpis = "".join([
    card(K["scope"], "In scope", "campaigns", "All"),
    card(K["paused"], "Recommend pause", m(K["spend_at_risk"]) + " at risk", "Paused", "stop"),
    card(K["stock"], "Stock rule", "unbuyable listings", "Stock", "stop"),
    card(K["r1"], "Rule 1", "ACOS ≥ %g%%" % TH["acos_ceiling"], "Rule 1", "blue"),
    card(K["r2"], "Rule 2", "clicks, no sales", "Rule 2", "amber"),
    card(K["running"], "Still running", "no rule matched", "Still running", "go"),
    card(K["off"], "Already off", "not evaluated", "Already off", "mute"),
    card(m(K["spend_all"]), "30D spend", "all campaigns", ""),
])

# ---------------------------------------------------------------- Pause Log rows
trs = []
for i, r in enumerate(rows):
    # `outcome` = the engine's decision; `status` = the campaign's own live state. Never conflate.
    cls = {"PAUSED": "p", "ALREADY OFF": "o"}.get(r["outcome"], "r")
    rule = r["rule"]
    ruleh = ('<span class="tag %s">%s</span>' % (RULE_KEY[rule], rule)) if rule != "—" \
        else '<span class="muted">—</span>'
    prioh = ('<span class="prio %s"><i></i><i></i><i></i>%s</span>'
             % (r["priority"].lower(), r["priority"])) if r["priority"] \
        else '<span class="muted">—</span>'
    a30 = "%.1f" % r["acos30"] if r["acos30"] is not None else None
    a7 = "%.1f" % r["acos7"] if r["acos7"] is not None else None
    a30h = ('<span class="%s">%s%%</span>'
            % ("hot" if r["acos30"] and r["acos30"] >= TH["acos_ceiling"] else "", a30)
            ) if a30 else '<span class="muted">—</span>'
    a7h = ('<span class="%s">%s%%</span>'
           % ("cool" if r["acos7"] is not None and r["acos7"] < TH["acos_rescue"] else "", a7)
           ) if a7 else '<span class="muted">—</span>'

    if r["listings"] == 0:
        stk = '<span class="muted">no advertised listings</span>'
    else:
        seg, ok = [], r["listings"] - r["out_of_stock"] - r["low_stock"] - r["no_stock_data"]
        if r["out_of_stock"]:
            seg.append('<b class="s-bad">%d out of stock</b>' % r["out_of_stock"])
        if r["low_stock"]:
            seg.append('<b class="s-warn">%d low</b>' % r["low_stock"])
        if r["no_stock_data"]:
            seg.append('<b class="s-none">%d no data</b>' % r["no_stock_data"])
        if not seg:
            seg.append('<b class="s-ok">all in stock</b>')
        p = lambda n: (n / r["listings"] * 100) if r["listings"] else 0
        bar = ('<span class="meter" role="img" aria-label="%d out of stock, %d low, %d no data, '
               '%d in stock, of %d listings">'
               '<i class="m-bad" style="width:%.2f%%"></i><i class="m-warn" style="width:%.2f%%"></i>'
               '<i class="m-none" style="width:%.2f%%"></i><i class="m-ok" style="width:%.2f%%"></i>'
               '</span>' % (r["out_of_stock"], r["low_stock"], r["no_stock_data"], ok, r["listings"],
                            p(r["out_of_stock"]), p(r["low_stock"]), p(r["no_stock_data"]), p(ok)))
        stk = ('<div class="stk"><div class="stk-t">%s</div>%s<div class="stk-n">%d listings</div></div>'
               % (" · ".join(seg), bar, r["listings"]))

    trace = "".join('<li class="%s"><span class="tr-l">%s</span><span class="tr-d">%s</span></li>'
                    % ("y" if ok else "n", e(l), e(dt)) for l, ok, dt in r["trace"])

    trs.append(
        '<tr class="%s" data-i="%d" data-cid="%s" data-rule="%s" data-prio="%s" data-status="%s" '
        'data-s="%s" data-spend="%.2f" data-acos="%s" data-listings="%d">'
        # NOTE: the flex layout lives on an inner <div>, never on the <th> itself. Setting
        # display:flex on a table cell drops it out of the table layout algorithm — the column
        # stops sizing with its header and every sibling cell loses vertical alignment.
        '<th scope="row" class="c-camp"><div class="c-in">'
        '<input type="checkbox" class="rowtog" id="rt%d" aria-controls="d%d">'
        '<label class="disc" for="rt%d" title="Show decision trace (or click anywhere on the row)">'
        '<svg viewBox="0 0 10 10" aria-hidden="true">'
        '<path d="M3 1.5 L7 5 L3 8.5" fill="none" stroke="currentColor" stroke-width="1.6" '
        'stroke-linecap="round" stroke-linejoin="round"/></svg></label>'
        '<span class="c-txt"><span class="camp">%s</span>'
        '<span class="meta">%s · campaign %s</span></span></div></th>'
        '<td>%s</td>'
        '<td><span class="st %s">%s</span><span class="cstate">campaign %s</span></td>'
        '<td>%s</td><td>%s</td>'
        '<td class="num acos"><span class="a30">%s</span><span class="a7">7D %s</span></td>'
        '<td class="num mono money">%s</td>'
        '<td class="c-reason"><div class="r-in">%s</div></td>'
        '<td><select class="dec" data-cid="%s" aria-label="Decision for %s"><option>Pending</option>'
        '<option>Approved</option><option>Rejected</option><option>On hold</option></select></td>'
        '<td><input class="note" data-cid="%s" placeholder="note…" aria-label="Note for %s"></td></tr>'
        '<tr class="detail" data-for="%d"><td colspan="10" id="d%d"><div class="dwrap">'
        '<section class="dcol"><h4>Decision trace</h4><ol class="trace">%s</ol></section>'
        '<section class="dcol"><h4>Why</h4><p class="dreason">%s</p>'
        '<dl class="dstats"><div><dt>30D spend</dt><dd>%s</dd></div>'
        '<div><dt>30D sales</dt><dd>%s</dd></div><div><dt>30D orders</dt><dd>%g</dd></div>'
        '<div><dt>14D clicks</dt><dd>%g</dd></div><div><dt>14D spend</dt><dd>%s</dd></div>'
        '<div><dt>Listings</dt><dd>%d</dd></div></dl>'
        '</section></div></td></tr>'
        % (cls, i, r["campaign_id"], rule, r["priority"] or "", r["outcome"],
           e((r["campaign"] + " " + r["campaign_id"] + " " + r["type"]).lower()),
           r["spend30"], a30 or "", r["listings"], i, i, i,
           e(r["campaign"]), e(r["type"]), r["campaign_id"],
           stk, cls, r["outcome"], e(r["status"]), ruleh, prioh, a30h, a7h,
           m(r["spend30"]),
           e(r["reason"]), r["campaign_id"], e(r["campaign"]), r["campaign_id"], e(r["campaign"]),
           i, i, trace, e(r["reason"]), m(r["spend30"]), m(r["sales30"]), r["ord30"],
           r["clicks14"], m(r["spend14"]), r["listings"]))

# ---------------------------------------------------------------- Campaign Data tab
data_rows = "".join(
    '<tr><th scope="row" class="camp">%s</th><td class="mono">%s</td><td>%s</td><td>%s</td>'
    '<td class="num mono">%d</td><td class="num mono money">%s</td><td class="num mono money">%s</td>'
    '<td class="num mono">%g</td><td class="num mono">%s</td><td class="num mono">%s</td>'
    '<td class="num mono">%g</td><td class="num mono">%g</td><td class="num mono money">%s</td></tr>'
    % (e(r["campaign"]), r["campaign_id"], e(r["type"]), r["status"], r["listings"],
       m(r["spend30"]), m(r["sales30"]), r["ord30"],
       "%.1f%%" % r["acos30"] if r["acos30"] is not None else "—",
       "%.1f%%" % r["acos7"] if r["acos7"] is not None else "—",
       r["ord14"], r["clicks14"], m(r["spend14"]))
    for r in sorted(rows, key=lambda x: -x["spend30"]))

rule_rows = "".join(
    '<tr><th scope="row">%s</th><td class="num mono val">%s</td><td class="muted">%s</td></tr>' % t
    for t in [
        ("Stock floor", "%d units" % TH["stock_floor"], "A listing below this counts as low stock"),
        ("Rule 1 — 30D ACOS ceiling", "%g%%" % TH["acos_ceiling"], "Pause at or above this"),
        ("Rule 1 — 7D ACOS rescue", "%g%%" % TH["acos_rescue"], "Skip the pause below this (improving trend)"),
        ("Rule 2 — 14D clicks minimum", "%d" % TH["clicks_min"], "Rule 2 only applies at or above this"),
        ("Rule 2 — 14D spend floor", m(TH["spend_floor"]), "Skip the pause below this (cheap organic clicks)"),
        ("Priority — High", "≥ %s" % m(TH["prio_high"]), "30D spend at risk"),
        ("Priority — Medium", "≥ %s" % m(TH["prio_med"]), "30D spend at risk"),
    ])

CSS = r"""
/* ============================================================ design tokens */
:root{
  /* type — platform-native variable stacks; no webfont is fetched */
  /* Sans carries ALL interface text — labels, buttons, chips, tabs, table headers. Mono is
     reserved for figures, IDs and code, where character alignment earns its lower legibility.
     Mono on small uppercase labels was the readability problem: narrow strokes + wide tracking
     + a 10.5px size compound into something you squint at. */
  --f-ui:"Segoe UI Variable Text","Segoe UI",-apple-system,BlinkMacSystemFont,"Inter","Roboto",
         "Helvetica Neue",Arial,system-ui,sans-serif;
  --f-hd:"Segoe UI Variable Display","Segoe UI",-apple-system,BlinkMacSystemFont,"Inter",
         "Helvetica Neue",Arial,system-ui,sans-serif;
  --f-mono:"Cascadia Mono","JetBrains Mono",ui-monospace,"SF Mono",Menlo,Consolas,
         "Liberation Mono",monospace;
  /* modular scale — every step raised; nothing on the page sits below 11.5px now */
  --t-2xs:11.5px; --t-xs:12.5px; --t-sm:13px; --t-md:14px; --t-lg:16px;
  --t-xl:21px; --t-2xl:30px;
  --lh-tight:1.25; --lh-snug:1.4; --lh-body:1.6;
  /* rhythm */
  --s1:4px; --s2:8px; --s3:12px; --s4:16px; --s5:20px; --s6:28px;
  --r-sm:6px; --r-md:9px; --r-lg:13px;
  --dur:.14s; --ease:cubic-bezier(.4,0,.2,1);

  /* ---- colour: one light theme, tuned.
     Four surface levels give real depth without heavy borders: --bg is the room, --surface the
     paper, --surface-2 a recessed strip, --surface-3 the chrome (table head, chips).
     Every text token is >=4.5:1 on the surface it is actually used against — measured with a
     contrast script, not eyeballed. --text-3 (#5F6B80) and --warn (#9A5F0E) were darkened from
     #77839A / #A96A12, which failed AA at small sizes — and --text-3 twice, because it also has to
     clear 4.5:1 on --surface-3 and --bg (the `.count` label and the low-priority pill sit there).
     Do not lighten them back. */
  --bg:#EBEFF5; --surface:#FFF; --surface-2:#F6F8FC; --surface-3:#ECF0F6;
  --line:#D8DFE9; --line-soft:#EAEEF4;
  --text:#16233B; --text-2:#4A586F; --text-3:#5F6B80;
  --brand:#2B5A96; --brand-ink:#1C3F6E; --brand-wash:#E8EFF8; --brand-line:#BFD3EA;
  --stop:#B5372A; --stop-wash:#FBEBE8; --stop-line:#EFC8C1;
  --go:#1B7048; --go-wash:#E6F4EC; --go-line:#BFE2CD;
  --warn:#9A5F0E; --warn-wash:#FBF1DE; --warn-line:#EBD8AE;
  --hd-a:#152741; --hd-b:#2A5285;
  /* layered shadows — a tight contact shadow plus a wide ambient one reads as real elevation */
  --sh-1:0 1px 1.5px rgba(16,32,58,.05),0 1px 3px rgba(16,32,58,.04);
  --sh-2:0 1px 2px rgba(16,32,58,.06),0 4px 10px rgba(16,32,58,.05),0 12px 26px rgba(16,32,58,.05);
  --sh-3:0 2px 6px rgba(16,32,58,.10),0 16px 40px rgba(16,32,58,.16);
  --focus:#2B5A96;
  /* gradients — kept as tokens so every surface shares one light direction (top-left) */
  --g-surface:linear-gradient(177deg,#FFF 0%,#FCFDFF 55%,#F8FAFD 100%);
  --g-head:linear-gradient(180deg,#F2F5FA 0%,#E9EEF6 100%);
  --g-brand:linear-gradient(135deg,#3568A8 0%,#2B5A96 55%,#234C81 100%);
  --g-stop:linear-gradient(135deg,#C4402F 0%,#B5372A 100%);
  --g-go:linear-gradient(135deg,#228154 0%,#1B7048 100%);
  --g-warn:linear-gradient(135deg,#B06D12 0%,#9A5F0E 100%);
  --g-sheen:linear-gradient(180deg,rgba(255,255,255,.9),rgba(255,255,255,0));
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%}
body{
  font-family:var(--f-ui);font-size:var(--t-md);line-height:var(--lh-body);color:var(--text);
  background:var(--bg);overflow:hidden;
  -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;
  font-feature-settings:"kern" 1,"liga" 1,"calt" 1;text-rendering:optimizeLegibility;
  font-variant-numeric:tabular-nums;
}
.mono{font-family:var(--f-mono);font-variant-numeric:tabular-nums;letter-spacing:-.01em}
.num{text-align:right}
.money{font-feature-settings:"tnum" 1}
.muted{color:var(--text-3)}
:where(button,select,input,[tabindex]):focus-visible{
  outline:2px solid var(--focus);outline-offset:2px;border-radius:var(--r-sm)}
::selection{background:var(--brand-wash);color:var(--brand-ink)}
.skip{position:absolute;left:-9999px;top:0;z-index:99;background:var(--surface);
  padding:var(--s3) var(--s4);border-radius:var(--r-md);box-shadow:var(--sh-3)}
.skip:focus{left:var(--s3);top:var(--s3)}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{
  animation-duration:.01ms!important;transition-duration:.01ms!important}}

/* ============================================================ shell */
.app{display:flex;flex-direction:column;height:100dvh}

header{
  background:
    radial-gradient(120% 180% at 88% -40%,rgba(120,172,230,.32) 0%,transparent 60%),
    radial-gradient(80% 140% at 0% 120%,rgba(43,90,150,.45) 0%,transparent 62%),
    linear-gradient(118deg,var(--hd-a) 0%,var(--hd-b) 100%);
  color:#fff;padding:var(--s4) var(--s5);display:flex;align-items:center;gap:var(--s5);
  flex-wrap:wrap;flex:none;position:relative;isolation:isolate}
header::after{content:"";position:absolute;inset:auto 0 0 0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.22),transparent)}
h1{font-family:var(--f-hd);font-size:var(--t-xl);font-weight:700;letter-spacing:-.02em;
  line-height:var(--lh-tight)}
.sub{font-family:var(--f-ui);font-size:var(--t-xs);font-weight:600;letter-spacing:.09em;
  text-transform:uppercase;color:#B2CFF0;margin-top:6px}
.hmeta{margin-left:auto;display:flex;gap:var(--s2);flex-wrap:wrap;align-items:center}
.pill{font-family:var(--f-ui);font-size:var(--t-xs);font-weight:550;letter-spacing:.005em;
  background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.22);color:#E6EEFA;
  padding:7px 13px;border-radius:100px;white-space:nowrap;backdrop-filter:blur(6px)}
.pill b{color:#FFD980;font-weight:600}
.pill.warn{background:rgba(255,209,128,.13);border-color:rgba(255,209,128,.32);color:#FFE3AE}
.iconbtn{width:34px;height:34px;display:grid;place-items:center;border-radius:var(--r-md);
  border:1px solid rgba(255,255,255,.22);background:rgba(255,255,255,.09);color:#DCE8F7;
  cursor:pointer;transition:background var(--dur) var(--ease)}
.iconbtn:hover{background:rgba(255,255,255,.2)}
.iconbtn svg{width:16px;height:16px}

/* ============================================================ KPI strip */
.kpis{display:flex;gap:var(--s2);padding:var(--s3) var(--s5) 0;overflow-x:auto;flex:none;
  scrollbar-width:thin}
.kpis::-webkit-scrollbar{height:6px}
.kpis::-webkit-scrollbar-thumb{background:var(--line);border-radius:100px}
.kpi{flex:1 0 auto;min-width:150px;text-align:left;background:var(--g-surface);
  border:1px solid var(--line);border-radius:14px;padding:15px 17px 13px;cursor:pointer;
  font:inherit;color:inherit;position:relative;overflow:hidden;box-shadow:var(--sh-1);
  transition:border-color var(--dur) var(--ease),box-shadow var(--dur) var(--ease),
             transform var(--dur) var(--ease)}
/* accent rail — a gradient, and it grows on hover so the card feels responsive */
.kpi::before{content:"";position:absolute;inset:0 0 auto 0;height:3px;background:var(--g-brand);
  transition:height var(--dur) var(--ease)}
/* inner top sheen — the highlight that makes a flat rectangle read as a raised card */
.kpi::after{content:"";position:absolute;inset:3px 0 auto 0;height:46px;
  background:var(--g-sheen);opacity:.65;pointer-events:none}
.kpi.t-stop::before{background:var(--g-stop)}.kpi.t-go::before{background:var(--g-go)}
.kpi.t-amber::before{background:var(--g-warn)}.kpi.t-blue::before{background:var(--g-brand)}
.kpi.t-mute::before{background:linear-gradient(135deg,#8A94A6,#6E798D)}
.kpi:hover{border-color:var(--brand-line);box-shadow:var(--sh-2);transform:translateY(-2px)}
.kpi:active{transform:translateY(0);box-shadow:var(--sh-1)}
.kpi:hover::before{height:5px}
.kpi[aria-pressed="true"]{border-color:var(--brand);
  box-shadow:0 0 0 3px var(--brand-wash),var(--sh-2)}
.kpi[aria-pressed="true"]::before{height:5px}
.kpi-v{display:block;font-family:var(--f-hd);font-size:var(--t-2xl);font-weight:700;
  line-height:1.08;letter-spacing:-.03em;color:var(--text);font-variant-numeric:tabular-nums}
.kpi-l{display:block;font-size:var(--t-xs);letter-spacing:.02em;color:var(--text-2);
  font-weight:650;margin-top:7px;line-height:1.3}
.kpi-s{display:block;font-size:var(--t-xs);color:var(--text-3);margin-top:3px;font-weight:450;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

/* ============================================================ tabs + toolbar */
/* ---- script-free tabs + row expansion ---------------------------------- */
.tabr{position:absolute;opacity:0;pointer-events:none;width:0;height:0}
.js-only{display:none}
html.js .js-only{display:flex}
.tabs{display:flex;gap:2px;padding:var(--s3) var(--s5) 0;border-bottom:1px solid var(--line);
  flex:none;flex-wrap:wrap}
.tab{border:0;background:none;font-family:var(--f-ui);font-size:var(--t-sm);font-weight:650;
  letter-spacing:.02em;color:var(--text-3);padding:11px 17px;cursor:pointer;
  border-bottom:2.5px solid transparent;margin-bottom:-1px;border-radius:9px 9px 0 0;
  transition:color var(--dur) var(--ease),border-color var(--dur) var(--ease),
             background var(--dur) var(--ease)}
.tab:hover{background:var(--surface-2)}
.tab{user-select:none}
#tab-log:checked    ~ .tabs label[for="tab-log"],
#tab-rules:checked  ~ .tabs label[for="tab-rules"],
#tab-data:checked   ~ .tabs label[for="tab-data"],
#tab-method:checked ~ .tabs label[for="tab-method"]{color:var(--brand);
  border-bottom-color:var(--brand)}
.tabr:focus-visible ~ .tabs label{outline:2px solid var(--focus);outline-offset:2px}
#tab-rules:checked  ~ .pane[data-t="rules"],
#tab-data:checked   ~ .pane[data-t="data"],
#tab-method:checked ~ .pane[data-t="method"]{display:block}
#tab-log:checked    ~ .pane[data-t="log"]{display:flex}
.tab:hover{color:var(--text)}
.tab[aria-selected="true"]{color:var(--brand);border-bottom-color:var(--brand)}

.tools{display:flex;gap:9px;align-items:center;padding:13px var(--s5);flex-wrap:wrap;
  flex:none;border-bottom:1px solid var(--line);background:var(--bg)}
.chip{font-family:var(--f-ui);font-size:var(--t-sm);font-weight:600;letter-spacing:.005em;
  padding:8px 15px;border:1px solid var(--line);background:var(--g-surface);color:var(--text-2);
  border-radius:100px;cursor:pointer;white-space:nowrap;box-shadow:var(--sh-1);
  transition:all var(--dur) var(--ease)}
.chip:hover{border-color:var(--brand-line);color:var(--brand);transform:translateY(-1px);
  box-shadow:var(--sh-2)}
.chip:active{transform:translateY(0);box-shadow:none}
.chip[aria-pressed="true"]{background:var(--g-brand);color:#fff;border-color:var(--brand-ink);
  font-weight:650;
  box-shadow:0 2px 5px rgba(27,63,110,.30),0 1px 2px rgba(27,63,110,.22),
             inset 0 1px 0 rgba(255,255,255,.22)}
.chip[aria-pressed="true"]:hover{color:#fff;transform:translateY(-1px);
  box-shadow:0 4px 10px rgba(27,63,110,.32),inset 0 1px 0 rgba(255,255,255,.22)}
.sep{width:1px;height:20px;background:var(--line);margin:0 2px}
.search{flex:1;min-width:200px;max-width:330px;border:1px solid var(--line);
  border-radius:100px;padding:9px 17px;font-family:var(--f-ui);font-size:var(--t-sm);
  font-weight:500;background:var(--surface);color:var(--text);box-shadow:var(--sh-1);
  transition:border-color var(--dur) var(--ease),box-shadow var(--dur) var(--ease)}
.search::placeholder{color:var(--text-3)}
.search:focus{outline:0;border-color:var(--brand);
  box-shadow:0 0 0 3.5px var(--brand-wash),var(--sh-1)}
.btn{font-family:var(--f-ui);font-size:var(--t-sm);font-weight:650;letter-spacing:.005em;
  padding:8px 15px;border:1px solid var(--line);background:var(--g-surface);color:var(--text-2);
  border-radius:9px;cursor:pointer;transition:all var(--dur) var(--ease);box-shadow:var(--sh-1)}
.btn:hover{border-color:var(--brand-line);color:var(--brand);transform:translateY(-1px);
  box-shadow:var(--sh-2)}
.btn:active{transform:translateY(0);box-shadow:none;background:var(--surface-3)}
.count{font-family:var(--f-ui);font-size:var(--t-sm);font-weight:550;color:var(--text-3);
  margin-left:auto;white-space:nowrap;font-variant-numeric:tabular-nums}

/* ============================================================ panes */
.pane{flex:1;overflow:auto;padding:0 var(--s5) var(--s5);display:none;scrollbar-width:thin}

/* The log pane does not scroll itself — its card does. That single change is what makes the
   sticky header work: the header now shares a scroll container with the rows it labels. */
.pane[data-t="log"]{flex-direction:column;overflow:hidden;padding-bottom:var(--s4)}

.pane[data-t="log"] .card{flex:1;min-height:0;overflow:auto}
.pane::-webkit-scrollbar{width:10px;height:10px}
.pane::-webkit-scrollbar-thumb{background:var(--line);border-radius:100px;
  border:2px solid var(--bg)}
.pane::-webkit-scrollbar-thumb:hover{background:var(--text-3)}

.card{background:var(--surface);border:1px solid var(--line);border-radius:14px;
  overflow:auto;margin-top:var(--s4);box-shadow:var(--sh-2);scrollbar-width:thin;
  position:relative}
table{width:100%;border-collapse:separate;border-spacing:0;font-size:var(--t-md)}
/* fixed layout ONLY where a <colgroup> defines the widths — applying it to a table without one
   forces every column to equal width. The Campaign Data and Thresholds tables size to content. */
#logtable{table-layout:fixed;min-width:1080px}   /* floor only — widths above are percentages */

thead th{position:sticky;top:0;z-index:3;background:var(--g-head);color:var(--text-2);
  text-align:left;font-family:var(--f-ui);font-size:var(--t-xs);font-weight:700;
  letter-spacing:.03em;padding:13px;white-space:normal;line-height:1.3;vertical-align:bottom;
  /* box-shadow, not border-bottom: a sticky cell's border detaches while scrolling */
  box-shadow:inset 0 -1px 0 var(--line),0 1px 0 var(--line)}
thead th.num{text-align:right}
thead th.s{cursor:pointer;user-select:none;transition:color var(--dur) var(--ease)}
thead th.s:hover{color:var(--brand)}
thead th.s::after{content:"↕";opacity:.4;margin-left:6px;font-size:11px;vertical-align:-1px}
thead th.s[data-dir="a"]::after{content:"↑";opacity:1;color:var(--brand)}
thead th.s[data-dir="d"]::after{content:"↓";opacity:1;color:var(--brand)}

tbody td,tbody th{padding:11px 13px;border-bottom:1px solid var(--line-soft);
  vertical-align:top;font-weight:400;text-align:left;overflow:hidden}
tbody td.num{text-align:right}
/* Optical alignment: a pill's text sits ~3px inside its own box, so without this nudge every
   badge floats above the campaign name's first baseline. 2px puts them on the same line. */
tbody td>.tag,tbody td>.prio,tbody td>.st{margin-top:2px}
/* Numbers share one line-height so decimal points line up down the column. */
tbody td.num{line-height:1.5;padding-top:12px}
tbody tr.p>*{background:color-mix(in srgb,var(--stop-wash) 55%,var(--surface))}
tbody tr.o>*{background:var(--surface-2);color:var(--text-3)}
tbody tr:not(.detail){cursor:pointer}
tbody tr:not(.detail):hover>*{background:var(--brand-wash)}
tbody tr.open>*{background:var(--brand-wash)}
/* the open row is the head of a group — tie it visually to its detail panel below */
tbody tr.open>*{box-shadow:inset 0 -1px 0 var(--brand-line)}
tbody tr.open>.c-camp{box-shadow:inset 0 -1px 0 var(--brand-line)}
/* controls are not part of the row's click target, so they must not inherit its cursor */
select.dec,input.note{cursor:auto}
select.dec{cursor:pointer}

/* sticky campaign column — survives horizontal scroll */
/* No horizontal scroll any more, so the campaign column no longer needs to be sticky —
   position:sticky on a cell also forces its own paint layer, which is wasted work here. */
.c-camp{background:var(--surface)}
.c-in{display:flex;gap:var(--s2);align-items:flex-start}
tbody tr.p>.c-camp{background:color-mix(in srgb,var(--stop-wash) 55%,var(--surface))}
tbody tr.o>.c-camp{background:var(--surface-2)}
tbody tr:not(.detail):hover>.c-camp,tbody tr.open>.c-camp{background:var(--brand-wash)}
.rowtog{position:absolute;opacity:0;pointer-events:none;width:0;height:0}
.disc{width:22px;height:22px;flex:none;display:grid;place-items:center;margin-top:1px;
  border:1px solid var(--line);background:var(--surface);border-radius:var(--r-sm);
  color:var(--text-3);cursor:pointer;transition:all var(--dur) var(--ease)}
.rowtog:focus-visible + .disc{outline:2px solid var(--focus);outline-offset:2px}
/* :has() lets a checked box in one row reveal the detail row that follows it — no script. */
tbody tr:has(.rowtog:checked) + tr.detail{display:table-row}
tbody tr:has(.rowtog:checked)>*{background:var(--brand-wash);
  box-shadow:inset 0 -1px 0 var(--brand-line)}
tbody tr:has(.rowtog:checked) .disc{color:var(--brand);border-color:var(--brand);
  background:var(--brand-wash)}
tbody tr:has(.rowtog:checked) .disc svg{transform:rotate(90deg)}
.disc svg{width:10px;height:10px;transition:transform var(--dur) var(--ease)}
.disc:hover{border-color:var(--brand);color:var(--brand)}
tr.open .disc{color:var(--brand);border-color:var(--brand);background:var(--brand-wash)}
tr.open .disc svg{transform:rotate(90deg)}
.c-txt{display:block;min-width:0;flex:1}
.camp{display:block;font-weight:650;font-size:var(--t-md);line-height:var(--lh-snug);
  letter-spacing:-.005em;overflow-wrap:anywhere}
.meta{display:block;font-family:var(--f-mono);font-size:var(--t-2xs);color:var(--text-3);
  margin-top:4px;letter-spacing:0;font-weight:500;overflow:hidden;text-overflow:ellipsis;
  white-space:nowrap}

.tag{display:inline-block;font-family:var(--f-ui);font-size:var(--t-xs);font-weight:650;
  padding:4px 11px;border-radius:100px;border:1px solid;white-space:nowrap;letter-spacing:.005em}
.tag.stock{color:var(--stop);border-color:var(--stop-line);background:var(--stop-wash)}
.tag.r1{color:var(--brand);border-color:var(--brand-line);background:var(--brand-wash)}
.tag.r2{color:var(--warn);border-color:var(--warn-line);background:var(--warn-wash)}

.prio{display:inline-flex;align-items:center;gap:6px;font-size:var(--t-xs);font-weight:650;
  padding:4px 12px 4px 9px;border-radius:100px;white-space:nowrap}
.prio i{width:3px;border-radius:2px;background:currentColor;opacity:.3}
.prio i:nth-child(1){height:6px}.prio i:nth-child(2){height:9px}.prio i:nth-child(3){height:12px}
.prio.high{background:var(--stop-wash);color:var(--stop)}
.prio.high i{opacity:1}
.prio.medium{background:var(--warn-wash);color:var(--warn)}
.prio.medium i:nth-child(1),.prio.medium i:nth-child(2){opacity:1}
.prio.low{background:var(--surface-3);color:var(--text-3)}
.prio.low i:nth-child(1){opacity:1}

.st{display:inline-block;font-family:var(--f-ui);font-size:var(--t-xs);font-weight:700;
  padding:4px 10px;border-radius:7px;white-space:nowrap;letter-spacing:.015em}
.st.p{background:var(--stop-wash);color:var(--stop)}
.st.r{background:var(--go-wash);color:var(--go)}
.st.o{background:var(--surface-3);color:var(--text-3)}
.cstate{display:block;font-family:var(--f-mono);font-size:var(--t-2xs);color:var(--text-3);
  margin-top:5px;letter-spacing:.02em}
.hot{color:var(--stop);font-weight:700}
.cool{color:var(--go);font-weight:700}
/* one column, two windows: 30D is the decision figure, 7D the trend beneath it */
td.acos{white-space:nowrap}
.a30{display:block;font-family:var(--f-mono);font-size:var(--t-md);font-weight:600}
.a7{display:block;font-family:var(--f-mono);font-size:var(--t-2xs);color:var(--text-3);
  margin-top:3px;font-weight:500}
.a7 .cool{font-weight:700}
table.dense .a7{display:none}

.stk{min-width:0}
.stk-t{font-size:var(--t-sm);line-height:var(--lh-snug)}
.stk-t b{font-weight:600}
.s-bad{color:var(--stop)}.s-warn{color:var(--warn)}.s-ok{color:var(--go)}.s-none{color:var(--text-3)}
.meter{display:flex;height:6px;border-radius:100px;overflow:hidden;margin:7px 0 5px;
  background:var(--surface-3);box-shadow:inset 0 1px 2px rgba(16,32,58,.08)}
.meter i{display:block}
.m-bad{background:var(--g-stop)}.m-warn{background:var(--g-warn)}
.m-none{background:var(--text-3);opacity:.35}.m-ok{background:var(--g-go)}
.stk-n{font-family:var(--f-mono);font-size:var(--t-2xs);color:var(--text-3)}

.c-reason{font-size:var(--t-sm);color:var(--text-2)}
/* the full reason is always one click away in the detail panel, so clamp it here */
.r-in{display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
table.dense .r-in{-webkit-line-clamp:2}
/* max-width on a <td> is only a hint the table layout may ignore — constrain the inner div. */
.r-in{line-height:var(--lh-body);text-wrap:pretty}
select.dec,input.note{font-family:var(--f-ui);font-size:var(--t-sm);font-weight:550;
  padding:7px 10px;border:1px solid var(--line);border-radius:8px;background:var(--g-surface);
  color:var(--text);box-shadow:var(--sh-1);transition:all var(--dur) var(--ease)}
input.note{width:100%;min-width:0;font-weight:450}
select.dec{width:100%;min-width:0}
select.dec:hover,input.note:hover{box-shadow:var(--sh-2)}
select.dec:hover,input.note:hover{border-color:var(--brand-line)}
select.dec:focus,input.note:focus{outline:0;border-color:var(--brand);
  box-shadow:0 0 0 3px var(--brand-wash)}
select.dec[data-v="Approved"]{background:var(--go-wash);color:var(--go);font-weight:600;
  border-color:var(--go-line)}
select.dec[data-v="Rejected"]{background:var(--stop-wash);color:var(--stop);font-weight:600;
  border-color:var(--stop-line)}
select.dec[data-v="On hold"]{background:var(--warn-wash);color:var(--warn);font-weight:600;
  border-color:var(--warn-line)}

/* density */
table.dense tbody td,table.dense tbody th{padding:6px 11px;font-size:var(--t-sm)}
table.dense .meta,table.dense .cstate,table.dense .stk-n{display:none}
table.dense .meter{margin:4px 0 0}
table.dense .r-in{font-size:var(--t-xs)}

/* detail row */
tr.detail{display:none}
tr.detail.show{display:table-row}
tr.detail>td{background:var(--surface-2)!important;border-bottom:2px solid var(--line);
  padding:0 13px 0 0}
.dwrap{display:flex;gap:var(--s6);flex-wrap:wrap;padding:var(--s4) var(--s3) var(--s5) 46px;
  animation:fade var(--dur) var(--ease)}
@keyframes fade{from{opacity:0;transform:translateY(-3px)}to{opacity:1;transform:none}}
.dcol{flex:1;min-width:290px}
.dcol h4{font-family:var(--f-ui);font-size:var(--t-xs);font-weight:700;letter-spacing:.06em;
  text-transform:uppercase;color:var(--text-3);margin-bottom:var(--s3)}
.dreason{font-size:var(--t-sm);line-height:var(--lh-body);max-width:62ch;color:var(--text-2);
  text-wrap:pretty}
ol.trace{list-style:none;font-size:var(--t-sm);counter-reset:t}
ol.trace li{padding:5px 0 5px 24px;position:relative;line-height:var(--lh-snug)}
ol.trace li::before{position:absolute;left:0;top:4px;width:17px;height:17px;border-radius:50%;
  display:grid;place-items:center;font-size:11px;font-weight:700;line-height:1}
ol.trace li.y::before{content:"✓";background:var(--go-wash);color:var(--go)}
ol.trace li.n::before{content:"✕";background:var(--stop-wash);color:var(--stop)}
.tr-l{display:block;color:var(--text)}
.tr-d{display:block;font-family:var(--f-mono);font-size:var(--t-2xs);color:var(--text-3);
  margin-top:1px}
.dstats{display:grid;grid-template-columns:repeat(auto-fit,minmax(112px,1fr));gap:var(--s3);
  margin-top:var(--s4)}
.dstats dt{font-family:var(--f-ui);font-size:var(--t-2xs);font-weight:650;letter-spacing:.04em;
  text-transform:uppercase;color:var(--text-3)}
.dstats dd{font-family:var(--f-mono);font-size:var(--t-lg);font-weight:600;margin-top:2px;
  letter-spacing:-.02em}

/* content blocks */
.notice{background:linear-gradient(135deg,#FDF6E8,var(--warn-wash));
  border:1px solid var(--warn-line);border-radius:var(--r-md);
  padding:12px 15px;font-size:var(--t-sm);line-height:var(--lh-body);margin-top:var(--s4);
  color:var(--text-2);max-width:110ch;text-wrap:pretty}
.notice b{color:var(--text);font-weight:600}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:var(--s3);
  margin-top:var(--s4)}
.box{background:var(--g-surface);border:1px solid var(--line);border-radius:var(--r-lg);
  padding:var(--s4) var(--s5);box-shadow:var(--sh-1);position:relative;overflow:hidden;
  transition:box-shadow var(--dur) var(--ease)}
.box::before{content:"";position:absolute;inset:0 0 auto 0;height:1px;
  background:linear-gradient(90deg,transparent,var(--brand-line),transparent)}
.box:hover{box-shadow:var(--sh-2)}
.box h3{font-family:var(--f-hd);font-size:var(--t-lg);font-weight:700;margin-bottom:var(--s3);
  letter-spacing:-.02em;color:var(--text)}
.box p,.box li{font-size:var(--t-sm);line-height:var(--lh-body);color:var(--text-2);
  text-wrap:pretty}
.box ul{margin:var(--s2) 0 0;padding-left:18px}
.box li{margin-bottom:6px}
.box li::marker{color:var(--text-3)}
.box table td,.box table th{padding:8px 9px;border-bottom:1px solid var(--line-soft);
  font-size:var(--t-sm)}
.box code,.mono-i{font-family:var(--f-mono);font-size:.92em;background:var(--surface-3);
  padding:1px 5px;border-radius:4px;color:var(--brand-ink)}
.val{font-weight:600;color:var(--brand)}
.gate{display:flex;gap:var(--s3);align-items:flex-start;padding:10px 0;
  border-bottom:1px solid var(--line-soft)}
.gate:last-child{border-bottom:0}
.gn{flex:none;width:25px;height:25px;border-radius:var(--r-sm);background:var(--g-brand);
  color:#fff;font-family:var(--f-mono);font-size:var(--t-xs);font-weight:600;display:grid;
  place-items:center;box-shadow:0 1px 2px rgba(27,63,110,.3),inset 0 1px 0 rgba(255,255,255,.2)}
.gate b{display:block;font-size:var(--t-md);margin-bottom:2px}
.empty{padding:56px var(--s5);text-align:center;color:var(--text-3);
  font-family:var(--f-ui);font-size:var(--t-md);font-weight:500}

/* toast */
.toast{position:fixed;bottom:var(--s5);left:50%;transform:translate(-50%,14px);
  background:linear-gradient(135deg,#22334F,#16233B);color:#F2F6FC;
  font-size:var(--t-sm);font-weight:500;
  padding:10px 18px;border-radius:100px;box-shadow:var(--sh-3);opacity:0;pointer-events:none;
  transition:opacity var(--dur) var(--ease),transform var(--dur) var(--ease);z-index:50}
.toast.show{opacity:1;transform:translate(-50%,0)}

@media (max-width:820px){
  header{padding:var(--s3) var(--s4)}
  .kpis,.tabs,.tools{padding-left:var(--s4);padding-right:var(--s4)}
  .pane{padding-left:var(--s4);padding-right:var(--s4)}
}
@media print{
  body{overflow:visible;background:#fff}
  .app{height:auto}
  .tools,.tabs,.kpis,.iconbtn,.disc,.toast{display:none!important}
  .card{box-shadow:none;border-color:#bbb}
  tr.detail{display:table-row!important}
  thead th{position:static;background:#eee;color:#000}
}
"""

JS = r"""
(function(){
var S={filter:'All',q:''},
    tb=document.getElementById('tbody'),
    rowsEl=[].slice.call(tb.querySelectorAll('tr:not(.detail)')),
    tbl=document.getElementById('logtable'),
    toastEl=document.getElementById('toast'),tt;

function store(k,v){try{localStorage.setItem('eppa:'+k,v)}catch(e){}}
function load(k){try{return localStorage.getItem('eppa:'+k)}catch(e){return null}}
function toast(msg){toastEl.textContent=msg;toastEl.classList.add('show');
  clearTimeout(tt);tt=setTimeout(function(){toastEl.classList.remove('show')},2200)}

/* density ---------------------------------------------------------------- */
function setDense(on){tbl.classList.toggle('dense',on);store('dense',on?'1':'');
  var b=document.getElementById('densebtn');
  b.setAttribute('aria-pressed',on?'true':'false');
  b.textContent=on?'COMFORTABLE':'COMPACT'}
setDense(load('dense')==='1');
document.getElementById('densebtn').onclick=function(){setDense(!tbl.classList.contains('dense'))};

/* staff decisions + notes (browser-local) --------------------------------- */
document.querySelectorAll('select.dec').forEach(function(s){
  var v=load('dec:'+s.dataset.cid); if(v){s.value=v} s.dataset.v=s.value;
  s.onchange=function(){s.dataset.v=s.value;store('dec:'+s.dataset.cid,s.value);
    toast('Decision saved — '+s.value)}});
document.querySelectorAll('input.note').forEach(function(n){
  var v=load('note:'+n.dataset.cid); if(v){n.value=v}
  n.oninput=function(){store('note:'+n.dataset.cid,n.value)}});

/* filtering -------------------------------------------------------------- */
function apply(){
  var n=0,f=S.filter,q=S.q;
  rowsEl.forEach(function(tr){
    var st=tr.dataset.status,r=tr.dataset.rule,p=tr.dataset.prio,ok;
    if(f==='All')ok=true;
    else if(f==='Paused')ok=st==='PAUSED';
    else if(f==='Still running')ok=st==='RUNNING';
    else if(f==='Already off')ok=st==='ALREADY OFF';
    else if(f==='High'||f==='Medium'||f==='Low')ok=p===f;
    else ok=(st==='PAUSED'&&r===f);
    if(ok&&q)ok=tr.dataset.s.indexOf(q)>=0;
    tr.style.display=ok?'':'none';
    var d=tb.querySelector('tr.detail[data-for="'+tr.dataset.i+'"]');
    if(d&&!ok){d.classList.remove('show');tr.classList.remove('open');
      tr.querySelector('.disc').setAttribute('aria-expanded','false')}
    if(ok)n++;});
  document.getElementById('count').textContent=n+' of '+rowsEl.length+' campaigns';
  document.getElementById('empty').style.display=n?'none':'block';
  document.querySelectorAll('.chip').forEach(function(c){
    c.setAttribute('aria-pressed',c.dataset.v===f?'true':'false')});
  document.querySelectorAll('.kpi').forEach(function(c){
    c.setAttribute('aria-pressed',(c.dataset.filter&&c.dataset.filter===f)?'true':'false')});
}
document.querySelectorAll('.chip').forEach(function(c){
  c.onclick=function(){S.filter=c.dataset.v;apply()}});
document.querySelectorAll('.kpi').forEach(function(c){
  c.onclick=function(){if(c.dataset.filter){S.filter=c.dataset.filter;show('log');apply()}}});
document.getElementById('q').oninput=function(){S.q=this.value.toLowerCase().trim();apply()};
document.getElementById('reset').onclick=function(){
  S.filter='All';S.q='';document.getElementById('q').value='';apply();toast('Filters cleared')};

/* expand / collapse — the WHOLE row is the target, not just the chevron ----- */
function toggleRow(tr,force){
  var d=tb.querySelector('tr.detail[data-for="'+tr.dataset.i+'"]'),
      open=(force===undefined)?!tr.classList.contains('open'):force;
  tr.classList.toggle('open',open);
  d.classList.toggle('show',open);
  tr.querySelector('.disc').setAttribute('aria-expanded',open?'true':'false');
  return open;
}
tb.addEventListener('click',function(ev){
  /* the staff controls own their clicks — toggling the row under them would be maddening */
  if(ev.target.closest('select,input,textarea,option,a'))return;
  /* a click that ends a text selection is a highlight, not a row activation */
  var sel=window.getSelection&&window.getSelection().toString();
  if(sel&&sel.length)return;
  var tr=ev.target.closest('tr');
  if(!tr||tr.classList.contains('detail')||!tr.dataset.i)return;
  toggleRow(tr);
});
/* Keyboard access is the chevron button's job — it is a real <button>, so Enter and Space
   already work and it sits in the natural tab order. No keydown handler here on purpose:
   a button's Enter/Space fires a native click that bubbles to the handler above, so a second
   handler would toggle twice and appear to do nothing. */

/* sorting ----------------------------------------------------------------- */
document.querySelectorAll('th.s').forEach(function(th){
  th.onclick=function(){
    var key=th.dataset.k,dir=th.dataset.dir==='a'?'d':'a';
    document.querySelectorAll('th.s').forEach(function(x){x.removeAttribute('data-dir')});
    th.dataset.dir=dir;
    var pairs=rowsEl.map(function(tr){
      return[tr,tb.querySelector('tr.detail[data-for="'+tr.dataset.i+'"]')]});
    pairs.sort(function(A,B){
      var a=A[0].dataset[key],b=B[0].dataset[key];
      if(key==='spend'||key==='acos'||key==='listings'){a=parseFloat(a||-1);b=parseFloat(b||-1)}
      else{a=(a||'').toLowerCase();b=(b||'').toLowerCase()}
      return (a<b?-1:a>b?1:0)*(dir==='a'?1:-1)});
    pairs.forEach(function(p){tb.appendChild(p[0]);tb.appendChild(p[1])});};});

/* tabs -------------------------------------------------------------------- */
function show(t){
  document.querySelectorAll('.tab').forEach(function(b){
    b.setAttribute('aria-selected',b.dataset.t===t?'true':'false')});
  document.querySelectorAll('.pane').forEach(function(p){p.dataset.on=p.dataset.t===t?'1':'0'});
  document.getElementById('toolbar').style.display=(t==='log')?'':'none';}
document.querySelectorAll('.tab').forEach(function(b){b.onclick=function(){show(b.dataset.t)}});

/* CSV of the current view -------------------------------------------------- */
document.getElementById('csv').onclick=function(){
  var head=['Campaign','Campaign ID','Type','Campaign state','Advertised listings','Out of stock',
    'Low stock','No stock data','Rule','Priority','30D ACOS %','7D ACOS %','30D orders',
    '14D clicks','30D spend','Status','Reason','Decision','Note'],out=[head.join(',')],n=0;
  rowsEl.forEach(function(tr){
    if(tr.style.display==='none')return;n++;
    var d=DATA[+tr.dataset.i],cid=tr.dataset.cid,
        dec=(document.querySelector('select.dec[data-cid="'+cid+'"]')||{}).value||'',
        note=(document.querySelector('input.note[data-cid="'+cid+'"]')||{}).value||'';
    out.push([d.campaign,d.campaign_id,d.type,d.status,d.listings,d.out_of_stock,d.low_stock,
      d.no_stock_data,d.rule,d.priority||'',d.acos30==null?'':d.acos30.toFixed(1),
      d.acos7==null?'':d.acos7.toFixed(1),d.ord30,d.clicks14,d.spend30.toFixed(2),d.outcome,
      d.reason,dec,note].map(function(v){
        v=String(v==null?'':v);return /[",\n]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v}).join(','));});
  var b=new Blob(['﻿'+out.join('\r\n')],{type:'text/csv;charset=utf-8'}),
      a=document.createElement('a');
  a.href=URL.createObjectURL(b);a.download='eppa_pause_log_'+ANCHOR+'.csv';a.click();
  URL.revokeObjectURL(a.href);toast('Exported '+n+' campaigns');};

/* keyboard ---------------------------------------------------------------- */
document.addEventListener('keydown',function(ev){
  if(ev.target.matches('input,select,textarea')){
    if(ev.key==='Escape')ev.target.blur();return}
  if(ev.key==='/'){ev.preventDefault();document.getElementById('q').focus()}
  else if(ev.key==='Escape'){document.getElementById('reset').click()}
  else if(ev.key==='d'||ev.key==='D'){document.getElementById('densebtn').click()}});

apply();
})();
"""

chips = "".join('<button class="chip" data-v="%s" aria-pressed="%s">%s</button>'
                % (x, "true" if x == "All" else "false", x)
                for x in ["All", "Paused", "Stock", "Rule 1", "Rule 2", "High", "Medium",
                          "Low", "Still running", "Already off"])

TPL = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<title>eBay PPC Pause Automation — LEDSone UK</title><style>__CSS__</style></head><body>
<a class="skip" href="#logtable">Skip to the pause log</a>
<div class="app">

<header>
 <div><h1>eBay PPC Product Pause Automation</h1>
 <div class="sub">LEDSone · eBay UK · Promoted Listings — Advanced (ON_SITE)</div></div>
 <div class="hmeta">
  <span class="pill">30D window <b>__W30__</b></span>
  <span class="pill">refreshed <b>__GEN__</b></span>
  <span class="pill">next run <b>Monday</b></span>
  <span class="pill warn">recommendation only — nothing is paused automatically</span>
 </div>
</header>

<div class="kpis">__KPIS__</div>

<!-- Tabs run on radio inputs, not script: the portal viewer executes no JavaScript, and a
     tab you cannot reach is a tab that does not exist. -->
<input type="radio" name="tab" id="tab-log" class="tabr" checked>
<input type="radio" name="tab" id="tab-rules" class="tabr">
<input type="radio" name="tab" id="tab-data" class="tabr">
<input type="radio" name="tab" id="tab-method" class="tabr">
<div class="tabs">
 <label class="tab" for="tab-log">PAUSE LOG</label>
 <label class="tab" for="tab-rules">RULES &amp; THRESHOLDS</label>
 <label class="tab" for="tab-data">CAMPAIGN DATA</label>
 <label class="tab" for="tab-method">METHOD</label>
</div>

<!-- Everything in this bar needs script. It is hidden unless JS runs, so the portal viewer
     shows a clean table rather than a row of controls that do nothing. -->
<div class="tools js-only" id="toolbar">
 __CHIPS__
 <span class="sep"></span>
 <input id="q" class="search" placeholder="Search campaign or ID…   /" aria-label="Search campaigns">
 <button id="reset" class="btn">RESET</button>
 <button id="densebtn" class="btn" aria-pressed="false">COMPACT</button>
 <button id="csv" class="btn">EXPORT CSV</button>
 <span id="count" class="count"></span>
</div>

<div class="pane" data-t="log">
 <div class="card"><table id="logtable">
 <!-- Percentage widths, not pixels: the table fills the viewport exactly and never scrolls
      sideways. Fixed widths are still essential (without them the browser sizes columns from
      content, so every filter or sort silently reflows the grid) — they are just relative now.
      30D orders and 14D clicks live in the row's detail panel and on the Campaign Data tab. -->
 <colgroup>
  <col style="width:18.5%"><col style="width:13%"><col style="width:8.5%">
  <col style="width:7%"><col style="width:7.5%"><col style="width:7.5%">
  <col style="width:7.5%"><col style="width:14.5%"><col style="width:8%">
  <col style="width:8%">
 </colgroup>
 <thead><tr>
  <th class="s" data-k="s" scope="col">Campaign</th>
  <th class="s" data-k="listings" scope="col">Stock position of advertised listings</th>
  <th class="s" data-k="status" scope="col">Status</th>
  <th class="s" data-k="rule" scope="col">Rule</th>
  <th class="s" data-k="prio" scope="col">Priority</th>
  <th class="s num" data-k="acos" scope="col"
      title="ACOS — 30 days (__W30__) with the 7-day figure (__W7__) beneath">ACOS</th>
  <th class="s num" data-k="spend" scope="col" title="30 days: __W30__">30D spend</th>
  <th scope="col">Reason</th><th scope="col">Decision</th><th scope="col">Note</th>
 </tr></thead>
 <tbody id="tbody">__ROWS__</tbody></table>
 <div id="empty" class="empty" style="display:none">No campaigns match this filter.</div>
 </div>
</div>

<div class="pane" data-t="rules">
 <div class="notice"><b>Thresholds are configuration, not code.</b> Every value below comes from the
 <i>Pause Rules</i> sheet of the source workbook and feeds the live calculation — change a value and
 the whole report recomputes. Rules are evaluated top to bottom and <b>the first match wins</b>.</div>
 <div class="grid">
  <div class="box"><h3>Thresholds</h3><table>__RULEROWS__</table></div>
  <div class="box"><h3>Gate order</h3>
   <div class="gate"><span class="gn">0</span><div><b>State check</b><p>If the campaign is not
    RUNNING it is not evaluated at all — status becomes ALREADY OFF and every rule column reads —.</p></div></div>
   <div class="gate"><span class="gn">1</span><div><b>Stock rule</b><p>Availability beats
    performance. Fires when the campaign advertises listings that are out of stock.</p></div></div>
   <div class="gate"><span class="gn">2</span><div><b>Rule 1 — high ACOS</b><p>Scope: 30D orders
    &gt; 0. Pauses at 30D ACOS ≥ __CEIL__%, unless 7D ACOS &lt; __RESC__% shows an improving trend.</p></div></div>
   <div class="gate"><span class="gn">3</span><div><b>Rule 2 — clicks without sales</b><p>Scope: 14D
    orders = 0. Pauses at ≥ __CLK__ clicks, unless 14D spend &lt; __FLOOR__ (cheap organic clicks).</p></div></div>
   <div class="gate"><span class="gn">4</span><div><b>Priority</b><p>Out-of-stock ranks High;
    otherwise by 30D spend at risk — High ≥ __PH__, Medium ≥ __PM__, else Low.</p></div></div>
  </div>
  <div class="box"><h3>Measurement windows</h3>
   <table>
    <tr><th scope="row">30 days</th><td class="mono val">__W30__</td>
        <td class="muted">Rule 1 ACOS · orders · spend at risk · priority</td></tr>
    <tr><th scope="row">14 days</th><td class="mono val">__W14__</td>
        <td class="muted">Rule 2 orders · clicks · spend floor</td></tr>
    <tr><th scope="row">7 days</th><td class="mono val">__W7__</td>
        <td class="muted">Rule 1 rescue — the improving-trend check</td></tr>
   </table>
   <p style="margin-top:12px">Every window <b>ends on __ANCHOR_LONG__ and includes it</b>. The
   anchor is the latest date present in the advertising data, never today's date — otherwise a
   late sync would leave the final day half-counted and quietly change decisions.</p>
  </div>
 </div>
</div>

<div class="pane" data-t="data">
 <div class="notice">The live inputs behind every decision — one row per campaign.
 <b>30D = __W30__</b> · 14D = __W14__ · 7D = __W7__ (each window ends on the anchor date
 __ANCHOR_LONG__ and includes it). ACOS is derived (<i>ad fees ÷ attributed sales × 100</i>),
 never stored.</div>
 <div class="card"><table><thead><tr>
  <th scope="col">Campaign</th><th scope="col">Campaign ID</th><th scope="col">Type</th>
  <th scope="col">State</th><th class="num" scope="col">Listings</th>
  <th class="num" scope="col">30D spend</th><th class="num" scope="col">30D sales</th>
  <th class="num" scope="col" title="30 days: __W30__">30D orders</th><th class="num" scope="col">30D ACOS</th>
  <th class="num" scope="col" title="7 days: __W7__">7D ACOS</th><th class="num" scope="col">14D orders</th>
  <th class="num" scope="col" title="14 days: __W14__">14D clicks</th><th class="num" scope="col">14D spend</th>
 </tr></thead><tbody>__DATAROWS__</tbody></table></div>
</div>

<div class="pane" data-t="method">
 <div class="grid">
  <div class="box"><h3>Where the data comes from</h3><ul>
   <li><b>Campaigns</b> — <code>ebay_campaigns.campaigns</code>, scoped to
       <code>marketplace_id='EBAY_GB'</code> + <code>sub_source=1</code> (LEDSone UK).</li>
   <li><b>Performance</b> — <code>ebay_campaigns.performance_data</code>: spend =
       <code>ad_fees_payout_currency</code>, sales = <code>sale_amount_payout_currency</code>,
       orders = <code>attributed_sales</code>.</li>
   <li><b>Listings &amp; stock</b> — <code>listings.ebay_listings</code> (with the mandatory
       <code>all_list=1</code> filter) → <code>inventory.products</code> →
       <code>local_inventory_current_stock_location_wise</code> (UK).</li>
   <li><b>Windows</b> — 30D <code>__W30__</code>, 14D <code>__W14__</code>, 7D <code>__W7__</code>.
       All anchor on the latest loaded date (<code>__ANCHOR_LONG__</code>), never
       <code>CURRENT_DATE</code>, so a late sync cannot produce a short final day.</li>
  </ul></div>
  <div class="box"><h3>What is deliberately excluded</h3><ul>
   <li><b>Standard (COST_PER_SALE) campaigns.</b> They record no per-click spend or sales, so ACOS
       cannot be computed and the Rule 2 spend-floor rescue would fire permanently. Stated rather
       than dropped quietly.</li>
   <li><b>Listings with no stock record</b> show as <i>no data</i> — never as zero, which would
       auto-recommend pausing a possibly well-stocked listing.</li>
  </ul></div>
  <div class="box"><h3>Known limits</h3><ul>
   <li><b>Stock is live as of today</b>; spend is windowed. The two are not aligned in time.</li>
   <li><b>Grain is the campaign</b>, matching the source task sheet. A campaign advertises many
       listings and each listing carries many variant SKUs, so there is no single "units in stock"
       per row — the Stock column reports the position across the campaign's listings instead.</li>
   <li>Ad history is a 60-day rolling window, which covers 30D/14D/7D but no longer trend.</li>
  </ul></div>
  <div class="box"><h3>Governance &amp; shortcuts</h3><ul>
   <li>Read-only. The report <b>recommends</b>; a human applies approved pauses in Seller Hub.</li>
   <li>Decisions and notes you enter are saved in this browser only.</li>
   <li>Refreshes automatically every <b>Monday</b>; each run recomputes the last 30 days.</li>
   <li><b>Click any row</b> to open its decision trace; click again to close.</li>
   <li>Keyboard: <code>/</code> search · <code>Esc</code> reset · <code>D</code> density.</li>
  </ul></div>
 </div>
</div>
</div>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<script>var ANCHOR=__ANCHORJS__,DATA=__DATAJS__;__JS__</script></body></html>"""

slim = [{k: r[k] for k in ("campaign", "campaign_id", "type", "status", "outcome", "listings",
                           "out_of_stock", "low_stock", "no_stock_data", "rule", "priority",
                           "acos30", "acos7", "ord30", "clicks14", "spend30", "reason")}
        for r in rows]

out = (TPL.replace("__CSS__", CSS).replace("__JS__", JS)
       .replace("__KPIS__", kpis).replace("__CHIPS__", chips)
       .replace("__ROWS__", "".join(trs)).replace("__DATAROWS__", data_rows)
       .replace("__RULEROWS__", rule_rows)
       .replace("__W30__", W30).replace("__W14__", W14).replace("__W7__", W7)
       .replace("__ANCHOR_LONG__", ANCHOR_LONG).replace("__ANCHOR__", ANCHOR)
       .replace("__GEN__", datetime.now().strftime("%d %b %Y %H:%M"))
       .replace("__CEIL__", "%g" % TH["acos_ceiling"]).replace("__RESC__", "%g" % TH["acos_rescue"])
       .replace("__CLK__", str(TH["clicks_min"])).replace("__FLOOR__", m(TH["spend_floor"]))
       .replace("__PH__", m(TH["prio_high"])).replace("__PM__", m(TH["prio_med"]))
       .replace("__ANCHORJS__", json.dumps(ANCHOR))
       .replace("__DATAJS__", json.dumps(slim, ensure_ascii=False)))

# Fail loudly on any placeholder the substitution chain missed. A stray __W30__ renders as
# literal text on the page and looks like a content bug, not a build bug — and the weekly job
# would publish it. Raising here makes the scheduled run fail closed and keep the last good file.
_left = sorted(set(re.findall(r"__[A-Z0-9_]+__", out)))
if _left:
    raise SystemExit("unsubstituted placeholders in the template: %s" % ", ".join(_left))

p = os.path.join(FINAL, "REQ-15-D01_eppa_dashboard.html")
open(p, "w", encoding="utf-8").write(out)
print("dashboard -> %s  (%.1f KB)" % (p, os.path.getsize(p) / 1024))
