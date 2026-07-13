# SYSTEM_REFERENCE — Paused Campaign Report (Utharsika)

Complete functional detail for the Paused Campaign report. Derived from the canonical sources
(`Utharsika_task.xlsx` / `PH-2026-07-UTHAR10` / `CLAUDE_CODE_HANDOFF_Paused_Campaign.md`) and
verified against the live `order_management_copy` DB on 2026-07-13. This is the single reference a
leader or new engineer reads to understand what the system does.

## 1. What the report is
A list of **Utharsika's Amazon PPC ad targets** that **automation paused** and that are **still
paused today**, one row per paused ad target (per ASIN), with seven columns:
**Campaign Name · Ad Group Name · ASIN · SKU · Pause Reason · Campaign Pause Date · Days Paused.**
It is **read-only** — no source table is written. Amazon automation pauses individual ads, not whole
campaigns; "Campaign Name" is the parent campaign the ad sits under.

## 2. Population (scope)
- Campaigns whose **name contains `Utharsika`** (case-insensitive, `ILIKE '%utharsika%'`). There is
  **no owner column** in `ppc` — the name token is the only scope key. *(Open item A.)*
- **Amazon only** (`source = 1`). **SB campaigns are excluded** — Amazon maps only one unrepresentative
  ASIN to an SB campaign, which corrupts ASIN-level rows. In practice the pause log only holds
  Amazon ad-level events, so no explicit SB filter is needed today (documented in the SQL note).

## 3. The pause source
- Table `public.ppc_etl_automation_log`, filtered to:
  `action_type = 'ad_pause_logs'` · `status = 'success'` · `applied_by = '0'` (automation only).
- **Latest pause per ad target:** `DISTINCT ON (record_id, source) … ORDER BY action_datetime DESC`.
- **Still paused:** kept only if the ad's **current** status in `public.ppc` is `paused`
  (`record_main_type='ad'`, `child_id = automation_log.record_id`). Ads re-activated after the pause
  are excluded. *(Open item C — 8 such were excluded on 2026-07-13.)*

