param(
  [int]$Rc = 0
)
$Dir = $PSScriptRoot   # this script lives in the automation folder; resolve paths from here
# Desktop failure alert for the EBPD weekly dashboard.
#   Rc = 0  -> success: clear any stale alert file.
#   Rc != 0 -> failure: drop a visible alert on the Desktop + best-effort popup.
$desktop = [Environment]::GetFolderPath('Desktop')
$alert   = Join-Path $desktop 'EBPD_ALERT_FAILED.txt'

if ($Rc -eq 0) {
    if (Test-Path $alert) { Remove-Item $alert -Force }
    exit 0
}

$log = Join-Path $Dir 'ebpd_run.log'
$run = Join-Path $Dir 'run_ebpd_weekly.bat'
$lines = @(
  'EBPD WEEKLY DASHBOARD FAILED',
  ('When      : ' + (Get-Date)),
  ('Exit code : ' + $Rc),
  '',
  'Fix: open the run log (newest error at the bottom), then re-run the dashboard:',
  ('  Log    : ' + $log),
  ('  Re-run : ' + $run),
  '',
  'This file clears itself automatically after the next successful run.'
)
Set-Content -Path $alert -Value $lines -Encoding utf8
try { msg * /TIME:0 'EBPD weekly dashboard FAILED - see EBPD_ALERT_FAILED.txt on your Desktop.' } catch {}
exit 0
