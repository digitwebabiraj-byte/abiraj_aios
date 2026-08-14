#!/usr/bin/env python3
"""
Merged dashboard builder — LEDSone PPC (Meshika)
Combines two already-delivered PPC dashboards for Meshika into ONE self-contained HTML with a
top-level task switch, so she has a single page instead of two. Independent-tab model: each task
keeps its OWN design, data and logic, isolated in its own iframe (srcdoc) — nothing is recomputed
and there are no CSS/JS collisions.

  Tab 1 — Amazon Keyword YoY   (akyp / PRJ-2026-024 / REQ-28-D01)
  Tab 2 — eBay PPC Pause       (eppa / PRJ-2026-013, ph_task id 878, assigned_user=meshika)

The shell is a single slim top bar (brand + segmented tab switcher with per-channel accent), so it
does not stack a second header on top of each dashboard's own header. Each iframe shows a loading
placeholder until it renders.

Sources (read-only, unchanged):
  - AKYP: the canonical REQ-28-D01 deliverable in its project folder.
  - EPPA: sources/eppa_ph878_meshika.html — snapshot pulled read-only from tech_team_outputs.ph_task
          id 878 (refresh by re-pulling that row when EPPA re-publishes).
Output:
  - merged_ledsone_ppc_meshika_dashboard.html  (self-contained; publish as one ph_task row)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
AKYP = os.path.normpath(os.path.join(
    HERE, "..", "..", "projects", "PRJ-2026-024_amazon-keyword-yoy-dashboard",
    "evidence", "final_outputs", "REQ-28_amazon-keyword-yoy-dashboard",
    "REQ-28-D01_amazon_keyword_yoy_dashboard.html"))
# EPPA source = its LIVE rendered deliverable (auto-refreshed by EPPA's weekly run); fall back to
# the one-time ph_task snapshot if the project deliverable isn't present.
EPPA_LIVE = os.path.normpath(os.path.join(
    HERE, "..", "..", "projects", "PRJ-2026-013_ebay-ppc-product-pause-automation",
    "evidence", "final_outputs", "REQ-15_ebay-ppc-product-pause-automation",
    "REQ-15-D01_eppa_dashboard.html"))
EPPA_SNAPSHOT = os.path.join(HERE, "sources", "eppa_ph878_meshika.html")
EPPA = EPPA_LIVE if os.path.exists(EPPA_LIVE) else EPPA_SNAPSHOT
OUT = os.path.join(HERE, "merged_ledsone_ppc_meshika_dashboard.html")

# Plain, self-explanatory names for the end user (Meshika).
PAGE_TITLE = "Meshika — Amazon Keyword YoY + eBay PPC Pause"
BRAND_MAIN = "Meshika"
BRAND_SUB = "Amazon Keyword YoY + eBay PPC Pause · combined in one page"
SWITCH_HINT = "Switch report:"

TABS = [
    {"id": "akyp", "label": "Amazon Ads — Keyword Year-on-Year",
     "sub": "amazon Ledsone · UK/US/CA/DE/FR/IT", "accent": "#e8912d", "src": AKYP},
    {"id": "eppa", "label": "eBay Ads — Pause Report",
     "sub": "LEDSone · eBay UK", "accent": "#3d7fca", "src": EPPA},
]


def esc_srcdoc(html):
    # attribute-safe escaping for the iframe srcdoc attribute
    return html.replace("&", "&amp;").replace('"', "&quot;")


def main():
    radios, labels, frames, per_tab_css = [], [], [], []
    for i, t in enumerate(TABS):
        with open(t["src"], "r", encoding="utf-8") as f:
            doc = f.read()
        checked = " checked" if i == 0 else ""
        radios.append(f'<input type="radio" name="mtab" id="mtab-{t["id"]}" class="mtabr"{checked}>')
        labels.append(
            f'<label class="mtab" for="mtab-{t["id"]}" data-accent="{t["accent"]}" tabindex="0">'
            f'<span class="mt-dot" style="background:{t["accent"]}"></span>'
            f'<span class="mt-txt"><span class="mt-l">{t["label"]}</span>'
            f'<span class="mt-s">{t["sub"]}</span></span></label>')
        frames.append(
            f'<div class="fr mf-{t["id"]}">'
            f'<div class="ph"><span class="spin"></span>Loading {t["label"]}…</div>'
            f'<iframe title="{t["label"]}" onload="this.parentNode.classList.add(&quot;ok&quot;)" '
            f'srcdoc="{esc_srcdoc(doc)}"></iframe></div>')
        # per-tab: active pill (.on, toggled by JS below) is FILLED with its channel accent
        # (Amazon amber / eBay blue) so the current report is obvious and colour-coded.
        per_tab_css.append(
            f'label[for="mtab-{t["id"]}"].on'
            f'{{background:{t["accent"]};border-color:{t["accent"]};color:#fff;'
            f'box-shadow:0 4px 12px {t["accent"]}55}}'
            f'\nlabel[for="mtab-{t["id"]}"].on .mt-s{{color:rgba(255,255,255,.92)}}'
            f'\nlabel[for="mtab-{t["id"]}"].on .mt-dot{{background:#fff}}')
    per_tab_css = "\n".join(per_tab_css)

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{PAGE_TITLE}</title>
<style>
  :root{{--navy:#0e2340;--navy2:#16324f;--ink:#1b2733;--muted:#5c6b7a;--bg:#f6f8fb;
        --sans:-apple-system,BlinkMacSystemFont,"Segoe UI","Inter",Roboto,Helvetica,Arial,sans-serif;}}
  *{{box-sizing:border-box}} html,body{{margin:0;padding:0;height:100%;overflow:hidden}}
  body{{font-family:var(--sans);color:var(--ink);background:var(--bg);display:flex;flex-direction:column;height:100vh;overflow:hidden}}
  .mtabr{{position:absolute;opacity:0;pointer-events:none;width:0;height:0}}

  /* light chrome bar so the switcher stands apart from each dashboard's own navy header;
     brand (left) + big colour-coded pill tabs (right) */
  .bar{{flex:0 0 auto;display:flex;align-items:center;justify-content:space-between;gap:16px;
       background:#ffffff;padding:0 16px;height:58px;border-bottom:1px solid #d7e0ea;
       box-shadow:0 3px 12px rgba(16,32,58,.10);position:relative;z-index:3}}
  .brand{{display:flex;align-items:center;gap:10px;color:var(--navy);font-size:14px;font-weight:800;white-space:nowrap}}
  .brand .logo{{width:26px;height:26px;border-radius:7px;background:var(--navy);color:#fff;
       display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:800}}
  .brand .mut{{color:#66788c;font-weight:600;font-size:10.5px;text-transform:uppercase;letter-spacing:.04em}}
  .switchhint{{color:#8493a5;font-size:10.5px;font-weight:800;text-transform:uppercase;letter-spacing:.06em;white-space:nowrap;align-self:center}}
  .seg{{display:flex;gap:9px;align-items:center}}
  .mtab{{display:flex;align-items:center;gap:10px;padding:8px 18px;border-radius:11px;cursor:pointer;
        background:#eef2f6;color:#465468;border:1px solid #dce4ed;user-select:none;
        transition:background .12s,color .12s,box-shadow .12s;outline:none;min-width:206px}}
  .mtab:hover{{background:#e4ebf3;border-color:#c8d4e0}}
  .mtab:focus-visible{{box-shadow:0 0 0 3px #bcd3ef}}
  .mt-dot{{width:9px;height:9px;border-radius:50%;flex:0 0 auto}}
  .mt-txt{{display:flex;flex-direction:column;line-height:1.18}}
  .mt-l{{font-size:13px;font-weight:800;letter-spacing:-.01em}}
  .mt-s{{font-size:9.5px;color:#7b8b9d;letter-spacing:.01em}}
  {per_tab_css}

  .mframes{{flex:1 1 auto;position:relative;min-height:0;background:var(--bg)}}
  .fr{{display:none;position:absolute;inset:0}}
  .fr iframe{{width:100%;height:100%;border:0;background:#fff;position:relative;z-index:1}}
  .ph{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:10px;
      color:var(--muted);font-size:13px;font-weight:600;background:var(--bg);z-index:2}}
  .fr.ok .ph{{display:none}}
  .spin{{width:16px;height:16px;border:2px solid #cdd8e6;border-top-color:var(--navy);border-radius:50%;animation:sp .7s linear infinite}}
  @keyframes sp{{to{{transform:rotate(360deg)}}}}

  @media(max-width:640px){{
    .bar{{height:auto;flex-direction:column;align-items:stretch;gap:8px;padding:9px 12px}}
    .seg{{height:auto}} .mtab{{flex:1;justify-content:center;padding:8px 10px}} .mt-s,.switchhint{{display:none}}
  }}
</style></head>
<body>
  {"".join(radios)}
  <div class="bar">
    <div class="brand"><span class="logo">M</span>{BRAND_MAIN} <span class="mut">{BRAND_SUB}</span></div>
    <div class="seg"><span class="switchhint">{SWITCH_HINT}</span>{"".join(labels)}</div>
  </div>
  <div class="mframes">{"".join(frames)}</div>
  <script>
  (function(){{
    var radios = [].slice.call(document.querySelectorAll('.mtabr'));
    function sync(){{
      radios.forEach(function(r){{
        var id  = r.id.replace('mtab-','');
        var lab = document.querySelector('label[for="'+r.id+'"]');
        var fr  = document.querySelector('.mf-'+id);
        if(lab){{
          var ac = lab.getAttribute('data-accent');
          var sub = lab.querySelector('.mt-s'), dot = lab.querySelector('.mt-dot');
          if(r.checked){{
            lab.style.background = ac; lab.style.borderColor = ac; lab.style.color = '#fff';
            lab.style.boxShadow = '0 4px 12px ' + ac + '55';
            if(sub) sub.style.color = 'rgba(255,255,255,.92)';
            if(dot) dot.style.background = '#fff';
          }} else {{
            lab.style.background = ''; lab.style.borderColor = ''; lab.style.color = '';
            lab.style.boxShadow = '';
            if(sub) sub.style.color = ''; if(dot) dot.style.background = ac;
          }}
        }}
        if(fr) fr.style.display = r.checked ? 'block' : 'none';
      }});
    }}
    radios.forEach(function(r){{ r.addEventListener('change', sync); }});
    sync();
  }})();
  </script>
</body></html>"""

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"OK  wrote {OUT}")
    print(f"    size={os.path.getsize(OUT):,} bytes  tabs={[t['label'] for t in TABS]}")


if __name__ == "__main__":
    main()
