@echo off
REM ---------------------------------------------------------------------------
REM Copy this file to  dst_secrets.bat  and fill in the two passwords.
REM
REM   dst_secrets.bat IS GIT-IGNORED AND MUST STAY THAT WAY.
REM   Never commit it, never paste these values into a tracked file.
REM
REM Both come from Abiraj's password manager. Neither is an admin credential -
REM Sajeesan or the DB owner can reissue either if lost.
REM ---------------------------------------------------------------------------

REM ledsone - READ-ONLY, the data source
set "LED_PGPASSWORD=<dbhub_readonly password>"

REM order_management_copy - the ph_task publish target only
set "PGPASSWORD=<temp_user password>"
