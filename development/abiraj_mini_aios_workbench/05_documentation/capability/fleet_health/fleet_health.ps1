# Fleet Health - mission-control status board for all 12 automated jobs.
# Reads Windows Task Scheduler (uniform for every job) + each job's status file, writes
# fleet_health.html next to this script and opens it. DB-free (no warehouse connection).
# Run:  double-click run_fleet_health.bat   (opens the page)
#       fleet_health.ps1 -NoOpen            (regenerate silently - used by the auto-refresh task)
param([switch]$NoOpen)
$ErrorActionPreference = 'SilentlyContinue'
$REFRESH = 300   # the open page reloads itself every N seconds to pick up the regenerated file
$proj = "C:\Users\digit\OneDrive\Desktop\Abiraj_AIOS\development\abiraj_mini_aios_workbench\projects"
$OUT  = Join-Path $PSScriptRoot 'fleet_health.html'

# job -> task name, group, cadence label, automation folder, status file
$JOBS = @(
 @{n='DST';  task='DST_Daily_Sales_Track';           grp='Daily';   cad='Every day 09:15';  dir="$proj\PRJ-2026-015_daily-sales-track\automation";                       f='dst_status.txt'}
 @{n='EBPD'; task='EBPD_Weekly_Dashboard';           grp='Weekly';  cad='Monday 09:30';     dir="$proj\PRJ-2026-011_ebay-account-performance-dashboard\automation";      f='ebpd_status.txt'}
 @{n='SMAW'; task='SMAW_Weekly_StockCheck';          grp='Weekly';  cad='Monday 10:00';     dir="$proj\PRJ-2026-004_smaw-table5-stock-check\automation";                 f='smaw_status.txt'}
 @{n='EPC';  task='EPC_Weekly_Price_Checker';        grp='Weekly';  cad='Monday 10:30';     dir="$proj\PRJ-2026-010_ebay-price-checker\automation";                      f='epc_status.txt'}
 @{n='EPPA'; task='EPPA_Weekly_Pause_Report';        grp='Weekly';  cad='Monday 11:00';     dir="$proj\PRJ-2026-013_ebay-ppc-product-pause-automation\automation";       f='eppa_status.json'}
 @{n='PC';   task='PC_Weekly_PausedCampaigns';       grp='Weekly';  cad='Wednesday 09:00';  dir="$proj\PRJ-2026-007_paused-campaign-report\automation";                  f='pc_status.txt'}
 @{n='T7';   task='T7_Weekly_SKU_Performance';       grp='Weekly';  cad='Thursday 11:00';   dir="$proj\PRJ-2026-005_weekly-sku-performance-check\automation";            f='t7_status.txt'}
 @{n='ESNM'; task='ESNM_Monthly_Slow_No_Moving';     grp='Monthly'; cad='2nd, 09:45';       dir="$proj\PRJ-2026-014_ebay-slow-no-moving-products\automation";            f='esnm_status.json'}
 @{n='SEG';  task='SEG_Monthly_Segmentation';        grp='Monthly'; cad='3rd, 09:00';       dir="$proj\PRJ-2026-001_ph-segmentation\automation";                         f='seg_status.txt'}
 @{n='ZSFO'; task='ZSFO_Monthly_ZeroSales';          grp='Monthly'; cad='4th, 09:00';       dir="$proj\PRJ-2026-006_zero-sales-full-optimization\automation";            f='zsfo_status.txt'}
 @{n='ERA';  task='ERA_Monthly_Dashboard';           grp='Monthly'; cad='5th, 09:30';       dir="$proj\PRJ-2026-012_ebay-return-analysis\automation";                    f='era_status.txt'}
 @{n='FRRC'; task='FRRC_Monthly_FBA_Returns_Report'; grp='Monthly'; cad='8th, 09:00';       dir="$proj\PRJ-2026-008_frrc-fba-returns-root-cause\capability\2026-07-15_monthly_run_toolkit"; f=$null}
)

