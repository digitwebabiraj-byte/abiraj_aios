@echo off
echo === EPPR automation status ===
type "%~dp0eppr_status.txt" 2>nul
echo.
echo === last good run ===
type "%~dp0eppr_last_good.json" 2>nul
echo.
echo === scheduled task ===
schtasks /Query /TN "EPPR_Monthly_Product_Performance" /V /FO LIST 2>nul | findstr /C:"Last Run Time" /C:"Last Result" /C:"Next Run Time" /C:"Scheduled Task State"
