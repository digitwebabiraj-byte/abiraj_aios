# Desktop failure alert for the BGCT monthly refresh (survives to the Desktop even with no popup session).
$status = (Get-Content "$PSScriptRoot\bgct_status.txt" -ErrorAction SilentlyContinue | Select-Object -Last 1)
$msg = "BGCT monthly keyword-gap refresh FAILED`n$status`nph_task id 980 was left UNCHANGED - Thuwaraga still sees the last good report."
try { $desk = [Environment]::GetFolderPath('Desktop'); Set-Content -Path (Join-Path $desk 'BGCT_AUTOMATION_ALERT.txt') -Value $msg -Encoding utf8 } catch {}
try { Add-Type -AssemblyName PresentationFramework -ErrorAction Stop; [void][System.Windows.MessageBox]::Show($msg,'BGCT automation alert') } catch {}
