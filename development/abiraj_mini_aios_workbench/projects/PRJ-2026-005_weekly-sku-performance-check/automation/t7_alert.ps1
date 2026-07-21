param([int]$Rc = 0)
$Dir = $PSScriptRoot
$desktop = [Environment]::GetFolderPath('Desktop')
$alert   = Join-Path $desktop 'T7_ALERT_FAILED.txt'
if ($Rc -eq 0) { if (Test-Path $alert) { Remove-Item $alert -Force }; exit 0 }
$log = Join-Path $Dir 't7_run.log'
$run = Join-Path $Dir 'run_t7_weekly.bat'
Set-Content -Path $alert -Encoding utf8 -Value @(
  'T7 WEEKLY SKU PERFORMANCE CHECK FAILED',
  ('When      : ' + (Get-Date)),
  ('Exit code : ' + $Rc + '   (2 = a data check failed · 3 = database · 4 = publish rolled back)'),
  '',
  'Nothing was published - the last good dashboard is still live for Thuwaraga.',
  'Fix: open the run log (newest error at the bottom), then re-run:',
  ('  Log    : ' + $log),
  ('  Re-run : ' + $run),
  '',
  'This file clears itself automatically after the next successful run.'
)
try { msg * /TIME:0 'T7 weekly SKU performance check FAILED - see T7_ALERT_FAILED.txt on your Desktop.' } catch {}
exit 0
