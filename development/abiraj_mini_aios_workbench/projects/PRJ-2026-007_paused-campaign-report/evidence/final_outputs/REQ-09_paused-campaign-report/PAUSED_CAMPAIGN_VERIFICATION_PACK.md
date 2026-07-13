# Paused Campaign Report — Independent Verification Pack

**Project:** PRJ-2026-007_paused-campaign-report · **Task:** REQ-09_paused-campaign-report (D01)
**Source req:** REQ-09-D01 · **Project code:** PH-2026-07-UTHAR10
**DB:** `order_management_copy` (read-only, Postgres MCP `execute_sql`) · **Run:** 2026-07-13
**Result:** **4 / 4 checks PASS**

Every check was run live against the production database and reconciled against the rendered
outputs (`data.json`, `.xlsx`, dashboard). Queries are in `sql/REQ-09_.../validation_checks.sql`.

---

## Check 1 — Report count (targets / distinct ASINs)  ✅ PASS
- Query: count check wrapping the report SELECT.
- **Expected:** 33 targets · 32 distinct ASINs.
- **DB result:** `{ targets: 33, asins: 32 }`.
- **Rendered:** `data.json` = 33 rows / 32 distinct `asin`; xlsx `Report` = 33 data rows / 32 distinct
  ASIN cells; **published dashboard** (`Utharsika_Paused_Campaigns_Report.html`) embedded payload = 33
  rows / 32 ASINs, "Paused ad targets 33".
- **Dashboard↔data parity (Check 1b):** the published dashboard's `<script id="payload">` was diffed
  against `data.json` — **33/33 row tuples (campaign · ad group · ASIN · SKU · pause date · days)
  match exactly, 0 differences**. Reason text differs only in presentation (leading `Date Range …`
  clause dropped, `≥`→`>=`, added summary/chips); verbatim reason retained in `data.json`/xlsx. ✅
- **Why 33 rows but 32 ASINs:** `B0DXQ84YT7` is paused under two ad groups (`Curvy-2pack` and
  `B0D7ZRWBS2`) → 2 rows, 1 ASIN. Correct at the ad-target grain.

## Check 2 — Still-paused vs all-pauses  ✅ PASS
- Query: latest automation pause per ad target, joined to current ad status.
- **Expected:** total 41 · still paused 33 · re-activated 8.
- **DB result:** `{ total: 41, still_paused: 33, reactivated: 8 }`.
- **Meaning:** 41 ad targets were paused by automation; 8 have since been re-activated and are
  correctly **excluded**; the remaining 33 populate the report. 33 (still-paused) = Check 1 targets.

## Check 3 — Pause-date waves  ✅ PASS
- Derived from the governed pull.
- **Expected / result:** two waves — **2026-06-10** (18 targets, 33 days paused) and
  **2026-06-17** (15 targets, 26 days paused). 18 + 15 = 33. Days Paused = `CURRENT_DATE − pause_date`
  (2026-07-13 − 2026-06-10 = 33; − 2026-06-17 = 26). Matches every row.

## Check 4 — Pause-reason integrity (verbatim, rule coverage)  ✅ PASS
- **Expected:** every `Pause Reason` is carried verbatim from `ppc_etl_automation_log.reason`; all
  three rule families appear (not only the workbook's Rule 2).
- **Result:** rule coverage across the 33 targets — **Rule 1 (ACOS): 9**, **Rule 2 (zero orders +
  spend): 22**, **Rule 3 (spend, orders dropped): 3** (sum 34 because `B0DPMQZ1WP` carries a combined
  `Rule 1 | Rule 3` reason). No reason string was paraphrased, bucketed or truncated — the dashboard
  shows the full text with `R1/R2/R3` tags derived from it, and the xlsx stores it unmodified.

---

## Scope / method notes
- **Scope key:** campaign `record_name ILIKE '%utharsika%'` (no owner column exists). *(Open item A.)*
- **Platform:** Amazon (`source=1`); SB excluded (the pause log holds only Amazon ad-level events).
- **Pause source:** `ppc_etl_automation_log` — `action_type='ad_pause_logs'`, `status='success'`,
  `applied_by='0'`; latest per target via `DISTINCT ON (record_id, source)`.
- **Field resolution:** campaign + ad-group names from `public.ppc`; ASIN (`ref_id`) + SKU from
  `public.ppc_performance` (`record_type='ad'`).
- **Live-DB caveat:** `ppc.record_status` is current (no history) — "still paused" and "Days Paused"
  are as-of-today. The ultimate external cross-check is the Amazon Ads console for the same campaigns;
  a mismatch there is an upstream ETL issue, not a report defect.
- **Illustrative-only:** the workbook's two sample rows (B0DH182H6J / B0CVKSQN9K, 2026-07-06, Days
  Paused 0) are **not** reproduced — they are examples of shape, not the answer.

## Open items (Satheesvaran — not decided here)
A. scope key · B. grain (per-ASIN vs per-campaign) · C. included set (33 vs 41) ·
D. platform · E. manual pauses. Items B and C would change the row count.
