# Count-based conversion — LIVE PUBLISH record (2026-07-13)

**What:** regenerated the 2026-07 PH dashboards under the **count-based conversion rule**
(Bietrick-approved 2026-07-10, `a.cvr>=b.bv` → `a.conv>=b.bcv`) and published all 31 rows live to
`tech_team_outputs.ph_task`. **Same window, same roster, same UI — only the segment data changed.**

- **Window:** weeks ending 2026-06-06/13/20/27 (rn 2..5) — identical to the D10 rate-based build.
- **Universe:** 9,947 ASINs / 30 PHs (unchanged). **No roster change** — 31 rows, all UPDATE, 0 INSERT/DELETE.
- **Distribution:** rate-based `HHH 42 · HHL 580 · HLH 173 · LHH 10 · LLH 626 · LLL 8516`
  → **count-based `HHH 180 · HHL 433 · HLH 173 · LHH 19 · LLH 144 · LLL 8998`**.
  Movement recomputed: IMPROVED 495 · DECLINED 466 · SAME 8797 · NEW 189.
- **Method:** read-only recompute via direct psycopg2 (`temp_user`), per-PH engine `01`; **utharsika
  (1,578) via the category-split** (`02` logic, 2 categories, 0 span) — the whole-PH two-window query
  exceeds the ~300s cap. HTML assembled from the byte-verified live template (LF). Publish = one atomic
  transaction, **backup-first + in-transaction md5-verify** (a `print`-encoding error first triggered a
  clean ROLLBACK with zero rows changed; re-run committed all 31).
- **Backups:** current (rate-based) live rows saved before overwrite — `scratchpad/rebuild/backups_live/`
  (31 files; leader old md5 `35fa7b66`). Restorable.

## Before → after md5 (all 31 rows)

| id | PH | before (rate) | after (count) |
|--:|---|---|---|
| 5 | LEADER (Bietrick) | 35fa7b66 | **a3043461** |
| 58 | Abinayaa | 7a5b2206 | f951b77c |
| 59 | Arudchelvi | 6b0fbd77 | 0a94ccd4 |
| 60 | Dilani | c4e0e19d | 3c57899e |
| 61 | Illakkiya | 589860db | c71b7c33 |
| 62 | Jasmini | d95cf070 | 06477c1e |
| 63 | Jubista | da4207f3 | 5be3b4b2 |
| 64 | Nithushana | 3c9578c4 | 5e7c482b |
| 66 | Renuha | 111dcf04 | 5a08d960 |
| 67 | Saranya | faa04f83 | 383ba569 |
| 68 | Shanthini | e396448d | f8ff10df |
| 69 | Tharshana | 05afe4d4 | fb074d4c |
| 70 | Tharsiga(nelli) | b5672f12 | 495f407b |
| 71 | Tharsika(jaffna) | 03738a00 | 5fef82d4 |
| 72 | Theepana | 29a1e92c | eddcaf57 |
| 73 | Thojika | 58c03978 | 2110054a |
| 74 | mothajini | 2d56d8d6 | 6be429b4 |
| 75 | paulr | 5f1fbadf | 49d97a09 |
| 76 | prasath | 4cf0b793 | 5171ee84 |
| 77 | preethi | 5973ed16 | 1c26870b |
| 78 | shimee | f713596a | 8b5ba1d6 |
| 80 | thuwaraga | 5ceb1b21 | ef021d6d |
| 81 | utharsika | b51dbe53 | 0c9fe4dc |
| 145 | Akalika | 8ae6642b | 48d2eb40 |
| 146 | Akanila | d8c84671 | 467f52bb |
| 147 | Dilakshiga | b0d6a900 | 64b853fa |
| 148 | Jathisha | f480c7c4 | 75d06862 |
| 149 | Ramsika | 61440dd7 | e2905727 |
| 150 | Sarbavi | ad060220 | 7296abc6 |
| 151 | thanusha | 8cfdae52 | 13f43652 |
| 152 | Vaishnavi | 0a9e6e94 | f1696c4a |

## Carried / open
- ⚠ **`analytics.ph_segment_report` is now further out of sync** — it still holds the old 8,149 build; the
  live dashboards are correct count-based HTML snapshots but the source table needs the count-based engine
  re-run (privileged `postgres` session; TRUNCATE+INSERT, keep the ~11 dependent views). See D10 open item.
- ⚠ **Bietrick awareness:** the count rule moved **~482 products LLH → LLL ("Dead Horses")**; he approved
  off the Champions example (HHL→HHH). Confirm he's seen the Dead-Horses side.
- 🔒 The `temp_user` DB password was shared in chat this session — consider rotating it. It was **not**
  written to any repo file.
