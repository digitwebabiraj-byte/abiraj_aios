# TASK REGISTER — PRJ-2026-017 (eckr)

| Deliverable | What | Status | Evidence |
|---|---|---|---|
| REQ-20-D01 | eBay Competitor & Keyword sheet — 9 categories × top-5 UK competitors (45 rows) + generated keywords + product images | ✅ DELIVERED · PUBLISHED (ph_task 496–499) — Jarsini sign-off pending | `evidence/final_outputs/REQ-20_ebay-competitor-keyword-research/` |
| REQ-20-D02 | Scheduled automation of the scrape (optional; new on-request stream) | NOT STARTED | — |

## Timeline
- **2026-07-30** — Onboarded from `Jarsini task.xlsx`. DB feasibility proven (no competitor/
  promotion/eBay-keyword tables → first live-scrape stream). Built 9-category × top-5 competitor
  + keyword dataset; interactive dashboard + Excel; published static page to `ph_task` 496–499.
- **2026-07-30 (same day, iterated)** — Cone category relabeled → "Metal Shade Pendant Light";
  off-type rows swapped after adding the image column; **full UK-only re-scrape** (LH_PrefLoc
  unreliable) → all 45 rows UK-verified; each category filled to **5**; UI polished (eBay logo,
  filters single-row, sticky columns/header, feedback bars); re-published each change.

## Locked decisions
- Own 13 eBay accounts excluded · top-5 per category · UK-located only (verified per listing) ·
  Shipping recorded free/paid but left LK-IP-derived · keywords generated · sold blank where eBay
  shows none.

## Open / next
Jarsini sign-off · EOD skill file (`DigitWeb_Works_Abiraj/30_07_2026/`) · canonical `.xlsx`
rename · decide whether to automate.
