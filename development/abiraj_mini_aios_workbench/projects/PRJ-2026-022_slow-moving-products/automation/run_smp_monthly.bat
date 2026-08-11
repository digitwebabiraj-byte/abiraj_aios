@echo off
REM SMP monthly runner — sources git-ignored secrets, then runs the fail-closed pipeline.
setlocal
cd /d "%~dp0"
if not exist "smp_secrets.bat" (
  echo [SMP] smp_secrets.bat missing - copy smp_secrets.template.bat and fill it in. >> smp_status.txt
  exit /b 1
)
call "smp_secrets.bat"
python "smp_monthly_run.py" >> "smp_run.log" 2>&1
exit /b %errorlevel%
