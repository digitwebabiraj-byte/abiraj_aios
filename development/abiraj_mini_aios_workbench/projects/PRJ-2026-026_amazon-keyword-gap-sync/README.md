# BGCT Keyword Collection & Cross-ASIN Gap Sync (bgct) — PRJ-2026-026

Concise landing page. Full context in `PROJECT_HOME.md`; execution rules in `CLAUDE.md`; field-by-field
source map in `SYSTEM_REFERENCE.md`; task index in `TASK_REGISTER.md`.

## What
A **two-phase Amazon UK keyword workflow** for LED bulb listings across two seller accounts.

- **Phase 1** collects the **top search terms** for each Top-Moving ASIN from Amazon **Search Query
  Performance (SQP)** — first-party Brand Analytics data, not estimates.
- **Phase 2** takes those confirmed terms and checks whether **other listings of the same base SKU** that are
  **declining or making no sales** already carry them — in the **title/bullets/description** (Method 1) and
  in the **backend generic keyword field** (Method 2), independently. Every gap is flagged with a
  **directional add target** (backend / bullet / both) and presented for one-click operator action.

Runs **monthly, per brand account**, with no manual keyword lookup.

## Who it's for
**User / Business Validator: Thuwaraga** (`staff.users` id 122, Jaffna, Active). **Assigned by HR**,
2026-08-19. Owner Abiraj · Tech Sajeesan · Queryability Tamil Selvan · Coordinator Varmen.
*(The source document itself names no one — it is addressed to the "Automation Team" and cites an "MD
instruction"; the assignment came from HR.)*

## Status
🟢 **BUILT 2026-08-19 — REQ-30-D01 + D02 produced, 6/6 QA checks pass.** 103 Top-Moving ASINs → 1,689
SQP terms → 66 underperforming listings → **Part A 38 rewrites + Part B 542 keyword rows (381 gaps)**.
Verified in-browser. **Not validated, not published, not automated, not committed.** Earlier status: Folder structure, source import (checksum-verified), governance
docs and a live data-foundation probe are done. **No build, no deliverable, nothing committed, nothing
published.** Next step is sending the discovery decision sheet to Thuwaraga + a GPT-approved implementation
prompt (this workbench: Claude executes approved prompts, it does not invent business logic).

## Expected benefit
Replace manual keyword lookup with a monthly automated cycle — the source's own "MD instruction" is that the
pipeline run **end-to-end with zero manual keyword lookup**. Take the terms **already proven** on a
Top-Moving ASIN (first-party SQP data, *"not estimated"*) and close the gap on sibling listings of the same
base SKU that are declining or dead, **routing each missing term to the right place** (backend / bullets /
both) rather than a blanket push — so two accounts' worth of per-ASIN Seller Central navigation becomes a
reviewed report whose only human actions are *Mark Reviewed* or *Add Missing Keywords*.

## 🟢 The headline finding — the data foundation is green, and Phase 1 needs no manual work
Unlike the previous project (#025, blocked on missing data), **every read this workflow needs already exists
in the raw `ledsone` database**, measured live 2026-08-19:

| What the spec asks for | Where it actually lives | Measured |
|---|---|---|
| SQP search terms (Phase 1, steps 2–8) | `business_reports.amz_search_query_performance` | **137,048 rows / 3,368 ASINs / 71,679 queries** (Ledsone UK) |
| Top-Moving ASINs (Phase 1 step 1) | `business_reports.amz_sales_and_traffic_by_asin` | 417,030 rows, live to **2026-08-17** |
| Drop / zero-sales ASINs (Phase 2 step 1) | same table | same |
| Title + description (Method 1) | `listings.amazon_listings.title`, `.product_description` | 18,721 UK rows, live to **2026-08-19** |
| Bullets (Method 1) | `listings.amazon_listing_bullet_points` | **429,224 rows** |
| Backend generic keywords (Method 2) | `listings.amazon_listing_search_engine_keywords` | **189,192 rows** |

**Phase 1 as written is 8 manual Seller Central steps. The database already holds that export**, so Phase 1
can be a query rather than a navigation procedure. That is a scope simplification for the requester to
approve, not one to assume — see open item #2.

## 🔴 The one hard boundary — this workbench does not write to Amazon
The spec's §2.7 ends in **automatic SP-API writes** to live listings ("no copy-paste, no listing-page
editing"). Editing a live Amazon listing's bullets or backend keywords is **destructive, public and
irreversible**, and no SP-API write credential exists in this workbench. **The AIOS deliverable stops at a
reviewed gap report with a per-keyword add-target recommendation.** The push is a separate, separately
approved system. See `CLAUDE.md` §2.

## 🟠 The seven traps found in the data (all measured, none in the spec)
1. **SQP is WEEK-grain only** — the spec's "Reporting Range → Monthly" has no equivalent row. Months must be
   assembled from weeks, and rate/median columns **cannot be summed**.
2. **Backend keywords are stored as phrase blobs, not discrete terms** — a keyword check is a *containment*
   test, never equality.
3. **SQP covers 3,368 of 16,963 Ledsone UK ASINs** — Amazon only reports queries above a volume floor.
4. **DCVOLTAGE SQP is 2 weeks staler than LEDSone** (ends 2026-07-25 vs 2026-08-08).
5. **SKU normalisation is far messier than `2PK`/`5PK`** — the spec's own example family really exists, and
   carries ` M`, ` R`, `-DC`, `-a`, `_DCVV`, `_AMD`, `_KP`, `3PK A` and `amzn.gr.…` forms too.
6. **27% of ASINs never appear in the sales table** — it is traffic-driven, so the deadest listings are the
   ones missing from it. Zero-sales must anchor on the catalogue.
7. **20% of listings have an empty backend keyword field and 11% are title-only** — for those, "keyword
   missing" is NO DATA, not a checked miss.

## ✅ Is it doable? Verified end-to-end 2026-08-19
**Yes — the reporting workflow is fully buildable today.** The whole chain was *run*, not assumed:
Top-Mover `B0B9Y5MRSK` → zero-sale twin `B07FNP5GYB` → live SQP terms → Method 1 + Method 2 → add target.
Top gap found: **"3 core electrical cable", 4,008 searches/month, missing from both surfaces.**

Three qualifications:
- 🔴 The **SP-API auto-push is out of scope here** (above) — a deliberate boundary, not a technical limit.
- ⚠ **Two unstated rules decide the output size**: SKU normalisation **~125×** (58 vs 7,396 candidate pairs)
  and keyword matching **~5×** (2/50 vs 10/50 hits). Guessing either makes the row count an accident.
- 🟠 **One correction to the spec's own method**: zero-sales must anchor on the catalogue — 27% of ASINs
  never appear in the sales table, and they are the deadest ones.

Full working: `evidence/logs_or_screenshots/REQ-30_amazon-keyword-gap-sync/2026-08-19_feasibility_assessment.md`

## Deliverables (planned, not built)
- **REQ-30-D01** — Phase 1: Top-Moving ASINs + their confirmed SQP top search terms, per account.
- **REQ-30-D02** — Phase 2: the 12-column keyword-gap contract (§2.9 of the spec) as Excel + an interactive
  review dashboard, showing tick/missing per keyword for both methods and the directional add target.

## Identity (provisional)
`PRJ-2026-026` / `REQ-30` / code `bgct`. **Provisional** — the source PDF carries no requirement number
(REQ-26 = esdt, REQ-28 = akyp, REQ-29 = avm). Confirm with Abiraj (cosmetic).

## Authoritative documents
- `PROJECT_HOME.md` — canonical project truth
- `SYSTEM_REFERENCE.md` — column → `schema.table.column` map and every derived-field rule
- `CLAUDE.md` — execution rules
- `TASK_REGISTER.md` — task/deliverable index
- `evidence/logs_or_screenshots/REQ-30_amazon-keyword-gap-sync/2026-08-19_data_foundation_probe.md` — the
  live probe behind every source claim above
- `evidence/logs_or_screenshots/REQ-30_amazon-keyword-gap-sync/2026-08-19_feasibility_assessment.md` — the
  end-to-end feasibility run and the sensitivity measurements
- `prompts/discovery/REQ-30_amazon-keyword-gap-sync/2026-08-19_DECISION_SHEET_for_requester.md` — the 12
  questions that block the build

## Next step
Send the decision sheet to **Thuwaraga**, leading with the SP-API scope question. Then a GPT-approved
implementation prompt before any build.
