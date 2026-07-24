# SMAW Table 5 Weekly Stock Check — Task Register

Project: PRJ-2026-004_smaw-table5-stock-check

One task (`REQ-06_table5-weekly-stock-check`) carries the REQ-06 stream; deliverables tracked per
row below (same pattern as REQ-05 D01–D09 in PRJ-2026-001, REQ-04 in PRJ-2026-003).

| Task ID / Deliverable | Requirement | Status | Task Home / Requirement Doc | Evidence Path | Validation Path | Closure Path | PASS/FAIL | Next Step |
|---|---|---|---|---|---|---|---|---|
| REQ-06_table5-weekly-stock-check · **D01** | REQ-06-D01 — Phase-01 Reporting & Data Model: discovery-first duplicate-risk scan of existing stock objects, map every Table 5 column to a real source (VERIFIED/PARTIAL/UNPROVEN), and — if duplicate-risk clears — build the read-only reporting view `v_table5_weekly_stock_check` + evidence note | **DELIVERED — pending review** | requirement doc: DigitWeb_Works_Abiraj/08_07_2026/2026-07-08_abiraj_REQ-smaw_REQ-06-D01.md | sql/REQ-06_table5-weekly-stock-check/generate_dataset.sql · evidence/source_documents/REQ-06_table5-weekly-stock-check/HANDOFF.md | validation/REQ-06_table5-weekly-stock-check/ (pending) | closure/REQ-06_table5-weekly-stock-check/ (pending) | **PENDING** | Reviewer sign-off (Tamil Selvan · Sajeesan) |
| REQ-06_table5-weekly-stock-check · **D02** | REQ-06-D02 — Phase-02 Reporting & Presentation: render the governed Table 5 output as a Portfolio-Holder-facing interactive HTML dashboard (colour-banded, filterable, CSV/PDF export), reconcile to live inventory truth, surface the legacy→canonical SKU risk, and scope the full-portfolio (all-ASIN) coverage expansion | **DELIVERED — pending review** | requirement doc: DigitWeb_Works_Abiraj/09_07_2026/2026-07-09_abiraj_REQ-smaw_REQ-06-D02.md | evidence/final_outputs/REQ-06_table5-weekly-stock-check/Table5_Weekly_Stock_Check_Thuwaraga.html · build_html.py · dataset.py · build_report.py | validation/REQ-06_table5-weekly-stock-check/ (pending) | closure/REQ-06_table5-weekly-stock-check/ (pending) | **PENDING** | (1) Thuwaraga's full-portfolio coverage decision · (2) reviewer sign-off |
| REQ-06_table5-weekly-stock-check · **D03** | REQ-06-D03 — Phase-03 Full-Portfolio Coverage + Publish: universe = every Amazon-UK ASIN with a live FBM listing OR a 90-day sale (listings ∪ ph_segment ∪ sales) → strict superset of the D01/D02 sellers, plus all idle-stock ASINs. Stock for all; velocity/days only where sold; no-sales-with-stock flagged idle; 0-stock split into Stockout vs Inactive. Amazon-FBM display corrected to read listing_data.quantity incl. wrong_sku (display-only). **Published to the ops registry.** | **DELIVERED & LIVE** | requirement/handoff: evidence/source_documents/REQ-06_table5-weekly-stock-check/RUN_IN_CLAUDE_CODE.md · sql/REQ-06_table5-weekly-stock-check/generate_dataset_all_asins.sql (fbm_all fix) | evidence/final_outputs/REQ-06_table5-weekly-stock-check/Table5_Weekly_Stock_Check_Thuwaraga_ALL.html · build_all_html.py · data_all.json · …_ALL.xlsx · **published: `tech_team_outputs.ph_task` id 122 (V1=733) · id 137 (V2=756, FBM-fixed), released** | **756 rows** · strict superset of the 240 sellers (**0 dropped**) · spot-checks LDSSTRE274=989, LDMA60E274=0, LDMA60E274WW=3,233 · breakdown 234 healthy / 9 stockout / 394 idle / 119 inactive · FBM fix verified (B09JZ61NJM 0→39) | closure/REQ-06_table5-weekly-stock-check/ (pending) | **PASS — built, reconciled 0-mismatch, published** | Reviewer sign-off (Tamil Selvan · Sajeesan) + Thuwaraga confirmation |

## Open items (carried in PROJECT_HOME → Known Risks)

1. **Full-portfolio coverage decision** — RESOLVED in D03: universe = listings ∪ `analytics.ph_segment`
   ∪ 90-day sales (all-ASIN, includes no-sales-with-stock). 733 ASINs delivered. Remaining: Thuwaraga
   sign-off + confirm the Stockout/Inactive labelling split.
2. **Legacy→canonical SKU mapping source** — not in `order_management_copy`; candidates unverified.
3. **4 UNPROVEN D01 fields** — FBA on-hand · container ETA · W1/W2/W3 · stock-checked date.
4. **Postgresql MCP reconnect** required before any live re-pull.

---

## 2026-07-24 — AUTOMATED (REQ-06 automation complete)

`SMAW_Weekly_StockCheck` registered on the permanent path — **Mondays 10:00**, first run
**2026-07-27**. `automation/smaw_weekly_run.py` + `run_smaw_weekly.bat` + `smaw_alert.ps1` +
`AUTOMATION_README.md`; task XML backed up in `05_documentation/capability/scheduled_tasks/`.

SQL already anchors on CURRENT_DATE (run-date safe); its 13 columns map 1:1 to the dashboard rows;
reuses the signed-off `build_all_html.py` (env-var paths). Weekly REPLACE in place (id 137, task_id
`SMAW_thuwaraga_table5_all_asins-V2`), backup-first, md5-verified.

**Two issues found + handled 2026-07-24:** (1) `temp_user` has no `supplier` schema access, but the
3 incoming columns were all-NULL in the live V2 (0/756), so the runner stubs the supplier CTE — zero
data loss, fails closed if the CTE anchor moves. (2) `build_all_html.py` wrote a hardcoded name, not
the env-overridable path — fixed `out = FILE_PATH`.

**The inventory feed blocker is CLEARED:** the note's "frozen at 2026-05-04" was stale — the feed is
live again (updated 2026-07-23). The live V2 (id 137) was built on the frozen feed, so the **first
automated run refreshes 2-month-stale stock to current**: dry-run 776 rows / 121 critical / 245
healthy (was 756 frozen). Stock numbers move on first publish — expected, the whole point.

Proven 2026-07-24 (dry-run + Task-Scheduler temp run `LastTaskResult=0`). Nothing published — first
real publish is the scheduled 2026-07-27 run. Owner authorised proceeding past the pending reviewer
sign-off. **PSLD (per-PH stock dashboards, dev Sarujanan) is a SEPARATE project — not in scope here.**
