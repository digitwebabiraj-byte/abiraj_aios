# CLAUDE.md — PRJ-2026-023 eBay UK Top 50 Sales Drop

Project execution rules. Inherits the workbench `CLAUDE.md`; the rules below are additional.

## Identity
- Project `PRJ-2026-023_ebay-top50-sales-drop` · code `esdt` · Task `REQ-26`. Owner Abiraj; Business
  Validator **Kobiga** (same PH as eBay Product Net Sales #019). **IDs provisional** — the source is a spec
  mock-up + workflow PDF with no requirement number; REQ-25 is taken by `slow-moving-products`. A new
  day/session does NOT mint a new Task ID.
- This report is a **synthesis of four proven eBay builds**, not a green-field one: sales from **epns #019 /
  eppr #016**, organic traffic from the **traffic_data** reference, PPC from **eppa #013**, stock from
  **smp #022 / fmp #020**. Reuse their query/build patterns; do not fork new data paths.

## 1. The source files are a spec, not data
Every value in `kobiga task (2).xlsx` and the PDF's example tables (SKU001, "Pendant Light", £800→£350,
"🔴 Critical", -56%) is an **illustrative sample**. They define the desired **columns, alert thresholds and
Action vocabulary** only. Never copy a sample number or label into a deliverable. Every delivered figure
traces to live data and is reconciled against an anchor before it is trusted.

## 2. Do NOT invent the business rules
"Which period", the **alert thresholds** (50/30/15%), the **Reason/Action** diagnosis matrix and the
**ranking grain** are business rules. The PDF gives *defaults* (§3/§6/§8) — treat them as **provisional,
pending Kobiga**. Do not present them as agreed logic and do not silently change them. This is a workbench
where Claude executes GPT-approved prompts and does not invent logic.

## 3. This is eBay UK — currency & the DST trap
The report is eBay **UK = £**. `orders.total` is in the marketplace's own currency and no FX table exists;
UK rows are already GBP so they sum safely, but **never blend a UK figure with another marketplace** and
never label a non-GBP value with £.

## 4. Filter/rank logic is fixed by the workflow (PDF §4–5)
Exclude SKUs with **no previous-period sales**; exclude SKUs where sales **rose or held**; rank survivors by
**absolute £ loss desc**, tie-break **Drop % desc**; take **Top 50**. Do not deviate without owner sign-off.

## 5. The two-database join is the hard part
Sales/PPC/stock live in RAW `mcp.ledsone`; organic Impressions/Clicks/CTR/CVR live in the **warehouse**
`public.traffic_data` (`which_channel=2`). The build must join across both on the same SKU/period grain.
Watch the traps: CPS logs £0 spend (ROAS/ACOS), ~89% eBay listings are multi-SKU (SKU↔Item ID not 1:1),
eBay title lives on the parent row (`all_list=0`).

## 6. Read the KB first; read-only; never fabricate
- Read the AIOS knowledge base (`docs.ledsone.co.uk/mcp`) BEFORE writing any SQL.
- READ-ONLY on all source tables. No INSERT/UPDATE/DELETE/DDL. The only future write is a guarded `ph_task`
  publish on explicit owner instruction after the audience is named and each recipient verified.
- Every filled column traces to a real `schema.table.column`. A metric with no truthful source renders a
  documented sentinel (e.g. NO DATA / "Never"), never a guessed number. A `0` is written only where the
  true value is zero. Credentials come from the git-ignored shared store, never committed.

## 7. One generator module
When built, the report (and any scheduled run) comes from the single module
`sql/REQ-26_ebay-top50-sales-drop/build_esdt_d01.py`. Do not fork a second fetch path.

## 8. Stop conditions (in addition to the workbench's)
- A rule (period, thresholds, ranking grain, Reason/Action vocabulary) is needed but unconfirmed by Kobiga →
  stop and put it on the discovery decision sheet; keep the documented default flagged, do not silently invent.
- The two-database join cannot be reconciled to a live anchor → stop and report, do not ship unverified numbers.
- A publish is requested before the audience is named and each recipient verified.
- Any request to blend currencies across marketplaces.
- No approved implementation prompt exists yet → do not start the build.

## Vocabulary
Sales Drop % = (Current − Previous) ÷ Previous × 100 · Loss £ = Current − Previous (negative) · Priority =
alert band from Drop % (provisional) · Action = diagnosis rule-engine output (provisional) · source_id 2 =
eBay · which_channel 2 = eBay organic traffic · ELECTRICALSONE = the eBay UK account · NO DATA = no truthful source.
