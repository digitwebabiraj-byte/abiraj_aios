# ==========================================================================
#  FRRC - register the monthly Windows Scheduled Task.
#  Runs run_frrc_monthly.bat on day 8 of every month at 07:00.
#  Re-run this script to update the task (it recreates it).
#
#  NOTE: New-ScheduledTaskTrigger has no -Monthly in Windows PowerShell 5.1,
#  so the task is created with schtasks.exe, then hardened via Set-ScheduledTask.
# ==========================================================================
$ErrorActionPreference = "Stop"
$TaskName = "FRRC_Monthly_FBA_Returns_Report"
$Bat      = Join-Path $PSScriptRoot "run_frrc_monthly.bat"
if (-not (Test-Path $Bat)) { throw "Not found: $Bat" }

if (-not [Environment]::GetEnvironmentVariable("FRRC_PGPASSWORD","User")) {
  Write-Warning "FRRC_PGPASSWORD is not set for your user - run .\set_credential.ps1 first, or the task will fail (exit 1)."
}

# --- create: day 8 of every month, 07:00 ---
# /IT = run only when this user is logged on -> no Windows password needs storing.
schtasks.exe /Create /TN $TaskName /TR "`"$Bat`"" /SC MONTHLY /D 8 /ST 07:00 /RU "$env:USERNAME" /IT /F | Out-Null
if ($LASTEXITCODE -ne 0) { throw "schtasks /Create failed with $LASTEXITCODE" }

# --- harden: wake the PC, catch up if it was off, retry on failure ---
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun `
              -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
              -MultipleInstances IgnoreNew `
              -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 15)
Set-ScheduledTask -TaskName $TaskName -Settings $settings | Out-Null

$desc = "FRRC monthly FBA Returns Root-Cause report: pulls the last 30 days (7-day settle buffer), rebuilds each Portfolio Holder dashboard and publishes to tech_team_outputs.ph_task. Fails closed - publishes nothing if any integrity check fails. Logs: capability\2026-07-15_monthly_run_toolkit\logs"
schtasks.exe /Change /TN $TaskName /RU "$env:USERNAME" | Out-Null 2>&1

Write-Host "Registered '$TaskName' - day 8 of every month, 07:00." -ForegroundColor Green
Get-ScheduledTask -TaskName $TaskName | Get-ScheduledTaskInfo |
  Format-List TaskName, NextRunTime, LastRunTime, LastTaskResult

Write-Host "`nTest now (safe - publishes nothing):" -ForegroundColor Cyan
Write-Host "   .\run_frrc_monthly.bat --dry-run"
Write-Host "Run for real on demand:" -ForegroundColor Cyan
Write-Host "   Start-ScheduledTask -TaskName '$TaskName'"
Write-Host "Remove:" -ForegroundColor Cyan
Write-Host "   Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
