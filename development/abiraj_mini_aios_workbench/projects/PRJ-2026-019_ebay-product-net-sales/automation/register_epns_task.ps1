# Registers EPNS_Weekly_Net_Sales — every Wednesday 11:30 (free slot, clear of the fleet).
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$bat  = Join-Path $here "run_epns_weekly.bat"
$action  = New-ScheduledTaskAction -Execute $bat -WorkingDirectory $here
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Wednesday -At 11:30
$set = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew `
        -ExecutionTimeLimit (New-TimeSpan -Hours 1)
Register-ScheduledTask -TaskName "EPNS_Weekly_Net_Sales" -Action $action -Trigger $trigger `
  -Settings $set -Description "eBay Product Net Sales (epns/REQ-22-D02): weekly settled net-sales refresh + ph_task publish for ebay_priors." -Force
Write-Host "Registered EPNS_Weekly_Net_Sales (Wed 11:30)."
