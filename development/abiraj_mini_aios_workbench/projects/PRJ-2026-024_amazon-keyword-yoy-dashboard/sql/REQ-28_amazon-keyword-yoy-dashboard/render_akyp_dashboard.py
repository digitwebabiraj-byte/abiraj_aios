#!/usr/bin/env python3
"""
REQ-28-D01 — Amazon PPC Keyword YoY Performance Dashboard (akyp) · renderer
PRJ-2026-024

Takes the spec HTML template (the imported source document) and the live payload from
build_akyp_d01.py, and produces the self-contained deliverable dashboard by embedding the
data and short-circuiting the spec's live-Amazon-API service to read from that embedded
snapshot instead. The ENTIRE spec UI + business logic (YoY calc, diagnosis/priority/root-
cause engine, filters, charts, table, export) is preserved untouched; only the data layer
is swapped from live-fetch to embedded, and the account/period are locked to the snapshot.

  input : ../evidence/source_documents/REQ-28_.../2026-08-14_source_amazon-keyword-yoy-dashboard-spec.html
          ./akyp_payload.json
  output: ../evidence/final_outputs/REQ-28_.../REQ-28-D01_amazon_keyword_yoy_dashboard.html
"""
import os, json

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = "REQ-28_amazon-keyword-yoy-dashboard"
TEMPLATE = os.path.normpath(os.path.join(
    HERE, "..", "..", "evidence", "source_documents", TASK,
    "2026-08-14_source_amazon-keyword-yoy-dashboard-spec.html"))
PAYLOAD = os.path.join(HERE, "akyp_payload.json")
OUT_DIR = os.path.normpath(os.path.join(
    HERE, "..", "..", "evidence", "final_outputs", TASK))
OUT = os.path.join(OUT_DIR, "REQ-28-D01_amazon_keyword_yoy_dashboard.html")

# ---- override layer appended AFTER the spec script: embed data, lock UI ----
OVERRIDE_JS = r"""
<script>
/* ===== AKYP delivery layer — embeds the live snapshot and swaps the spec's live
   Amazon API for the embedded data. No business logic is changed. ===== */
(function(){
  var P = window.AKYP_EMBEDDED;
  if(!P){ return; }

  // Lock the reference clock to the snapshot so MTD windows match the fetched data.
  CONFIG.REFERENCE_DATE = P.referenceDate;

  // Serve embedded keyword data for the selected marketplace instead of fetching Amazon.
  API.getKeywordPerformance = function(period){
    var mkt = $("selMkt").value;
    var m = P.markets[mkt];
    if(!m){ return Promise.resolve({ syncedAt:P.generatedAt, account:P.account,
      marketplace:mkt, currency:"", current:{start:period.curStart,end:period.curEnd,daily:[]},
      previous:{start:period.prevStart,end:period.prevEnd,daily:[]}, keywords:[] }); }
    return Promise.resolve({
      syncedAt: P.generatedAt, account: P.account, marketplace: mkt, currency: m.currency,
      current: m.current, previous: m.previous, keywords: m.keywords
    });
  };

  function lockUI(){
    // Account: LEDSone only.
    var acc = $("selAccount");
    acc.innerHTML = '<option value="LEDSone">amazon Ledsone</option>';
    acc.value = "LEDSone"; acc.disabled = true;
    // Data source: embedded snapshot only.
    var src = $("selSource");
    if(src){ src.innerHTML = '<option value="api">Embedded snapshot</option>'; src.disabled = true; }
    // Period is fixed to the fetched snapshot window — lock it so labels stay truthful.
    var per = $("selPeriod");
    per.value = "mtd"; per.disabled = true;
    var cw = $("customWrap"); if(cw){ cw.classList.remove("show"); }
    // This is a static snapshot: hide live-sync / demo / CSV / auto-sync controls.
    ["btnSync","demoWrap","autoSyncWrap"].forEach(function(id){
      var el = $(id); if(el){ el.style.display = "none"; }
    });
    var db = $("demoBar"); if(db){ db.classList.remove("show"); }
    var cb = document.querySelector(".csvbar"); if(cb){ cb.classList.remove("show"); }
    // Header chips reflect the snapshot.
    $("hdAccount").textContent = P.account;
    $("hdSync").textContent = P.generatedAt;
  }

  document.addEventListener("DOMContentLoaded", function(){
    lockUI();
    // init() already registered first and painted the empty state; now load the snapshot.
    sync();
  });
})();
</script>
"""

BANNER_HTML = (
    '<div class="demobar show" style="background:#eef4fb;border-color:#d3e1f0;color:#2c4a6b">'
    '<div class="inner"><span>📊</span><span><b>Static snapshot</b> — live figures from the '
    'Amazon PPC keyword warehouse (amazon_campaigns.keyword_performance_data, 7-day '
    'attribution), generated {gen}. Current period = {cs} → {ce} vs the same window one '
    'year earlier. The current window under-reports vs the settled prior year because '
    "Amazon's 7-day attribution has not matured on the last ~7 days.</span></div></div>"
)


def main():
    with open(TEMPLATE, "r", encoding="utf-8") as f:
        html = f.read()
    with open(PAYLOAD, "r", encoding="utf-8") as f:
        payload = json.load(f)

    # 1) embed the payload just before the spec's main script
    marker = '<script>\n"use strict";'
    assert marker in html, "spec main-script marker not found"
    embed = ('<script>window.AKYP_EMBEDDED = '
             + json.dumps(payload, separators=(",", ":")) + ';</script>\n')
    html = html.replace(marker, embed + marker, 1)

    # 2) append the delivery/override layer before </body>
    html = html.replace("</body>", OVERRIDE_JS + "\n</body>", 1)

    # 3) swap the amber DEMO banner for a truthful snapshot banner
    import re
    banner = BANNER_HTML.format(gen=payload["generatedAt"],
                                cs=payload["curStart"], ce=payload["curEnd"])
    html = re.sub(r'<div class="demobar" id="demoBar">.*?</div>\s*</div>',
                  banner, html, count=1, flags=re.S)

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    kw = sum(len(m["keywords"]) for m in payload["markets"].values())
    print(f"OK  wrote {OUT}\n    markets={len(payload['markets'])} keyword_rows={kw} "
          f"snapshot={payload['curStart']}..{payload['curEnd']}")


if __name__ == "__main__":
    main()
