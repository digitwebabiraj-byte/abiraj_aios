# SKILL FILE — DAILY KNOWLEDGE EXTRACTION
# DIGITWEB LK LTD · Daily Skill Increment System · v3.0

---

## ── METADATA BLOCK ──────────────────────────────────────────────────────────

| Field | Value |
| :---- | :---- |
| **date** | 2026-07-03 |
| **developer** | abiraj |
| **project** | PH ASIN Segmentation — Growth Protection Engine (GPE) |
| **project\_code** | ph-asin |
| **phase** | Phase-08 — Count Confirmation & Per-PH Dashboard Hand-Over |
| **requirement\_id** | REQ-05 |
| **deliverable\_id** | REQ-05-D08 |
| **status** | **COMPLETE for today's increment.** Delivered: (1) read-only confirmation that the dashboard **Assigned Listings** card is correct for all 24 PHs (reconciles to `traffic_data`, diff 0; paulr = 466 listings / 464 distinct ASINs); (2) a preview-only clarity pass on the segmentation dashboard — internal jargon removed ("Method-A", "returning-aware"; 0 remaining), category-click filtering, explicit window date ranges, a per-PH allocated card, and plain Segment-mix / Movement labels; (3) **24 single-PH-locked standalone dashboards**, one per PH, each opening only to its own data with all other PHs physically removed, dropdown hidden, and filenames matching Bietrick's authoritative spelling list. Read-only against the live DB throughout — no writes, no push, nothing dropped. Carried-open (project items, unchanged): clarity pass awaiting approval to push live; monthly-routine UI swap before 3 Aug; Bietrick sign-offs. |
| **evidence\_location** | Read-only MCP verification: Assigned Listings = distinct owned UK-Amazon current-window ASINs per PH, reconciled to `public.traffic_data`, **diff 0 all 24 PHs** (paulr 466/464). Preview (local, not live): jargon grep 0/0, category filter, window date strip, allocated card, clearer labels. Deliverables handed to Abiraj: 24 locked files in `/mnt/user-data/outputs/ph_views/`, per-file verified (paulr 466 rows / allocated 503 / 39 not active / 7 cards; Dilani 282; Saranya 76; utharsika 1408; Abinayaa 206; Jasmini 1178; Tharsiga(nelli) 278; Tharsika(jaffna) 379), ~45–142 KB each (avg ~63 KB) vs 891 KB all-data original. No live DB writes. No Git SHA — local files + read-only DB. |
| **blos\_keys\_used** | NONE — project does not consume BLOS rule/threshold keys. |
| **hardcoded\_thresholds** | Classification logic unchanged (Method-A CVR, benchmark top-30/10/manual, Option-B map, FBM/UK/Amazon scope, escalation thresholds). Strict segment-rank movement (HHH=1…LLL=6) carried from D07, unchanged. No new thresholds. **Assigned Listings** = distinct owned UK-Amazon ASINs per PH in the current 4-week window (`which_channel=1`, `market_place='UK'`, owner `user_name IS NOT NULL`; window **2026-05-31 … 2026-06-27**, previous **2026-05-03 … 2026-05-30**). |
| **three\_am\_standard** | PASS |
| **llm\_queryable** | YES |
| **company\_knowledge\_candidate** | YES |
| **domain** | DATABASE \| SEGMENTATION \| REPORTING \| AMAZON-LISTINGS \| DATA-QUALITY \| UI/UX \| PRIVACY |
| **user** | Bietrick |
| **benefit\_status** | **DELIVERED** — (1) The count every PH sees is proven right — Assigned Listings confirmed against raw data for all 24 PHs, diff 0. (2) A jargon-free, readable dashboard — plain wording, category filtering, explicit date ranges, an allocated card, and clear labels (in preview, ready to push on approval). (3) Each PH gets a private dashboard — 24 standalone files, one per person, showing only their own listings, no dropdown, ~63 KB each. (4) Clean hand-over — filenames exactly per Bietrick's list; all work read-only against the live DB. |

