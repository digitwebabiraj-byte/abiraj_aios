# Register the EPPR monthly refresh — 2nd Wednesday of each month at 10:00.
# Always a weekday, ~monthly cadence, and 10:00 is clear of the other 9 fleet jobs (which run
# 09:00-09:45 and the Mon/Thu 10:30-11:00 slots on the shared temp_user account).
# Registers against THIS folder (the stable main-tree path) — never a temporary git worktree
# (the OneDrive 0xC000013A silent-no-run trap).
$ErrorActionPreference = 'Stop'
$bat = Join-Path $PSScriptRoot 'run_eppr_monthly.bat'
if (-not (Test-Path $bat)) { throw "wrapper not found: $bat" }
$tn = 'EPPR_Monthly_Product_Performance'
$tr = "cmd /c `"`"$bat`"`""
schtasks /Create /TN $tn /TR $tr /SC MONTHLY /MO SECOND /D WED /ST 10:00 /RL LIMITED /F
Write-Host "Registered '$tn' -> 2nd Wednesday monthly 10:00 -> $bat"
schtasks /Query /TN $tn /V /FO LIST | Select-String 'TaskName|Next Run Time|Start Time|Schedule Type|Months|Days'
