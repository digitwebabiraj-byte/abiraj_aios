param([int]$Rc = 0)
$Dir = $PSScriptRoot
$desktop = [Environment]::GetFolderPath('Desktop')
$alert   = Join-Path $desktop 'SEG_ALERT_FAILED.txt'
if ($Rc -eq 0) { if (Test-Path $alert) { Remove-Item $alert -Force }; exit 0 }
Set-Content -Path $alert -Encoding utf8 -Value @(
  'PH ASIN SEGMENTATION MONTHLY RUN FAILED',
  ('When      : ' + (Get-Date)),
  ('Exit code : ' + $Rc + '   (2 = a gate failed / DB unreachable - nothing was published)'),
  '',
  'Nothing was published - the previous month''s dashboards are still live.',
  'This runs MONTHLY (the 3rd), so a silent failure would otherwise go unnoticed for a month.',
  ('Log : ' + (Join-Path $Dir 'seg_run.log')),
  ('Re-run once the DB is healthy : ' + (Join-Path $Dir 'run_seg_monthly.bat')),
  '',
  'This file clears itself automatically after the next successful run.'
)
try { msg * /TIME:0 'PH ASIN Segmentation monthly run FAILED - see SEG_ALERT_FAILED.txt on your Desktop.' } catch {}
exit 0
