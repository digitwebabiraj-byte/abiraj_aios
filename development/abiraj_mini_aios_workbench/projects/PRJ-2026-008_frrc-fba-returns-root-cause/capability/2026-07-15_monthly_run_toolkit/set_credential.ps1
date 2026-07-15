# ==========================================================================
#  FRRC - store the DB password ONCE for the unattended monthly run.
#  Run this yourself (Claude never writes the secret to disk).
#  It is stored as a USER env var, readable only by your Windows account.
#  Sajeesan should approve storing a production write-credential this way.
# ==========================================================================
$pw = Read-Host "Enter the FRRC DB password (temp_user)" -AsSecureString
$plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
           [Runtime.InteropServices.Marshal]::SecureStringToBSTR($pw))
[Environment]::SetEnvironmentVariable("FRRC_PGPASSWORD", $plain, "User")
Write-Host "Saved. Close and reopen any terminal for it to take effect." -ForegroundColor Green
Write-Host "Verify with:  [Environment]::GetEnvironmentVariable('FRRC_PGPASSWORD','User').Length"
