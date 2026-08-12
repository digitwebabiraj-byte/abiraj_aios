# Registers ESDT_Monthly_Sales_Drop - the 6th of each month at 10:00.
# Fleet monthly slots: 3rd 09:00 (SEG), 4th 10:00 (SMP), 5th (ERA), 2nd Wed 10:00 (EPPR). 6th 10:00 is free.
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$bat  = Join-Path $here "run_esdt_monthly.bat"
if (-not (Test-Path $bat)) { throw "runner not found: $bat" }
# schtasks is used because New-ScheduledTaskTrigger has no monthly option.
# Path has no spaces, so pass /TR unquoted to avoid PowerShell native-quote mangling.
schtasks /Create /TN ESDT_Monthly_Sales_Drop /TR $bat /SC MONTHLY /D 6 /ST 10:00 /RL LIMITED /F
if ($LASTEXITCODE -ne 0) { throw "schtasks /Create failed (exit $LASTEXITCODE)" }
Write-Host "Registered ESDT_Monthly_Sales_Drop (day 6 of each month, 10:00)."
