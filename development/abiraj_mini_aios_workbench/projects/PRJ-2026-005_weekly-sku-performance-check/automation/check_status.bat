@echo off
REM Show the last 15 T7 runs (newest at the bottom) and whether an alert is open.
echo ============== T7 weekly SKU performance check - last runs ==============
if exist "%~dp0t7_status.txt" (powershell -NoProfile -Command "Get-Content '%~dp0t7_status.txt' -Tail 15") else (echo (no runs recorded yet))
echo.
if exist "%USERPROFILE%\Desktop\T7_ALERT_FAILED.txt" (echo *** AN ALERT IS OPEN - the last run FAILED. See T7_ALERT_FAILED.txt on your Desktop. ***) else (echo No open alert - last run was OK.)
echo.
echo Next scheduled run:
powershell -NoProfile -Command "try{(Get-ScheduledTask -TaskName 'T7_Weekly_SKU_Performance' | Get-ScheduledTaskInfo).NextRunTime}catch{'(task not registered yet - run register_t7_task.ps1)'}"
pause
