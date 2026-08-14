# Merged Dashboard — "Meshika — Advertising Dashboards"

One self-contained page combining Meshika's two PPC dashboards, so she has a single link instead
of two. **Independent-tab model** — each task keeps its own design, data and logic, isolated in its
own `<iframe srcdoc>`; nothing is recomputed and there are no CSS/JS collisions.

**End-user display name:** page title & brand = **"Meshika — Advertising Dashboards"** (plain
wording chosen so the user immediately understands it).

| Tab (shown to Meshika) | Task | Source |
|---|---|---|
| **Amazon Ads — Keyword Year-on-Year** | akyp · PRJ-2026-024 · REQ-28-D01 | canonical deliverable in the akyp project |
| **eBay Ads — Pause Report** | eppa · PRJ-2026-013 | `sources/eppa_ph878_meshika.html` — snapshot of `tech_team_outputs.ph_task` **id 878** (assigned_user=meshika), pulled read-only |

## Why merge is valid
Both are PPC decision dashboards for the same user (Meshika) and company (LEDSone): shared account,
a Rule/Priority/Reason/Decision ≈ Diagnosis/Priority/Root-cause/Action engine, a data table, and a
rules/method view. Channel (Amazon vs eBay), grain (keyword vs campaign) and comparison (YoY vs 30d)
differ — which the independent-tab model handles by keeping each task whole.

## Build / refresh
```bash
python build_merged_meshika.py   # reads both sources -> merged_ledsone_ppc_meshika_dashboard.html
```
Refresh the eBay tab by re-pulling ph_task id 878 into `sources/eppa_ph878_meshika.html`; refresh the
Amazon tab by re-running the akyp build/render. Then re-run this builder.

## Output / publish
`merged_ledsone_ppc_meshika_dashboard.html` — self-contained. Intended to publish as **one** ph_task
row for Meshika (replacing the separate akyp + eppa rows, or as a new merged row) — **on explicit
owner instruction only**; read-only until then.

## Verified 2026-08-14 (in-browser)
Both tabs render; switch works (Amazon: 8 KPIs / 2,202 rows · eBay: 154 rows); no console errors.
