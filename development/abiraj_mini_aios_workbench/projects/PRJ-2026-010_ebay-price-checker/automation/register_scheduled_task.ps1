# Registers/updates the EPC weekly run: every Monday 07:00.
# Run once, in PowerShell, from this folder.  Re-running safely updates the task.
$ErrorActionPreference = 'Stop'
$Dir  = $PSScriptRoot
$Bat  = Join-Path $Dir 'run_epc_weekly.bat'
$Name = 'EPC_Weekly_Price_Checker'
if (-not (Test-Path $Bat)) { throw "run_epc_weekly.bat not found in $Dir" }
if (-not (Test-Path (Join-Path $Dir 'epc_secrets.bat'))) {
  Write-Warning "epc_secrets.bat is missing - copy epc_secrets.template.bat to epc_secrets.bat and fill it in, or the run will abort (safely)."
}
$action  = New-ScheduledTaskAction  -Execute $Bat -WorkingDirectory $Dir
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 07:00
$set     = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable `
             -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 2)
Register-ScheduledTask -TaskName $Name -Action $action -Trigger $trigger -Settings $set `
  -Description 'EPC - eBay Price Checker: weekly refresh of the 4 ph_task dashboards (REQ-12).' -Force | Out-Null
Write-Host "Registered '$Name' - every Monday 07:00." -ForegroundColor Green
Write-Host "Next run: $((Get-ScheduledTask -TaskName $Name | Get-ScheduledTaskInfo).NextRunTime)"
Write-Host "Test safely now:  .\run_epc_weekly.bat --dry-run"