## 4. Locked business rules
| Rule | Definition |
|---|---|
| **Scope key** | campaign `record_name ILIKE '%utharsika%'` (no owner column exists). |
| **Platform** | Amazon (`source = 1`); SB excluded (unrepresentative ASIN mapping). |
| **Pause source** | `ppc_etl_automation_log`, `action_type='ad_pause_logs'`, `status='success'`, `applied_by='0'`. |
| **Still paused** | current `ppc.record_status = 'paused'` at ad grain (`child_id = record_id`). |
| **Pause Reason** | taken **verbatim** from `ppc_etl_automation_log.reason` — never paraphrased or invented. |
| **Campaign Pause Date** | `action_datetime::date` of the latest pause. |
| **Days Paused** | `CURRENT_DATE − pause_date` in calendar days (the workbook's only stated rule). |
| **Field resolution** | campaign + ad-group name from `public.ppc`; ASIN (`ref_id`) + SKU from `public.ppc_performance` (`record_type='ad'`, by `record_id`). |

## 5. Pause-reason rules (real data uses three, not just the workbook's Rule 2)
The `reason` text is emitted by the automation engine. Three rule families appear:
- **Rule 1 — ACOS based:** 30-day ACOS ≥ 50% (or last-7-day ACOS crosses the threshold).
- **Rule 2 — zero orders + spend by price band:** 0 orders in window with spend above a
  price-band threshold (Condition 1 ≤ £15 · Condition 2 £15–25 · Condition 3 £25–35 …).
- **Rule 3 — spend based, orders dropped in last 7 days:** last-7-day spend above a price-band
  threshold with last-30-day orders > 0 but last-7-day orders = 0.
One target can carry a **combined** reason (e.g. `Rule 1 … | Rule 3 …`) — kept verbatim.

## 6. Data model (read-only source objects)
| Table | Use | Key filters / columns |
|---|---|---|
| `public.ppc` (campaign) | scope + campaign name | `record_main_type='campaign'`, `record_name ILIKE '%utharsika%'`, `parent_id`, `source` |
| `public.ppc` (ad) | still-paused test | `record_main_type='ad'`, `child_id = log.record_id`, `record_status='paused'` |
| `public.ppc` (ad_group) | ad-group name | `record_main_type='ad_group'`, `parent_id`, `child_id`, `source` |
| `public.ppc_etl_automation_log` | pause events | `action_type='ad_pause_logs'`, `status='success'`, `applied_by='0'`, `reason`, `action_datetime`, `record_id`, `parent_id`, `child_id`, `source` |
| `public.ppc_performance` | ASIN + SKU | `record_type='ad'`, `record_id`, `ref_id` (ASIN), `sku`, `source` |

Join keys: automation log `parent_id/source` → campaign `parent_id/source`; log `record_id` → ad
`child_id` (still-paused) and → `ppc_performance.record_id` (ASIN/SKU); log `parent_id + child_id` →
ad_group `parent_id + child_id`.

## 7. Report columns & deliverables
`Campaign Name · Ad Group Name · ASIN · SKU · Pause Reason · Campaign Pause Date · Days Paused` — the
seven columns the workbook specifies, in that order. ASIN and SKU are `string_agg(DISTINCT …)` so a
target that resolves to multiple performance rows shows a comma-joined value rather than duplicating.

**Published dashboard:** `Utharsika_Paused_Campaigns_Report.html` (hand-finished, owner-supplied) is
the **canonical** presentation — full-bleed layout, animated summary, rule tabs, search/sort, and a
per-row structured breakdown (rule badge · plain-English summary · metric chips). Its embedded
`<script id="payload">` is the spine; data parity with `data.json` is verified exact (33 rows / 32
ASINs / every row tuple matches).

**Verbatim vs presented reason (approved presentation decision):** the **verbatim** `reason` string
is preserved in `data.json` and the `.xlsx` (system of record). The published dashboard shows a
**cleaned presentation** of the same reason — it drops the leading `Date Range for performance date:
YYYY-MM-DD - YYYY-MM-DD,` clause, normalises `≥`→`>=`, and derives `summary` + metric `chips` — for
readability. No figure is altered; the trimmed clause is the performance window, which is already
implied by the pause date. If a fully-verbatim on-screen reason is later required, source it from
`data.json`.

## 8. Reconciliation (2026-07-13)
- Report: **33** targets · **32** distinct ASINs (B0DXQ84YT7 under two ad groups → 2 rows, 1 ASIN).
- Still-paused vs all-pauses: **41** total automation pauses → **33** still paused · **8** re-activated.
- Two pause waves: **2026-06-10** (18 targets @ 33 days) · **2026-06-17** (15 targets @ 26 days).
- Independent 4-check pack (`PAUSED_CAMPAIGN_VERIFICATION_PACK.md`) = **4/4 PASS**.

## 9. Regeneration / re-run
1. Run `sql/REQ-09_.../generate_report.sql` (the `json_agg` form) via the Postgres MCP (read-only);
   save the result as `data.json`. Days Paused recomputes from `CURRENT_DATE` automatically.
2. `python build_report.py` → `Paused_Campaign_Report_Utharsika.xlsx`.
3. Refresh the **published** dashboard `Utharsika_Paused_Campaigns_Report.html`: replace its embedded
   `<script id="payload">` array with the new rows and update the `RUN` date constant. (Optional:
   `python build_html.py` re-renders a plain audit data view `…_dataview.html` — not the published file.)
4. Run `sql/REQ-09_.../validation_checks.sql`; require the count check and still-paused check to agree
   with the rendered outputs (4/4) before release.

## 10. Known limits
- Business edge cases (scope key, grain, included set, platform, manual pauses — items A–E) **await
  Satheesvaran sign-off**.
- `ppc.record_status` is **current** (no history) — "still paused" and "Days Paused" are as-of-today.
- The ultimate external cross-check is the **Amazon Ads console** for the same campaigns; a mismatch
  there is an upstream ETL issue, not a report bug.
- Scheduling not wired — the query uses `CURRENT_DATE`, so it is already run-date safe, but no
  automated recurring trigger exists yet (would be REQ-09-D02).
