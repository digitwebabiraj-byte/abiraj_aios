# Registers REQ-17-D02 with Windows Task Scheduler: every morning at 09:00.
#
#   Run this ONCE, from an elevated PowerShell:
#       .\register_dst_task.ps1
#
#   Preview without registering:
#       .\register_dst_task.ps1 -WhatIf
#
# NOTE ON THE TIME. 09:00 was chosen by the owner. It is the fleet's only DAILY job
# and its only 09:00 job except FRRC, which fires at 09:00 on the 8th of each month.
# On that one morning both hit the shared temp_user login at once, so the runner
# retries the connection four times with a backoff rather than failing the day.
# Moving to 09:05 would remove the overlap entirely - change $At below if wanted.
#
# Fleet slots already taken:
#   EBPD  Mon 09:30    ERA   day 5  09:30    FRRC  day 8  09:00
#   EPC   Mon 10:30    EPPA  Mon 11:00       T7    Thu 11:00

param([switch]$WhatIf)

$TaskName = "DST_Daily_Sales_Track"
$At       = "09:00"
$Here     = Split-Path -Parent $MyInvocation.MyCommand.Path
$Bat      = Join-Path $Here "run_dst_daily.bat"

if (-not (Test-Path $Bat)) { throw "run_dst_daily.bat not found at $Bat" }
if (-not (Test-Path (Join-Path $Here "dst_secrets.bat"))) {
    throw "dst_secrets.bat is missing. Copy dst_secrets.template.bat and fill it in first."
}

# Never point a scheduled task at a .claude\worktrees\... path - worktrees get deleted
# and the schedule then breaks silently.
if ($Here -match "\\\.claude\\worktrees\\") {
    throw "Refusing to register: this copy lives in a git worktree ($Here). Register from the main tree."
}

Write-Host "Task    : $TaskName"
Write-Host "Runs    : every day at $At"
Write-Host "Command : $Bat"

if ($WhatIf) { Write-Host "`n-WhatIf given - nothing registered."; return }

$action  = New-ScheduledTaskAction -Execute $Bat -WorkingDirectory $Here
$trigger = New-ScheduledTaskTrigger -Daily -At $At
$set     = New-ScheduledTaskSettingsSet -StartWhenAvailable `
             -DontStopOnIdleEnd -ExecutionTimeLimit (New-TimeSpan -Minutes 30) `
             -MultipleInstances IgnoreNew
# StartWhenAvailable matters: if the machine is asleep at 09:00 the run still happens
# once it wakes, instead of being silently skipped for the day.

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
    -Settings $set -Description "REQ-17-D02 Daily Sales Track - rebuilds and republishes ph_task 422-425 each morning" -Force | Out-Null

Write-Host "`nRegistered. Prove it before trusting it:"
Write-Host "  Start-ScheduledTask -TaskName $TaskName"
Write-Host "  Get-ScheduledTaskInfo -TaskName $TaskName | Select LastRunTime,LastTaskResult"
Write-Host "`nLastTaskResult 0 = success. 3221225786 (0xC000013A) with an EMPTY log means the"
Write-Host "job never started - that is the OneDrive hydration trap, not a code failure."
