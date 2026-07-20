<#
  Set the GLOBAL database credentials by typing them in (use this if no project secrets file exists).
  Passwords are typed masked, stored as Windows user environment variables, never echoed or logged.
  Press Enter to leave any value unchanged.
#>
$ErrorActionPreference = 'Stop'
function AskPlain($name,$default){
  $cur=[Environment]::GetEnvironmentVariable($name,'User'); if(-not $cur){$cur=$default}
  $shown = if($cur){$cur}else{'(none)'}
  $v=Read-Host "$name [$shown]"; if([string]::IsNullOrWhiteSpace($v)){$cur}else{$v}
}
function AskSecret($name){
  $has=[Environment]::GetEnvironmentVariable($name,'User')
  $hint = if($has){'set - Enter to keep'}else{'not set'}
  $s=Read-Host "$name ($hint)" -AsSecureString
  $p=[Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($s))
  if([string]::IsNullOrWhiteSpace($p)){$has}else{$p}
}
Write-Host "--- ledsone (READ: live prices) ---" -ForegroundColor Cyan
$v=@{}
$v.LED_PGHOST=AskPlain 'LED_PGHOST' ''
$v.LED_PGPORT=AskPlain 'LED_PGPORT' '5432'
$v.LED_PGDATABASE=AskPlain 'LED_PGDATABASE' 'ledsone'
$v.LED_PGUSER=AskPlain 'LED_PGUSER' ''
$v.LED_PGPASSWORD=AskSecret 'LED_PGPASSWORD'
Write-Host "--- warehouse (WRITE: ph_task only) ---" -ForegroundColor Cyan
$v.PGHOST=AskPlain 'PGHOST' '149.28.134.54'
$v.PGPORT=AskPlain 'PGPORT' '5435'
$v.PGDATABASE=AskPlain 'PGDATABASE' 'order_management_copy'
$v.PGUSER=AskPlain 'PGUSER' 'temp_user'
$v.PGPASSWORD=AskSecret 'PGPASSWORD'
foreach($k in $v.Keys){ if($v[$k]){ [Environment]::SetEnvironmentVariable($k,$v[$k],'User') } }
Write-Host ""
Write-Host "Stored as USER environment variables (values not shown)." -ForegroundColor Green
Write-Host "Open a NEW terminal, then verify:  python verify_global_credentials.py" -ForegroundColor Yellow
