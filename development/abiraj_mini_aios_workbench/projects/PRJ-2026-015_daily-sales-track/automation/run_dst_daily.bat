@echo off
REM ---------------------------------------------------------------------------
REM REQ-17-D02 - Daily Sales Track, daily run wrapper (Windows Task Scheduler).
REM Plain ASCII only: a non-ASCII character in a .bat breaks cmd.exe.
REM
REM   run_dst_daily.bat              full run, publishes
REM   run_dst_daily.bat --dry-run    rebuild + gates, publishes nothing
REM ---------------------------------------------------------------------------
setlocal

set "HERE=%~dp0"
cd /d "%HERE%"

if not exist "%HERE%dst_secrets.bat" (
  echo [ERROR] dst_secrets.bat not found. Copy dst_secrets.template.bat and fill it in.
  powershell -ExecutionPolicy Bypass -File "%HERE%dst_alert.ps1" -Reason "dst_secrets.bat missing"
  exit /b 2
)
call "%HERE%dst_secrets.bat"

python "%HERE%dst_daily_run.py" %* >> "%HERE%dst_run.log" 2>&1
set RC=%ERRORLEVEL%

if not "%RC%"=="0" (
  echo [FAILED] rc=%RC% - see dst_run.log
  powershell -ExecutionPolicy Bypass -File "%HERE%dst_alert.ps1" -Reason "Daily Sales Track run failed (rc=%RC%)"
)

REM never leave credentials in the environment after the run
set "PGPASSWORD="
set "LED_PGPASSWORD="
exit /b %RC%
