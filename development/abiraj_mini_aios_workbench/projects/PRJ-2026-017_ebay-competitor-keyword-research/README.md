# PRJ-2026-017 · eBay Competitor & Keyword Research (`eckr`)

Jarsini's per-product competitor + keyword intelligence report. 9 eBay product categories, the
**top-5 UK competitors** each (id · brand · title · sold · price · feedback · shipping · promotion
· product image) plus generated primary/secondary/long-tail keywords. **45 rows, all UK-verified.**

**First live-eBay-scrape project** (the internal DB has no competitor/promotion/eBay-keyword data —
see `evidence/DATA_SOURCE_ANALYSIS.md`). Start with `PROJECT_HOME.md`.

- **Method:** `capability/METHOD.md`
- **Deliverables:** `evidence/final_outputs/REQ-20_ebay-competitor-keyword-research/`
  (dashboard HTML · Excel with embedded images · static `ph_task` page)
- **Reproducible build:** `sql/REQ-20_ebay-competitor-keyword-research/` (`build_req20.py`,
  `gen_dashboard.py`, `gen_static.py`, `build_xlsx_final.py`, `images.json`, `publish_eckr_ph_task.py`)
- **Published:** `ph_task` ids 496–499 (`ebay_priors`)

**Note:** shipping figures are the eBay-to-Sri-Lanka (this env IP) estimate, not UK-accurate (owner
call). Spider/Pipe have minimal UK competition → some blank Sold cells (genuine).
