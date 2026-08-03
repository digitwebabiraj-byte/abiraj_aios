@echo off
REM EPNS weekly runner — sources git-ignored secrets, then runs the fail-closed pipeline.
setlocal
cd /d "%~dp0"
if not exist "epns_secrets.bat" (
  echo [EPNS] epns_secrets.bat missing - copy epns_secrets.template.bat and fill it in. >> epns_status.txt
  exit /b 1
)
call "epns_secrets.bat"
python "epns_weekly_run.py" >> "epns_run.log" 2>&1
exit /b %errorlevel%
