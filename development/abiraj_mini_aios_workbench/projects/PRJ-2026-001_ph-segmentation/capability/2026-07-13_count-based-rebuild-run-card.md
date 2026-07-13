# Count-based July rebuild — RUN CARD (for the authorised DB session)

**Goal:** regenerate the **2026-07** PH dashboards with the **count-based conversion rule**
(Bietrick-approved 2026-07-10) and publish. **Same window, same roster, same UI — only the segment
data changes.** This is the "update those HTMLs" ask from 2026-07-13.

## Already verified READ-ONLY on 2026-07-13 (via Postgres MCP) — you can trust these
- **Window** = the same 4 weeks as the live D10 build: weeks ending **2026-06-06, 06-13, 06-20, 06-27**
  (now `rn 2..5`, because a newer week ending **2026-07-04** has since loaded). Prev = 05-09/16/23/30
  (`rn 6..9`); prior = 04-11/18/25 + 05-02 (`rn 10..13`). `01`/`03` already default to these rn offsets.
- **Universe unchanged:** total **9,947 ASINs / 30 PHs**; every per-PH count identical to the D10
  `EXPECT_PH` (Abinayaa 224 … utharsika 1578 … Vaishnavi 69). Roster unchanged → **no INSERT/DELETE**, 31 rows stay.
- **New count-based distribution** (same 9,947): **HHH 180 · HHL 433 · HLH 173 · LHH 19 · LLH 144 · LLL 8998**.
  (Was rate-based 42 · 580 · 173 · 10 · 626 · 8516.) Net moves: **HHL→HHH ≈ +138 Champions**, and
  **LLH→LLL ≈ +482 into Dead Horses** — Bietrick approved off the Champions example; make sure he's
  aware of the Dead-Horses side before it goes to PHs.
- **Template is byte-exact with live id-5** (`35fa7b66`): first 15,707 bytes md5 `5ad24840a75b6820621a198f37203c16`,
  last 11,402 bytes md5 `00dc68947e30ff3f63493eaac3f4c833` == the committed `tmpl_prefix.txt`/`tmpl_suffix.txt`
  (LF). So you may **reuse the committed templates** (normalise to LF) or re-run `dissect.py` on live id-5 — either way the UI matches.

## Steps
1. **Pull `main`** — the toolkit SQL (`01`/`02`/`03`) is already **count-based**; `assemble_leader.py`
   `EXPECT_SEG` is already updated to `180/433/173/19/144/8998` (EXPECT_TOTAL/EXPECT_PH unchanged).
2. **Recompute per PH** — run `sql/01_recompute_per_ph.sql` (replace `__PHNAME__`) once per holder →
   `raw/<PH>.json`. **utharsika (1578)** will time out on the two-window query → use
   `sql/02_recompute_category_split.sql` per category and merge. **Jasmini (1220)** — watch; split if it times out.
3. **Alloc** — `sql/04_alloc_counts.sql` → `alloc.json` (or keep the committed ALLOC map).
4. **Build** — set `BASE` in `py/assemble_leader.py` + `py/build_per_ph.py`; run both.
   `assemble_leader` **hard-asserts** total 9,947 + the count-based seg gate + per-PH counts; a wrong number aborts.
5. **Validate** — run `sql/03_validate_counts.sql` (count-based, `rn 2..5`); the whole-portfolio
   distribution must equal **180/433/173/19/144/8998** and every per-PH count must match the HTML.
6. **Publish** (writes, `temp_user`, backup-first + md5-verified in-transaction):
   `py/push_leader.py` (id 5) then `py/push_all_ph.py` (30 rows — all **UPDATE**, no INSERT/DELETE this cycle).
   **Never** `DROP/CREATE`. Back up id-5 (`35fa7b66`) and each per-PH row before overwrite.

## Notes
- `GENERATED` label stays **"10 Jul 2026"** / period **"2026-07"** to keep "only data changed" — bump to
  13 Jul only if Bietrick wants the regeneration date shown.
- The stale `analytics.ph_segment_report` backfill is a **separate** open item; if you backfill it, use the
  **count-based** engine + the **same window** so the table agrees with these new dashboards.
