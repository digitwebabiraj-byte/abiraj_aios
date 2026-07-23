param([string]$Reason = "Daily Sales Track run failed")

# Drops a plain-text alert on the Desktop when the daily run fails. A silent failure
# is the real danger: the report simply stops being today's and nobody notices,
# because the previous day's copy is still sitting there looking current.

$stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$file  = Join-Path ([Environment]::GetFolderPath("Desktop")) "DAILY_SALES_TRACK_FAILED.txt"

$body = @"
DAILY SALES TRACK (REQ-17-D02) DID NOT RUN CLEANLY
$stamp

Reason: $Reason

WHAT THIS MEANS
  The four ph_task rows (422-425) still hold the PREVIOUS day's report.
  It is stale, not wrong - the job fails closed and never publishes a bad pull.

WHAT TO CHECK
  1. automation\dst_run.log      - the full trace of the failed run
  2. automation\dst_status.txt   - one line per run, newest at the bottom
  3. Can this machine still reach both databases?
       ledsone            207.148.78.148:5432
       order_management   149.28.134.54:5435
  4. Is dst_secrets.bat still present and correct?

TO RE-RUN BY HAND
  cd "$PSScriptRoot"
  run_dst_daily.bat --dry-run     (safe: rebuilds and gates, publishes nothing)
  run_dst_daily.bat               (publishes)

Delete this file once resolved.
"@

Set-Content -Path $file -Value $body -Encoding utf8
