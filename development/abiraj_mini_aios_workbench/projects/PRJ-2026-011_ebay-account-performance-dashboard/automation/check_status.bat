@echo off
REM Double-click this any time to see whether the weekly dashboard ran and succeeded.
echo(
echo ================ EBPD Weekly Dashboard - Status ================
echo(
echo --- Recent runs (most recent last) ---
if exist "%~dp0ebpd_status.txt" (
  powershell -NoProfile -Command "Get-Content '%~dp0ebpd_status.txt' -Tail 8"
) else (
  echo   (no runs recorded yet)
)
echo(
echo --- Windows Task Scheduler record ---
powershell -NoProfile -Command "$i=Get-ScheduledTaskInfo -TaskName 'EBPD_Weekly_Dashboard' -ErrorAction SilentlyContinue; if($i){ 'State    : ' + (Get-ScheduledTask -TaskName 'EBPD_Weekly_Dashboard').State; 'Last run : ' + $i.LastRunTime; 'Result   : ' + $(if($i.LastTaskResult -eq 0){'OK (0)'}else{'CHECK - code ' + $i.LastTaskResult}); 'Next run : ' + $i.NextRunTime } else { 'Scheduled task not found.' }"
echo(
echo ===============================================================
pause
