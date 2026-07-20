param([int]$Rc = 0)
# ERA failure alert: on non-zero exit, drop a visible marker file on the Desktop; clear it on success.
$flag = Join-Path ([Environment]::GetFolderPath('Desktop')) 'ERA_ALERT_FAILED.txt'
if ($Rc -ne 0) {
    $msg = "ERA monthly eBay Return Analysis run FAILED (exit $Rc) at $(Get-Date -Format 'yyyy-MM-dd HH:mm').`r`n" +
           "See automation\era_run.log for the error. This file auto-clears on the next successful run."
    Set-Content -Path $flag -Value $msg -Encoding UTF8
} elseif (Test-Path $flag) {
    Remove-Item $flag -Force -ErrorAction SilentlyContinue
}