## File path:
# 2026-07-03__abiraj__ph-asin__REQ-05-D08.md
# DigitWeb_Works_Abiraj/03_07_2026/

---

## SECTION 1 · SYSTEM STATE

- **Start of today.** D07 (2 Jul) had delivered live the dashboard restyle, card redesign, strict-rank movement rule (report + baked dashboard + engine), and a full read-only verification of the 2026-07 report. Assigned Listings was already verified correct (paulr 466/464, diff 0). Today's brief: re-confirm the count for all holders, clean up the dashboard, and give each PH their own private view.
- **Trigger.** The user asked, in order, to: re-verify Assigned Listings for all holders; clean the dashboard preview (remove "Method-A" / "returning-aware", finalise the clarity features); produce each PH's view as a separate standalone file; lock each file to only that PH's data (no dropdown); and name the files using the authoritative 24-name list.
- **What was working.** The live report and dashboard were correct and reconciled (re-confirmed read-only). Today turned the verified count into a per-PH, privacy-safe hand-over plus a jargon-free preview — live DB untouched.
- **Approach.** Re-confirm read-only; build every change as a preview or standalone file; push nothing live; leave the live DB and baked dashboard exactly as D07 left them.

> **In plain terms:** I confirmed, from raw data, that the dashboard's **Assigned Listings** number is correct for all 24 people (exact match, zero errors). I then tidied the dashboard so anyone can read it: removed the code-words, spelled out the date ranges, added an allocated card, added category filtering, and made the segment/movement labels plain (NEW now reads "first time seen") — all in a preview, not on the live site. Finally I built **24 separate mini-dashboards, one per person**, each opening straight to only their numbers with everyone else's data removed and no dropdown — safe to hand out one to one. Filenames use your exact spellings. Nothing was written to the database.

---

## SECTION 2 · WHAT CHANGED TODAY

Read-only confirmation of Assigned Listings (all 24 PHs), a preview-only clarity pass, and 24 single-PH-locked standalone dashboards. Live DB untouched.

- **Change 1 — Assigned Listings confirmed correct (read-only).** Re-derived the card count per PH and reconciled to `public.traffic_data`: **diff 0 for all 24 PHs**. paulr = 466 listings / 464 distinct ASINs — the current-window, owned, UK-Amazon count each PH sees.
- **Change 2 — Internal jargon removed from the preview.** Replaced both "Method-A" mentions with plain wording (meta strip: "Top-30 best-sellers / category · average conversion rate"; category header: "CVR = average of each product's conversion rate"). Verified **0** "Method-A" and **0** "returning-aware" remaining. Wording only.
- **Change 3 — Clarity features finalised (preview only).** Category-click filtering (arrows + "filtering ✓" cue); explicit window date ranges (**31 May–27 Jun** vs **3 May–30 May**); a dynamic per-PH allocated count (greeting line + a 7th allocated card — paulr allocated **503**, 39 not active); plain Segment-mix / Movement labels (NEW = "first time seen"). Existing segments, movement, cards, and ASIN table left intact.
- **Change 4 — One standalone HTML file per PH generated.** 24 self-contained files from the finished preview — all data and styling baked in, open in any browser, no server or internet.
- **Change 5 — Auto-select corrected (index, not name).** The option `value` is the PH index, not the name; setting the value to the index made each file auto-open to the correct PH (paulr 466, utharsika 1408, Dilani 282, Saranya 76).
- **Change 6 — Files re-generated locked to a single PH.** Filtered `D.rows` / `D.cats` to the PH index (field `[0]`), re-indexed to a single-PH array, reduced `D.phs` / `alloc` to one, hid the dropdown, auto-rendered. Other PHs' rows are physically removed; files drop to ~45–142 KB (avg ~63 KB) from ~891 KB. Per-file verified: correct PH, dropdown hidden, `phs_in_data: 1`, full view intact.
- **Change 7 — Filenames set to the authoritative spelling list.** Content spellings already matched Bietrick's 24-name list exactly; filenames regenerated to match, parentheses kept (`Tharsiga(nelli).html`, `Tharsika(jaffna).html`). Re-verified locked and correct (Tharsiga(nelli) 278 rows, Tharsika(jaffna) 379 rows).