$now = Get-Date
function FileUrl($p) { if ($p) { 'file:///' + ($p -replace '\\','/') } else { '' } }
function LastSummary($path) {
  # The authoritative status is the pill (Task Scheduler). This note is a human hint, so show the
  # last SUCCESSFUL summary rather than the raw last line - status files also hold manual dry-run /
  # negative-test lines whose FAILED text would otherwise contradict a healthy pill.
  if (-not ($path -and (Test-Path $path))) { return '' }
  if ($path -like '*.json') {
    try {
      $o = Get-Content $path -Raw -Encoding utf8 | ConvertFrom-Json
      $parts = @()
      foreach ($p in $o.PSObject.Properties) {
        if ($p.Value -is [string] -or $p.Value -is [int] -or $p.Value -is [long] -or $p.Value -is [double]) {
          if ($p.Name -notmatch 'md5|html|id$') { $parts += ('{0} {1}' -f $p.Name, $p.Value) }
        }
      }
      if ($parts) { return (($parts | Select-Object -First 5) -join ' | ') }
    } catch {}
    return ''
  }
  $lines = @(Get-Content $path -Tail 15 -Encoding utf8 | Where-Object { $_.Trim() })
  $good  = @($lines | Where-Object { ($_ -match 'OK|PUBLISHED|done') -and ($_ -notmatch 'FAILED|ABORT') })
  if ($good.Count)  { return $good[-1].Trim() }
  if ($lines.Count) { return $lines[-1].Trim() }
  return ''
}
function HtmlEsc($s) { ($s -replace '&','&amp;' -replace '<','&lt;' -replace '>','&gt;' -replace '"','&quot;') }
function Countdown($next) {
  if (-not $next) { return '' }
  $d = $next - $now
  if ($d.TotalSeconds -lt 0) { return 'overdue' }
  if ($d.TotalDays  -ge 1)   { return ('in {0}d' -f [math]::Floor($d.TotalDays)) }
  if ($d.TotalHours -ge 1)   { return ('in {0}h' -f [math]::Floor($d.TotalHours)) }
  return ('in {0}m' -f [math]::Max(1,[math]::Floor($d.TotalMinutes)))
}

$data = @()
foreach ($j in $JOBS) {
  $t = Get-ScheduledTask -TaskName $j.task
  $i = Get-ScheduledTaskInfo -TaskName $j.task
  $code = if ($i) { [int64]$i.LastTaskResult } else { -1 }
  $overdue = ($i.NextRunTime -and $i.NextRunTime -lt $now.AddMinutes(-30))
  $sev  = if (-not $t) { 'crit' }
          elseif ($code -eq 0)      { 'ok' }
          elseif ($code -eq 267011) { 'wait' }
          elseif ($code -eq 267009) { 'run' }
          elseif ($overdue)         { 'crit' }
          else { 'crit' }
  $txt  = switch ($code) {
            0 {'Healthy'} 267011 {'Waiting for first run'} 267009 {'Running now'} 267014 {'Terminated'}
            3221225786 {'Never started (OneDrive?)'} -1 {'NOT REGISTERED'} default {"Failed - code $code"} }
  $statusfile = if ($j.f) { Join-Path $j.dir $j.f } else { $null }
  $raw = LastSummary $statusfile
  $data += [pscustomobject]@{
    n=$j.n; grp=$j.grp; cad=$j.cad; sev=$sev; txt=$txt;
    last = if ($i.LastRunTime -and $i.LastRunTime.Year -gt 2000) { $i.LastRunTime.ToString('ddd dd MMM, HH:mm') } else { $null }
    next = if ($i.NextRunTime) { $i.NextRunTime.ToString('ddd dd MMM, HH:mm') } else { $null }
    cd   = Countdown $i.NextRunTime
    state= if ($t) { "$($t.State)" } else { '-' }
    summary = HtmlEsc $raw
    logurl  = FileUrl (Join-Path $j.dir ($j.n.ToLower()+'_run.log'))
    dirurl  = FileUrl $j.dir
  }
}

$nOK   = ($data | Where-Object sev -eq 'ok').Count
$nWait = ($data | Where-Object sev -eq 'wait').Count
$nRun  = ($data | Where-Object sev -eq 'run').Count
$nCrit = ($data | Where-Object sev -eq 'crit').Count

# banner
if ($nCrit -gt 0) {
  $bannerCls='crit'; $bannerIcon='&#9888;'
  $names = ($data | Where-Object sev -eq 'crit' | ForEach-Object { $_.n }) -join ', '
  $bannerMsg = "$nCrit job$(if($nCrit-ne1){'s'}) need attention: $names"
} elseif ($nRun -gt 0) {
  $bannerCls='run'; $bannerIcon='&#9679;'; $bannerMsg = "$nRun running now - the rest are healthy"
} else {
  $bannerCls='ok'; $bannerIcon='&#10003;'
  $bannerMsg = if ($nWait -gt 0) { "All systems healthy - $nOK run clean, $nWait waiting for their first run" } else { "All $nOK jobs healthy" }
}

