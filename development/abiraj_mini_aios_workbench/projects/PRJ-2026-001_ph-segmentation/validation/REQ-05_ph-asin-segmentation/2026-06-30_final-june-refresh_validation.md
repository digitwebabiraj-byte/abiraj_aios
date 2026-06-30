# PH Segmentation — Final-June Refresh Validation (30 June 2026)

## Project ID

PRJ-2026-001_ph-segmentation

## Task ID

REQ-05_ph-asin-segmentation (second delivery/refresh increment, 2026-06-30)

> Delivery record:
> `handover/REQ-05_ph-asin-segmentation/2026-06-30_delivery_final-june-refresh-and-data-quality-validation.md`.

## Validation Date

2026-06-30

## Validation Type

READ-ONLY documentation audit in the workbench. No SQL executed, no database queried, no automation
touched. The substantive data validation was performed by Abiraj in the live Claude Chat session; this
record audits and files those reported results against the evidence discipline.

## Evidence Source

Reported by Abiraj on 2026-06-30 (chat session recap). No separate signed reviewer artifact and no
saved execution evidence (rebuilt HTML, SQL diff, DB result set, screenshots) were imported into the
repo. The pre-refresh baseline is cross-checked against in-repo files.

## Method

Cross-checked each reported claim against files present in the project tree and against
`SYSTEM_REFERENCE.md`. No live system was contacted from the workbench.

## Claim-by-Claim Result

| # | Claim | Verdict | Basis |
|---|---|---|---|
| 1 | Pre-refresh distribution 77/479/157/17/349/6,776 = 7,855 | **VERIFIED** | `SYSTEM_REFERENCE.md` §7; 2026-06-24 + 2026-06-26 HTML `segTotal` |
| 2 | Upstream window refilled to 239,353 rows / 15 windows (Apr 2025–Jun 2026); no `pg_cron`; wipe-and-reload | REPORTED_BY_ABIRAJ | Live DB inspection; DB not queried here |
| 3 | Lineage `traffic_data` → `ph_segment_30days_window` + `analytics.ph_segment` | REPORTED_BY_ABIRAJ | Consistent with `SYSTEM_REFERENCE.md` §10 |
| 4 | Dashboard reads only `tech_team_outputs.ph_task` row 5 HTML; counts in `segTotal`; three layers + banner (24/20) matched | REPORTED_BY_ABIRAJ | Consistent with `SYSTEM_REFERENCE.md` §8; DB not queried |
| 5 | Backups taken before edit (`ph_task_id5_backup_20260630`, `ph_segment_report_backup_20260630`) | REPORTED_BY_ABIRAJ | DB state; not pulled |
| 6 | Engine re-run with one-time forced window selector (one line changed); HTML rebuilt server-side into row 5; description/timestamp updated | REPORTED_BY_ABIRAJ | No SQL diff or rebuilt HTML imported |
| 7 | Post-refresh distribution = 51/426/139/5/440/7,088 = **8,149**; June window 15,608 → 16,378 rows; banner 24/21 | REPORTED_BY_ABIRAJ | Rebuilt HTML not imported |
| 8 | Internal consistency: 0 mismatches across 8,149 rows (segment, movement, CVR, manual-flag, account, benchmark uniformity, duplicates) | REPORTED_BY_ABIRAJ | Recomputed live; not re-run in workbench |
| 9 | Signal vs source: 8/8 (June window) and 10/10 (direct `traffic_data` sum) | REPORTED_BY_ABIRAJ | Recomputed live |
| 10 | Benchmark recompute (thuwaraga/Bulbs): 135 sellers, Imp 2,097, Clk 24.9, CVR 91.46% — matched stored | REPORTED_BY_ABIRAJ | Recomputed live |
| 11 | Four protocol-undefined points are documented engine choices, not errors (66 lateral SAME; zero-click→LOW; conv>clicks→HIGH; HLL→HLH / LHL→HHL) | MIXED | Three already in `SYSTEM_REFERENCE.md` §4/§7/§11 (**VERIFIED in-repo**); the **66 lateral-SAME** treatment is **REPORTED_BY_ABIRAJ** (not yet written down) |
| 12 | Data-quality findings (weekly snapshots; 4-complete-weeks window; universe 8,134=8,134; zero NULLs over 4 June weeks; cross-week attribution examples) | REPORTED_BY_ABIRAJ | Live session + screenshot (weeks 22–26) not imported |

## Protocol Compliance Note

The reported validation is consistent with the canonical protocol and the as-built engine as
described in `SYSTEM_REFERENCE.md` (§3 benchmark, §4 segments + Option B map, §7 classification edges).
No contradiction with the protocol was reported. The benchmark recompute matching the stored values
is the strongest reported check.

## Source-of-Truth Divergence (open)

`SYSTEM_REFERENCE.md` §1/§7 still carry the superseded 7,855 distribution. The 8,149 build supersedes
it but is REPORTED_BY_ABIRAJ. **The reference must not be overwritten until the rebuilt HTML is
imported and checksummed.** Tracked in the delivery record's "Source-of-Truth Note".

## Prohibited-Action Confirmation

- SQL executed (from workbench): NO
- Live database modified (from workbench): NO
- Automation initialised / created / enabled: NO
- New Task IDs minted: NO (kept REQ-05)
- Canonical reference numbers overwritten: NO
- Committed / pushed: NO

## Known Limits

- No 30 June artifact is in-repo, so the refresh, the validation maths and the data-quality findings
  are all REPORTED_BY_ABIRAJ; only the pre-refresh baseline and three of the four edge-case
  interpretations are VERIFIED in-repo.

## Decision

AMBER — end-state recorded faithfully and read-only. The reported checks are internally coherent and
consistent with the protocol, but cannot be upgraded to VERIFIED until the rebuilt HTML, the SQL diff
and a chat link are imported.

## One Next Step

Import the 30 June work products so claims 5–12 can move from REPORTED_BY_ABIRAJ to VERIFIED, then
update `SYSTEM_REFERENCE.md` §1/§7 to the 8,149 build in a governed step.
