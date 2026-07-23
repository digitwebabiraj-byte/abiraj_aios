@echo off
REM ---------------------------------------------------------------------------
REM REQ-17-D02 - Daily Sales Track, daily run wrapper (Windows Task Scheduler).
REM Plain ASCII only: a non-ASCII character in a .bat breaks cmd.exe.
REM
REM   run_dst_daily.bat              full run, publishes
REM   run_dst_daily.bat --dry-run    rebuild + gates, publishes nothing
REM
REM CREDENTIALS. The fleet standard is the GLOBAL credential store - PGPASSWORD and
REM LED_PGPASSWORD as Windows *user* environment variables, installed once by
REM 05_documentation\capability\shared_db_credentials\set_global_db_credentials.ps1.
REM No project should need its own secrets file. This wrapper therefore:
REM   1. uses the global store if it is present, and
REM   2. falls back to a local git-ignored dst_secrets.bat only if it is not.
REM ---------------------------------------------------------------------------
setlocal

set "HERE=%~dp0"
cd /d "%HERE%"

if defined PGPASSWORD if defined LED_PGPASSWORD goto :haveCreds

if exist "%HERE%dst_secrets.bat" (
  call "%HERE%dst_secrets.bat"
  goto :haveCreds
)

echo [ERROR] No credentials. Either the global store is not installed
echo         (run shared_db_credentials\set_global_db_credentials.ps1, then open a
echo         NEW terminal - env vars only reach processes started afterwards),
echo         or copy dst_secrets.template.bat to dst_secrets.bat.
powershell -ExecutionPolicy Bypass -File "%HERE%dst_alert.ps1" -Reason "No DB credentials available"
exit /b 2

:haveCreds
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