# rows grouped by cadence
$sections = ''
foreach ($g in 'Daily','Weekly','Monthly') {
  $grp = $data | Where-Object grp -eq $g
  if (-not $grp) { continue }
  $rowsHtml = ''
  foreach ($r in $grp) {
    $sum = if ($r.summary) { $r.summary } else { '<span class="mut">no run recorded yet</span>' }
    $cd  = if ($r.cd) { "<span class='cd'>$($r.cd)</span>" } else { '' }
    $nx  = if ($r.next) { "$($r.next) $cd" } else { '&mdash;' }
    $lr  = if ($r.last) { $r.last } else { '&mdash;' }
    $rowsHtml += @"
      <tr class="sev-$($r.sev)">
        <td class="stripe"></td>
        <td class="job"><a href="$($r.dirurl)" title="Open this job's folder">$($r.n)</a></td>
        <td class="status"><span class="chip"><span class="dot"></span>$($r.txt)</span></td>
        <td class="tnum">$lr</td>
        <td class="tnum">$nx</td>
        <td class="sum">$sum</td>
        <td class="log"><a href="$($r.logurl)" title="Open run log">log &rsaquo;</a></td>
      </tr>
"@
  }
  $sections += @"
    <section class="grp">
      <div class="ghead"><h2>$g</h2><span class="gcount">$($grp.Count)</span></div>
      <table><tbody>$rowsHtml</tbody></table>
    </section>
"@
}

$stamp = $now.ToString('dddd dd MMM yyyy, HH:mm')
$html = @"
<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="$REFRESH">
<title>AIOS Automation - Fleet Health</title>
<style>
:root{
  --bg:#eef2f9; --bg2:#f7f9fd; --panel:#ffffff; --line:#e6ebf4; --line2:#eef2f8;
  --ink:#1b2540; --ink2:#33405c; --mut:#7b879e; --accent:#4d6ef5;
  --ok:#12a150; --ok-bg:#e7f7ee; --ok-bd:#bfe6cf;
  --wait:#b57611; --wait-bg:#fdf3e0; --wait-bd:#f0dcae;
  --crit:#dc2b3a; --crit-bg:#fdebec; --crit-bd:#f6c9cd;
  --run:#2f63e6; --run-bg:#e9f0ff; --run-bd:#c6d8fb;
  --shadow:0 1px 2px rgba(20,32,64,.04), 0 4px 16px rgba(20,32,64,.06);
  --shadow-sm:0 1px 2px rgba(20,32,64,.05);
}
*{box-sizing:border-box} html,body{margin:0}
body{background:linear-gradient(180deg,var(--bg2),var(--bg)) fixed;
  color:var(--ink); font:14px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,sans-serif;
  padding:34px clamp(16px,5vw,52px); -webkit-font-smoothing:antialiased; letter-spacing:.005em}
.tnum{font-variant-numeric:tabular-nums}
header{display:flex;align-items:baseline;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:20px}
h1{font-size:20px;letter-spacing:-.01em;margin:0;font-weight:700}
h1 .b{color:var(--mut);font-weight:500}
.asof{color:var(--mut);font-size:12.5px}
.banner{display:flex;align-items:center;gap:13px;border-radius:16px;padding:17px 20px;margin-bottom:22px;
  font-size:15px;font-weight:600;box-shadow:var(--shadow);border:1px solid var(--line)}
