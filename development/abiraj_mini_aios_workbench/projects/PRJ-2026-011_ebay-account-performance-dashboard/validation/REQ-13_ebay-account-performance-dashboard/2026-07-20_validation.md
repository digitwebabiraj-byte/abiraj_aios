# REQ-13-D01 — Validation & Reconciliation record (2026-07-20)

Read-only. Every headline was reconciled to the **owner's own independent live-DB (MCP) checks** — this
project was corrected five times precisely because early passes didn't reconcile.

## A · Owner-anchored reconciliation (PASS)
| Check | Owner's live-DB figure | Dashboard | Result |
|---|---|---|---|
| led_sone **UK** revenue (order_total, Completed, June) | £28,975.37 | £28,975.37 | ✅ exact |
| led_sone UK units | 2,452 | 2,452 | ✅ exact |
| so_926407 **UK** ON_SITE ad spend | £884.07 | £884.07 | ✅ exact |
| so_926407 UK ON_SITE orders / clicks / impressions | 434 / 5,612 / 3,032,285 | 434 / 5,612 / 3,032,285 | ✅ exact |

## B · Cross-format consistency (HTML ⇄ Excel) — PASS
The Excel builder (`build_excel_v3.py`) **imports the exact `R` dataset from `build_html_v3.py`**, so the
two cannot drift. Totals verified equal across both:
| Metric | HTML & Excel |
|---|---|
| Rows | 22 |
| Revenue (order_total, Completed) | £95,455.18 |
| Orders / Units | 4,625 / 7,330 |
| ON_SITE Ad Spend / Ad Sales | £7,788.75 / £42,100.97 |
| Overall TACOS | 8.16% |
| Active (per-site) / New / Stock | 12,799 / 248 / 13,579,887 |

## C · Internal integrity — PASS
- Per-account marketplace revenues sum to the account total (e.g. led_sone UK+DE+FR+US+IT = £36,500.62 whole-store; each marketplace row ties to the live per-marketplace pull).
- Marketplace rollup sums to £95,455.18 (= June total).
- Excel recalculated via LibreOffice headless — **0 formula errors**; HTML script `node --check` clean; live-served DOM checks: filters, sticky headers, CSV export all work.
- eBay-only ad filter verified (all `source_name='EBAY'`; no Amazon/Shopify contamination).

## D · Method decisions confirmed against source (not invented)
Revenue = `SUM(order_total)`; rows = account × marketplace; conversion = `traffic_data which_channel=2`;
advertising = `ppc` `record_subtype='ON_SITE'` joined to `ppc_performance` on `record_id=parent_id`; new
listings = ledsone `listings.ebay_listings.created_at`; sales rank by revenue.

## E · Open (owner's) — resolved-as-accepted 2026-07-20 ("all ok")
- **Orders count** — `COUNT(DISTINCT order_id)` kept (led_sone UK 1,517). The owner's other analysis used
  `COUNT(*)` line-count (1,619). Noted; not adopted.
- **Conversion RAG threshold** — kept as the mockup's (green >4.5%); whole-account conversion is ~2–3%, so
  it mostly reads amber/red. Documented in the Excel Definitions sheet; recalibration = future work.

## F · Publish verification — PASS
`tech_team_outputs.ph_task` rows **333–336** (Thinesh/Jarsini/kobiga/powsteena), `project_code=ebpd`,
`assigned_user_team=ebay_priors`, `released`; HTML content confirmed to be the final version (per-marketplace
heading, order_total note, £28,975 value present). Guarded `temp_user` publish (pre-DELETE + INSERT).

**Verdict: GREEN — technically reconciled and business-accepted ("all ok", 2026-07-20).** Reviewer gates
(Sajeesan technical, Tamil Selvan queryability) not formally recorded.
