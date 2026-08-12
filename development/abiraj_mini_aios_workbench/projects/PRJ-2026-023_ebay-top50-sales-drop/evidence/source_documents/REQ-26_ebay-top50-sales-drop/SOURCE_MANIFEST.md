# SOURCE MANIFEST — REQ-26 eBay UK Top 50 Sales Drop

Imported 2026-08-12. These are the **original requester inputs**, verbatim. They are a **specification**
(desired columns, alert thresholds, Action vocabulary, method) — **not data**. Never copy a sample value
into a deliverable.

| File (in this folder) | Original name | Type | What it defines |
|---|---|---|---|
| `2026-08-12_source_top50-sales-drop-spec.xlsx` | `kobiga task (2).xlsx` | Excel, 1 sheet | Task ID/Name/Objective/Scope/Action-Required header + a 14-column "Final Output" mock table with **sample** rows (SKU001 Pendant Light £800→£350 🔴 Critical, etc.). Account named: **ELECTRICALSONE**. |
| `2026-08-12_source_top50-sales-drop-workflow.pdf` | `eBay UK Top 50 Sales Drop Automation Workflow.pdf` | PDF, 6 pp / 12 §§ | Full method: §1 objective · §2 the 19 data fields to collect · §3 period-comparison maths · §4 filter logic · §5 ranking logic · §6 alert thresholds · §7 diagnosis dimensions · §8 reason matrix · §9 output shape · §10 schedule · §11 recommended workflow · §12 final goal. |

## Key facts extracted
- **Requester / PH:** Kobiga. **Account:** ELECTRICALSONE. **Channel:** eBay **UK** (£).
- **Objective:** identify the Top-50 eBay UK SKUs with the biggest sales decline, current vs previous equal
  period, and make it actionable (why it dropped + what to fix).
- **Report columns (14):** Rank · SKU · Item ID · Product · Previous Sales · Current Sales · Loss £ · Drop %
  · CTR · CVR · ROAS · Stock · Priority · Action.
- **Filter/rank:** exclude no-prior-sales & increases; rank by £ loss desc, tie-break Drop % desc; Top 50.
- **Alert bands (provisional):** 🔴 ≥50% · 🟠 30–49.99% · 🟡 15–29.99% · 🟢 <15%.
- **Schedule idea (§10):** daily data refresh · weekly report · monthly recurring-drop review.

## Integrity
Copied byte-for-byte from `C:\Users\digit\Downloads\`. No edits. Renamed to the workbench
`YYYY-MM-DD_[stage]_[task-name].[ext]` convention.