.banner .ic{font-size:16px;line-height:1;width:30px;height:30px;display:grid;place-items:center;border-radius:9px;flex:0 0 auto}
.banner.ok{background:var(--panel);color:#0c7a3c} .banner.ok .ic{background:var(--ok-bg);color:var(--ok)}
.banner.wait,.banner.run{background:var(--panel);color:#234ec2} .banner.run .ic,.banner.wait .ic{background:var(--run-bg);color:var(--run)}
.banner.crit{background:var(--panel);color:#b21f2c} .banner.crit .ic{background:var(--crit-bg);color:var(--crit)}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:28px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:15px;padding:16px 18px;box-shadow:var(--shadow-sm)}
.kpi b{font-size:28px;display:block;line-height:1.05;font-variant-numeric:tabular-nums;letter-spacing:-.02em}
.kpi span{color:var(--mut);font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;font-weight:600}
.kpi.ok b{color:var(--ok)} .kpi.wait b{color:var(--wait)} .kpi.crit b{color:var(--crit)} .kpi.tot b{color:var(--ink)}
.grp{margin-bottom:26px}
.ghead{display:flex;align-items:center;gap:10px;margin:0 4px 10px}
.ghead h2{font-size:11.5px;text-transform:uppercase;letter-spacing:.15em;color:var(--mut);font-weight:700;margin:0}
.gcount{font-size:11px;color:var(--mut);background:var(--panel);border:1px solid var(--line);border-radius:20px;padding:1px 9px;box-shadow:var(--shadow-sm)}
table{width:100%;border-collapse:separate;border-spacing:0;background:var(--panel);border:1px solid var(--line);border-radius:16px;overflow:hidden;box-shadow:var(--shadow)}
td{padding:13px 16px;border-top:1px solid var(--line2);vertical-align:middle;font-size:13.5px}
tbody tr:first-child td{border-top:none}
tr{transition:background .12s}
tr:hover td{background:#f8faff}
td.stripe{width:4px;padding:0}
tr.sev-ok td.stripe{background:var(--ok)} tr.sev-wait td.stripe{background:var(--wait)}
tr.sev-crit td.stripe{background:var(--crit)} tr.sev-run td.stripe{background:var(--run)}
td.job{font-weight:700;letter-spacing:.01em;width:78px}
td.job a{color:var(--ink);text-decoration:none;border-bottom:1.5px solid transparent}
td.job a:hover{border-bottom-color:var(--accent);color:var(--accent)}
td.status{white-space:nowrap;width:200px}
.chip{display:inline-flex;align-items:center;gap:7px;padding:4px 11px 4px 9px;border-radius:20px;
  font-size:12px;font-weight:600;border:1px solid var(--line)}
.chip .dot{width:7px;height:7px;border-radius:50%;background:var(--mut)}
tr.sev-ok .chip{background:var(--ok-bg);color:#0c7a3c;border-color:var(--ok-bd)} tr.sev-ok .dot{background:var(--ok)}
tr.sev-wait .chip{background:var(--wait-bg);color:#9a6410;border-color:var(--wait-bd)} tr.sev-wait .dot{background:var(--wait)}
tr.sev-crit .chip{background:var(--crit-bg);color:#b21f2c;border-color:var(--crit-bd)} tr.sev-crit .dot{background:var(--crit)}
tr.sev-run .chip{background:var(--run-bg);color:#234ec2;border-color:var(--run-bd)} tr.sev-run .dot{background:var(--run);animation:pulse 1.4s infinite}
@keyframes pulse{50%{opacity:.35}}
@media(prefers-reduced-motion:reduce){.dot{animation:none!important}}
td.tnum{color:var(--ink2);white-space:nowrap;width:158px}
.cd{color:var(--accent);font-size:11.5px;margin-left:5px;font-weight:600}
td.sum{color:var(--mut);max-width:1px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:12.5px}
td.log{width:54px;text-align:right}
td.log a{color:var(--mut);text-decoration:none;font-size:12.5px;font-weight:600}
td.log a:hover{color:var(--accent)}
.mut{color:var(--mut)}
footer{color:var(--mut);font-size:12px;margin-top:24px;line-height:1.75;border-top:1px solid var(--line);padding-top:16px}
footer b{color:var(--ink2)}
@media (max-width:760px){td.sum,td.tnum:nth-child(4){display:none} .kpis{grid-template-columns:repeat(2,1fr)}}
</style></head><body>
<header>
  <h1>AIOS Automation <span class="b">&middot; Fleet Health</span></h1>
  <span class="asof tnum">as of $stamp</span>
</header>
<div class="banner $bannerCls"><span class="ic">$bannerIcon</span><span>$bannerMsg</span></div>
<div class="kpis">
  <div class="kpi tot"><b>12</b><span>Jobs</span></div>
  <div class="kpi ok"><b>$nOK</b><span>Healthy</span></div>
  <div class="kpi wait"><b>$nWait</b><span>Awaiting first run</span></div>
  <div class="kpi crit"><b>$nCrit</b><span>Need attention</span></div>
</div>
$sections
<footer>
  <b>How to read this.</b> Each job's stripe and dot show its last scheduled result &mdash;
  <span style="color:var(--ok)">green healthy</span>, <span style="color:var(--wait)">amber waiting for its first run</span>,
  <span style="color:var(--crit)">red needs attention</span>. Click a job name to open its folder, or <b>log &rsaquo;</b> for its run log.<br>
  A red job showing <i>Never started (OneDrive?)</i> with no status line never launched &mdash; not a code failure. First real runs land 27 Jul &ndash; 8 Aug.<br>
  Auto-refreshes every 5 min (a background task regenerates this page every 15 min). Open it once and leave the tab Source: Windows Task Scheduler + each job's status file. Refresh any time &mdash; double-click <b>run_fleet_health.bat</b>.mdash; it stays live. Force a refresh: double-click <b>run_fleet_health.bat</b>.
</footer>
</body></html>
"@
Set-Content -Path $OUT -Value $html -Encoding utf8
"Fleet health written: $OUT  ($nOK healthy / $nWait waiting / $nCrit attention)"
if (-not $NoOpen) { Start-Process $OUT }
