# Registers/updates the EPC weekly run: every Monday 10:30.
# Run once, in PowerShell, from this folder.  Re-running safely updates the task.
#
# Why 10:30 - it must not collide with the other scheduled jobs on this machine, because they
# share the same restricted warehouse account (temp_user), whose pool intermittently returns
# "too many clients":
#     FRRC_Monthly_FBA_Returns_Report  09:00 (day 8)
#     EBPD_Weekly_Dashboard            09:30 MONDAY  <- same day as EPC
#     ERA_Monthly_Dashboard            09:30 (5th)
# 10:30 leaves a full hour after EBPD even if it runs long.
$ErrorActionPreference = 'Stop'
$Dir  = $PSScriptRoot
$Bat  = Join-Path $Dir 'run_epc_weekly.bat'
$Name = 'EPC_Weekly_Price_Checker'
if (-not (Test-Path $Bat)) { throw "run_epc_weekly.bat not found in $Dir" }
# Credentials may come from EITHER this project's secrets file OR the shared global store.
# Only warn when NEITHER is present - that is the only case where a run would abort.
$hasFile   = Test-Path (Join-Path $Dir 'epc_secrets.bat')
$hasGlobal = [bool][Environment]::GetEnvironmentVariable('LED_PGPASSWORD','User') -and
             [bool][Environment]::GetEnvironmentVariable('PGPASSWORD','User')
if     ($hasFile)   { Write-Host "Credentials: this project's epc_secrets.bat (overrides the global store)." -ForegroundColor Cyan }
elseif ($hasGlobal) { Write-Host "Credentials: shared GLOBAL store (user environment variables)." -ForegroundColor Cyan }
else {
  Write-Warning ("No credentials found - neither epc_secrets.bat nor the global store is set. The task will " +
                 "register, but every run aborts safely (publishing nothing) until you set them. Fix: " +
                 "05_documentation\capability\shared_db_credentials\promote_project_secrets_to_global.ps1")
}
$action  = New-ScheduledTaskAction  -Execute $Bat -WorkingDirectory $Dir
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 10:30
$set     = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable `
             -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 2)
Register-ScheduledTask -TaskName $Name -Action $action -Trigger $trigger -Settings $set `
  -Description 'EPC - eBay Price Checker: weekly refresh of the 4 ph_task dashboards (REQ-12).' -Force | Out-Null
Write-Host "Registered '$Name' - every Monday 10:30 (clear of EBPD 09:30 / FRRC 09:00 / ERA 09:30)." -ForegroundColor Green
Write-Host "Next run: $((Get-ScheduledTask -TaskName $Name | Get-ScheduledTaskInfo).NextRunTime)"
Write-Host "Test safely now:  .\run_epc_weekly.bat --dry-run"
