# FMP automation — REQ-23-D01 weekly refresh

Weekly refresh of the **Fast Moving Products (Germany)** report — regenerates the Excel workbook and
the HTML dashboard from the **raw `mcp.ledsone` DB**. **No `ph_task` publish** (held pending Mahima's
audience/sign-off); this job only refreshes the two deliverables in `evidence/final_outputs/`.

## Schedule
Windows Task **`FMP_Weekly_Fast_Moving_Products`** — **every Tuesday 10:30** (a free slot, clear of the
fleet: Mon 11:00 EPPA, Wed 10:00 EPPR, Wed 11:30 EPNS, Thu 11:00 T7, daily 09:05 DST, 3rd 09:00 SEG).

## Files
| File | Role |
|---|---|
| `fmp_weekly_run.py` | Orchestrator (fail-closed): fetch raw → gate → build xlsx + dashboard → publish to `evidence/final_outputs`. |
| `run_fmp_weekly.bat` | Sources `fmp_secrets.bat`, runs the orchestrator, logs to `fmp_run.log`. |
| `register_fmp_task.ps1` | Registers the Windows scheduled task. Re-run to (re)create it. |
| `fmp_secrets.template.bat` | Credential template → copy to `fmp_secrets.bat` (git-ignored) and fill `LED_PGPASSWORD`. |
| `../sql/REQ-23_.../fmp_fetch_raw.py` | Raw psycopg2 fetch (order_management + inventory) → `fmp_payload.json`. |
| `../sql/REQ-23_.../build_fmp_d01.py` · `gen_dashboard.py` | Render Excel / dashboard from the payload. |
| `../sql/REQ-23_.../fmp_payload_curated.json` | Curated Product-Name/Category labels carried by SKU (numbers stay raw). |

## Fail-closed gates
- **Credential check** — aborts if `LED_PGHOST/USER/PASSWORD` are unset.
- **Row-floor** — each channel + combined must have ≥ 10 ranked rows, else abort.
- **Collapse guard** — aborts if a channel's fresh row count < 60% of the last good run.
- On any failure: outputs are **left untouched** (last-good preserved), and `~/Desktop/FMP_ALERT.txt` is written.
- Success writes `fmp_status.txt` + `fmp_last_good.json`; git-ignored run artefacts.

## Manual run / setup
```bat
:: one-time: create the real secrets file and register the task (PowerShell)
copy fmp_secrets.template.bat fmp_secrets.bat   & rem then edit LED_PGPASSWORD
powershell -ExecutionPolicy Bypass -File register_fmp_task.ps1
:: manual test
run_fmp_weekly.bat
```

## Notes / traps
- **Data source = raw `mcp.ledsone`** (`order_management` + `inventory`); Germany = `market_place='10'`,
  channels via `sub_source.source_id` (1/2/3), status `Completed`, rolling 30/90-day windows.
- **Windows/OneDrive `0xC000013A` "never ran" trap** — if the task shows LastTaskResult `0xC000013A`,
  it's the OneDrive-in-path issue seen across the fleet; re-run manually and/or move the repo out of OneDrive.
- **Derived Trend/Action/Final-Decision rules** are still defaults pending Mahima — unchanged by automation.
- To start publishing to `ph_task`, add a publish step only after Mahima's audience/team is confirmed.
