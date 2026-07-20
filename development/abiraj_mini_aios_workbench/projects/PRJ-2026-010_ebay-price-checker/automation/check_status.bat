@echo off
REM Show the last 15 EPC runs (newest at the bottom) and whether an alert is open.
echo ================= EPC weekly price checker - last runs =================
if exist "%~dp0epc_status.txt" (powershell -NoProfile -Command "Get-Content '%~dp0epc_status.txt' -Tail 15") else (echo (no runs recorded yet))
echo.
if exist "%USERPROFILE%\Desktop\EPC_ALERT_FAILED.txt" (echo *** AN ALERT IS OPEN - the last run FAILED. See EPC_ALERT_FAILED.txt on your Desktop. ***) else (echo No open alert - last run was OK.)
echo.
echo Next scheduled run:
powershell -NoProfile -Command "try{(Get-ScheduledTask -TaskName 'EPC_Weekly_Price_Checker' | Get-ScheduledTaskInfo).NextRunTime}catch{'(task not registered yet - run register_scheduled_task.ps1)'}"
pause
