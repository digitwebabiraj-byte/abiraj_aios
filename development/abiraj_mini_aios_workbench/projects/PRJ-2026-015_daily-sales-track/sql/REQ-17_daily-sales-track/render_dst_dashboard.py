# -*- coding: utf-8 -*-
"""
REQ-17-D01 — Daily Sales Track reviewer dashboard (HTML).

Reads the governed dataset `dst_d01_data.json` produced by build_dst_d01.py, so the dashboard and
the workbook are two renderings of ONE dataset and cannot drift. (REQ-16 shipped a defect where the
two were built from separate fetches; this is the fix.)

Every row is PRE-RENDERED as static HTML — the ph_task viewer runs no JavaScript, so anything drawn
by JS shows blank there. JS here is progressive enhancement only (filter, sort, export, fullscreen);
the full table is readable with scripting completely disabled.

Read-only. Writes one .html.
"""

import io
import json
import os
from datetime import date

TREND_UP, TREND_DOWN, TREND_FLAT = "up", "down", "flat"

# ---------------------------------------------------------------------------
# Palettes. Structure and markup are identical across themes — only colour
# variables change, so the verification harness stays valid for all of them.
# ---------------------------------------------------------------------------
THEMES = {
    # Light, airy, editorial. White masthead, ink text, soft slate table chrome.
    "porcelain": {
        # contrast-tuned: every text colour below clears WCAG AA (4.5:1) on its own background
        "bg": "#f4f6fb", "panel": "#ffffff", "line": "#dfe3ec", "line2": "#c3c9d8",
        "ink": "#0f1526", "ink2": "#414a60", "ink3": "#5c6478",
        "head_bg": "linear-gradient(180deg,#ffffff 0%,#f5f7fc 100%)",
        "head_glow": "radial-gradient(620px 180px at 92% -60%,rgba(79,70,229,.12),transparent 70%)",
        "head_ink": "#0f1526", "head_sub": "#414a60", "head_accent": "#4338ca",
        "tag_bg": "#eceffa", "tag_line": "#d5dbec", "tag_ink": "#333c52",
        "thead_bg": "#e7ebf6", "thead_ink": "#25304a", "thead_hover": "#dbe1f1",
        "grp_bg": "#d9e0f2", "grp_ink": "#2f2a8f",
        "foot_bg": "#141a2e", "foot_ink": "#ffffff",
        "primary": "#4338ca", "primary2": "#6d28d9",
        "hero": "linear-gradient(135deg,#4338ca,#6d28d9)", "hero_ink": "#e7e3fd",
        "bar": "linear-gradient(90deg,#4338ca,#9333ea)", "grp_divider": "#9aa3bd",
        "pos": "#06724c", "pos_bg": "#d3f5e5", "neg": "#be1240", "neg_bg": "#ffdfe7",
        "flat": "#8a5106", "flat_bg": "#fceccb",
    },
    # Fresh commerce green. Deep emerald masthead, warm-neutral page.
    "emerald": {
        "bg": "#f2f7f4", "panel": "#ffffff", "line": "#dfe9e3", "line2": "#c6d5cd",
        "ink": "#0d2620", "ink2": "#4a6158", "ink3": "#8ea69b",
        "head_bg": "linear-gradient(115deg,#052e23 0%,#0b5c43 52%,#0f766e 100%)",
        "head_glow": "radial-gradient(640px 190px at 90% -55%,rgba(52,211,153,.4),transparent 70%)",
        "head_ink": "#ffffff", "head_sub": "#a7f3d0", "head_accent": "#6ee7b7",
        "tag_bg": "rgba(255,255,255,.11)", "tag_line": "rgba(255,255,255,.22)", "tag_ink": "#d1fae5",
        "thead_bg": "#0d3b31", "thead_ink": "#a7f3d0", "thead_hover": "#14513f",
        "grp_bg": "#062a21", "grp_ink": "#6ee7b7",
        "foot_bg": "#0d3b31", "foot_ink": "#ffffff",
        "primary": "#0f766e", "primary2": "#059669",
        "hero": "linear-gradient(135deg,#0f766e,#059669)", "hero_ink": "#ccfbf1",
        "bar": "linear-gradient(90deg,#0f766e,#34d399)", "grp_divider": "#7ea79a",
        "pos": "#047857", "pos_bg": "#d1fae5", "neg": "#d92650", "neg_bg": "#ffe4ea",
        "flat": "#a16207", "flat_bg": "#fef3c7",
    },
    # Warm graphite with coral. Distinctive without being loud.
    "sunset": {
        "bg": "#f8f5f2", "panel": "#ffffff", "line": "#ece5df", "line2": "#dbd0c7",
        "ink": "#241c18", "ink2": "#6b5b52", "ink3": "#a89a90",
        "head_bg": "linear-gradient(115deg,#2b1d1a 0%,#7c2d3a 55%,#b4453a 100%)",
        "head_glow": "radial-gradient(640px 190px at 90% -55%,rgba(251,146,60,.45),transparent 70%)",
        "head_ink": "#ffffff", "head_sub": "#fed7c3", "head_accent": "#fdba74",
        "tag_bg": "rgba(255,255,255,.11)", "tag_line": "rgba(255,255,255,.22)", "tag_ink": "#ffe4d6",
        "thead_bg": "#3b2723", "thead_ink": "#f5d7c6", "thead_hover": "#4d332d",
        "grp_bg": "#2b1d1a", "grp_ink": "#fdba74",
        "foot_bg": "#3b2723", "foot_ink": "#ffffff",
        "primary": "#c2410c", "primary2": "#e11d48",
        "hero": "linear-gradient(135deg,#c2410c,#e11d48)", "hero_ink": "#ffe4d6",
        "bar": "linear-gradient(90deg,#c2410c,#fb923c)", "grp_divider": "#c0a99c",
        "pos": "#0f7a52", "pos_bg": "#d5f5e6", "neg": "#c0304c", "neg_bg": "#ffe1e6",
        "flat": "#9a5b06", "flat_bg": "#fdeecd",
    },
}
DEFAULT_THEME = "porcelain"


