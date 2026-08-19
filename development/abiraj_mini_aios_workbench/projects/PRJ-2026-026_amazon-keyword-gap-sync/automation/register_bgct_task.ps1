# Register the BGCT monthly keyword-gap refresh - 20th of each month at 12:00.
#
# WHY THE 20th AT 12:00
#  * 12:00 is the only clock slot with NO other fleet job on it. The 14 existing jobs cluster at
#    09:00-09:45, 10:00, 10:30, 11:00 and 11:30, and the shared temp_user pool intermittently
#    throws "connection slots reserved for SUPERUSER" when jobs overlap.
#  * Day 20 is clear of every other monthly job (2, 3, 4, 5, 6, 8 and EPPR's 2nd Wednesday).
#  * More importantly, this report's window is the 3 most recent COMPLETE calendar months, and
#    Amazon delivers each account's SQP on its own schedule - DCVOLTAGE measured 25 days behind on
#    2026-08-19. Running on the 20th gives the newest month in the window ~3 weeks to arrive.
#
# Registers against THIS folder (the stable main-tree path) - never a temporary git worktree,
# which is the OneDrive 0xC000013A "task never ran" trap.
$ErrorActionPreference = 'Stop'
$bat = Join-Path $PSScriptRoot 'run_bgct_monthly.bat'
if (-not (Test-Path $bat)) { throw "wrapper not found: $bat" }
if ($PSScriptRoot -like '*\.claude\worktrees\*') {
  throw "REFUSED: this is a git worktree path ($PSScriptRoot). Register from the main tree, or the task will silently never run (0xC000013A)."
}
$tn = 'BGCT_Monthly_Keyword_Gap'
$tr = "cmd /c `"`"$bat`"`""
schtasks /Create /TN $tn /TR $tr /SC MONTHLY /D 20 /ST 12:00 /RL LIMITED /F
Write-Host "Registered '$tn' -> 20th monthly 12:00 -> $bat"
schtasks /Query /TN $tn /V /FO LIST | Select-String 'TaskName|Next Run Time|Start Time|Schedule Type|Days|Months'
