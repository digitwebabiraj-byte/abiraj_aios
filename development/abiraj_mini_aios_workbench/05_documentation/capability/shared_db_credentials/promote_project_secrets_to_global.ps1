<#
  Promote an EXISTING project secrets file to GLOBAL (Windows user environment variables),
  so every project's automation inherits the same credentials and no project needs its own copy.

  The values are read and written entirely on THIS machine. They are never printed,
  never logged, and never written into any tracked file.

  Usage (PowerShell, from this folder):
      .\promote_project_secrets_to_global.ps1                     # uses project 11 (EBPD) as the source
      .\promote_project_secrets_to_global.ps1 -Source "C:\path\to\other_secrets.bat"
#>
param(
  [string]$Source = "$PSScriptRoot\..\..\..\projects\PRJ-2026-011_ebay-account-performance-dashboard\automation\ebpd_secrets.bat"
)
$ErrorActionPreference = 'Stop'
$Source = (Resolve-Path $Source).Path
if (-not (Test-Path $Source)) { throw "Source secrets file not found: $Source" }
Write-Host "Reading credentials from: $Source" -ForegroundColor Cyan

# Only these names are promoted. Anything else in the file is ignored.
$allow = 'LED_PGHOST','LED_PGPORT','LED_PGDATABASE','LED_PGUSER','LED_PGPASSWORD',
         'PGHOST','PGPORT','PGDATABASE','PGUSER','PGPASSWORD'

$set = @(); $skipped = @()
foreach ($line in Get-Content $Source) {
    if ($line -match '^\s*set\s+"?([A-Za-z_][A-Za-z0-9_]*)=(.*?)"?\s*$') {
        $name = $Matches[1].ToUpper(); $val = $Matches[2]
        if ($allow -notcontains $name) { continue }
        if ([string]::IsNullOrWhiteSpace($val)) { $skipped += $name; continue }
        [Environment]::SetEnvironmentVariable($name, $val, 'User')   # value never displayed
        $set += $name
    }
}
Write-Host ""
Write-Host "Promoted to USER environment variables (values not shown):" -ForegroundColor Green
$set | Sort-Object -Unique | ForEach-Object { Write-Host "   $_" }
if ($skipped.Count) { Write-Host "Skipped (blank in the source file): $($skipped -join ', ')" -ForegroundColor Yellow }
Write-Host ""
Write-Host "IMPORTANT: open a NEW terminal (and re-register scheduled tasks) so they pick these up." -ForegroundColor Yellow
Write-Host "Verify with:  python verify_global_credentials.py"