def _trend(cur, prev, band):
    if prev == 0 and cur == 0:
        return None
    if prev == 0:
        return TREND_UP
    g = (cur - prev) / prev
    return TREND_UP if g > band else (TREND_DOWN if g < -band else TREND_FLAT)


def _pill(t):
    if t is None:
        return '<span class="pill pill-none">—</span>'
    label = {TREND_UP: "Up", TREND_DOWN: "Down", TREND_FLAT: "Stable"}[t]
    arrow = {TREND_UP: "▲", TREND_DOWN: "▼", TREND_FLAT: "▬"}[t]
    return '<span class="pill pill-{0}"><i>{1}</i>{2}</span>'.format(t, arrow, label)


def _money(v):
    return "£{0:,.2f}".format(v) if v is not None else '<span class="na">—</span>'


def _pct(cur, prev):
    if prev == 0:
        return '<span class="na">—</span>'
    g = (cur - prev) / prev
    cls = "pos" if g > 0 else ("neg" if g < 0 else "zero")
    sign = "+" if g > 0 else ""
    return '<span class="delta {0}">{1}{2:.1f}%</span>'.format(cls, sign, g * 100)


def _num(v):
    return "{0:,}".format(int(v))


def render(data, out_path, theme=DEFAULT_THEME):
    pal = THEMES[theme]
    band = data["trend_band"]
    a = data["anchor"]
    d_today = date.fromisoformat(a["today"])
    d_yest = date.fromisoformat(a["yesterday"])
    d_ly = date.fromisoformat(a["same_day_last_year"])
    generated = date.fromisoformat(data["generated"])

    rows, tot = [], {"s1": 0.0, "s2": 0.0, "sly": 0.0, "o1": 0, "o2": 0, "oly": 0,
                     "u": 0, "act": 0, "ah": 0, "ph": 0, "ahs": 0.0, "phs": 0.0}

    for acc in data["rows"]:
        s1, s2, sly = acc["s_r1"], acc["s_r2"], acc["s_ly"]
        o1, o2, oly = acc["o_r1"], acc["o_r2"], acc["o_ly"]
        ph1, ah1 = acc["ph_r1"], acc["ah_r1"]
        ph2, ah2 = acc["ph_r2"], acc["ah_r2"]
        active, ph_l, ah_l = acc["active"], acc["ph_l"], acc["ah_l"]
        u = acc["units_r1"]

        for k, v in (("s1", s1), ("s2", s2), ("sly", sly), ("o1", o1), ("o2", o2),
                     ("oly", oly), ("u", u), ("act", active), ("ah", ah_l),
                     ("ph", ph_l), ("ahs", ah1), ("phs", ph1)):
            tot[k] += v

        t_acc = _trend(s1, s2, band)
        t_ah = _trend(ah1, ah2, band)
        t_ph = _trend(ph1, ph2, band)
        aov = (s1 / o1) if o1 else None
        share = (ph_l / active * 100.0) if active else 0.0
        holder = acc["holder"]
        h_cls = "muted" if "not assigned" in holder else ""

        rows.append("""
      <tr data-account="{disp}" data-trend="{tkey}" data-search="{search}" data-trading="{trading}">
        <th scope="row" class="acct t-{tkey}"><span class="dot"></span>{disp}</th>
        <td class="mkt">{site}</td>
        <td class="num strong gs">{s1}</td>
        <td class="num dim">{s2}</td>
        <td class="num">{diff}</td>
        <td class="num">{grow}</td>
        <td class="num dim">{sly}</td>
        <td class="num strong gs">{o1}</td>
        <td class="num dim">{o2}</td>
        <td class="num">{ogrow}</td>
        <td class="num dim">{oly}</td>
        <td class="num gs">{u}</td>
        <td class="num">{aov}</td>
        <td class="num gs">{act}</td>
        <td class="split">
          <div class="bar" title="PH {ph} of {act} ({share:.0f}%)">
            <span style="width:{share:.1f}%"></span>
          </div>
          <em>{ph} PH / {ah} AH</em>
        </td>
        <td class="num gs">{ahs}</td>
        <td>{tah}</td>
        <td class="num gs">{phs}</td>
        <td>{tph}</td>
        <td class="gs">{tacc}</td>
        <td class="holder {hcls}">{holder}</td>
      </tr>""".format(
            disp=acc["display"], site=acc["site"], tkey=(t_acc or "none"),
            trading=("1" if o1 > 0 else "0"),
            search=(acc["display"] + " " + acc["site"] + " " + holder).lower(),
            s1=_money(s1), s2=_money(s2),
            diff='<span class="delta {0}">{1}£{2:,.2f}</span>'.format(
                "pos" if s1 - s2 > 0 else ("neg" if s1 - s2 < 0 else "zero"),
                "+" if s1 - s2 > 0 else ("−" if s1 - s2 < 0 else ""), abs(s1 - s2)),
            grow=_pct(s1, s2), sly=_money(sly),
            o1=_num(o1), o2=_num(o2), ogrow=_pct(o1, o2), oly=_num(oly), u=_num(u),
            aov=(_money(aov) if aov is not None else '<span class="na">—</span>'),
            act=_num(active), ph=_num(ph_l), ah=_num(ah_l), share=share,
            ahs=_money(ah1), phs=_money(ph1),
            tah=_pill(t_ah), tph=_pill(t_ph), tacc=_pill(t_acc),
            holder=holder, hcls=h_cls))

    ov_g = (tot["s1"] - tot["s2"]) / tot["s2"] if tot["s2"] else 0
    og_g = (tot["o1"] - tot["o2"]) / tot["o2"] if tot["o2"] else 0
    aov_all = tot["s1"] / tot["o1"] if tot["o1"] else 0
    ph_share = tot["ph"] / tot["act"] * 100 if tot["act"] else 0

    def card(label, value, sub="", tone="", big=False, sort=None, filt=None, hint=""):
        act = ""
        if sort is not None:
            act = ' data-sort="{0}" tabindex="0" role="button"'.format(sort)
        elif filt:
            act = ' data-filter="{0}" tabindex="0" role="button"'.format(filt)
        return """
        <article class="kpi {tone}{big}{clk}"{act} title="{hint}">
          <p class="k-label">{label}</p>
          <p class="k-value">{value}</p>
          <p class="k-sub">{sub}</p>
        </article>""".format(label=label, value=value, sub=sub, tone=tone,
                             big=" kpi-hero" if big else "",
                             clk=" clickable" if act else "", act=act, hint=hint)

    def dchip(v):
        cls = "pos" if v > 0 else ("neg" if v < 0 else "zero")
        return '<span class="chip {0}">{1}{2:.2f}%</span>'.format(cls, "+" if v > 0 else "", v * 100)

    n_trading = sum(1 for x in data["rows"] if x["o_r1"] > 0)
    kpis = "".join([
        card("Total Sales Today", "£{0:,.2f}".format(tot["s1"]),
             "{0} vs £{1:,.2f} yesterday".format(dchip(ov_g), tot["s2"]), "tone-primary", True,
             sort=2, hint="Click to rank rows by today's sales"),
        card("Total Orders", _num(tot["o1"]),
             "{0} vs {1} yesterday".format(dchip(og_g), _num(tot["o2"])), "tone-blue",
             sort=7, hint="Click to rank rows by today's orders"),
        card("Units Sold", _num(tot["u"]), "across {0} orders".format(_num(tot["o1"])), "tone-violet",
             sort=11, hint="Click to rank rows by units sold"),
        card("Average Order Value", "£{0:,.2f}".format(aov_all), "portfolio-wide", "tone-amber",
             sort=12, hint="Click to rank rows by average order value"),
        card("Same Day Last Year", "£{0:,.2f}".format(tot["sly"]),
             "{0} · {1} orders".format(d_ly.strftime("%d %b %Y"), _num(tot["oly"])), "tone-slate",
             sort=6, hint="Click to rank rows by last-year sales"),
        card("Active Listings", _num(tot["act"]),
             "{0} PH ({1:.0f}%) · {2} AH".format(_num(tot["ph"]), ph_share, _num(tot["ah"])), "tone-teal",
             sort=13, hint="Click to rank rows by live listing count"),
        card("Rows Trading", "{0} / {1}".format(n_trading, len(data["rows"])),
             "had at least one order", "tone-green",
             filt="trading", hint="Click to show only accounts that traded"),
    ])

    tvars = dict(("t_" + k, v) for k, v in pal.items())
    html = TEMPLATE.format(
        today=d_today.strftime("%A, %d %B %Y"),
        today_iso=d_today.isoformat(),
        yest=d_yest.strftime("%d %b"),
        ly=d_ly.strftime("%d %b %Y"),
        generated=generated.strftime("%d %b %Y"),
        band=int(band * 100),
        kpis=kpis,
        rows="".join(rows),
        n=len(data["rows"]),
        f_s1="£{0:,.2f}".format(tot["s1"]), f_s2="£{0:,.2f}".format(tot["s2"]),
        f_o1=_num(tot["o1"]), f_o2=_num(tot["o2"]), f_u=_num(tot["u"]),
        f_sly="£{0:,.2f}".format(tot["sly"]), f_oly=_num(tot["oly"]),
        f_aov="£{0:,.2f}".format(aov_all), f_act=_num(tot["act"]),
        f_ah=_num(tot["ah"]), f_ph=_num(tot["ph"]),
        f_ahs="£{0:,.2f}".format(tot["ahs"]), f_phs="£{0:,.2f}".format(tot["phs"]),
        **tvars
    )
    with io.open(out_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return out_path


TEMPLATE = u"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Daily Sales Track — {today_iso}</title>
<style>
  *,*::before,*::after{{box-sizing:border-box}}
  :root{{
    --bg:{t_bg}; --panel:{t_panel}; --ink:{t_ink}; --ink2:{t_ink2}; --ink3:{t_ink3};
    --line:{t_line}; --line2:{t_line2};
    --primary:{t_primary}; --primary2:{t_primary2};
    --pos:{t_pos}; --pos-bg:{t_pos_bg}; --neg:{t_neg}; --neg-bg:{t_neg_bg};
    --flat:{t_flat}; --flat-bg:{t_flat_bg};
    --head-bg:{t_head_bg}; --head-glow:{t_head_glow};
    --head-ink:{t_head_ink}; --head-sub:{t_head_sub}; --head-accent:{t_head_accent};
    --tag-bg:{t_tag_bg}; --tag-line:{t_tag_line}; --tag-ink:{t_tag_ink};
    --thead-bg:{t_thead_bg}; --thead-ink:{t_thead_ink}; --thead-hover:{t_thead_hover};
    --grp-bg:{t_grp_bg}; --grp-ink:{t_grp_ink};
    --foot-bg:{t_foot_bg}; --foot-ink:{t_foot_ink};
    --hero:{t_hero}; --hero-ink:{t_hero_ink}; --bar:{t_bar};
    --grp-divider:{t_grp_divider};
    --radius:14px; --shadow:0 1px 2px rgba(20,26,46,.05),0 10px 26px -14px rgba(20,26,46,.22);
  }}
  html,body{{height:100%}}
  body{{
    margin:0; background:var(--bg); color:var(--ink);
    font:15px/1.5 ui-sans-serif,-apple-system,"Segoe UI",Roboto,Inter,Helvetica,Arial,sans-serif;
    font-variant-numeric:tabular-nums; display:flex; flex-direction:column;
    -webkit-font-smoothing:antialiased;
  }}
  .num,.k-value{{font-variant-numeric:tabular-nums lining-nums}}

  /* ---------- masthead ---------- */
  header.top{{
    background:var(--head-bg); color:var(--head-ink); padding:9px 20px 10px;
    position:relative; overflow:hidden; flex:none; border-bottom:1px solid var(--line);
  }}
  header.top::after{{
    content:""; position:absolute; inset:0; background:var(--head-glow); pointer-events:none;
  }}
  .top-row{{display:flex;align-items:flex-end;gap:20px;flex-wrap:wrap;position:relative;z-index:1}}
  h1{{margin:0;font-size:20px;letter-spacing:-.5px;font-weight:750}}
  h1 span{{color:var(--head-accent)}}
  .sub{{margin:3px 0 0;color:var(--head-sub);font-size:13.5px}}
  .sub b{{color:var(--head-ink);font-weight:700}}
  .top-meta{{margin-left:auto;display:flex;gap:7px;flex-wrap:wrap}}
  .tag{{
    background:var(--tag-bg); border:1px solid var(--tag-line); color:var(--tag-ink);
    padding:6px 12px; border-radius:8px; font-size:13px; white-space:nowrap; font-weight:600;
  }}
  .tag b{{color:var(--head-ink);font-weight:750}}

  /* ---------- KPI strip ---------- */
  .kpis{{
    display:grid; grid-template-columns:repeat(auto-fit,minmax(168px,1fr));
    gap:9px; padding:8px 20px 3px; flex:none;
  }}
  .kpi{{
    --tone:var(--primary);
    background:var(--panel); border-radius:var(--radius); padding:7px 12px 7px;
    box-shadow:var(--shadow); border:1px solid var(--line); position:relative;
    overflow:hidden; transition:transform .16s ease, box-shadow .16s ease;
  }}
  .kpi.clickable{{cursor:pointer;user-select:none}}
  .kpi.clickable:hover{{transform:translateY(-2px);box-shadow:0 2px 4px rgba(20,26,46,.06),0 16px 32px -16px rgba(20,26,46,.34)}}
  .kpi.clickable:focus-visible{{outline:3px solid var(--primary);outline-offset:2px}}
  .kpi.clickable::before{{
    content:"↕ click to rank"; position:absolute; right:11px; bottom:9px;
    font-size:11px; font-weight:700; color:var(--ink3); opacity:0; transition:opacity .15s;
  }}
  .kpi[data-filter]::before{{content:"⦿ click to filter"}}
  .kpi.clickable:hover::before{{opacity:1}}
  .kpi-hero.clickable::before{{color:var(--hero-ink)}}
  .kpi.active{{border-color:var(--primary);box-shadow:0 0 0 2px var(--primary) inset}}
  .kpi.active::before{{opacity:1;color:var(--primary)}}
  .kpi-hero.active{{box-shadow:0 0 0 3px rgba(255,255,255,.7) inset}}
  /* soft tint wash instead of a hard left bar */
  .kpi::after{{
    content:""; position:absolute; right:-28px; top:-34px; width:86px; height:86px;
    border-radius:50%; background:var(--tone); opacity:.09; pointer-events:none;
  }}
  .k-label{{
    margin:0; font-size:11px; letter-spacing:.02em;
    color:var(--ink2); font-weight:700; display:flex; align-items:center; gap:7px;
  }}
  .k-label::before{{
    content:""; width:7px; height:7px; border-radius:2px; background:var(--tone); flex:none;
  }}
  .k-value{{margin:2px 0 1px;font-size:21px;font-weight:750;letter-spacing:-.7px;line-height:1.05}}
  .k-sub{{margin:0;font-size:11.5px;color:var(--ink2)}}
  .kpi-hero{{background:var(--hero);border-color:transparent;color:#fff}}
  .kpi-hero .k-label{{color:var(--hero-ink)}}
  .kpi-hero .k-label::before{{background:rgba(255,255,255,.85)}}
  .kpi-hero .k-sub{{color:var(--hero-ink)}}
  .kpi-hero::after{{background:#fff;opacity:.14}}
  .tone-blue{{--tone:#2563eb}}  .tone-violet{{--tone:#9333ea}}
  .tone-amber{{--tone:#d97706}} .tone-slate{{--tone:var(--ink2)}}
  .tone-teal{{--tone:#0d9488}}  .tone-green{{--tone:#16a34a}}
  .chip{{padding:1px 7px;border-radius:6px;font-weight:700;font-size:11px}}
  .chip.pos{{background:var(--pos-bg);color:var(--pos)}}
  .chip.neg{{background:var(--neg-bg);color:var(--neg)}}
  .chip.zero{{background:var(--line);color:var(--ink2)}}
  .kpi-hero .chip.pos,.kpi-hero .chip.neg{{background:rgba(255,255,255,.24);color:#fff}}

  /* ---------- toolbar ---------- */
  .toolbar{{
    display:flex;gap:7px;align-items:center;flex-wrap:wrap;padding:6px 20px 7px;flex:none;
  }}
  .search{{
    flex:1 1 210px;max-width:300px;padding:6px 12px;border:1.5px solid var(--line2);
    border-radius:9px;background:#fff;font-size:14.5px;color:var(--ink);
  }}
  .search::placeholder{{color:var(--ink3)}}
  .search:focus{{outline:2px solid var(--primary);outline-offset:-1px;border-color:transparent}}
  .btn{{
    padding:6px 12px;border:1.5px solid var(--line2);background:#fff;border-radius:8px;
    font-size:13.5px;font-weight:700;color:var(--ink2);cursor:pointer;
  }}
  .btn:hover{{border-color:var(--primary);color:var(--primary)}}
  .btn.on{{background:var(--primary);border-color:var(--primary);color:#fff}}
  .btn-primary{{background:var(--ink);border-color:var(--ink);color:#fff}}
  .btn-primary:hover{{background:var(--primary);border-color:var(--primary);color:#fff}}
  .seg{{display:flex;gap:6px;padding-left:6px;border-left:1.5px solid var(--line2)}}
  .count{{margin-left:auto;font-size:14px;color:var(--ink2)}}
  .count b{{color:var(--ink);font-weight:750}}

  /* ---------- table ---------- */
  .wrap{{
    flex:1 1 auto; min-height:0; margin:0 20px 8px; background:var(--panel);
    border:1px solid var(--line); border-radius:var(--radius); box-shadow:var(--shadow);
    overflow:auto;
  }}
  table{{border-collapse:separate;border-spacing:0;width:100%;font-size:14.5px}}
  thead th{{
    position:sticky; top:0; z-index:3; background:var(--thead-bg); color:var(--thead-ink);
    font-size:12.5px; font-weight:700; letter-spacing:0;
    padding:7px 5px; text-align:right; white-space:nowrap; cursor:pointer;
    border-bottom:2px solid var(--line2);
  }}
  thead th:first-child{{text-align:left;left:0;z-index:5}}
  thead th:hover{{background:var(--thead-hover)}}
  thead th.grp{{
    background:var(--grp-bg);color:var(--grp-ink);text-align:center;font-size:11.5px;
    cursor:default;letter-spacing:.06em;text-transform:uppercase;padding:4px 9px;
    font-weight:800;
  }}
  /* alternate group tint so neighbouring blocks never blur together */
  thead th.grp.alt{{background:color-mix(in srgb,var(--grp-bg) 55%,#fff)}}

  /* ---- group dividers: run the full height of the table ---- */
  thead th.gs, tbody td.gs, tfoot td.gs{{
    border-left:2px solid var(--grp-divider);
  }}
  thead th.grp.gs{{border-left:2px solid var(--grp-divider)}}
  tbody th{{
    position:sticky;left:0;z-index:2;background:#fff;text-align:left;font-weight:700;
    font-size:14.5px;padding:9px 9px;white-space:nowrap;border-right:2px solid var(--line);
  }}
  tbody td{{padding:9px 5px;text-align:right;white-space:nowrap;border-bottom:1px solid var(--line)}}
  tbody th{{border-bottom:1px solid var(--line)}}
  tbody tr:nth-child(even) th,tbody tr:nth-child(even) td{{background:var(--bg)}}
  tbody tr:hover th,tbody tr:hover td{{background:var(--pos-bg);background:color-mix(in srgb,var(--primary) 7%,#fff)}}
  tbody tr.hide{{display:none}}
  .acct .dot{{
    display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:9px;
    background:var(--ink3);vertical-align:middle;
  }}
  .t-up .dot{{background:var(--pos);box-shadow:0 0 0 3px var(--pos-bg)}}
  .t-down .dot{{background:var(--neg);box-shadow:0 0 0 3px var(--neg-bg)}}
  .t-flat .dot{{background:var(--flat);box-shadow:0 0 0 3px var(--flat-bg)}}
  .strong{{font-weight:750}}
  .dim{{color:var(--ink2)}}
  .na{{color:var(--ink3)}}
  .delta{{font-weight:700}}
  .delta.pos{{color:var(--pos)}} .delta.neg{{color:var(--neg)}} .delta.zero{{color:var(--ink2)}}
  .pill{{
    display:inline-flex;align-items:center;gap:5px;padding:4px 11px;border-radius:7px;
    font-size:13px;font-weight:700;
  }}
  .pill i{{font-style:normal;font-size:10px}}
  .pill-up{{background:var(--pos-bg);color:var(--pos)}}
  .pill-down{{background:var(--neg-bg);color:var(--neg)}}
  .pill-flat{{background:var(--flat-bg);color:var(--flat)}}
  .pill-none{{background:#f1f5f9;color:#cbd5e1}}
  td.split{{text-align:left;min-width:96px}}
  .bar{{height:6px;border-radius:99px;background:var(--line);overflow:hidden;margin-bottom:4px}}
  .bar span{{display:block;height:100%;background:var(--bar)}}
  td.split em{{font-style:normal;font-size:12.5px;color:var(--ink2);font-weight:600}}
  td.mkt{{text-align:left;font-weight:600;color:var(--ink2);font-size:13px;padding-right:4px}}
  td.holder{{text-align:left;font-size:13.5px;white-space:normal;min-width:84px;line-height:1.3}}
  td.holder.muted{{color:var(--ink3);font-style:italic}}
  tfoot th,tfoot td{{
    position:sticky;bottom:0;background:var(--foot-bg);color:var(--foot-ink);font-weight:700;
    padding:7px 5px;text-align:right;border-top:2px solid var(--primary);z-index:3;
  }}
  tfoot th{{text-align:left;left:0;z-index:4}}

  footer.notes{{padding:0 20px 7px;flex:none}}
  footer.notes summary{{
    cursor:pointer;font-size:13px;font-weight:700;color:var(--primary);
    padding:4px 0;list-style:none;display:flex;align-items:center;gap:7px;
  }}
  footer.notes summary::-webkit-details-marker{{display:none}}
  footer.notes summary::before{{content:"▸";font-size:12px;transition:transform .15s}}
  footer.notes details[open] summary::before{{transform:rotate(90deg)}}
  footer.notes p{{margin:0 0 7px;font-size:13.5px;line-height:1.55;color:var(--ink2);max-width:150ch}}
  footer.notes b{{color:var(--ink)}}
  footer.notes b{{color:var(--ink)}}
  .warn{{color:#b45309}}
  body.dense tbody td,body.dense tbody th{{padding:2px 5px;font-size:13.5px}}
  body.dense thead th{{padding:4px 5px}}
  body.dense thead th.grp{{padding:2px 9px}}
  body.dense tfoot th,body.dense tfoot td{{padding:4px 5px}}
  body.dense header.top .sub{{display:none}}
  body.dense .bar{{display:none}}
  body.dense footer.notes{{display:none}}
  body.dense .kpis{{display:none}}
  @media print{{.toolbar{{display:none}} .wrap{{overflow:visible;box-shadow:none}}}}
</style>
</head>
<body>

<header class="top">
  <div class="top-row">
    <div>
      <h1>Daily Sales Track <span>· eBay</span></h1>
      <p class="sub">Trading day <b>{today}</b> — compared with <b>{yest}</b> and the same date last year, <b>{ly}</b></p>
    </div>
    <div class="top-meta">
      <span class="tag">Generated <b>{generated}</b></span>
      <span class="tag">Accounts <b>{n}</b></span>
      <span class="tag">Orders <b>placed</b>, excl. cancelled</span>
      <span class="tag">Trend band <b>±{band}%</b></span>
    </div>
  </div>
</header>

<section class="kpis">{kpis}</section>

<div class="toolbar">
  <input id="q" class="search" type="search" placeholder="Search account or holder…" autocomplete="off">
  <div class="seg">
    <button class="btn on" data-f="all">All</button>
    <button class="btn" data-f="up">▲ Up</button>
    <button class="btn" data-f="down">▼ Down</button>
    <button class="btn" data-f="flat">▬ Stable</button>
  </div>
  <div class="seg">
    <button class="btn" id="dense">Maximise table</button>
    <button class="btn" id="full">Full screen</button>
    <button class="btn btn-primary" id="csv">Export CSV</button>
  </div>
  <p class="count"><b id="shown">{n}</b> of {n} rows</p>
</div>

<div class="wrap" id="wrap">
<table id="tbl">
  <thead>
    <tr>
      <th class="grp" style="text-align:left" colspan="2">Account</th>
      <th class="grp gs" colspan="5">Sales</th>
      <th class="grp gs alt" colspan="4">Orders</th>
      <th class="grp gs" colspan="2">Volume</th>
      <th class="grp gs alt" colspan="2">Listings</th>
      <th class="grp gs" colspan="2">Account Holder</th>
      <th class="grp gs alt" colspan="2">Portfolio Holder</th>
      <th class="grp gs" colspan="2">Overall</th>
    </tr>
    <tr>
      <th>Account</th><th>Market</th>
      <th class="gs">Today £</th><th>Yesterday £</th><th>Diff</th><th>Growth</th><th>Same day LY £</th>
      <th class="gs">Today</th><th>Yesterday</th><th>Growth</th><th>Same day LY</th>
      <th class="gs">Units</th><th>AOV £</th>
      <th class="gs">Active</th><th>PH / AH split</th>
      <th class="gs">AH sales £</th><th>AH trend</th>
      <th class="gs">PH sales £</th><th>PH trend</th>
      <th class="gs">Trend</th><th>AH holder</th>
    </tr>
  </thead>
  <tbody id="tb">{rows}
  </tbody>
  <tfoot>
    <tr>
      <th>All rows</th><td></td>
      <td class="gs">{f_s1}</td><td>{f_s2}</td><td>—</td><td>—</td><td>{f_sly}</td>
      <td class="gs">{f_o1}</td><td>{f_o2}</td><td>—</td><td>{f_oly}</td>
      <td class="gs">{f_u}</td><td>{f_aov}</td>
      <td class="gs">{f_act}</td><td style="text-align:left">{f_ph} PH / {f_ah} AH</td>
      <td class="gs">{f_ahs}</td><td>—</td><td class="gs">{f_phs}</td><td>—</td><td>—</td><td></td>
    </tr>
  </tfoot>
</table>
</div>

<footer class="notes">
<details>
  <summary>How to read this report — definitions and caveats</summary>
  <p><b>How to read this.</b> A report generated on one morning reports the <b>previous</b> day —
  today's trading is still in progress and cannot be counted. Sales are every order
  <b>placed</b> that day excluding cancellations, because orders only reach “Completed” about two
  days after purchase; counting completed-only would understate yesterday by roughly two thirds.
  <b>AH</b> (Account Holder) listings are those with no portfolio-holder assignment, so
  <b>AH + PH = Active</b> on every row.</p>
  <p class="warn"><b>&#9888; Active Listing is understated by roughly 5&ndash;6% &mdash; do not quote it against
  Seller Hub.</b> Measured 22 Jul for LEDSone UK: eBay shows <b>3,033</b> active on the UK site and
  <b>6,883</b> across all sites; this report shows <b>2,843</b> and <b>6,510</b>. The listings mirror
  flags a listing ended when its end date passes, but eBay auto-renews Good-&rsquo;Til-Cancelled
  listings and the flag is not cleared until a full re-sync. A defect in the listings sync, outside
  this report. <b>Sales, orders, units and AOV are unaffected</b> &mdash; they come from the orders
  table and reconcile exactly to Seller Hub (LEDSone UK / UK = &pound;837.93). AH and PH listing
  counts split the same understated total, so their proportions hold but their absolute counts
  inherit the shortfall.</p>
  <p class="warn"><b>Caveats.</b> AH and PH sales are line-level and do not sum exactly to
  Today's Sales — the difference is postage and discount (0.85% channel-wide on this run).
  Same-day-last-year uses the same calendar date, so the weekday differs. The ±{band}% trend band is
  provisional. The AH holder column is a <b>manual map</b> — no database records who owns an account,
  so it must be maintained by hand; seven accounts have no holder assigned.
  <b>Sunsone shows two holders because it is one eBay account</b> (<code>so_926407</code>) selling into
  both UK and Germany — there is no separate Sunsone DE account. LEDSone UK and LEDSone DE <i>are</i>
  two separate accounts, but LEDSone UK still sells into Germany itself, so its row mixes both.
  Figures do not tie to the monthly EBPD dashboard, which counts completed orders only.</p>
</details>
</footer>

<script>
(function(){{
  var rows=[].slice.call(document.querySelectorAll('#tb tr')),
      q=document.getElementById('q'), shown=document.getElementById('shown'),
      filt='all', tradingOnly=false;
  function apply(){{
    var s=q.value.trim().toLowerCase(), n=0;
    rows.forEach(function(r){{
      var okF = filt==='all' || r.dataset.trend===filt,
          okS = !s || r.dataset.search.indexOf(s)>-1,
          okT = !tradingOnly || r.dataset.trading==='1';
      r.classList.toggle('hide', !(okF&&okS&&okT));
      if(okF&&okS&&okT) n++;
    }});
    shown.textContent=n;
  }}
  q.addEventListener('input',apply);
  [].forEach.call(document.querySelectorAll('[data-f]'),function(b){{
    b.addEventListener('click',function(){{
      [].forEach.call(document.querySelectorAll('[data-f]'),function(x){{x.classList.remove('on');}});
      b.classList.add('on'); filt=b.dataset.f; apply();
    }});
  }});
  document.getElementById('dense').addEventListener('click',function(){{
    document.body.classList.toggle('dense'); this.classList.toggle('on');
  }});
  document.getElementById('full').addEventListener('click',function(){{
    if(document.fullscreenElement){{document.exitFullscreen();}}
    else{{document.documentElement.requestFullscreen&&document.documentElement.requestFullscreen();}}
  }});
  // ---- KPI cards drive the table ----
  var tbody=document.getElementById('tb'), sortState={{}};
  function sortBy(i,desc){{
    rows.sort(function(a,b){{
      var x=cell(a,i), y=cell(b,i);
      if(typeof x==='number'&&typeof y==='number') return desc?y-x:x-y;
      return desc?String(y).localeCompare(String(x)):String(x).localeCompare(String(y));
    }});
    rows.forEach(function(r){{tbody.appendChild(r);}});
  }}
  [].forEach.call(document.querySelectorAll('.kpi.clickable'),function(c){{
    function fire(){{
      if(c.dataset.filter==='trading'){{
        tradingOnly=!tradingOnly; c.classList.toggle('active',tradingOnly); apply(); return;
      }}
      var i=+c.dataset.sort;
      sortState[i]=(sortState[i]===undefined)?true:!sortState[i];  // first click = highest first
      sortBy(i,sortState[i]);
      [].forEach.call(document.querySelectorAll('.kpi[data-sort]'),function(x){{
        x.classList.remove('active');
      }});
      c.classList.add('active');
    }}
    c.addEventListener('click',fire);
    c.addEventListener('keydown',function(e){{
      if(e.key==='Enter'||e.key===' '){{e.preventDefault();fire();}}
    }});
  }});

  // sort on the second header row
  var hdr=document.querySelectorAll('#tbl thead tr:nth-child(2) th');
  [].forEach.call(hdr,function(th,i){{
    var asc=false;
    th.addEventListener('click',function(){{
      asc=!asc;
      var tb=document.getElementById('tb');
      rows.sort(function(a,b){{
        var x=cell(a,i), y=cell(b,i);
        if(typeof x==='number'&&typeof y==='number') return asc?x-y:y-x;
        return asc?String(x).localeCompare(String(y)):String(y).localeCompare(String(x));
      }});
      rows.forEach(function(r){{tb.appendChild(r);}});
    }});
  }});
  function cell(tr,i){{
    var c=tr.children[i]; if(!c) return '';
    var t=c.textContent.replace(/[£,%\\s]/g,'').replace('−','-');
    var v=parseFloat(t);
    return isNaN(v)?c.textContent.trim():v;
  }}
  document.getElementById('csv').addEventListener('click',function(){{
    var out=[], hs=[];
    [].forEach.call(hdr,function(h){{hs.push('"'+h.textContent.trim()+'"');}});
    out.push(hs.join(','));
    rows.forEach(function(r){{
      if(r.classList.contains('hide')) return;
      var cs=[];
      [].forEach.call(r.children,function(c){{
        cs.push('"'+c.textContent.trim().replace(/\\s+/g,' ').replace(/"/g,'""')+'"');
      }});
      out.push(cs.join(','));
    }});
    var b=new Blob([out.join('\\n')],{{type:'text/csv;charset=utf-8;'}}),
        a=document.createElement('a');
    a.href=URL.createObjectURL(b); a.download='daily_sales_track_{today_iso}.csv'; a.click();
  }});
}})();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.abspath(os.path.join(
        here, "..", "..", "evidence", "final_outputs", "REQ-17_daily-sales-track"))
    with io.open(os.path.join(out_dir, "dst_d01_data.json"), encoding="utf-8") as fh:
        data = json.load(fh)

    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    theme = args[0] if args else DEFAULT_THEME
    if theme not in THEMES:
        raise SystemExit("unknown theme {0!r}; choose from {1}".format(theme, sorted(THEMES)))

    if "--preview-all" in sys.argv:
        # side-by-side comparison copies; the shipped deliverable is untouched
        target = args[1] if len(args) > 1 else out_dir
        for name in THEMES:
            p = render(data, os.path.join(target, "preview_{0}.html".format(name)), name)
            print("preview: {0}".format(p))
    else:
        p = render(data, os.path.join(out_dir, "REQ-17-D01_dst_dashboard.html"), theme)
        print("dashboard ({0}): {1}".format(theme, p))
