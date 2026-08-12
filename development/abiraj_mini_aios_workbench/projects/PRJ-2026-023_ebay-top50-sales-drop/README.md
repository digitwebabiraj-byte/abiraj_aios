# eBay UK Top 50 Sales Drop (esdt) — PRJ-2026-023

Concise landing page. Full context in `PROJECT_HOME.md`; execution rules in `CLAUDE.md`; field-by-field
source map in `SYSTEM_REFERENCE.md`; task index in `TASK_REGISTER.md`.

## What
An **eBay UK Top-50 Sales Drop** report for **Kobiga**, account **ELECTRICALSONE**. It compares the
**current period against the previous equal-length period**, finds the eBay UK SKUs whose sales fell the
most, ranks the **Top 50 by absolute £ sales loss**, and — for each — attaches the traffic (impressions /
clicks / CTR), conversion (units / CVR), advertising (PPC sales / spend / ROAS / ACOS) and stock context
needed to say **why** it dropped and **what to do**. The goal is an *actionable* report, not just numbers.

## Status
🟡 **SETUP / SCAFFOLD ONLY — 2026-08-12.** Folder structure, source import and governance docs created and
the task understood. **No build, no SQL executed, no deliverable yet.** Next step is a discovery decision
sheet + a GPT-approved implementation prompt (this workbench: Claude executes approved prompts, it does not
invent business logic). Nothing committed.

> ⚠ The source workbook (`kobiga task (2).xlsx`) is a **layout mock-up with sample rows** (SKU001, "Pendant
> Light", £800→£350, "🔴 Critical"). It defines the desired **columns, alert thresholds and Action
> vocabulary only** — never copy a sample value. Every delivered figure must trace to live data.

## Identity (provisional)
`PRJ-2026-023` / `REQ-26` / code `esdt`. **Provisional** — the source has no requirement number (REQ-25 is
taken by `slow-moving-products`). Confirm `PRJ-2026-023` / `REQ-26` / `esdt` with Abiraj (cosmetic).

## The report shape (14 columns, from the source workbook §9)
`Rank · SKU · Item ID · Product · Previous Sales · Current Sales · Loss £ · Drop % · CTR · CVR · ROAS ·
Stock · Priority · Action`

## Alert thresholds (from workflow PDF §6 — to confirm with Kobiga)
🔴 Critical Drop ≥ 50% · 🟠 High 30–49.99% · 🟡 Medium 15–29.99% · 🟢 Stable < 15%.

## Deliverable (planned)
- **REQ-26-D01** — eBay UK Top-50 Sales Drop report, one data layer rendered as **Excel** (Notes + report
  table) + **interactive HTML dashboard** (KPI tiles, searchable, sortable), built from one read-only fetch.

## Authoritative documents
- `PROJECT_HOME.md` — canonical project truth
- `SYSTEM_REFERENCE.md` — column → `schema.table.column` map and every derived-field rule
- `CLAUDE.md` — execution rules
- `TASK_REGISTER.md` — task/deliverable index

## Next step
Discovery decision sheet to **Kobiga** (see `PROJECT_HOME.md` → Open items): exact period definition &
length, whether ranking grain is SKU or Item ID, the alert thresholds and the Reason/Action vocabulary.
Then a GPT-approved implementation prompt before any build.
