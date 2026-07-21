param(
  [string]$Time = "11:00",   # Monday run time — 11:00 keeps clear of the other scheduled jobs
  [switch]$Remove            # pass -Remove to delete the task
)
# Register (or remove) the Windows Scheduled Task that refreshes the EPPA report every Monday.
#
# Fleet slots already taken on the shared machine:
#   FRRC  09:00 on day 8      EBPD  Monday 09:30
#   ERA   09:30 on the 5th    EPC   Monday 10:30
# -> EPPA takes Monday 11:00.

$TaskName = "EPPA_Weekly_Pause_Report"
$Bat = Join-Path $PSScriptRoot "run_eppa_weekly.bat"

if ($Remove) {
    schtasks /Delete /TN $TaskName /F
    exit $LASTEXITCODE
}

if (-not (Test-Path $Bat)) { Write-Error "run_eppa_weekly.bat not found at $Bat"; exit 1 }
if (-not (Test-Path (Join-Path $PSScriptRoot "eppa_secrets.bat"))) {
    Write-Warning "eppa_secrets.bat not found - copy eppa_secrets.template.bat to eppa_secrets.bat and fill in LED_PGPASSWORD before the task can run."
}

schtasks /Create /TN $TaskName /TR "cmd /c `"$Bat`"" /SC WEEKLY /D MON /ST $Time /RL LIMITED /F
if ($LASTEXITCODE -eq 0) {
    Write-Host "Registered '$TaskName' - runs every Monday at $Time."
    Write-Host "Verify:  schtasks /Query /TN $TaskName /V /FO LIST"
    Write-Host "Run now: schtasks /Run  /TN $TaskName"
    Write-Host "Status:  check_status.bat"
    Write-Host "Remove:  powershell -File register_eppa_task.ps1 -Remove"
}
exit $LASTEXITCODE
