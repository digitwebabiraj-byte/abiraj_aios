param(
  [string]$Time = "11:30",   # Friday run time — 11:30 keeps clear of the Monday 11:00 EPPA slot
  [switch]$Remove            # pass -Remove to delete the task
)
# Register (or remove) the Windows Scheduled Task that refreshes the Amazon Keyword YoY dashboard
# and republishes Meshika's merged "Advertising Dashboards" ph_task row, every Friday.
#
# The eBay tab of the merged page comes from EPPA's own weekly (Monday) run; this Friday job
# refreshes the Amazon tab and rebuilds+publishes the merged page.

$TaskName = "AKYP_Weekly_Amazon_Keyword_YoY"
$Bat = Join-Path $PSScriptRoot "run_akyp_weekly.bat"

if ($Remove) {
    schtasks /Delete /TN $TaskName /F
    exit $LASTEXITCODE
}

if (-not (Test-Path $Bat)) { Write-Error "run_akyp_weekly.bat not found at $Bat"; exit 1 }
if (-not (Test-Path (Join-Path $PSScriptRoot "akyp_secrets.bat"))) {
    Write-Warning "akyp_secrets.bat not found - if the GLOBAL env vars are not set, copy akyp_secrets.template.bat to akyp_secrets.bat and fill in LED_PGPASSWORD + PGPASSWORD before the task can publish."
}

# path has no spaces -> pass /TR unquoted-inside (schtasks mangles nested quotes on this machine)
schtasks /Create /TN $TaskName /TR "cmd /c `"$Bat`"" /SC WEEKLY /D FRI /ST $Time /RL LIMITED /F
if ($LASTEXITCODE -eq 0) {
    Write-Host "Registered '$TaskName' - runs every Friday at $Time."
    Write-Host "Verify:  schtasks /Query /TN $TaskName /V /FO LIST"
    Write-Host "Run now: schtasks /Run  /TN $TaskName"
    Write-Host "Remove:  powershell -File register_akyp_task.ps1 -Remove"
}
exit $LASTEXITCODE
