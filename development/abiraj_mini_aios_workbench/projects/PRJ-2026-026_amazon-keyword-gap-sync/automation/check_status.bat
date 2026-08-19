@echo off
echo === BGCT automation status ===
type "%~dp0bgct_status.txt" 2>nul
echo.
echo === last good run ===
type "%~dp0bgct_last_good.json" 2>nul
echo.
echo === scheduled task ===
schtasks /Query /TN "BGCT_Monthly_Keyword_Gap" /V /FO LIST 2>nul | findstr /C:"Last Run Time" /C:"Last Result" /C:"Next Run Time" /C:"Scheduled Task State"
