# TASK REGISTER — PRJ-2026-021 Channel Opportunity

Canonical index of tasks/deliverables within this project. Detail lives in `PROJECT_HOME.md` /
`SYSTEM_REFERENCE.md`.

| Task | Deliverable | Description | Status |
|---|---|---|---|
| REQ-24 | **REQ-24-D01** | **Channel Opportunity** report for Mahima — per base SKU, sales laid side by side across **Shopify · Amazon · eBay**, with an **Opportunity** class (Shopify winner / Marketplace winner / Missing channel) and a recommended **Action** (Improve Amazon/eBay listing / Add Shopify promotion / Create eBay listing …). Excel workbook (Notes + cross-channel table), built from one read-only query. | 🟢 **BUILT & DELIVERED (2026-08-05) — pending Mahima sign-off.** Germany, UNITS metric, rolling 90 days (data through 2026-08-04), **RAW `mcp.ledsone` DB** (`order_management`), clean-SKU = strip `-IDE`. **283 opportunity rows** (270 Missing channel · 10 Marketplace winner · 3 Shopify winner). Reconciled against raw DB on 5 SKUs incl. zero/absent channels (raw is source of record; agrees with warehouse mirror within ±2 units). Opportunity/Action use documented DEFAULT rules (Notes tab) awaiting Mahima. Not published to ph_task, not committed. |

## Source
`evidence/source_documents/REQ-24_channel-opportunity/mahima task.xlsx`
(SHA-256 `d7ff471cc2e10f236a8b8ef77e7504fa17db893dc878367e9c107d83afa2f2e0`, imported 2026-08-05).
The workbook is a **layout mock-up with 3 sample rows** — it defines the columns, the Opportunity classes
and the Action vocabulary, not data.

## Build (2026-08-05)
- Builder: `sql/REQ-24_channel-opportunity/build_chop_d01.py` (one generator module) reads a governed JSON
  snapshot (`chop_payload_2026-08-05.json`, 2,436 SKUs) of per-base-SKU units-by-channel pulled READ-ONLY
  from the **RAW `mcp.ledsone` `order_management`** schema (Germany=market_place '10'; channels via
  `source.source_name`; clean-SKU = strip `-IDE`), classifies Opportunity/Action, renders the Excel.
  Knowledge/query patterns from the AIOS KB (`docs.ledsone.co.uk`, `text-to-sql-multi`).
- Outputs: `evidence/final_outputs/REQ-24_.../REQ-24-D01_channel_opportunity.xlsx` **and** a self-contained
  interactive **HTML dashboard** (`…_channel_opportunity.html`) — full-width light theme, KPI cards, filter
  by Opportunity class, search, sortable columns, inline channel bars. No external resources.
- Output: `evidence/final_outputs/REQ-24_channel-opportunity/REQ-24-D01_channel_opportunity.xlsx`
  (Notes & Method + Channel Opportunity, 285 rows). Reconciliation note in `evidence/logs_or_screenshots/`.

## Rule status — DEFAULTS LOCKED ON OWNER AUTHORITY (Abiraj, 2026-08-05)
Mahima was unavailable; the owner authorised proceeding with the documented defaults. Locked:
market = Germany · metric = UNITS · window = rolling 90d · FLOOR = 10 · Shopify-winner ≥50% ·
Marketplace-winner ≥60% & Shopify ≤20% · combos kept in · columns = the 6 mock-up columns + Total Units.
Decision sheet retained at `prompts/discovery/REQ-24_.../DECISION_SHEET_for_Mahima.md` — Mahima may still
review/adjust later; the report re-runs on any change. These are now APPROVED defaults, not invented.

## Publish record — ph_task (PUBLISHED 2026-08-05 on owner instruction)
✅ Inserted into `tech_team_outputs.ph_task` (host `149.28.134.54:5435`, DB `order_management_copy`, temp_user)
via guarded `automation/publish_chop_ph_task.py` (dry-run preview → `--commit` INSERT … RETURNING + md5 read-back).

| id | project_code | task_id | assigned_user | assigned_user_team | team | version | html md5 |
|---|---|---|---|---|---|---|---|
| **699** | chop | chop-2026-08-05-DE-Mahi | **Mahi** (staff.users id 40) | **german_priors** | Development | 1 (released) | `367ca934…` (DB read-back MATCH) |

HTML = the full-screen interactive dashboard (50,222 chars). Conventions mirror fmp id 673. ⚠ Dashboard is
JS-rendered — renders on the portal like fmp; add a static fallback only if Mahi's tile shows blank.

## Still open (do NOT block the delivered build)
- Automation — NOT scheduled (default off). Weekly refresh available on request (fmp pattern).
- Confirm provisional identity `PRJ-2026-021` / `REQ-24` / code `chop` (cosmetic).
- Optional later reviewer gates: Sajeesan (technical), Tamil Selvan (queryability), Mahima (business).

## Automation
Not automated (not built). A weekly refresh would follow the fmp pattern if requested after sign-off.

## Publish record — ph_task
None yet.

## Sign-off
None yet.
