@echo off
REM Quick health check for the weekly EPPA refresh.
setlocal
cd /d "%~dp0"
echo === EPPA weekly refresh =========================================
schtasks /Query /TN EPPA_Weekly_Pause_Report /FO LIST 2>nul | findstr /C:"TaskName" /C:"Next Run Time" /C:"Last Run Time" /C:"Last Result" /C:"Status"
echo.
echo --- last run status --------------------------------------------
if exist "eppa_status.json" (type "eppa_status.json") else (echo   no status file yet - the job has not run)
echo.
echo --- last 12 log lines ------------------------------------------
if exist "eppa_run.log" (powershell -NoProfile -Command "Get-Content 'eppa_run.log' -Tail 12") else (echo   no log yet)
echo.
echo Run now:  schtasks /Run /TN EPPA_Weekly_Pause_Report
pause
