@echo off
REM Last few runs of the Daily Sales Track job, newest at the bottom.
setlocal
set "HERE=%~dp0"
echo.
echo === last 25 status lines ===
if exist "%HERE%dst_status.txt" (
  powershell -NoProfile -Command "Get-Content '%HERE%dst_status.txt' -Tail 25"
) else (
  echo   no status file yet - the job has not run
)
echo.
echo === scheduled task ===
schtasks /Query /TN "DST_Daily_Sales_Track" /V /FO LIST 2>nul | findstr /I "TaskName Next Last Result Status"
if errorlevel 1 echo   task not registered - run register_dst_task.ps1
echo.