### Deliverables (today)
- 24 single-PH-locked standalone dashboards in `/mnt/user-data/outputs/ph_views/` — one per PH, own data only, dropdown hidden, filenames per the authoritative list.
- The improved dashboard preview (jargon removed, category filter, window dates, allocated card, clearer labels) — preview only, not live.
- Assigned-Listings confirmation (diff 0, all 24 PHs; paulr 466/464).

Evidence: read-only MCP count confirmation + local preview edits (jargon grep 0/0) + 24 locked files (per-file verified). No live writes. No credentials. No Git SHA.

---

## SECTION 3 · POSTGRESQL / MCP / DATABASE FINDING

> **PostgreSQL via MCP — read-only today.** No `INSERT/UPDATE/DELETE/DDL`, no push. All changes live in a local preview and 24 standalone files; the live DB is exactly as D07 left it.

**Objects read today:** `analytics.ph_segment_report` (Assigned Listings source), `public.traffic_data` (reconciliation), `tech_team_outputs.ph_task` id 5 (read only). No writes.

- **Finding A — Assigned Listings is correct for all 24 PHs.** Distinct owned UK-Amazon ASINs in the current 4-week window; reconciles to `traffic_data` with diff 0 across all 24 PHs. paulr = 466 / 464. This is the number shown on each PH's card and on each of the 24 standalone files.
- **Finding B — Every row keys on the PH index at field `[0]`.** In the `D` data object each `rows` / `cats` entry carries the PH index at position `[0]`; filtering on it and re-indexing to a single-PH array is what makes a truly private per-PH file.
- **Finding C — The dropdown option `value` is the PH index, not the name.** Programmatic pre-selection must set the index; the auto-selected view must be render-verified before hand-over.
- **Finding D — Single-PH locking shrinks each file ~14×.** ~891 KB (all data) → ~63 KB avg (one PH) — smaller, faster, and private, since there is no other PH's data inside.

---

## SECTION 4 · GAP FOUND

- **Gap A — Clarity pass is preview-only.** The jargon removal and new features are in the preview and the 24 files, not on live `ph_task` id 5. Pushing live (if approved) uses the D07 backup-first, byte-verified method. Owner: abiraj → Bietrick approval.
- **Gap B — Standalone files are a 2026-07 snapshot.** They do not auto-update; regenerate each cycle. An "as of" line and a repeatable regenerate step can be added on request. Owner: abiraj.
- **Gap C — Monthly routine still builds the OLD tabs UI (carried).** The 3-Aug auto-run would rebuild the old layout unless the routine's shell + fill are aligned first. Owner: abiraj.
- **Gap D — Carried sign-offs (Bietrick).** NEW definition (live 191 vs engine 121), edge-case protocol, 492 orphan assignments — untouched today. Owner: Bietrick.
- **Gap E — D06/D07 backup set retained.** No backups added today (no writes); the existing set is the rollback net until formal acceptance. Owner: abiraj.

> `GAP: no blocking gaps for today's deliverables — the 24 locked files are verified (correct PH, dropdown hidden, single-PH data, correct filenames) and the count is diff 0. Remaining items are carried project items (live push approval, monthly-routine UI swap, sign-offs).`

---

## SECTION 5 · VALIDATION RULE ADDED OR CHANGED

- **Assigned Listings pinned + verified.** = distinct owned UK-Amazon ASINs per PH in the current 4-week window (2026-05-31 … 2026-06-27), `which_channel=1`, `market_place='UK'`, owner `user_name IS NOT NULL`. Diff 0 vs `traffic_data`, all 24 PHs.
- **Single-PH lock = physically filter, not just hide.** Filter the data object to the PH index (`[0]`) and re-index; hiding the dropdown alone is not privacy.
- **Drive a `<select>` by its real value scheme.** The option value is the PH index; set it, then render-verify the auto-opened view.
- **Filenames follow the authoritative list exactly, parentheses kept** (`Tharsiga(nelli)`, `Tharsika(jaffna)`).
- **Carried, unchanged:** strict segment-rank movement (D07); 4-week window over calendar month; dashboard data is baked (live change needs a byte-verified push); returning-aware NEW (engine, pending sign-off); benchmark top-30/10/manual; Option-B map; FBM/UK/Amazon scope; flag-don't-act escalations.

