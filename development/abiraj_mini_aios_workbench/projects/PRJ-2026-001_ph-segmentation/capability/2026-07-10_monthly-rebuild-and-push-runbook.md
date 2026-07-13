# PH ASIN Segmentation — Monthly Rebuild & Dashboard Push (Repeatable Runbook)

> **Purpose.** Rebuild the PH-ASIN segmentation dashboards from live data and push them to the
> team database — the **leader** (all-PH) view and **one dashboard per Portfolio Holder** — so
> everyone sees current, correct numbers. Written **2026-07-10** from the run that corrected the
> July report (8,149/24 → **9,947 ASINs / 30 PHs**) and pushed all 31 rows.
>
> **Toolkit (all scripts referenced here):** `2026-07-10_monthly_rebuild_toolkit/`
> **Supersedes** the older `2026-07-06_next-cycle-run-checklist.md` for the "how" (that one assumed
> the in-DB engine routine; this one is the read-only recompute + direct push that actually shipped).

---

## 0. When to run
- **Monthly**, after the new window's 4 complete weeks are loaded in `public.traffic_data`; **or**
- **Any time the database is corrected** and the published dashboards need to match again (that was the 2026-07-10 trigger).

## 1. Tools & access
- **Read-only** recompute/validation → **Postgres MCP** connector (`execute_sql`).
- **Writes** (push/insert/delete) → direct **psycopg2 as `temp_user`** (`host 149.28.134.54:5435`,
  `order_management_copy`). Password from **env var `PGPASSWORD`**; the value is only in
  `Downloads/temp_user 1.py` — never in the repo.
- Python + `psycopg2-binary`.

---

## 2. FIRST DECISION — which window?  (this sets every number)
The engine looks at **the last 4 complete Saturday-ending weeks** vs the previous 4. `rn 1` = newest week.

| Goal | cur / prev / prior weeks | report_period | Use when |
|---|---|---|---|
| **Correct the current published report** | `rn 2..5 / 6..9 / 10..13` (drops the just-loaded newest week so the window == the published one) | stays the same (e.g. 2026-07) | data was fixed; you want the *same* report right |
| **Normal monthly roll-forward** | `rn 1..4 / 5..8 / 9..12` | next month (window_end month +1) | new cycle |

> 2026-07-10 used the **correction** window (`rn 2..5` = weeks ending 6/13/20/27 Jun = 31 May–27 Jun).
> The `rn` offsets are the ONLY thing that encodes this choice — set them in `sql/01`, `sql/02`, `sql/03`.

---

## 3. THE RUN — 6 steps

### Step 1 — Correct holder names (roster)  ·  `sql/00_roster_names.sql`  (read-only)
Join `user` + `ph_categories` + `ph_cate_products` → the unique holder names. **Use each name
EXACTLY, character-for-character** (per `Downloads/PH_assigned_user_Standard.docx`). This set drives
everything. *(2026-07-10: 30 holders.)*

### Step 2 — Recompute each PH (read-only)  ·  `sql/01_recompute_per_ph.sql`
Run once per holder (replace `PHNAME`). Returns that PH's rows (segment, movement, benchmarks, sku)
+ cats as JSON. Save each to `raw/<PH>.json` as `{"nrows":N,"rows":[…],"cats":[…]}`.
- **This replays the strict-rank engine as pure SELECTs** — it does **not** write `analytics.ph_segment_report`.
- **Big PH times out?** (utharsika 1578 did): use `sql/02_recompute_category_split.sql` — one category
  at a time (safe: benchmark is per PH+category, 0 ASINs span categories), then merge and recompute
  the per-PH rank in Python.
- Large results auto-save to a `tool-results/*.txt` file as a Python-repr string → parse with
  `ast.literal_eval(json.load(open(path))["result"][0]["text"])`.

### Step 3 — Allocated counts  ·  `sql/04_alloc_counts.sql`  → `alloc.json`
The "Allocated" card number per PH. Save as `{"<PH>": n, …}`.

### Step 4 — Build the HTML (no DB)  ·  `py/assemble_leader.py` + `py/build_per_ph.py`
- `dissect.py` first, against the **current live id-5 HTML**, to refresh `tmpl_prefix/suffix` so the UI
  matches production exactly (byte-exact reconstruct — only the `const D={…}` data changes).
- `assemble_leader.py` → the all-PH leader HTML (embeds all PHs; dropdown + category filter).
- `build_per_ph.py` → one **locked single-PH** HTML per holder (same UI, auto-opens on that person).
- Both carry **hard checksums** (total ASINs, per-segment, per-PH) — a wrong number aborts the build.

### Step 5 — VALIDATE against live DB  ·  `sql/03_validate_counts.sql`
Re-pull the whole-portfolio counts fresh, then compare **cell-by-cell** to the numbers embedded in the
built HTML (total, 6 segments, roster, every per-PH count). Must be 100% match before pushing.
*(2026-07-10: total 9,947; HHH 42 · HHL 580 · HLH 173 · LHH 10 · LLH 626 · LLL 8516 — matched.)*
> ⚠ **That distribution is the RATE-based D10 build.** The toolkit SQL (`01`/`02`/`03`) was switched to the
> **COUNT-based** conversion rule (Bietrick-approved 2026-07-10) — so the **next** rebuild's segment counts
> **will differ** (some HHL Leaky Buckets → HHH Champions). Do **not** validate a count-based build against
> these numbers; re-checksum the freshly built count-based HTML. Old rate rule is preserved in each SQL header.

