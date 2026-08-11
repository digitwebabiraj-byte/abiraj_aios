# Registers SMP_Monthly_Slow_Moving_Products — the 4th of each month at 10:00.
# Fleet slots in use: Mon 11:00 (EPPA), Tue 10:30 (FMP), Wed 11:30 (EPNS), Wed 10:00 (EPPR 2nd Wed),
# Thu 11:00 (T7), daily 09:05 (DST), 3rd 09:00 (SEG), 5th (ERA monthly). The 4th 10:00 is free.
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$bat  = Join-Path $here "run_smp_monthly.bat"
# New-ScheduledTaskTrigger has no monthly option, so register via schtasks.exe.
schtasks /Create /TN "SMP_Monthly_Slow_Moving_Products" /TR "\"$bat\"" /SC MONTHLY /D 4 /ST 10:00 /RL LIMITED /F | Out-Null
Write-Host "Registered SMP_Monthly_Slow_Moving_Products (day 4 of each month, 10:00)."
