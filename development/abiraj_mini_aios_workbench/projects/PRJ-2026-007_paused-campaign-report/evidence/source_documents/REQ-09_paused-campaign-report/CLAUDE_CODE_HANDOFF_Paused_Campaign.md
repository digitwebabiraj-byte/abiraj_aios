# Claude Code Handoff — Paused Campaign Report (PH-2026-07-UTHAR10)

This is a complete, self-contained brief for continuing the **Paused Campaign** task in Claude Code.
Give Claude Code this file plus the reference files listed in section 2, connect the Postgres
MCP server, and it will have everything it needs to reproduce, run, and extend the report.

---

## 1. What this task is (in one paragraph)

Produce a **Paused Campaign report for Utharsika**: a list of her Amazon PPC ad targets that
automation has paused and are **still paused today**, with seven columns — Campaign Name,
Ad Group Name, ASIN, SKU, Pause Reason, Campaign Pause Date, Days Paused. It is a **read-only
reporting task** (no source table is ever written to). Source of truth for the requirement is
`Utharsika_task.xlsx`, sheet `PH-2026-07-UTHAR10 - Abiraj - 1`. As of the 2026-07-13 build it
returns **33 paused ad targets (32 distinct ASINs)**.

---

## 2. Files to give Claude Code

Put these in the project so Claude Code can read them (a `/docs` folder is fine):

| File | Why it's needed |
|---|---|
| `CLAUDE_CODE_HANDOFF_Paused_Campaign.md` (this file) | The task brief + the validated SQL + rules |
| `Utharsika_task.xlsx` | Original requirement (column shape, "Days paused" rule, "consult Satheesvaran" instruction) |
| `TABLE_ppc.md` | **Critical.** Schema + join rules for `ppc`, `ppc_performance`, `ppc_etl_change_log`, `ppc_etl_automation_log` |
| `SKILL_single_table.md` | Intent routing + the mandatory "execute the SQL, never return SQL alone" rule |
| `SKILL_multi_table.md` | Join-path conventions if the report is extended across domains |
| `SKILL_ppc_stock_lookup.md` | Only if ASIN→inventory-SKU cleanup is later added |
| `2026-07-13_abiraj_REQ-pc_REQ-09-D01.md` | The formal requirement/planning record (optional but useful context) |
| `Paused_Campaign_Report_Utharsika_2026-07-13.xlsx` | The current verified output, to diff against |

**Connector:** connect the Postgres MCP server used here
(`https://mcp.vintageinterior.co.uk/mcp`, name `Postgresql`) so Claude Code can run
`execute_sql`. Everything is read-only; no write access is required or wanted.

---

## 3. How to set it up in Claude Code

1. Create a project folder and drop the files above into `/docs`.
2. Add a `CLAUDE.md` at the project root with this line so the context always loads:
   > This project builds the Paused Campaign report for Utharsika. Read `docs/CLAUDE_CODE_HANDOFF_Paused_Campaign.md` first. All database work is READ-ONLY. Always execute SQL via the Postgres MCP tool and return real rows — never SQL alone. For any unclear business rule, flag it for Satheesvaran; do not invent rules.
3. Connect the `Postgresql` MCP server (Settings → connectors / `.mcp.json`).
4. Kick off with the prompt in section 8.

---

## 4. Scope and business rules (confirmed against the database)

- **Who:** campaigns whose name contains `Utharsika` (case-insensitive). There is **no owner
  column** — the name token is the only scope key. (Held item A below.)
- **Platform:** Amazon only (`source = 1`). SB campaigns are **excluded** — Amazon maps only one
  unrepresentative ASIN to an SB campaign, which corrupts ASIN-level rows.
- **Pause source:** `public.ppc_etl_automation_log`, `action_type = 'ad_pause_logs'`,
  `status = 'success'`, `applied_by = '0'` (automation only).
- **Grain:** one row per **paused ad target** (per ASIN). This matches the workbook sample, whose
  rows each carry a single ASIN, one ad group, and a product-specific pause reason. Amazon
  automation pauses individual ads, not whole campaigns — "Campaign Name" is the parent campaign.
- **Still paused:** only targets whose current ad status in `public.ppc` is `paused`
  (`record_main_type='ad'`, `child_id = automation_log.record_id`). 8 more were paused by
  automation but have since been re-activated and are excluded. (Held item C below.)
- **Pause Reason:** taken verbatim from `ppc_etl_automation_log.reason`. Real data uses three
  rules, not just the workbook's Rule 2: **Rule 1 (ACOS based)**, **Rule 2 (zero orders + spend by
  price band)**, **Rule 3 (spend based, orders dropped in last 7 days)**.
