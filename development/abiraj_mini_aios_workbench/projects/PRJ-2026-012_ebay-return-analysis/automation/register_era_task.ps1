param(
  [string]$Time = "09:30",     # run time on the 5th
  [int]$Day = 5,               # day of month
  [switch]$Remove              # pass -Remove to delete the task
)
# Register (or remove) the Windows Scheduled Task that runs ERA on the 5th of every month.
$TaskName = "ERA_Monthly_Dashboard"
$Bat = Join-Path $PSScriptRoot "run_era_monthly.bat"

if ($Remove) {
    schtasks /Delete /TN $TaskName /F
    exit $LASTEXITCODE
}

if (-not (Test-Path $Bat)) { Write-Error "run_era_monthly.bat not found at $Bat"; exit 1 }
if (-not (Test-Path (Join-Path $PSScriptRoot "era_secrets.bat"))) {
    Write-Warning "era_secrets.bat not found — copy era_secrets.template.bat to era_secrets.bat and fill it in before the task can publish."
}

# /SC MONTHLY /D <day> runs on that calendar day each month. Cmd wraps the .bat.
schtasks /Create /TN $TaskName /TR "cmd /c `"$Bat`"" /SC MONTHLY /D $Day /ST $Time /RL LIMITED /F
if ($LASTEXITCODE -eq 0) {
    Write-Host "Registered '$TaskName' — runs day $Day of every month at $Time."
    Write-Host "Verify:  schtasks /Query /TN $TaskName /V /FO LIST"
    Write-Host "Run now: schtasks /Run  /TN $TaskName"
    Write-Host "Remove:  powershell -File register_era_task.ps1 -Remove"
}
exit $LASTEXITCODE