### Step 6 — PUSH to `tech_team_outputs.ph_task`  (writes, temp_user)
**Always back up first; verify md5 inside the transaction.**
1. **Leader** → `py/push_leader.py` — backs up id 5, UPDATEs `html_content`, verifies stored md5 == file md5.
2. **Per-PH** → `py/push_all_ph.py`:
   - refresh the `EXISTING` id↔assigned_user map (`SELECT id,assigned_user FROM ph_task WHERE project_code='ph-asin'`);
   - **UPDATE** rows whose `assigned_user` matches a current holder (back each up first);
   - **INSERT** new holders — `task_id='ph-asin-<period>-<lowername>'`, phase 4, version 1, `released`,
     and **`assigned_user_team='ph_priors'`** (REQUIRED — not in the sample DDL);
   - one atomic transaction; every roster row md5-verified before commit.
3. **Departed holders** → `py/delete_departed.py` — if the dashboard shows more cards than the roster,
   back up the full rows and DELETE the leavers. *(2026-07-10: deleted Poovitha #65 + thanucha #79 → 33→31 cards.)*

---

## 4. Backups (all under `evidence/final_outputs/REQ-05_ph-asin-segmentation/`)
- `<date>_ph_task_id5_PRE-UPDATE_backup.html` — leader before overwrite.
- `<date>_per_ph_PRE-UPDATE_backups/<id>_<name>.html` — every per-PH row before overwrite.
- `<date>_deleted_rows_backup/ph_task_<id>_<name>.json` — full rows of deleted holders (re-INSERTable).

## 5. Verify it's live
`SELECT id,assigned_user,task_id,length(html_content),assigned_user_team,updated_at FROM ph_task WHERE project_code='ph-asin' ORDER BY id;`
Expect **1 leader + N per-PH** (N = roster size), all `assigned_user_team='ph_priors'`, dated today.
*(2026-07-10: 31 rows.)*

---

## 6. GOTCHAS (the things that cost time on 2026-07-10)
- **Timeouts.** MCP `execute_sql` dies > ~1300 ASINs or on the full two-window query. Go **per-PH**;
  category-split the giants. The `sku` full-history scan and the `order_date::date` cast are the cost
  traps — restrict `asin IN (SELECT ref_id FROM ca)` and use `order_date >= d AND < d+1`.
- **`assigned_user_team`.** Not in the sample DDL; all ph-asin rows use `'ph_priors'`. INSERTs that skip
  it leave NULL → the card's team is blank. `push_all_ph.py` now sets it.
- **Names.** Exact, character-for-character from `sql/00` (e.g. `Tharsiga(nelli)`, lowercase `paulr`).
- **thanucha ≠ thanusha.** thanucha **left**; thanusha is a **different, new** employee — never merge them.
- **Repr parsing.** Big MCP results are saved Python-repr text, not JSON — `ast.literal_eval`, not `json.loads`.
- **Read-only vs write.** The recompute never touches `analytics.ph_segment_report`. Rebuilding that
  table (DROP/CREATE) is a separate authorised DB-session write.

## 7. OPEN ITEMS (carried)
- **`analytics.ph_segment_report` still stale** (old 8,149 build) — the source table needs the engine
  re-run to match the dashboards. **This CANNOT be done via the `temp_user` write path** (verified
  2026-07-10: `temp_user` has **NO** privilege on the `analytics` schema — no CREATE/USAGE/INSERT; the
  table is owned by `postgres`), AND the table has **~11 dependent `staging_ai` views**
  (v_ph_benchmark_validation_engine_2026_07, v_ph_identity_assignment_audit_2026_07,
  v_ph_category_mapping_audit_2026_07, v_ph_metric_semantic_validation_2026_07,
  v_ph_paulr_466_asin_value_score_2026_07, v_ph_benchmark_reconciliation_jasmini_2026_07,
  v_ph_paulr_top30_benchmark_summary_v1, …) — so a plain `DROP TABLE` **fails**, and `DROP … CASCADE`
  would **delete those views**. **Safe method (privileged `postgres` session ONLY):** (1) back up —
  `CREATE TABLE analytics.ph_segment_report_backup_<date> AS SELECT * FROM analytics.ph_segment_report;`
  (2) **`TRUNCATE` + `INSERT INTO`** the existing table (keeps the 11 views alive) using the engine
  logic **pinned to the SAME window as the dashboards** (correction = `rn 2..5`); (3) verify new counts
  == dashboards (9,947 / 30 / 42·580·173·10·626·8516) before accepting. **Never `DROP/CREATE` this table.**
  **NOTE (2026-07-10 conversion change):** those counts match the *rate-based* live dashboards. The toolkit
  engine is now *count-based*; if the count-based rule is adopted, rebuild the **dashboards and the table
  together** to the NEW distribution (they must agree). The rate figures above apply only to backfilling the
  table to match the *existing, unchanged* live dashboards.
- **Roster sign-off** — the 30-PH roster (7 new, Poovitha/thanucha out) is live for Bietrick to ratify.
- Monthly in-DB routine still builds the OLD UI (from D06–D09 notes) — align before any auto-run.
