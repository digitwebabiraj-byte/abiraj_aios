@echo off
REM Quick health check for the ESNM monthly job.
echo === Scheduled task ===
schtasks /Query /TN "ESNM_Monthly_Slow_No_Moving" /V /FO LIST 2>nul | findstr /C:"Task To Run" /C:"Next Run Time" /C:"Last Run Time" /C:"Last Result" /C:"Status"
echo.
echo === Last run status ===
if exist "%~dp0esnm_status.json" (type "%~dp0esnm_status.json") else (echo   no esnm_status.json yet - the job has never completed)
echo.
echo === Last 15 log lines ===
if exist "%~dp0esnm_run.log" (powershell -NoProfile -Command "Get-Content '%~dp0esnm_run.log' -Tail 15") else (echo   no esnm_run.log yet)
echo.
echo === Desktop failure flag ===
if exist "%USERPROFILE%\Desktop\ESNM_ALERT_FAILED.txt" (echo   *** FAILURE FLAG PRESENT *** & type "%USERPROFILE%\Desktop\ESNM_ALERT_FAILED.txt") else (echo   none - last run was clean)
