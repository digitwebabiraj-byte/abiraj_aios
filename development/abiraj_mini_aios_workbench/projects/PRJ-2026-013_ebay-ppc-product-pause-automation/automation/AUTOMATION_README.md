# EPPA eBay PPC Pause Automation — automation (REQ-15-D02)

Weekly refresh of the REQ-15-D01 pause report. It **recommends** pauses; it does **not** pause
anything. No campaign, listing or bid is ever written to.

## What runs, and when

| | |
|---|---|
| Task | `EPPA_Weekly_Pause_Report` |
| When | **Mondays 11:00** |
| Anchor | the most recent complete day of PPC data |
| Reads | `ledsone` — READ-ONLY (the RAW DB, **not** the warehouse: the warehouse hides SMART campaigns) |
| Writes | one row in `tech_team_outputs.ph_task` (`eppa`) |
| Entry | `run_eppa_weekly.bat` → `eppa_weekly_run.py` → `eppa_publish_ph_task.py` |

First live run 2026-07-21: **45 campaigns · 15 paused · 8 stock-flagged · £1,403.54 spend-at-risk**,
published as ph_task id 405.

## Credentials

Read from the **global credential store**
(`05_documentation/capability/shared_db_credentials/`). A local `eppa_secrets.bat` still wins if
present, but is no longer required — the runner aborts before writing if either password is
missing, so a blank credential can never publish a half-empty report.

## The gates (all fail closed, before anything on disk or in `ph_task` is touched)

| Gate | Catches |
|---|---|
| Missing credential env var | a partial run against one database |
| 0 campaigns returned | an empty pull replacing a good report |
| Below `MIN_CAMPAIGNS` (20) | a broken pull dressed up as a quiet week |
| **Collapse vs last good run** (`MAX_DROP`, 40%) | a feed that half-empties — invisible to a fixed floor |
| Total 30-day spend = 0 | the advertising join silently returning nothing |
| **md5 of the stored row vs the file** | a truncated or corrupted payload |

The collapse guard is this project's own invention and has since been **backported to T7, EPC,
EBPD and ERA** — a gradual erosion (2,166 listings → 400) clears an absolute floor but trips this.

`version_status` is deliberately **not** asserted: recipients marking their own task `completed`
is normal workflow, and asserting `released` would roll back every future publish.

## Everyday use

```bat
run_eppa_weekly.bat            :: a real refresh, now
check_status.bat               :: last run + next scheduled run
```

`eppa_status.json` holds one machine-readable record of the last run (counts, spend-at-risk,
`ph_task` id, html md5). On failure `eppa_alert.ps1` raises a Desktop alert and the previous
report stays live.

## Known data traps (from the build — do not re-derive)

- **Use the RAW `ledsone` DB, not the warehouse.** The warehouse hides SMART campaigns entirely.
- **CPS campaigns log £0 spend** — cost-per-sale fees land in `accounting`, not the campaign feed.
- **89% of listings are multi-SKU**, so a campaign rarely maps to one product.
- **`ebay_listings.status` is 99.4% NULL** — it cannot be used as a live/ended filter.
- **Unbridged ≠ zero stock.** A SKU that fails to bridge is unknown, not out of stock; the report
  reports it as No-Stock-Data, never as 0.

## Related

Same five-stage pattern as PRJ-2026-008/010/011/012;
method doc `05_documentation/capability/2026-07-15_monthly-report-automation-pattern.md`.
