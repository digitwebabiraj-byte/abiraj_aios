# sql/REQ-28 — Amazon PPC Keyword YoY Dashboard build

Single generator pair; read-only; live ledsone DB via `LED_*` env creds (shared store).

| File | Purpose |
|---|---|
| `build_akyp_d01.py` | Reads `amazon_campaigns.keyword_performance_data` (+ `keywords`, `campaigns`, `ad_groups`) at keyword grain for amazon Ledsone (sub_source 8) across UK/US/CA/DE/FR/IT; 7-day attribution; computes like-for-like current vs previous-YEAR windows in one pass; writes `akyp_payload.json`. |
| `render_akyp_dashboard.py` | Embeds `akyp_payload.json` into the spec template and appends the delivery layer → `evidence/final_outputs/REQ-28_.../REQ-28-D01_amazon_keyword_yoy_dashboard.html`. |
| `akyp_payload.json` | Snapshot of the fetched per-market keyword rows + daily series (audit/repro + render input). |

## Run
```bash
python build_akyp_d01.py            # optional: AKYP_REFERENCE_DATE=YYYY-MM-DD to pin the window
python render_akyp_dashboard.py
```

## Notes / gotchas
- **Source** = `keyword_performance_data` (manual-targeting keywords only; auto search terms
  excluded by design). Do **not** use `search_term_performance_data` — larger auto-inclusive
  universe, starts only 2025-11-16.
- **Grain** = one row per `keyword_id` = keyword × campaign × ad group.
- **Attribution** = 7-day (`sales_7d` / `purchases_7d`); `cost` = spend.
- **status / bid** from the current `keywords` row (`state`, `keyword_bid`).
- **suggestedBid** has no source column anywhere → `null`.
- **YoY is live** (history back to 2023). Current MTD under-reports vs settled prior year because
  7-day attribution has not matured on the last ~7 days — expected, not a gap.
- **US** has near-zero recent keyword activity; **CA** has no current-window rows but a populated
  prior year (shows as a full YoY decline).
