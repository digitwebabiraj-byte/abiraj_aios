# Desktop failure alert for the EPPR monthly refresh (survives to the Desktop even if no popup session).
$status = (Get-Content "$PSScriptRoot\eppr_status.txt" -ErrorAction SilentlyContinue | Select-Object -Last 1)
$msg = "EPPR monthly refresh FAILED`n$status`nLast good ph_task rows (472-475) were left UNCHANGED."
try { $desk = [Environment]::GetFolderPath('Desktop'); Set-Content -Path (Join-Path $desk 'EPPR_AUTOMATION_ALERT.txt') -Value $msg -Encoding utf8 } catch {}
try { Add-Type -AssemblyName PresentationFramework -ErrorAction Stop; [void][System.Windows.MessageBox]::Show($msg,'EPPR automation alert') } catch {}
