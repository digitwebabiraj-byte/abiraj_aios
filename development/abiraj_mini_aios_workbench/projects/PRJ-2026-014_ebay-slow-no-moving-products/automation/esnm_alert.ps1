param([int]$Rc = 0)
# ESNM failure alert: on non-zero exit drop a visible marker on the Desktop; clear it on success.
$flag = Join-Path ([Environment]::GetFolderPath('Desktop')) 'ESNM_ALERT_FAILED.txt'
if ($Rc -ne 0) {
    $msg = "ESNM monthly eBay Slow/No-Moving Products run FAILED (exit $Rc) at $(Get-Date -Format 'yyyy-MM-dd HH:mm').`r`n" +
           "The PREVIOUS report is untouched and still correct - this job fails closed.`r`n" +
           "See automation\esnm_run.log and automation\esnm_status.json for the reason.`r`n" +
           "This file auto-clears on the next successful run."
    Set-Content -Path $flag -Value $msg -Encoding UTF8
} elseif (Test-Path $flag) {
    Remove-Item $flag -Force -ErrorAction SilentlyContinue
}