> `VALIDATION RULE: Assigned Listings pinned + verified diff 0 (all 24 PHs); single-PH files must physically filter data; a <select> must be driven by its real value scheme; filenames follow the authoritative list.`

---

## SECTION 6 · FAILURE MODE OR EDGE CASE

- **Auto-select mismatch (caught, fixed).** Files first opened to "Select a Portfolio Holder" because the pre-select used the PH name while the option value is the index. Fixed by setting the index; re-verified auto-open. Caught before hand-over; no live impact.
- **Privacy — hidden ≠ removed (handled).** The first standalone pass still carried every PH's data internally. Re-generated with other PHs' rows physically filtered out and the dropdown hidden; verified `phs_in_data: 1` per file.
- **Parentheses in names vs filenames (handled).** `Tharsiga(nelli)` / `Tharsika(jaffna)` were underscored at first; content spellings already matched the list, filenames regenerated keeping the parentheses.

---

## SECTION 7 · DECISIONS MADE TODAY

- **D-52 (executed) — Confirm Assigned Listings read-only for all 24 PHs.** Diff 0; paulr 466/464.
- **D-53 (executed) — Remove "Method-A" / "returning-aware" jargon from the preview.** 0 remaining.
- **D-54 (executed) — Finalise clarity features (category filter, window dates, allocated card, clearer labels).** Preview only.
- **D-55 (executed) — Generate one standalone file per PH.** 24 self-contained files.
- **D-56 (executed) — Auto-select on the PH index, not the name.** Correct auto-open.
- **D-57 (approved + executed) — Lock each file to a single PH (strip other data + hide dropdown).** `phs_in_data: 1`, ~63 KB avg.
- **D-58 (executed) — Name files per the authoritative list, parentheses kept.**
- **D-59 (decision) — Push nothing live; keep the clarity pass as a preview pending approval.**
- (D-0…D-51 from D01–D07 remain in force.)

---

## SECTION 8 · COMPANY KNOWLEDGE EXTRACT

### Business Rule
A PH's **Assigned Listings** = distinct owned UK-Amazon ASINs in the current 4-week window — "listings this PH is working this window" — verified correct against `traffic_data` (diff 0, all 24 PHs). Each PH may be handed a private single-PH dashboard showing only their own listings, with all other PHs' data physically removed.

