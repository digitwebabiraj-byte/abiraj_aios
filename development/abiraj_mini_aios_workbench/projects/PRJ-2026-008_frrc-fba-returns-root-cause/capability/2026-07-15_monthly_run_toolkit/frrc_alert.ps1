param([int]$Rc = 0)
$Dir = $PSScriptRoot
$desktop = [Environment]::GetFolderPath('Desktop')
$alert   = Join-Path $desktop 'FRRC_ALERT_FAILED.txt'
if ($Rc -eq 0) { if (Test-Path $alert) { Remove-Item $alert -Force }; exit 0 }
$log = Join-Path $Dir 'logs'
$run = Join-Path $Dir 'run_frrc_monthly.bat'
Set-Content -Path $alert -Encoding utf8 -Value @(
  'FRRC MONTHLY FBA RETURNS REPORT FAILED',
  ('When      : ' + (Get-Date)),
  ('Exit code : ' + $Rc + '   (1 = credential · 2 = a data check failed · 3 = database · 4 = publish rolled back)'),
  '',
  'Nothing was published - the last good per-PH dashboards are still live.',
  'This runs MONTHLY (day 8), so a silent failure would otherwise go unnoticed for a month.',
  'Fix: open the newest file in the log folder, then re-run:',
  ('  Logs   : ' + $log),
  ('  Re-run : ' + $run),
  '',
  'This file clears itself automatically after the next successful run.'
)
try { msg * /TIME:0 'FRRC monthly FBA returns report FAILED - see FRRC_ALERT_FAILED.txt on your Desktop.' } catch {}
exit 0
