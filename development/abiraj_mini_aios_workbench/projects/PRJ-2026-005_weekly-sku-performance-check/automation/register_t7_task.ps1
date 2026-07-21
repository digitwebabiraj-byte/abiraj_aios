# Registers/updates the T7 weekly run: every Thursday 11:00.
# Run once, in PowerShell, FROM THE MAIN REPO PATH (never a .claude\worktrees\... copy - a worktree
# is deleted and the schedule then silently breaks).  Re-running safely updates the task.
#
# Why Thursday 11:00 - the business rule is a Thursday run, and 11:00 keeps it clear of every other
# job on this machine, which all share the same restricted warehouse account (temp_user) whose pool
# intermittently returns "too many clients":
#     FRRC_Monthly_FBA_Returns_Report  09:00 (day 8)   <- can fall on a Thursday
#     ERA_Monthly_Dashboard            09:30 (day 5)   <- can fall on a Thursday
#     EBPD_Weekly_Dashboard            09:30 Monday
#     EPC_Weekly_Price_Checker         10:30 Monday
$ErrorActionPreference = 'Stop'
$Dir  = $PSScriptRoot
$Bat  = Join-Path $Dir 'run_t7_weekly.bat'
$Name = 'T7_Weekly_SKU_Performance'
if (-not (Test-Path $Bat)) { throw "run_t7_weekly.bat not found in $Dir" }
if ($Dir -like '*\.claude\worktrees\*') {
  throw "Refusing to register from a git worktree ($Dir). Merge to main first, then run this from the main repo path."
}
# Credentials may come from EITHER this project's secrets file OR the shared global store.
# Only warn when NEITHER is present - that is the only case where a run would abort.
$hasFile   = Test-Path (Join-Path $Dir 't7_secrets.bat')
$hasGlobal = [bool][Environment]::GetEnvironmentVariable('PGPASSWORD','User')
if     ($hasFile)   { Write-Host "Credentials: this project's t7_secrets.bat (overrides the global store)." -ForegroundColor Cyan }
elseif ($hasGlobal) { Write-Host "Credentials: shared GLOBAL store (user environment variables)." -ForegroundColor Cyan }
else {
  Write-Warning ("No credentials found - neither t7_secrets.bat nor the global store is set. The task will " +
                 "register, but every run aborts safely (publishing nothing) until you set them. Fix: " +
                 "05_documentation\capability\shared_db_credentials\set_global_db_credentials.ps1")
}
$action  = New-ScheduledTaskAction  -Execute $Bat -WorkingDirectory $Dir
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Thursday -At 11:00
$set     = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable `
             -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 2)
Register-ScheduledTask -TaskName $Name -Action $action -Trigger $trigger -Settings $set `
  -Description 'T7 - Weekly SKU Performance Check (Thuwaraga): refreshes ph_task row WSPC (REQ-07-D02).' -Force | Out-Null
Write-Host "Registered '$Name' - every Thursday 11:00 (clear of FRRC 09:00 / ERA 09:30)." -ForegroundColor Green
Write-Host "Next run: $((Get-ScheduledTask -TaskName $Name | Get-ScheduledTaskInfo).NextRunTime)"
Write-Host "Test safely now:  .\run_t7_weekly.bat --dry-run"
Write-Host "Regression test:  .\run_t7_weekly.bat --dry-run --window 2026-07-02"
