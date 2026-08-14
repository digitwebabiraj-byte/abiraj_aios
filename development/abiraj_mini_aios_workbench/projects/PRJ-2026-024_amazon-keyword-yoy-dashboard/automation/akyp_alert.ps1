# Desktop alert raised by run_akyp_weekly.bat when the weekly refresh fails.
# The job fails CLOSED: on failure the existing files and the live ph_task row are untouched,
# so a stale-but-correct page remains until the cause is fixed.
$here = $PSScriptRoot
$status = Join-Path $here "akyp_status.json"
$msg = "AKYP weekly refresh FAILED. The merged dashboard was NOT republished (last good version kept)."
if (Test-Path $status) {
    try { $s = Get-Content $status -Raw | ConvertFrom-Json; if ($s.message) { $msg += "`nReason: " + $s.message } } catch {}
}
try {
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.MessageBox]::Show($msg, "AKYP Weekly Refresh", "OK", "Error") | Out-Null
} catch {
    Write-Host $msg
}
