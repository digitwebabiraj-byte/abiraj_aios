# SKILL FILE — DAILY KNOWLEDGE EXTRACTION
# DIGITWEB LK LTD · Daily Skill Increment System · v3.0

---

## ── METADATA BLOCK ──────────────────────────────────────────────────────────

| Field | Value |
| :---- | :---- |
| **date** | 2026-07-02 |
| **developer** | abiraj |
| **project** | PH ASIN Segmentation — Growth Protection Engine (GPE) |
| **project\_code** | ph-asin |
| **phase** | Phase-07 — Live Dashboard Restyle, Card Redesign, Strict-Rank Movement Rule & Engine Alignment |
| **requirement\_id** | REQ-05 |
| **deliverable\_id** | REQ-05-D07 |
| **status** | **COMPLETE (for today's increment) · automation still PENDING (Windows feature) · monthly-routine UI swap still OPEN.** Today delivered, in order: (1) a **full read-only verification** of the live 2026-07 report (segments, CVR, movement, source reconciliation all re-derived, 0 mismatches) confirming nothing was wrong before any change; (2) a **live dashboard restyle** — a gold header + greeting bar over a slate/teal body, a stronger escalation banner, and amber highlighting of NEEDS_REVIEW rows — scoped tightly (gold on the header/greeting only, after an initial too-broad pass was corrected) and pushed live via the byte-verified method with the ~840 KB data payload never moving; (3) a **card redesign** — per-card icons + colour-coding, Champions=green / Dead Horses=red emphasised, with a ribbon-medal + warning-triangle icon set the user chose — pushed live and verified byte-identical to the approved preview; (4) a **new movement rule** (strict segment rank HHH=1…LLL=6, replacing the equal-weight h-count where HHL/HLH/LHH were tied) — applied to the **report table** (65 rows moved SAME→IMPROVED/DECLINED, verified 8,149/8,149) **and** to the **baked dashboard data** (65 mov cells corrected, byte-verified) after the user caught that the dashboard held stale movement values; (5) the **v2 engine updated to the strict-rank rule** and **sandbox-validated** (reproduced 8,149 rows, 0 movement mismatches, never touched live); and (6) a **plain-language walkthrough + source verification** of the NEW-movement mechanic against `traffic_data` for real ASINs (Saranya, paulr), confirming counts are real and surfacing that NEW differences reduce to the still-pending returning-aware sign-off. All live pushes were backup-first, byte/md5-verified, and reversible; nothing dropped. |
| **evidence\_location** | **Live MCP calls this session (read + write, authorised — D-0):** read-only verification SELECTs (segment re-derivation 7,145/7,145, CVR 8,149/8,149, movement 7,958/7,958, source reconciliation 8,146/8,149 exact); backups `tech_team_outputs.ph_task_id5_backup_20260702_css`, `ph_task_id5_backup_20260702_cards`, `ph_task_id5_backup_20260702_movdata` (all 1 row, md5-matched pre-change), `analytics.ph_segment_report_backup_20260702_movrule` (8,149 rows); three live dashboard pushes via base64-chunk → temp table → server-side md5-verify → guarded replace() (CSS md5 `740b8eeb…`, cards md5 `e2dfbfd9…`) → Playwright render-verify; strict-rank `UPDATE` on `ph_segment_report` (65 rows) + 65-row baked-data correction in id 5 (applied in verified multi-line batches after an over-long single-statement failed atomically with no change); sandbox validation of the strict-rank engine in schema `sandbox.*` (8,149 rows reproduced, 0 movement mismatches), all sandbox tables dropped after. **Artifacts (handed to Abiraj):** `preview_v2.html`, `preview_v3.html` (approved dashboard previews), `ph_segment_engine.sql` (v3 strict-rank, sandbox-validated) + `ph_segment_engine_prev-equalweight.sql.bak`, live copies `live_v4_movrule.html` (current live state). Live output: `tech_team_outputs.ph_task` id 5 = 888,511 bytes (restyle + cards + corrected movement). No Git SHA — files + live DB rows. |
| **blos\_keys\_used** | NONE — project does not consume BLOS rule/threshold keys. |
| **hardcoded\_thresholds** | Classification logic (Method-A CVR, benchmark top-30/top-10/manual-flag, Option-B letter map, FBM/UK/Amazon scope, escalation PH >30% LLL / >5 declined) **unchanged**. **NEW this session:** (a) **Strict segment rank** for movement — HHH=1, HHL=2, HLH=3, LHH=4, LLH=5, LLL=6 (lower = better), replacing the equal-weight h-count (HHH=3, HHL/HLH/LHH=2, LLH=1, LLL=0). Movement = current rank vs previous rank: `<` IMPROVED, `>` DECLINED, `=` SAME, no previous = NEW. This makes HHL/HLH/LHH **distinct** ranks (previously tied → SAME), so 65 lateral moves that were SAME are now correctly IMPROVED/DECLINED. **Decided by the user (2026-07-02)** — a directed rule change, not a Bietrick protocol sign-off; applied live to the 2026-07 report and dashboard, and baked into the v2 engine for 2026-08. (b) **Window basis confirmed** = last 4 COMPLETE weeks (current) vs previous 4 (Saturday-ending) — the live 4-week window is authoritative over "calendar month" (user confirmed). **Carried unchanged:** returning-aware NEW rule (in engine, still pending Bietrick sign-off vs the live simple rule); benchmark top-30/10/manual; conv edges; Option B map HLL→HLH, LHL→HHL; scope which_channel=1/UK/FBM; engine abort guards; schedule cron `0 9 3 * *` (still not created — Windows feature pending). |
| **three\_am\_standard** | PASS |
| **llm\_queryable** | YES |
| **company\_knowledge\_candidate** | YES |
| **domain** | DATABASE \| SEGMENTATION \| REPORTING \| AMAZON-LISTINGS \| DATA-QUALITY \| VALIDATION \| UI/UX \| AUTOMATION-SCHEDULING |
| **daily\_benefit\_delivered** | (1) **A clearer, more usable live dashboard** — a gold header + greeting bar over a slate/teal body, plus redesigned colour-coded cards (Champions green / Dead Horses red with icons), delivered live and byte-verified against the approved preview. (2) **Critical issues now stand out** — the escalation banner is bolder (a portfolio in trouble is unmissable) and NEEDS_REVIEW data-quality rows are highlighted amber so questionable numbers are easy to spot among hundreds of rows. (3) **More accurate movement** — the strict-rank rule now correctly flags 65 lateral HHL/HLH/LHH moves that were previously hidden as "SAME", applied to both the report and the dashboard, with the engine updated so August stays correct. (4) **Confidence the numbers are real** — a full read-only verification proved every calculation re-derives from source (0 mismatches), and real NEW ASINs were traced to `traffic_data` to confirm counts are genuine. All changes were backup-first, byte/md5-verified, and fully reversible; nothing dropped, no data lost. |

## File path:
# 2026-07-02__abiraj__ph-asin__REQ-05-D07.md
# DigitWeb_Works_Abiraj/02_07_2026/

---

## SECTION 1 · SYSTEM STATE

- **At start of today:** D06 (1 July) had delivered live the Bietrick-approved Option-A movement fix, the Orphan-ASIN monitor + flag + 492-row CSV, the returning-aware v2 engine (validated in scratch, deployed to file but not run live), the new per-PH dropdown dashboard (19 columns, navy theme), and the Protocol v1.0 Clarifications. Two things were known-open going in: the monthly routine still built the OLD tabs layout (would revert the UI on the 3 Aug auto-run), and three items awaited Bietrick sign-off (NEW definition, edge-case protocol, 492 orphan assignments).
- **Trigger for today's work:** the user asked, in sequence, to (a) "final verify everything perfect", then (b) restyle the live dashboard with more attractive colours + subtle animations, then (c) improve the summary cards, then (d) after examining a single ASIN's movement and finding the dashboard showing "SAME" where the rule said "DECLINED", to adopt and apply a **strict segment-rank** movement rule, and finally (e) to bake that rule into the engine so August is correct.
- **What was working:** the live 2026-07 report and dashboard were correct and reconciled going into today; the verification pass confirmed this before any change. The work items were presentation quality, a movement-rule refinement the user decided on, and forward-engine alignment.
- **Starting point today:** verify the live state read-only; then make each visual/logic change as a local preview first, get explicit approval, and push live only via the established backup-first + byte-verified method; keep every change reversible.

> **In plain terms:** Today I first double-checked that the live report was fully correct (it was — every number re-derives from the raw data with zero errors). Then I made the dashboard look much better — a premium black-and-gold header with a slate/teal body, redesigned cards with icons where "Champions" is green and "Dead Horses" is red, a bolder danger banner, and highlighting for rows whose numbers look impossible so nobody trusts a bad figure. I got the colours and icons exactly how the user wanted through a few rounds of previews. Then the user studied how one product's movement is decided and spotted that the old rule treated three different "2-strong" segments as equal, hiding real up/down moves as "no change"; they chose a stricter 1-to-6 ranking, and I applied it to the data, then to the dashboard (the user caught that the dashboard still showed the old values — a real miss on my part, which I fixed), and finally baked the same rule into the engine and tested it safely so next month stays correct. Everything was backed up first and checked byte-for-byte before going live.

---

## SECTION 2 · WHAT CHANGED TODAY

A **full verification, a live restyle + card redesign, a movement-rule change applied to both the data and the dashboard, and an engine update — all backup-first, byte/md5-verified, reversible, and nothing dropped.**

- **Change 1 — Full read-only verification of the live 2026-07 report (all PASS).** Re-derived every stored value from source, changing nothing: structure (8,149 rows / 8,134 ASINs / period 2026-07; 0 null asin/owner/account/segment/movement; 0 bad codes; 0 dup asin+account; 1,004 needs_manual); **segment re-derivation 7,145/7,145 scored rows match**; **CVR 8,149/8,149 correct**; **movement 7,958/7,958 rows-with-prev correct** by the then-current h-count rule; **source reconciliation 8,146/8,149 exact** on impr/clk/conv (the 3 differ by ±1 conversion only — benign late Amazon attribution). Benchmark uniform within each PH+category; needs_manual consistent; escalations recompute 24/22; orphans 15,914/492; 0 orphan∩owned overlap; `ph_task` 50 rows intact.
- **Change 2 — Live dashboard restyle, scope-corrected mid-task.** Built several theme previews locally (full navy+animation, slate/teal, black&gold). The user flagged the first full black-&-gold as "too much gold everywhere" and clarified the scope: **gold on the header + greeting bar only, slate/teal for the rest**. Rebuilt to that scope (verified cards/chips/tables/meta byte-identical to the prior live), then toned the gold further when the dropdown option list rendered gold-on-dark and hurt readability — made the dropdown white/dark-text, gold kept only as the title + accent line.
- **Change 3 — Two action-focused highlights added (display-only).** (a) **Escalation banner** strengthened — bolder text, larger %, a solid 4px red left-bar, calm pulse — so a portfolio in trouble is unmissable. (b) **NEEDS_REVIEW rows** in the ASIN table tinted amber with a left marker (verified 114 such rows for utharsika), so data-quality flags (conv>clicks, CVR>100%, conv-with-zero-clicks) stand out among hundreds of rows. Implemented via one small JS hook that reads the existing `statusOf()` result to set a CSS class — no logic changed.
- **Change 4 — Restyle (v2) pushed live, byte-verified.** Backup `ph_task_id5_backup_20260702_css` (md5 `9b65e429…`); new `<style>` block staged via base64 chunks, **server-side md5-verified `740b8eeb…` before any write**, then a targeted `replace()` of the style block + the one JS hook (the ~840 KB data never moved). Live row confirmed byte-identical to the approved `preview_v2.html` (md5 `c1a3555c…`, 884,616 bytes); 0 placeholder leftovers; sample ASIN + SEGCOL map intact; render-verified.
- **Change 5 — Card redesign (v3) pushed live, byte-verified.** User chose "add icons + colour-code each card" and "make Champions=green / Dead Horses=red stand out." Built per-card colour classes (teal list / blue tag / purple box / slate grid / green Champions / red Dead Horses) with inline-SVG icon badges, bigger bold numbers, and tinted panels for the two headline cards. Icons refined per user feedback (trophy/alert → **ribbon-medal** for Champions + a **bolder warning-triangle** for Dead Horses — geometry verified by rasterising the SVG and inspecting it). Pushed live: backup `ph_task_id5_backup_20260702_cards`; new style staged + server-side md5-verified `e2dfbfd9…`; `replace()` of style block + the one card-map JS line (adds index class + icon slot). Live md5 `6d5a45e2…`, 888,251 bytes, byte-identical to approved `preview_v3.html`; render-verified (6 cards, correct values, Champions green + Dead Horses red).
- **Change 6 — Strict-rank movement rule adopted (user decision) and applied to the report table.** User compared HHL vs HLH/LHH and chose the strict 1–6 rank (HHL=2, HLH=3, LHH=4) over the equal-weight tie. Impact measured read-only first: **65 rows change, all one-way** (SAME → IMPROVED 23 / DECLINED 42), NEW unchanged. Backup `analytics.ph_segment_report_backup_20260702_movrule` (8,149 rows, old dist SAME 6777/IMPR 607/DECL 574/NEW 191). Applied the `UPDATE` (movement only) → new dist **SAME 6712 / IMPROVED 630 / DECLINED 616 / NEW 191**; re-derivation **8,149/8,149 match, 0 mismatches**; escalations stable (22 PHs, none newly triggered).
- **Change 7 — Dashboard baked-data corrected (user caught a real miss).** After Change 6, the user found the live dashboard still showing "SAME" for `B0C5TJDGHJ` where the table now said "DECLINED." Root cause: the dashboard's movement values are **baked into the HTML**, not read live — I had wrongly stated no push was needed. Corrected: backup `ph_task_id5_backup_20260702_movdata`; verified locally that **exactly the 65 mov cells** differed (only field index 3 changed, incl. the one duplicate-ASIN conflict `preethi/B0BW9LNTTD` disambiguated by account/impressions); applied 65 targeted `replace()`s in verified multi-line batches (an initial single 8 KB statement failed atomically with a syntax error and changed nothing). Live md5 `b7ae5e46…`, 888,511 bytes, byte-identical to target; dashboard now shows `B0C5TJDGHJ` = HLH / DECLINED.
- **Change 8 — v2 engine updated to strict-rank and sandbox-validated.** Edited `ph_segment_engine.sql` in 3 places (current-window rank, previous-window rank, and the movement comparison — flipped so lower rank = better) + header docs. Validated in a **sandbox schema only** (never against live): reproduced **8,149 rows**, strict-rank movement **0 mismatches** across 8,028 scored rows. Sandbox output distribution (returning-aware NEW still on): IMPROVED 660 / DECLINED 610 / SAME 6758 / NEW 121. Sandbox tables dropped after. Saved as the new `ph_segment_engine.sql` (+ `ph_segment_engine_prev-equalweight.sql.bak`).
- **Change 9 — NEW-movement mechanic explained and source-verified for the user.** Walked one ASIN end-to-end (benchmark → current/previous segment → rank compare → movement). Confirmed the 6 segments + 4 movement types are both in the requirement doc (Sections 2.1, 2.3). Traced real NEW ASINs to `traffic_data`: Saranya's 8 and paulr's 8 are all genuine (0 UK rows in the previous window) — an earlier "these look mislabelled" concern was **my error** (I compared across all marketplaces; the report is UK-only). Surfaced that the NEW count difference (live 191 vs engine 121) reduces entirely to the **returning-aware definition** — the open Bietrick sign-off.

### Deliverables (today)
- Live restyled + card-redesigned + movement-corrected dashboard (`ph_task` id 5, 888,511 bytes) — `live_v4_movrule.html` (final live copy).
- `preview_v2.html` (approved restyle preview) · `preview_v3.html` (approved card preview).
- `ph_segment_engine.sql` (v3, strict-rank, sandbox-validated) + `ph_segment_engine_prev-equalweight.sql.bak`.
- `analytics.ph_segment_report` (8,149 rows, strict-rank movement live).

Evidence: live MCP read-only verification + 3× byte-verified dashboard pushes (backup → base64 → server-side md5 → guarded replace → render-verify) + strict-rank UPDATE + 65-row baked-data correction + sandbox engine validation. No credentials. No Git SHA.

---

## SECTION 3 · POSTGRESQL / MCP / DATABASE FINDING

> **PostgreSQL via MCP — read + write (authorised, D-0).** MCP is the only DB access path. The `temp_user.py` script offered mid-session (with a hardcoded DB password) was **declined** — all work went through the MCP connector; no credentials handled.

**Tables/objects touched today:** `public.traffic_data` (read — verification + NEW tracing), `public.order_transaction` (read), `analytics.ph_segment_report` (read verification + write: strict-rank movement update + backup), `analytics.v_orphan_asins` (read), `tech_team_outputs.ph_task` (read + write: id 5 restyle, cards, movement-data correction + 3 backups), `sandbox.*` (created, validated, dropped).

### Finding A — the live report was already fully correct (proven, not assumed)
Every stored value re-derives from source with 0 mismatches: segment 7,145/7,145, CVR 8,149/8,149, movement 7,958/7,958, source reconciliation 8,146/8,149 exact (3 rows ±1 conversion, benign). Verification was read-only; nothing changed.

### Finding B — the dashboard bakes its data into the HTML (it does not read the table live)
The movement values shown are embedded in `ph_task` id 5's `html_content`, not queried live from `ph_segment_report`. Consequence: a change to the report table does **not** propagate to the dashboard until the baked payload is updated. This was surfaced when the user saw the table say DECLINED while the dashboard still said SAME. My earlier claim that "the dashboard reads movement live, no push needed" was **wrong and is corrected here**.

### Finding C — strict-rank movement changes exactly 65 rows, all lateral, one-way
Because the equal-weight h-count tied HHL/HLH/LHH, every lateral move among them was previously SAME. The strict 1–6 rank makes them distinct, so 65 rows move SAME → IMPROVED (23) / DECLINED (42); no other movement type changes; NEW unchanged; escalations stable. Verified 8,149/8,149 against the rule.

### Finding D — a duplicate (PH, ASIN, segment) key required account-level disambiguation
15 (user, asin, segment) keys appear twice (same PH, two accounts) — 14 had identical movement on both sides; **1** (`preethi / B0BW9LNTTD / LLL`) genuinely differed (LEDSone=NEW, DCVoltage=SAME). The baked-data correction keyed on impressions/account to update the right row, not both — proving that ASIN-only text replacement on baked data is unsafe.

### Finding E — an over-long single UPDATE failed atomically; batching succeeded
A 65-nested-`replace()` statement (~8 KB, one line) failed with a syntax error and changed **nothing** (atomic). Re-running as smaller multi-line batches (5 + 15 + 15 + 15 + 20, with a few harmless re-applied no-ops) succeeded. Lesson: keep large chained-replace statements multi-line and batched.

### Finding F — the engine reproduces the live universe under the strict-rank rule (sandbox)
Run entirely in `sandbox.*` (live untouched): 8,149 rows reproduced, strict-rank movement 0 mismatches across 8,028 scored rows. Output differs from live only in NEW (121 vs 191) — the returning-aware rule the engine carries but the live one-time report does not.

### Finding G — real NEW ASINs are genuine; the report is UK-only
Saranya's 8 and paulr's 8 NEW ASINs all have 0 UK rows in the previous 4-week window (traced in `traffic_data`), so NEW is correct for them under the current rule. An earlier suspicion of mislabelling was **my mistake** — I compared across all marketplaces (France/Germany rows) while the report filters UK-only.

---

## SECTION 4 · GAP FOUND

- **Gap A — Cloud scheduler still not created (MEDIUM, BLOCKED, carried).** Pending the Windows Virtual Machine Platform feature (or pg_cron `0 9 3 * *`, or manual on 3 Aug). Owner: abiraj.
- **Gap B — Monthly routine's HTML shell (BLOCK 1) still builds the OLD tabs layout (MEDIUM, OPEN, carried from D06).** The engine now carries today's strict-rank rule, but the routine that renders the dashboard page still builds the old UI. If the 3 Aug run fires before this is swapped, it would regenerate the old layout (data/logic correct, screen reverted). **This is the single most important open item.** Owner: abiraj.
- **Gap C — Engine `bm_conversion` column (LOW, OPEN, carried from D07 plan).** The D07 morning plan also scoped baking `bm_conversion` into the engine for Avg-Conv consistency from 2026-08; not done today (today's engine work was the strict-rank rule). Owner: abiraj.
- **Gap D — NEW-definition sign-off still open (MEDIUM, needs Bietrick).** Engine = returning-aware (NEW 121); live report = simple (NEW 191). One engine clause depends on this. Cannot be closed by the developer. Owner: Bietrick.
- **Gap E — Rule-set items still open (LOW/MEDIUM).** From the user's Segment-Comparison rule set: strict-rank order is now DECIDED + LIVE; still open are Rule 4 **frozen monthly snapshots** (a new stored-history table — does not exist yet; system is single-cycle DROP+CREATE) and the **"Status" naming clash** (rule set calls movement "Status"; dashboard already has a Status column = ABOVE/NEAR/BELOW/NEEDS_REVIEW). Owner: abiraj → Bietrick for the naming decision.
- **Gap F — Backup-table set has grown further (HOUSEKEEPING, deliberately deferred).** Added today: `ph_task_id5_backup_20260702_css`, `_cards`, `_movdata`, and `ph_segment_report_backup_20260702_movrule` — on top of the six from D06. All intact and verified; **none dropped** — retained as the rollback net until Bietrick's formal acceptance. Owner: abiraj.

> `GAP: no blocking gaps for today's live deliverables (all render-verified and byte-matched to approved previews). The main carried risk remains Gap B — the automated routine would rebuild the OLD UI on 3 Aug, now also losing today's card redesign and the strict-rank movement in the baked payload unless the routine's shell + fill are aligned before then.`

---

## SECTION 5 · VALIDATION RULE ADDED OR CHANGED

- **RULE — Strict segment-rank movement (NEW, DECIDED + LIVE today).** HHH=1, HHL=2, HLH=3, LHH=4, LLH=5, LLL=6 (lower = better). Movement = current vs previous rank: `<` IMPROVED, `>` DECLINED, `=` SAME, no previous = NEW. Replaces the equal-weight h-count that tied HHL/HLH/LHH. Applied to the 2026-07 report + dashboard and baked into the v2 engine. Decided by: user (2026-07-02).
- **RULE — 4-week window is authoritative over "calendar month" (CONFIRMED today).** Movement compares the last 4 complete weeks vs the previous 4 (Saturday-ending); the live 4-week basis stands, not a calendar-month interpretation. Confirmed by: user.
- **RULE — Dashboard data is baked, not live (OPERATIONAL, established today).** Any change to `ph_segment_report` that must appear on the dashboard requires updating the baked payload in `ph_task` id 5 — the page does not query the table at render time. Verify table AND baked data after any data-affecting change.
- **RULE — Baked-data edits must key on a unique row signature (NEW, operational).** ASIN alone is not unique in the baked array (same ASIN across accounts, or duplicate PH+ASIN+segment); include segment + account/impressions to target the exact row. Prefer multi-line batched `replace()` over one over-long single statement.
- **RULE (carried, unchanged):** returning-aware NEW (engine; pending sign-off); byte-verified large-payload transfer (base64 → server-side md5 → guarded replace → render-verify); backup-first/verify-after; benchmark top-30/10/manual; Method-A CVR; conv edges; Option B map; FBM/UK/Amazon scope; flag-don't-act escalations; engine abort guards.

> `VALIDATION RULE: strict segment-rank movement adopted live (HHL/HLH/LHH now distinct); 4-week window reaffirmed over calendar month; "dashboard data is baked, not live" established as an operational rule; baked-data edits must use a unique row signature + batched replaces.`

---

## SECTION 6 · FAILURE MODE OR EDGE CASE

- **Failure mode (CAUGHT by the user, then FIXED) — stale dashboard movement.** Trigger: updating the report table's movement but not the baked dashboard payload; I incorrectly said the dashboard read the table live. Detection: user saw `B0C5TJDGHJ` = SAME on the dashboard while the table said DECLINED. Recovery: corrected the 65 baked mov cells (byte-verified). Risk was MEDIUM (dashboard showing outdated movement) → resolved; the honest lesson (Finding B) is recorded.
- **Failure mode (CAUGHT, FAILED SAFELY) — over-long chained UPDATE.** Trigger: 65 `replace()`s on one ~8 KB line hit a syntax error. Detection: statement error returned; atomic → nothing changed. Recovery: re-ran in small multi-line batches. Risk NONE (no partial write).
- **Edge case (HANDLED) — duplicate (PH, ASIN, segment) with conflicting movement.** `preethi / B0BW9LNTTD / LLL` was NEW on one account, SAME on the other; disambiguated by account/impressions so the correct baked row was updated. Risk was LOW (could have set the wrong row) → handled explicitly.
- **Edge case (SELF-CORRECTED) — my "mislabelled NEW" suspicion was wrong.** I initially flagged Saranya/paulr NEW ASINs as possibly mis-classified by comparing across all marketplaces; the report is UK-only, so they are correctly NEW. Corrected in-session; no live impact. Risk NONE (analysis only).
- **Edge case (SCOPE) — restyle initially applied too broadly.** First black-&-gold pass themed the whole dashboard and the dropdown list rendered unreadable gold-on-dark; user flagged it; re-scoped to header/greeting gold only + readable white dropdown before any live push. Risk NONE (previews only; nothing wrong went live).

---

## SECTION 7 · DECISIONS MADE TODAY

- **D-41 (executed) — Full read-only verification of the live report before any change.** All re-derivations passed (0 mismatches); nothing modified.
- **D-42 (approved) — Restyle scope = header/greeting gold + slate/teal body only; rest of dashboard styling upgraded but data untouched.** Re-scoped after the "too much gold" feedback; dropdown made readable.
- **D-43 (executed) — Push restyle (v2) live, byte-verified.** Backup-first; server-side md5 `740b8eeb…`; data payload never moved.
- **D-44 (approved) — Card redesign: icons + colour-coding, Champions green / Dead Horses red; ribbon-medal + warning-triangle icons.** Chosen by user across two icon rounds.
- **D-45 (executed) — Push card redesign (v3) live, byte-verified.** Backup-first; server-side md5 `e2dfbfd9…`; live md5 `6d5a45e2…`.
- **D-46 (approved + executed) — Adopt strict segment-rank movement (HHH=1…LLL=6); apply to the 2026-07 report.** Impact measured first (65 rows, one-way); backup-first; verified 8,149/8,149.
- **D-47 (executed) — Correct the baked dashboard movement (65 cells) after the stale-data miss.** Backup-first; unique-signature batched replaces; live byte-matched to target.
- **D-48 (executed) — Bake strict-rank into the v2 engine; validate in sandbox only.** 8,149 rows reproduced, 0 movement mismatches; live never touched; sandbox dropped.
- **D-49 (decision) — Keep all backup tables; do not drop.** Rollback net retained until Bietrick's formal acceptance.
- **D-50 (decision) — `temp_user.py` direct-connection script declined; MCP-only path upheld.** No credentials handled; the MCP login is the user's to authenticate.
- **D-51 (flagged, not decided) — NEW definition (live 191 vs engine 121) remains Bietrick's call.** Engine currently returning-aware; one clause depends on the decision.
- (D-0…D-40 from D01–D06 remain in force.)

---

## SECTION 8 · COMPANY KNOWLEDGE EXTRACT

### Business Rule
Every UK-Amazon **FBM** ASIN owned by a PH is classified monthly into one of six segments (Impressions, Clicks, CVR vs a per-PH per-category top-30-units benchmark), with movement vs the previous 4-week window. **Movement is now decided by a strict segment rank (HHH=1 best … LLL=6 worst): a move to a lower-numbered rank is IMPROVED, higher is DECLINED, equal is SAME, and no prior-window presence is NEW.** The three "two-strong" segments HHL/HLH/LHH are **distinct** ranks (2/3/4), so a lateral shift among them is a real movement, not "no change." The system flags; it never acts. The dashboard is a presentation layer whose data is **baked in** — it must be re-pushed when the underlying report changes.

### Operational Assumption
A dashboard that embeds its data will not reflect a table change until re-pushed — always verify both the table and the baked payload. When editing baked data, a row must be targeted by a **unique** signature (ASIN can repeat across accounts). Large live pushes should assemble + md5-verify server-side before any write, and chained-replace statements should be batched multi-line (an over-long single statement can fail atomically). A classification rule change (like strict-rank movement) must be applied in **three** places to be durable: the current report table, the baked dashboard, and the engine that builds future cycles — otherwise the next automated run silently reverts it.

### Reusable Logic / Formula
- **Strict ordinal ranking for movement:** replace tied/equal-weight scores with a strict 1..N rank when "lateral" moves must count as up/down; movement = sign(previous_rank − current_rank). Generalises to any tier/grade progression tracking.
- **Three-surface durability check:** when a metric is computed by an engine, stored in a table, AND baked into a UI, a rule change must hit all three or it will regress on the next rebuild.
- **Baked-data safe edit:** target rows by a unique multi-field signature, verify the exact change count locally (only the intended field differs) before pushing, and batch chained replaces.
- **Measure-before-apply:** compute the exact impact of a data rule change read-only (how many rows change, in which direction) before writing, so the result is expected, not discovered.
- **UK-only reconciliation caveat:** when a report is scoped to one marketplace, any "missing/mislabelled" check must apply the **same** marketplace filter, or cross-market rows will produce false anomalies.

### Canonical Vocabulary
| Term | Meaning |
| :---- | :---- |
| strict segment rank | fixed 1–6 order HHH<HHL<HLH<LHH<LLH<LLL (lower = better) used to decide movement; replaces the equal-weight h-count |
| lateral move | a change between HHL/HLH/LHH — previously tied (SAME), now a real IMPROVED/DECLINED under strict rank |
| baked data | report values embedded in the dashboard's HTML (`ph_task` id 5), not queried live — must be re-pushed on any table change |
| returning-aware NEW | engine rule: an ASIN absent the previous 4 weeks but present in the 4 before = SAME, not NEW (pending Bietrick sign-off vs the live simple rule) |
| three-surface change | a rule that must be applied to report table + baked dashboard + engine to persist across the next automated run |

### Cross-Project Applicability
- **Strict ordinal ranking** applies to any progression/movement metric where equal-weight scoring hides real transitions.
- **Three-surface durability** applies wherever a value is simultaneously engine-computed, table-stored, and UI-embedded.
- **Baked-data safe edit + batched replace** applies to any large content stored in a single row edited through a constrained interface.
- **Measure-before-apply** applies to any bulk data mutation where the blast radius should be known first.
- **Same-filter reconciliation** applies to any scoped (region/segment) report being audited for completeness.

---

## SECTION 9 · LLM STANDARD CHECK

| Check | YES / NO |
| :---- | :---- |
| Could an unknown developer continue from this file without reading source code? | ✅ YES |
| Is every business threshold visible (not buried in code)? | ✅ YES — strict-rank table, 4-week window, returning-aware NEW, escalation thresholds all in metadata + S5 |
| Is the GAP FOUND section completed or marked NONE? | ✅ YES — 6 items, incl. the carried routine-UI risk (Gap B) |
| Is the COMPANY KNOWLEDGE EXTRACT section substantive? | ✅ YES |
| Are evidence locations referenced? | ✅ YES — read-only verification chain + 3 byte-verified live pushes + strict-rank UPDATE + 65-row baked correction + sandbox engine validation; no Git SHA (files), stated plainly |
| Is metadata complete (incl. blos_keys_used + hardcoded_thresholds)? | ✅ YES |
| Are section names per standard template (1–9)? | ✅ YES |
| Is this extracting knowledge — not just logging activity? | ✅ YES |

### Three-AM Standard Self-Assessment
A developer with no context could, from this file alone:
- **WHAT** was done today — **verified** the live 2026-07 report end-to-end read-only (0 mismatches); **restyled the live dashboard** (gold header/greeting over a slate/teal body, stronger escalation banner, amber NEEDS_REVIEW rows) and **redesigned the cards** (per-card icons + colour-coding, Champions green / Dead Horses red, ribbon-medal + warning-triangle icons), both pushed live byte-verified against approved previews; **adopted a strict segment-rank movement rule** (HHH=1…LLL=6) and applied it to the **report table** (65 rows SAME→IMPROVED/DECLINED, 8,149/8,149 verified) **and** to the **baked dashboard** (after the user caught the dashboard held stale movement); and **updated the v2 engine** to the strict-rank rule, sandbox-validated (8,149 rows, 0 movement mismatches, live untouched).
- **WHAT** is NOT yet done — swap the monthly routine's HTML shell + fill to the new UI (Gap B, the real pre-3-Aug risk, now also carrying the card design + strict-rank baked movement); bake `bm_conversion` into the engine (Gap C); Bietrick's NEW-definition sign-off (Gap D) + the edge-case protocol + 492 orphan assignments; Rule-4 frozen snapshots and the "Status" naming decision (Gap E); drop the grown backup set once accepted (Gap F); Cloud routine Create (Windows feature, Gap A).
- **WHY** — verification first proved nothing was broken before touching anything; every visual change was previewed and approved before a backup-first, byte/md5-verified live push because these are user-facing irreversible edits; the strict-rank rule was the user's decision to make lateral HHL/HLH/LHH moves visible; the rule had to be applied to report + dashboard + engine (three surfaces) or the next run would revert it; the dashboard's baked-data nature (my earlier wrong assumption, corrected) is why the table change alone wasn't enough.
- **WHO / WHERE / NEXT** — owner abiraj (NEW-definition + "Status" naming + edge-case + orphan-assignment decisions → Bietrick); live output `tech_team_outputs.ph_task` id 5 (888,511 bytes, restyle + cards + strict-rank movement, live now); source `analytics.ph_segment_report` (8,149, strict-rank movement); engine `ph_segment_engine.sql` v3 (strict-rank, sandbox-validated, first live run 3 Aug on 2026-08); next: swap the routine's shell + fill to the new UI **before 3 Aug**, bake `bm_conversion`, get the three sign-offs, then drop the backup set.

---

## ── SUBMISSION CHECKLIST ─────────────────────────────────────────────────────

- [x] File named correctly: `2026-07-02__abiraj__ph-asin__REQ-05-D07.md`
- [x] Saved under dated folder `DigitWeb_Works_Abiraj/02_07_2026/`
- [x] Metadata complete — incl. `blos_keys_used` (NONE), `hardcoded_thresholds` (strict-rank table + 4-week window + carried constants), and `daily_benefit_delivered` (folded into metadata, no separate bottom section)
- [x] Live query/DDL evidence in Section 3 (read-only verification + 3 byte-verified pushes + strict-rank UPDATE + 65-row baked correction + sandbox engine validation)
- [x] Section names 1–9 match standard template
- [x] No credentials, passwords, or API keys included (`temp_user.py` direct-connect script explicitly declined)
- [x] LLM Standard Check table completed
- [x] Three-AM Standard self-assessment written (WHAT/WHY/WHO/WHERE/NEXT)
- [x] Evidence referenced (live MCP outputs + handed-over files); no Git SHA (files), stated plainly
- [x] ✅ **DONE TODAY:** full read-only verification (0 mismatches) · live restyle (gold header/greeting + slate/teal body, stronger escalation banner, amber NEEDS_REVIEW rows) pushed byte-verified · card redesign (icons + colour-coding, Champions green / Dead Horses red) pushed byte-verified · strict segment-rank movement adopted + applied to report (65 rows) AND baked dashboard (65 cells) · v2 engine updated to strict-rank + sandbox-validated · NEW mechanic explained + source-verified (Saranya/paulr real)
- [x] **NEXT SCHEDULED STEPS (not blockers):** swap monthly routine BLOCK 1 + BLOCK 2 to the new UI (before 3 Aug) · bake `bm_conversion` into engine · Bietrick sign-offs (NEW definition, edge-case protocol, 492 orphan assignments) · Rule-4 snapshots + "Status" naming decision · drop backup set after acceptance · Cloud routine Create (Windows feature)
