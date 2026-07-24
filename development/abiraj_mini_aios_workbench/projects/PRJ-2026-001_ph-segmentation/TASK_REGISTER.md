# PH Segmentation — Task Register

Project: PRJ-2026-001_ph-segmentation

| Task ID | Requirement | Status | Task Home | Prompt Path | Evidence Path | Validation Path | Closure Path | PASS/FAIL | Next Step |
|---|---|---|---|---|---|---|---|---|---|
| REQ-05_ph-asin-segmentation | PH ASIN segmentation: (a) onboarding/preservation of the prior work; (b) the 2026-06-26 **delivery increment** — dashboard card-UI & sidebar fixes, indicator strengthening, full-report live release to `tech_team_outputs.ph_task` (row id 5), downloadable HTML delivery, and the monthly PostgreSQL routine build (paused at creation); (c) the 2026-06-30 **delivery increment** — final-June refresh (engine re-run on the complete June window, HTML rebuilt into row id 5, 7,855 → 8,149), full report validation vs source + protocol, and data-quality review (weekly-snapshot finding + 4-complete-weeks window); (d) the 2026-07-01 **delivery increment (REQ-05-D06)** — Option-A movement fix live (declines 628→574, segments unchanged), returning-aware NEW rule, Orphan-ASIN monitor (`analytics.v_orphan_asins`) + 492-row list + live flag, engine v2 (weekly `traffic_data`, scratch-validated), monthly routine v2 update, protocol v1.0 clarifications, and a dropdown/one-view UI redesign (logic unchanged); (e) the 2026-07-02 **delivery increment (REQ-05-D07)** — read-only live verification, dashboard restyle (gold/slate-teal) + card redesign, strict segment-rank movement rule (65 rows SAME→IMPROVED/DECLINED; user-decided, not Bietrick-ratified), engine v3 (strict-rank, sandbox-validated), and 24 per-PH locked views; (f) the 2026-07-03 **delivery increment (REQ-05-D08)** — Assigned-Listings confirmation (diff 0, all 24 PHs; paulr 466/464), a clarity pass (jargon removed, category filter, window dates, allocated card) **pushed LIVE 3 Jul 14:19, md5 1f657a1b** (corrected 6 Jul from "preview only"), and 24 single-PH-locked hand-over dashboards (cross-referenced from D07); (g) the 2026-07-06 **delivery increment (REQ-05-D09)** — **backup housekeeping** (first project DROP): 9 `ph_task_id5_backup_*` archived byte-verified + dropped single-transaction (≈1.8 MB), post-check 0 remain / live id-5 md5 `1f657a1b` unchanged / 3 report backups kept | DELIVERY (onboarding CLOSED-PASS; all imports PASS/GREEN as of 6 Jul; delivery ACTIVE) | handover/REQ-05_ph-asin-segmentation/TASK_HOME.md + 2026-06-26_delivery_dashboard-ui-live-report-release.md + 2026-06-30_delivery_final-june-refresh-and-data-quality-validation.md + 2026-07-01__abiraj__ph-asin__REQ-05-D06.md + 2026-07-02__abiraj__ph-asin__REQ-05-D07.md + 2026-07-03__abiraj__ph-asin__REQ-05-D08.md + 2026-07-06__abiraj__ph-asin__REQ-05-D09.md + 2026-07-10__abiraj__ph-asin__REQ-05-D10.md | prompts/implementation/REQ-05_ph-asin-segmentation/ (incl. 2026-07-01_ph_asin_monthly_routine.txt) | evidence/source_documents/REQ-05_ph-asin-segmentation/SOURCE_MANIFEST.md ; evidence/final_outputs/REQ-05_ph-asin-segmentation/ (2026-06-24 + 2026-06-26 release HTML + 2026-06-26_release_evidence_manifest.md) — 30 Jun rebuilt HTML NOT yet imported ; evidence/logs_or_screenshots/REQ-05_ph-asin-segmentation/2026-07-01_req-05-d06_source_manifest.md (D06: **all 6 artifacts imported** — UI template, unowned/orphan CSV, engine v2, routine, protocol, and the **1 Jul navy live HTML** found 6 Jul in Downloads\files (2)\, md5 9b65e429; + Option-A fix SQL bonus) ; 2026-07-02_req-05-d07_source_manifest.md (D07: knowledge file + 3 dashboard previews + 24 per-PH views + transcript + **strict-rank engine imported 6 Jul**; only the superseded 2 Jul intermediate live is absent) ; 2026-07-03_req-05-d08_source_manifest.md (D08: knowledge file imported; Assigned-Listings diff 0 all 24 PHs; 24 views + clarity pass cross-referenced from D07; clarity pass went LIVE 3 Jul) ; 2026-07-06_req-05-d09_source_manifest.md (D09: knowledge file imported; first project DROP documented; 9 id-5 backups archived local + dropped; local archives LOCAL_NOT_IMPORTED) | validation/REQ-05_ph-asin-segmentation/ (onboarding all PASS; 2026-06-26_release_validation.md AMBER; 2026-06-30_final-june-refresh_validation.md AMBER; 2026-07-01_req-05-d06_aios_validation.md PASS; 2026-07-02_req-05-d07_aios_validation.md PASS; 2026-07-03_req-05-d08_aios_validation.md PASS/GREEN; 2026-07-06_req-05-d09_aios_validation.md PASS/GREEN) | closure/REQ-05_ph-asin-segmentation/2026-06-25_final_onboarding_closure.md (onboarding scope) | PASS (onboarding) · D06 PASS · D07 PASS · D08 GREEN (clarity pass live 3 Jul) · D09 GREEN (housekeeping DROP documented) — all imports PASS/GREEN as of 6 Jul · delivery ACTIVE (v_orphan_asins backup + routine BLOCK-1 swap + engine first live run + 3 Bietrick sign-offs open) | Export v_orphan_asins.sql; swap the monthly routine's HTML BLOCK 1 to the new UI before the 3 Aug run; get Bietrick's NEW-definition decision; then update SYSTEM_REFERENCE §1/§7 to 8,149 |

