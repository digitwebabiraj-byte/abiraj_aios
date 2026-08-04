# Registers FMP_Weekly_Fast_Moving_Products — every Tuesday 10:30 (free slot, clear of the fleet).
# Fleet slots in use: Mon 11:00 (EPPA), Wed 11:30 (EPNS), Wed 10:00 (EPPR 2nd Wed), Thu 11:00 (T7),
# daily 09:05 (DST), 3rd 09:00 (SEG). Tuesday 10:30 is free.
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$bat  = Join-Path $here "run_fmp_weekly.bat"
$action  = New-ScheduledTaskAction -Execute $bat -WorkingDirectory $here
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Tuesday -At 10:30
$set = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew `
        -ExecutionTimeLimit (New-TimeSpan -Hours 1)
Register-ScheduledTask -TaskName "FMP_Weekly_Fast_Moving_Products" -Action $action -Trigger $trigger `
  -Settings $set -Description "Fast Moving Products (fmp/REQ-23-D01): weekly DE top-seller refresh (Excel + dashboard) from raw mcp.ledsone. No ph_task publish (held for Mahima)." -Force
Write-Host "Registered FMP_Weekly_Fast_Moving_Products (Tuesday 10:30)."
