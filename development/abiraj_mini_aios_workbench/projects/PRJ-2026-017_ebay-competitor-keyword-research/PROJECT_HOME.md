# PRJ-2026-017 — eBay Competitor & Keyword Research (eckr)

**End user / requester:** Jarsini (`staff.users` id 91, username `Jarsini`, team `ebay_priors`)
**Owner/developer:** Abiraj · **Requirement:** REQ-20 · **Code:** `eckr`
**Onboarded / delivered:** 2026-07-30 · **Source:** `Jarsini task.xlsx`

## What this is
Jarsini's first requested report. For each of her **9 product categories**, the **top-5 UK
competing eBay sellers** — competitor listing ID, brand, title, sold quantity, price, seller
feedback, shipping and promotion — plus generated **primary / secondary / long-tail keyword**
sets per product. 14-column layout from the source brief, + a product **Image** column.

## The defining fact
**This is the first AIOS project NOT sourced from the internal databases.** A deep probe (see
`evidence/DATA_SOURCE_ANALYSIS.md`) proved the warehouse + raw `ledsone` DB have **no competitor
tables, no promotion/markdown tables and no eBay keyword tables**. So the competitor columns come
from **live eBay UK scraping** (browser) and the keyword columns are **generated** — a new
capability class for this workbench.

## Method (locked — see `capability/METHOD.md`)
- eBay UK search per category; **exclude our own 13 eBay seller accounts** (they were 50–80% of
  every result — see the store list in the postgres-warehouse-sql skill).
- **UK-only, verified:** eBay's `LH_PrefLoc=1` filter is unreliable (US/China sellers ship to UK
  and slip through — the whole Pipe & Spider categories were foreign at first). Real fix =
  exclude any search card showing `from <China|United States|…>` **and** confirm each listing's
  `Located in … United Kingdom`. All 45 rows are UK-verified.
- **Top-5 sold-proven** competitors where they exist; Brand from eBay item specifics; product
  **image** = per-listing `og:image` thumbnail (click → listing).
- Keywords generated from the product name/type.

## Deliverables (REQ-20-D01)
- `evidence/final_outputs/REQ-20_.../REQ-20-D01_dashboard.html` — interactive dashboard (eBay
  wordmark, filter bar + sort + search, sticky Image/Product columns + header, zebra, feedback
  mini-bars, image hover-zoom).
- `..._ebay_competitor_keyword_FINAL.xlsx` — Excel with embedded product images.
- `..._REQ-20-D01_ph_task.html` — static publish page (full UI + pre-rendered table fallback).
- Reproducible scripts in `sql/REQ-20_.../`: `build_req20.py` (dataset), `gen_dashboard.py`,
  `gen_static.py`, `build_xlsx_final.py`, `images.json`, `publish_eckr_ph_task.py`.

## Published
`tech_team_outputs.ph_task` ids **496–499** (`ebay_priors`: Thinesh/Jarsini/kobiga/powsteena),
guarded `temp_user` publisher (dry-run default, SELECT-then-INSERT/UPDATE, `assigned_user_team=
'ebay_priors'`, read-back verify). `task_name`/`description` blanked for a full-screen embed.

## Honest limitations (by design, disclosed)
- **Shipping** values are eBay's estimate to this environment's IP (**Sri Lanka**), not UK — owner
  chose to leave as-is. UK free/paid is only reliably readable via the listing JSON-LD `GBR`
  shipping leg, and only for GSP-enrolled items.
- **Spider & Pipe** have almost no UK sold-proven competition → 8 blank Sold cells across those two
  categories, verified genuine (eBay shows no "X sold" for low-volume UK niche sellers).

## Open items
Jarsini sign-off · today's EOD skill file · canonical `.xlsx` rename (Excel currently locked) ·
not automated (new on-request stream). Requirement doc: `DigitWeb_Works_Abiraj/30_07_2026/`.
