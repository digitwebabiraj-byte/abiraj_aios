param([int]$Rc = 0)
$Dir = $PSScriptRoot
$desktop = [Environment]::GetFolderPath('Desktop')
$alert   = Join-Path $desktop 'EPC_ALERT_FAILED.txt'
if ($Rc -eq 0) { if (Test-Path $alert) { Remove-Item $alert -Force }; exit 0 }
$log = Join-Path $Dir 'epc_run.log'
$run = Join-Path $Dir 'run_epc_weekly.bat'
Set-Content -Path $alert -Encoding utf8 -Value @(
  'EPC WEEKLY PRICE CHECKER FAILED',
  ('When      : ' + (Get-Date)),
  ('Exit code : ' + $Rc),
  '',
  'Nothing was published - the last good dashboard is still live.',
  'Fix: open the run log (newest error at the bottom), then re-run:',
  ('  Log    : ' + $log),
  ('  Re-run : ' + $run),
  '',
  'This file clears itself automatically after the next successful run.'
)
try { msg * /TIME:0 'EPC weekly price checker FAILED - see EPC_ALERT_FAILED.txt on your Desktop.' } catch {}
exit 0
