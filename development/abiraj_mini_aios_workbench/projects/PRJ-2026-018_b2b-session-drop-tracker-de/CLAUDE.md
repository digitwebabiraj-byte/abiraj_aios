# CLAUDE.md — PRJ-2026-018 B2B Session Drop Tracker (Amazon.de)

Project execution rules. Inherits the workbench `CLAUDE.md`; the rules below are additional and
specific to this project.

## 1. The database is NOT the source — the Amazon report is

The single most important fact about this build (owner-confirmed 2026-07-31).

The sheet was generated **from a direct Amazon.de Seller Central Business Report export** (Detail
Page Sales and Traffic by Child Item, B2B columns). That export is the **system of record**.

The warehouse's `business_reports.amz_traffic_by_asin` is a **partial, gappy mirror** of that report
and **cannot** reproduce it: **May 2026 is entirely missing** for .de, ~half the sheet's ASINs have
zero B2B there, and 77% of rows report more B2B sessions on the sheet than the DB holds all-time
(Germany scope). Do **not** rebuild this report from the database. Build FRRC-style: enrich the
owner-supplied export.

The DB mirror's incompleteness is a separate data-engineering issue (raise with Sajeesan) — it is
**not** this report's source.

## 2. Prove coverage, never trust one ASIN

A single exact ASIN reconciliation (`B0DLWRP73C`: DB 19 = sheet 15 + 4) proved the **column
mapping**, and was initially mis-read as "fully reproducible". It is not — a **full-population**
completeness test is what exposed the ~half-missing coverage. Always run the whole-population test
before declaring a source usable.

## 3. Scope: Amazon.de (Germany) account only

Single account, Germany only. The source is the DE Seller Central report, so it is DE-only by
definition. The DB's per-marketplace "UK/FR matches" seen during the audit are noise from the
incomplete mirror and are irrelevant (the DB is not the source).

## 4. Tier is set by MAX(prev, current) B2B Sessions — nothing else

`Tier = IF(MAX(prev,current) ≥ Tier3_min → "Tier 3 - High", ELSE IF ≥ Tier2_min → "Tier 2 - Moderate",
ELSE "Tier 1 - Low")`. Session Change, Units Orders and Buy Box % are **context only** — they never
change Tier, Status or Action. Status and Action follow directly from Tier.

## 5. Thresholds stay configuration, never code

Tier 2 (≥ 5) and Tier 3 (≥ 10) session boundaries live on the **Thresholds** sheet as editable
cells; the Tracker's Tier column is a live formula that reads them (`Thresholds!B4`, `Thresholds!B5`).
Never inline a threshold into a script or hardcode a tier.

## 6. Include an ASIN only if it has B2B traffic in ≥ 1 window

Sessions or page views in the current or previous window. Zero-both ASINs are excluded (no B2B
signal). This mirrors the source's own inclusion rule.

## 7. B2B-only columns — never the blended totals

Use Sessions·Total·**B2B**, Page Views·Total·**B2B**, Units ordered·**B2B**. Never the blended
B2B+B2C totals. B2B Conversion % is deliberately **not** used — .de per-ASIN B2B volume is too low
for a percentage to be reliable.

## 8. Windows are fixed by the export, not "last 30 days from today"

Current = 2026-06-16 → 2026-07-15; Previous = 2026-05-17 → 2026-06-15 (owner-confirmed). Each future
cycle uses whatever two matching 30-day windows the new export covers — carry the labels from the
export, do not assume today.

## 9. Read-only until gated

Read-only throughout. No `ph_task` publish, no scheduled task, no git commit until the open items in
`PROJECT_HOME.md` (ph_task audience/team, IDs) are confirmed and reviewer gates pass.