> **Re-homing note (2026-06-26):** the 26 June dashboard/release work was briefly filed under a
> non-compliant dated ID `REQ-20260626-002_dashboard-ui-live-report-release`. Per the project
> ID-naming convention ("use the real requirement ID … NOT a freshly-invented dated ID") it was
> folded back into **REQ-05** — the real requirement this report delivers — as a delivery
> increment. The dated ID is retired. Ratified by Abiraj on 2026-06-26.

> **(h) 2026-07-10 delivery increment — REQ-05-D10 (corrected rebuild + full dashboard push).**
> The DB was corrected after the July report published, so the **2026-07 report was regenerated
> READ-ONLY** for the same window (6–27 Jun) with current data: **8,149 / 24 PHs → 9,947 ASINs /
> 30 PHs** (segments 42/580/173/10/626/8,516). The **+1,798 is an ownership/orphan-assignment
> restructure, not a method change** (rules unchanged). Pushed live to `tech_team_outputs.ph_task`
> via `temp_user`, backup-first + md5-verified: **leader id 5** (`1f657a1b`→`35fa7b66`) + **30 per-PH**
> rows (22 UPDATE + 8 INSERT incl. new hire **thanusha**; all `assigned_user_team='ph_priors'`);
> **deleted** departed holders Poovitha #65 + thanucha #79 → project now **31 rows**. Roster names
> from the `user`+`ph_categories`+`ph_cate_products` join (`PH_assigned_user_Standard.docx`), used
> exactly. **Repeatable toolkit + runbook saved:** `capability/2026-07-10_monthly_rebuild_toolkit/`
> + `capability/2026-07-10_monthly-rebuild-and-push-runbook.md`. Status **GREEN**.
> **OPEN (carried):** `analytics.ph_segment_report` still the old 8,149 build — dashboards are correct
> HTML snapshots but the **source table needs the engine re-run** (authorised DB session); Bietrick
> **roster sign-off** (30 PHs). This **supersedes** the earlier "update SYSTEM_REFERENCE §1/§7 to 8,149"
> next-step — current build is **9,947 / 30**.

---

## 2026-07-21 — correction: what this report actually reads, and how automatable it is

Raised by the owner, verified against the toolkit's own SQL. Two errors in the record are corrected
here; **no method, figure or deliverable changes.**

