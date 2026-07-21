# Raise a visible failure alert when the weekly EPPA refresh fails.
# The scheduled task runs unattended, so a silent failure would leave a stale report on screen
# with nobody aware. This drops a file on the Desktop and shows a toast/balloon if possible.
$ErrorActionPreference = "SilentlyContinue"

$status = Join-Path $PSScriptRoot "eppa_status.json"
$msg = "unknown error"
if (Test-Path $status) {
    try { $msg = (Get-Content $status -Raw | ConvertFrom-Json).message } catch {}
}
$stamp = Get-Date -Format "yyyy-MM-dd HH:mm"
$desktop = [Environment]::GetFolderPath("Desktop")
$file = Join-Path $desktop "EPPA_REFRESH_FAILED.txt"

@"
eBay PPC Pause Automation - WEEKLY REFRESH FAILED
=================================================
When   : $stamp
Reason : $msg

The PUBLISHED report (ph_task) was NOT overwritten - the job fails closed, so the
row still live for the assigned user is the last good one.

NOTE: depending on where the run stopped, the LOCAL files under evidence/final_outputs
may already have been rebuilt. If the failure was at the publish step, those files are
newer than the published row. Re-running a successful job resolves both.

Check : $PSScriptRoot\eppa_run.log
Rerun : schtasks /Run /TN EPPA_Weekly_Pause_Report
"@ | Out-File -FilePath $file -Encoding utf8

try {
    Add-Type -AssemblyName System.Windows.Forms
    $n = New-Object System.Windows.Forms.NotifyIcon
    $n.Icon = [System.Drawing.SystemIcons]::Error
    $n.Visible = $true
    $n.ShowBalloonTip(20000, "EPPA weekly refresh failed", $msg, 'Error')
    Start-Sleep -Seconds 12
    $n.Dispose()
} catch {}
