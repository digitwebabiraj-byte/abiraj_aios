@echo off
REM ESDT monthly runner - sources git-ignored secrets, then runs the fail-closed pipeline.
setlocal
cd /d "%~dp0"
if not exist "%~dp0esdt_secrets.bat" (
  echo [ESDT] esdt_secrets.bat missing - copy esdt_secrets.template.bat and fill it in. >> esdt_status.txt
  exit /b 1
)
call "%~dp0esdt_secrets.bat"
python "%~dp0esdt_monthly_run.py" >> "%~dp0esdt_run.log" 2>&1
exit /b %errorlevel%
