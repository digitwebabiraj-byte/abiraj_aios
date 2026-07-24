param([int]$Rc = 0)
$Dir = $PSScriptRoot
$desktop = [Environment]::GetFolderPath('Desktop')
$alert   = Join-Path $desktop 'ZSFO_ALERT_FAILED.txt'
if ($Rc -eq 0) { if (Test-Path $alert) { Remove-Item $alert -Force }; exit 0 }
Set-Content -Path $alert -Encoding utf8 -Value @(
  'ZSFO WEEKLY ZERO-SALES RUN FAILED (Utharsika)',
  ('When      : ' + (Get-Date)),
  ('Exit code : ' + $Rc + '   (2 = a gate failed / DB unreachable - nothing was published)'),
  '',
  'Nothing was published - last week''s dashboard is still live.',
  ('Log : ' + (Join-Path $Dir 'zsfo_run.log')),
  ('Re-run once the DB is healthy : ' + (Join-Path $Dir 'run_zsfo_weekly.bat')),
  '',
  'This file clears itself automatically after the next successful run.'
)
try { msg * /TIME:0 'ZSFO weekly zero-sales run FAILED - see ZSFO_ALERT_FAILED.txt on your Desktop.' } catch {}
exit 0
