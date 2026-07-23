param(
  [string]$Time = "09:45",   # default avoids the EBPD Monday 09:30 slot
  [int]$Day     = 2,         # 2nd of the month - see note below on why not the 1st
  [switch]$Remove
)
# Register (or remove) the Windows Scheduled Task that refreshes ESNM on the 2nd of every month.
#
# WHY DAY 2, NOT DAY 1
#   The report anchors on the LAST DAY OF THE PREVIOUS MONTH. Running on the 2nd gives that
#   final day a full extra day for late order syncs and eBay attribution to settle before the
#   month is measured. Because the window is a closed calendar month, running on the 2nd, 3rd
#   or later produces the IDENTICAL dataset - the run date does not change the numbers.
#
# WHY 09:45, NOT 09:30
#   EBPD_Weekly_Dashboard already holds Monday 09:30 and ERA_Monthly_Dashboard holds day-5
#   09:30. Whenever the 2nd falls on a Monday, a 09:30 slot here would collide with EBPD on the
#   same shared temp_user warehouse login. 09:45 is clear of the whole fleet:
#     FRRC  day 8  09:00      EBPD  Mon 09:30      ERA  day 5 09:30
#     EPC   Mon    10:30      T7    Thu 11:00      EPPA Mon  11:00
#   Override with -Time if you want it elsewhere.
#
# ⚠ REGISTER AGAINST THE MAIN TREE, NEVER A GIT WORKTREE. A worktree path can be deleted
#   between runs and the task then fails silently. This script refuses a .claude\worktrees path.

$TaskName = "ESNM_Monthly_Slow_No_Moving"
$Bat = Join-Path $PSScriptRoot "run_esnm_monthly.bat"

if ($Remove) {
    schtasks /Delete /TN $TaskName /F
    exit $LASTEXITCODE
}

if (-not (Test-Path $Bat)) { Write-Error "run_esnm_monthly.bat not found at $Bat"; exit 1 }

if ($PSScriptRoot -match '\\\.claude\\worktrees\\') {
    Write-Error @"
REFUSING TO REGISTER from a git worktree:
  $PSScriptRoot
Worktrees are temporary. Register from the main tree instead:
  C:\Users\digit\OneDrive\Desktop\Abiraj_AIOS\development\abiraj_mini_aios_workbench\projects\PRJ-2026-014_ebay-slow-no-moving-products\automation\register_esnm_task.ps1
"@
    exit 1
}

# Credentials: the global store is the normal path; a local secrets file is only an override.
$hasGlobal = [Environment]::GetEnvironmentVariable('PGPASSWORD','User') -and
             [Environment]::GetEnvironmentVariable('LED_PGPASSWORD','User')
if (-not $hasGlobal -and -not (Test-Path (Join-Path $PSScriptRoot "esnm_secrets.bat"))) {
    Write-Warning "Neither the global credentials (PGPASSWORD + LED_PGPASSWORD) nor esnm_secrets.bat were found - the job will abort before writing anything until one is present."
}

schtasks /Create /TN $TaskName /TR "cmd /c `"$Bat`"" /SC MONTHLY /D $Day /ST $Time /RL LIMITED /F
if ($LASTEXITCODE -eq 0) {
    Write-Host "Registered '$TaskName' - runs day $Day of every month at $Time."
    Write-Host ""
    Write-Host "Verify   : schtasks /Query /TN $TaskName /V /FO LIST"
    Write-Host "Test now : schtasks /Run   /TN $TaskName        (publishes for real)"
    Write-Host "Safe test: .\run_esnm_monthly.bat --dry-run     (rebuilds, no ph_task write)"
    Write-Host "Health   : .\check_status.bat"
    Write-Host "Remove   : powershell -File register_esnm_task.ps1 -Remove"
}
exit $LASTEXITCODE
