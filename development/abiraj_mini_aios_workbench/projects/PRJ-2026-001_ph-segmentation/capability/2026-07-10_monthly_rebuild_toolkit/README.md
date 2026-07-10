# Monthly Rebuild Toolkit — PH ASIN Segmentation

Reusable scripts + templates that produced the **2026-07-10 corrected rebuild** (leader
dashboard + 30 per-PH dashboards, all pushed to `tech_team_outputs.ph_task`). Use these every
cycle. The **full step-by-step is the runbook**:
`../2026-07-10_monthly-rebuild-and-push-runbook.md` — read that first.

## Files

| File | What it does |
|---|---|
| `sql/00_roster_names.sql` | Correct PH holder names (the assigned_user standard) — join `user`+`ph_categories`+`ph_cate_products`, unique names, use EXACTLY. |
| `sql/01_recompute_per_ph.sql` | Read-only recompute of ONE PH (segment + movement + benchmarks + sku) → JSON. Replace `PHNAME`. Run once per PH. |
| `sql/02_recompute_category_split.sql` | Fallback for a PH too big to run whole (e.g. utharsika) — one category at a time. |
| `sql/03_validate_counts.sql` | Whole-portfolio counts in one query — the authoritative totals to validate the HTML against. |
| `sql/04_alloc_counts.sql` | Allocated/roster count per PH (the "Allocated" card). |
| `tmpl/dissect.py` | Split the CURRENT live leader HTML into `tmpl_prefix.txt` + `tmpl_suffix.txt` (template shell). Re-run against the live id-5 so the UI always matches production. |
| `tmpl/tmpl_prefix.txt`, `tmpl_suffix.txt` | Leader template shell (everything except the `const D={…}` data). Byte-exact reconstruct. |
| `tmpl/tmpl_suffix_single.txt` | Per-PH suffix — same as `tmpl_suffix` plus a one-line auto-select so a single-PH file opens straight on that person. |
| `py/assemble_leader.py` | Build the all-PH leader HTML from `raw/<PH>.json` + templates, with hard checksums. |
| `py/build_per_ph.py` | Build one locked single-PH HTML per holder from `raw/<PH>.json` + `alloc.json`. |
| `py/push_leader.py` | Back up + push the leader HTML to `ph_task` id 5, md5-verified. |
| `py/push_all_ph.py` | Back up + push the 30 per-PH HTMLs (UPDATE existing by assigned_user, INSERT new incl. `assigned_user_team='ph_priors'`), one transaction, md5-verified. |
| `py/delete_departed.py` | Back up + delete `ph_task` rows for holders who have LEFT the roster. |

## Credentials — never committed
The DB write path is a **direct psycopg2 connection as `temp_user`** (host/port/db are in the
scripts; **password is read from the `PGPASSWORD` env var**). The actual password lives only in
`C:\Users\digit\Downloads\temp_user 1.py` on Abiraj's machine — do not paste it into any repo file.
Set it per run:  PowerShell `$env:PGPASSWORD="…"`  ·  bash `export PGPASSWORD="…"`.
(The read-only recompute/validation SQL runs through the **Postgres MCP** connector, not temp_user.)

## What to refresh EACH cycle (don't run blind)
1. **Window** — the Saturday week-ending dates / `rn` offsets (see runbook §2 and the header of `03`).
2. **Roster** — re-run `00`; the holder set changes (people join/leave).
3. **`EXISTING` id-map + `ROSTER`** in `push_all_ph.py` — query `ph_task WHERE project_code='ph-asin'`
   for the current id ↔ assigned_user map before pushing.
4. **Period-specific literals** — `task_id` prefix (`ph-asin-2026-07-…`), description window text,
   `PERIOD`/`GENERATED`, and all dated backup folders.
5. **Paths** — the `BASE`/`NEW`/`BKDIR` paths at the top of each `.py` (session working dir differs each run).

## Golden rules (learned the hard way — see runbook §Gotchas)
- Recompute is **read-only**; the engine table rebuild (`analytics.ph_segment_report`) is a separate DB-session write.
- MCP `execute_sql` **times out > ~1300 ASINs / two windows** — go **per-PH**; category-split the giant ones.
- Avoid the `sku` full-history scan and the `order_date::date` cast (index traps) — restrict `asin IN (…)`, use `order_date >= d AND < d+1`.
- Every live write is **backup-first + md5-verified in-transaction**.
- INSERTs MUST set **`assigned_user_team='ph_priors'`** (not in the sample DDL).
- Use holder names **exactly** as `00` returns them (character-for-character).