### Operational Assumption
When packaging a per-entity view, filter the data to that entity (don't rely on a default over the full dataset), render-verify the view, and confirm no other entity's data remains. A presentation change stays a preview until approved and pushed by the backup-first, byte-verified method.

### Reusable Logic / Formula
- **Physical filter for privacy:** strip other entities' rows and re-index; hiding the switcher is not enough.
- **Drive UI controls by their real value scheme:** use the option's actual value (index here) and render-verify.
- **Authoritative-list naming:** take names and filenames verbatim from the owner's canonical list, preserving special characters.
- **Confirm-before-handover:** prove a displayed figure from source (diff 0) before distributing a copy of it.

### Canonical Vocabulary
| Term | Meaning |
| :---- | :---- |
| Assigned Listings | dashboard card = distinct owned UK-Amazon ASINs for a PH in the current 4-week window; verified diff 0 vs `traffic_data`, all 24 PHs |
| allocated card | 7th dashboard card = listings a PH is allocated (paulr 503, 39 not active); distinct from active in-window listings |
| single-PH-locked file | standalone dashboard with only one PH's data (others removed) and the dropdown hidden — safe to hand to that PH |
| authoritative spelling list | Bietrick's canonical 24 PH names, used verbatim for filenames, parentheses kept |

### Cross-Project Applicability
- **Physical-filter-for-privacy** — any per-recipient export cut from a shared dataset.
- **Drive-controls-by-real-value-scheme + render-verify** — any generated page that must auto-open to a specific state.
- **Authoritative-list naming** — any generated artifact that must match an owner's canonical labels.
- **Preview-until-approved** — any live, baked, user-facing surface.

---

## SECTION 9 · LLM STANDARD CHECK

| Check | YES / NO |
| :---- | :---- |
| Could an unknown developer continue from this file without reading source code? | ✅ YES |
| Is every business threshold visible (not buried in code)? | ✅ YES — Assigned Listings scope + window, carried constants in metadata + S5 |
| Is the GAP FOUND section completed or marked NONE? | ✅ YES — 5 carried project items; none block today's deliverables |
| Is the COMPANY KNOWLEDGE EXTRACT section substantive? | ✅ YES |
| Are evidence locations referenced? | ✅ YES — read-only count confirmation (diff 0, all 24) + preview edits + 24 locked files; no live writes; no Git SHA (files), stated |
| Is metadata complete (incl. blos_keys_used + hardcoded_thresholds)? | ✅ YES |
| Are section names per standard template (1–9)? | ✅ YES |
| Is this extracting knowledge — not just logging activity? | ✅ YES |

### Three-AM Standard Self-Assessment
- **WHAT** — confirmed Assigned Listings correct for all 24 PHs (diff 0; paulr 466/464); cleaned the dashboard preview (jargon removed; category filter, window dates, allocated card, clearer labels) — preview only; packaged 24 single-PH-locked standalone dashboards (own data only, dropdown hidden, filenames per the authoritative list), fixing two bugs on the way (auto-select index, single-PH filter).
- **NOT DONE (carried project items)** — push the clarity pass live if approved (Gap A); add "as of" line / regenerate step (Gap B); swap the monthly routine before 3 Aug (Gap C); Bietrick sign-offs (Gap D).
- **WHY** — prove the count before handing each PH a copy; remove jargon for non-technical readers; keep the clarity pass a preview because live changes go through a backup-first, byte-verified push; physically filter each file because hiding the dropdown alone still ships every PH's data.
- **WHO / WHERE / NEXT** — owner abiraj (live-push decision → Bietrick); deliverables in `/mnt/user-data/outputs/ph_views/` (24 files) + preview; live `ph_task` id 5 unchanged (D07 state); source `analytics.ph_segment_report` + `traffic_data` (read-only); next: get approval to push the clarity pass live; keep the 3-Aug routine-UI swap on track.

---

## ── SUBMISSION CHECKLIST ─────────────────────────────────────────────────────

- [x] File named correctly: `2026-07-03__abiraj__ph-asin__REQ-05-D08.md`
- [x] Saved under dated folder `DigitWeb_Works_Abiraj/03_07_2026/`
- [x] Metadata complete — incl. `blos_keys_used` (NONE), `hardcoded_thresholds`, `user`, and `benefit_status`
- [x] Live query evidence in Section 3 (read-only count confirmation, diff 0 all 24 PHs) — no writes today
- [x] Section names 1–9 match standard template
- [x] No credentials, passwords, or API keys included
- [x] LLM Standard Check table completed
- [x] Three-AM Standard self-assessment written (WHAT / NOT DONE / WHY / WHO-WHERE-NEXT)
- [x] Evidence referenced (read-only MCP outputs + 24 locked files + preview); no live push; no Git SHA (files), stated
- [x] ✅ **DONE TODAY:** Assigned Listings confirmed (diff 0, all 24 PHs) · jargon removed (0 remaining) · clarity features finalised (preview) · 24 single-PH-locked dashboards generated, verified, named per the authoritative list · two bugs fixed
- [x] **NEXT STEPS (carried):** get approval to push the clarity pass live · add "as of" line / regenerate step · swap monthly routine before 3 Aug · Bietrick sign-offs