- **Days Paused:** `CURRENT_DATE - pause_date` in calendar days, where
  `pause_date = action_datetime::date`. (This is the workbook's only stated rule.)
- **Field resolution:** campaign name and ad-group name from `public.ppc`; ASIN + SKU from
  `public.ppc_performance` (`record_type='ad'`, by `record_id`).

---

## 5. The validated SQL (produces the report)

```sql
WITH util_camp AS (
    SELECT DISTINCT p.parent_id, p.source, p.record_name AS campaign_name
    FROM public.ppc p
    WHERE p.record_main_type = 'campaign'
      AND p.record_name ILIKE '%utharsika%'
),
pauses AS (   -- latest successful automation pause per ad target
    SELECT DISTINCT ON (al.record_id, al.source)
           al.parent_id, al.child_id, al.record_id, al.source, al.reason, al.action_datetime
    FROM public.ppc_etl_automation_log al
    JOIN util_camp uc ON al.parent_id = uc.parent_id AND al.source = uc.source
    WHERE al.action_type = 'ad_pause_logs'
      AND al.status = 'success'
      AND al.applied_by = '0'
    ORDER BY al.record_id, al.source, al.action_datetime DESC
)
SELECT uc.campaign_name                          AS "Campaign Name",
       ag.record_name                            AS "Ad Group Name",
       string_agg(DISTINCT pp.ref_id, ',')       AS "ASIN",
       string_agg(DISTINCT pp.sku, ',')          AS "SKU",
       ps.reason                                 AS "Pause Reason",
       ps.action_datetime::date                  AS "Campaign Pause Date",
       (CURRENT_DATE - ps.action_datetime::date) AS "Days Paused"
FROM pauses ps
JOIN util_camp uc ON ps.parent_id = uc.parent_id AND ps.source = uc.source
JOIN public.ppc st  ON st.record_main_type='ad'
                   AND st.child_id = ps.record_id AND st.source = ps.source
                   AND st.record_status = 'paused'          -- still paused only
LEFT JOIN public.ppc ag ON ag.record_main_type='ad_group'
                   AND ag.parent_id = ps.parent_id AND ag.child_id = ps.child_id
                   AND ag.source = ps.source
LEFT JOIN public.ppc_performance pp ON pp.record_id = ps.record_id
                   AND pp.source = ps.source AND pp.record_type='ad'
GROUP BY uc.campaign_name, ag.record_name, ps.reason, ps.action_datetime
ORDER BY "Days Paused" DESC, "Campaign Name";
```

> Note: `util_camp` is intentionally NOT filtered to `source=1` / non-SB here because the pause
> log only contains Amazon ad-level events anyway; if you later widen the automation to other
> platforms, add `AND p.source=1 AND p.record_subtype <> 'SB'` to `util_camp`.

---

## 6. How to validate the output (run these every time)

1. **Count check** — expect 33 targets / 32 distinct ASINs today:
   ```sql
   -- wrap the SELECT above as sub-query q:
   SELECT COUNT(*) AS targets,
          COUNT(DISTINCT "ASIN") AS asins
   FROM ( <the query from section 5> ) q;
   ```
2. **Still-paused vs all-pauses** — expect 41 total automation pauses, 33 still paused, 8 re-activated:
   ```sql
   WITH util_camp AS (
     SELECT DISTINCT parent_id, source FROM public.ppc
     WHERE record_main_type='campaign' AND record_name ILIKE '%utharsika%'),
   pauses AS (
     SELECT DISTINCT ON (al.record_id, al.source) al.record_id, al.source
     FROM public.ppc_etl_automation_log al
     JOIN util_camp uc ON al.parent_id=uc.parent_id AND al.source=uc.source
     WHERE al.action_type='ad_pause_logs' AND al.status='success' AND al.applied_by='0'
     ORDER BY al.record_id, al.source, al.action_datetime DESC)
   SELECT COUNT(*) total,
          COUNT(*) FILTER (WHERE st.record_status='paused') still_paused,
          COUNT(*) FILTER (WHERE st.record_status<>'paused' OR st.record_status IS NULL) reactivated
   FROM pauses ps
   LEFT JOIN public.ppc st ON st.record_main_type='ad'
         AND st.child_id=ps.record_id AND st.source=ps.source;
   ```
3. **Spot check** — pick any row's `record_id`, pull its `ppc_performance` ad rows, confirm the
   ASIN/SKU match. (Counts here are internal consistency; the ultimate cross-check is the Amazon
   Ads console for the same campaigns — a mismatch there is an upstream ETL issue, not a report bug.)

---

## 7. Open items — flag to Satheesvaran, do NOT decide silently

- **A. Scope key:** is name-token matching ("Utharsika" in the campaign name) the intended
  definition, or should an owner field be added upstream?
- **B. Grain:** one row per paused ASIN (current) vs one aggregated row per campaign?
- **C. Included set:** still-paused only (current, 33) vs every pause event incl. re-activated (41)?
- **D. Platform:** Amazon only (all that the pause log contains) vs include eBay/SD/SB if pause
  automation is added there later?
- **E. Manual pauses:** automation-only (`applied_by='0'`, current) vs also include manual pauses?

The workbook's two sample rows (ASINs B0DH182H6J / B0CVKSQN9K, pause date 2026-07-06, Days Paused 0)
are **illustrative only** and must not be reproduced as the answer.

---

## 8. Ready-to-paste kickoff prompt for Claude Code

> You are continuing the **Paused Campaign report for Utharsika**. Read
> `docs/CLAUDE_CODE_HANDOFF_Paused_Campaign.md` and `docs/TABLE_ppc.md` first. Using the Postgres
> MCP connector (READ-ONLY), run the validated SQL in section 5 of the handoff, execute it, and
> return the real rows with the seven columns: Campaign Name, Ad Group Name, ASIN, SKU, Pause
> Reason, Campaign Pause Date, Days Paused. Then run the validation queries in section 6 and report
> the counts (expect 33 targets / 32 ASINs / 41 total pauses / 8 re-activated). Do not write to any
> table. For any unclear rule listed in section 7, flag it for Satheesvaran rather than deciding it.
> Finally, save the result as an .xlsx matching the current output file.

---

## 9. Deliverables already produced (for reference/diff)

- `Paused_Campaign_Report_Utharsika_2026-07-13.xlsx` — the report (33 rows) + Watchlist/Summary/Notes.
- `Utharsika_Paused_Campaigns_Dashboard.html` — interactive dashboard, same 7 columns, "33 targets · 32 ASINs".
- `2026-07-13_abiraj_REQ-pc_REQ-09-D01.md` — formal requirement/planning record.