**1. The dashboards do NOT read `analytics.ph_segment_report`.** The 2026-07-10 rebuild recomputes
entirely from source: **22 queries across `public.traffic_data` (13), `public.order_transaction` (7)
and `public.ph_categories` (2)**. The engine table is never selected from. The HTML footer
nevertheless told every reader *"Source: analytics.ph_segment_report (read-only)"* — inaccurate, and
inaccurate in the direction that matters, since that table is still the old **8,149 / 24** build
while the dashboards are the corrected **9,947 / 30**.

Corrected in `capability/2026-07-10_monthly_rebuild_toolkit/tmpl/tmpl_suffix.txt` and
`tmpl_suffix_single.txt`, which generate all future dashboards. **The 55 published HTML files under
`evidence/` were deliberately left untouched** — they are the record of what was actually shown to
people, and rewriting evidence to match a later understanding would falsify it. Anyone reading an
old dashboard should use this entry, not the caption, to know where the figures came from.

**2. The stale engine table is NOT a blocker for the monthly report.** It was previously treated as
one. Because the recompute is read-only from source, the report is the same shape as every automated
job in this workbench: read source tables → build HTML → guarded publish to `ph_task`. The stale
`analytics.ph_segment_report` matters only to consumers querying **that table directly** — a real
but separate open item, unchanged by this entry.

**Remaining blockers to automating the monthly run** (this is the accurate list):
- **Bietrick's roster sign-off** on the 30-PH set — the same class of gate as ZSFO / Paused Campaign.
- **HTML BLOCK 1 still builds the old UI** — flagged for swap before 3 Aug.
- The **MCP `execute_sql` timeout above ~1,300 ASINs** shaped the per-PH/category-split method. An
  automated runner uses direct `psycopg2` with no MCP, so this limit may not apply — **worth
  re-testing before assuming the split is still necessary.**
- Automation was aimed at a **Cloud Routine on the Postgres platform**, not Windows Task Scheduler,
  and is paused mid-setup ("Run now" deliberately never clicked). That target is *more* correct than
  Task Scheduler, not less — it is where the rest of the fleet should eventually move.

Git: see the commit carrying this entry.

---

## 2026-07-24 — MEASURED CORRECTION: the live dashboards already use the COUNT rule

I read the actual published bytes of `ph_task` id 5 (the leader) on 2026-07-24 and tallied the
segment column of its embedded data block directly. The result contradicts the "rate rule / 42
Champions" figure this register and the SQL headers have been citing:

| Source | HHH | HHL | HLH | LHH | LLH | LLL | Total |
|---|--:|--:|--:|--:|--:|--:|--:|
| **LIVE published bytes (id 5, measured 2026-07-24)** | **180** | 433 | 173 | 19 | 144 | 8,998 | 9,947 |
| Documented "D10 rate rule" (cited everywhere) | 42 | 580 | 173 | 10 | 626 | 8,516 | 9,947 |
| Count rule, normal last-4-week window (today) | 205 | 382 | 136 | 24 | 159 | 9,125 | 10,031 |

The live total is 9,947 (the D10 correction window) and `HLH` matches exactly (173), so the WINDOW
is the D10 one — but the conversion split gives **HHH ≈ 180**, which is the COUNT rule, not the
rate rule's 42. Whatever the documented history says, **what is actually in front of the portfolio
holders today is the count-based conversion rule.**

**Consequence — corrects the 2026-07-21 entry above.** That entry (and my advice at the time)
warned that running the count rule would be a large, unreviewed change from live (42 → 205). That
was based on the stale "42" figure and is **wrong**: live is already ~180. So the toolkit's current
count-rule SQL (`01`/`02`/`03`) is the SAME logic already published — automating it is a refresh,
not a rule change, and needs no fresh Bietrick sign-off on the rule itself.

The only intended difference for the monthly job is the WINDOW: the live build used the one-off
correction window (rn 2..5); the monthly automation uses the normal roll-forward (rn 1..4, the last
4 complete weeks). That is a fresh-values change, not a logic change.

Method verified the same day: the whole-portfolio recompute runs in ONE direct-psycopg2 query
(10,031 ASINs, 30 PHs, ~read-only) with no timeout — so the MCP ~1,300-ASIN limit that forced the
per-PH split does NOT apply to an autonomous runner.
