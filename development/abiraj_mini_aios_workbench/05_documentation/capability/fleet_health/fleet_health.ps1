# Fleet Health - mission-control status board for all 12 automated jobs.
# Reads Windows Task Scheduler (uniform for every job) + each job's status file, writes
# fleet_health.html next to this script and opens it.
# Run:  double-click run_fleet_health.bat   (or: powershell -ExecutionPolicy Bypass -File fleet_health.ps1)

$ErrorActionPreference = 'SilentlyContinue'
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
  $raw = ''
  if ($statusfile -and (Test-Path $statusfile)) { $ll = Get-Content $statusfile -Tail 1; if ($ll) { $raw = $ll.Trim() } }
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
        <td class="status"><span class="dot"></span>$($r.txt)</td>
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
<title>AIOS Automation - Fleet Health</title>
<style>
:root{
  --bg:#0d1420; --panel:#141d2c; --panel2:#111927; --line:#25344b; --ink:#eaf0f9; --mut:#8493ab;
  --accent:#48b6d8;
  --ok:#3ec98a; --ok-bg:#0f2e20; --wait:#e0a63e; --wait-bg:#2e2410; --crit:#ff5f66; --crit-bg:#331317; --run:#5b8cff; --run-bg:#131f3d;
}
*{box-sizing:border-box} html,body{margin:0}
body{background:radial-gradient(1200px 600px at 20% -10%, #16233a 0%, var(--bg) 60%) fixed;
  color:var(--ink); font:14px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  padding:30px clamp(16px,4vw,44px); -webkit-font-smoothing:antialiased}
.tnum{font-variant-numeric:tabular-nums}
header{display:flex;align-items:baseline;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:18px}
h1{font-size:18px;letter-spacing:.02em;margin:0;font-weight:650}
h1 .b{color:var(--mut);font-weight:400}
.asof{color:var(--mut);font-size:12.5px}
.banner{display:flex;align-items:center;gap:12px;border-radius:13px;padding:15px 18px;margin-bottom:20px;
  border:1px solid var(--line);font-size:15px;font-weight:600}
.banner .ic{font-size:19px;line-height:1}
.banner.ok{background:linear-gradient(90deg,var(--ok-bg),transparent);border-color:#1c5238;color:#7fe3b4}
.banner.wait,.banner.run{background:linear-gradient(90deg,var(--run-bg),transparent);border-color:#274a86;color:#9db9ff}
.banner.crit{background:linear-gradient(90deg,var(--crit-bg),transparent);border-color:#6a2027;color:#ff9297}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:26px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.kpi b{font-size:26px;display:block;line-height:1.1;font-variant-numeric:tabular-nums}
.kpi span{color:var(--mut);font-size:12px;text-transform:uppercase;letter-spacing:.05em}
.kpi.ok b{color:var(--ok)} .kpi.wait b{color:var(--wait)} .kpi.crit b{color:var(--crit)} .kpi.tot b{color:var(--ink)}
.grp{margin-bottom:24px}
.ghead{display:flex;align-items:center;gap:10px;margin:0 2px 8px}
.ghead h2{font-size:12px;text-transform:uppercase;letter-spacing:.14em;color:var(--mut);font-weight:700;margin:0}
.gcount{font-size:11px;color:var(--mut);background:var(--panel);border:1px solid var(--line);border-radius:20px;padding:1px 9px}
table{width:100%;border-collapse:separate;border-spacing:0;background:var(--panel);border:1px solid var(--line);border-radius:12px;overflow:hidden}
td{padding:12px 14px;border-top:1px solid var(--line);vertical-align:middle;font-size:13.5px}
tbody tr:first-child td{border-top:none}
tr:hover td{background:rgba(255,255,255,.018)}
td.stripe{width:4px;padding:0;background:var(--mut)}
tr.sev-ok    td.stripe{background:var(--ok)}   tr.sev-wait td.stripe{background:var(--wait)}
tr.sev-crit  td.stripe{background:var(--crit)} tr.sev-run  td.stripe{background:var(--run)}
td.job{font-weight:700;letter-spacing:.02em;width:74px}
td.job a{color:var(--ink);text-decoration:none;border-bottom:1px dotted transparent}
td.job a:hover{border-bottom-color:var(--accent);color:#fff}
td.status{white-space:nowrap;width:210px;color:var(--mut)}
td.status .dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:8px;vertical-align:middle;background:var(--mut)}
tr.sev-ok .dot{background:var(--ok);box-shadow:0 0 0 3px var(--ok-bg)}
tr.sev-wait .dot{background:var(--wait);box-shadow:0 0 0 3px var(--wait-bg)}
tr.sev-crit .dot{background:var(--crit);box-shadow:0 0 0 3px var(--crit-bg)}
tr.sev-run  .dot{background:var(--run);box-shadow:0 0 0 3px var(--run-bg);animation:pulse 1.4s infinite}
@keyframes pulse{50%{opacity:.4}}
tr.sev-ok td.status{color:#8fe6bd} tr.sev-crit td.status{color:#ff9297}
td.tnum{color:var(--mut);white-space:nowrap;width:150px}
.cd{color:var(--accent);font-size:12px;margin-left:4px}
td.sum{color:var(--mut);max-width:1px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
td.log{width:52px;text-align:right}
td.log a{color:var(--mut);text-decoration:none;font-size:12.5px}
td.log a:hover{color:var(--accent)}
.mut{color:var(--mut)}
footer{color:var(--mut);font-size:12px;margin-top:22px;line-height:1.7;border-top:1px solid var(--line);padding-top:14px}
@media (max-width:720px){td.sum,td.tnum:nth-child(4){display:none} .kpis{grid-template-columns:repeat(2,1fr)}}
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
  Source: Windows Task Scheduler + each job's status file. Refresh any time &mdash; double-click <b>run_fleet_health.bat</b>.
</footer>
</body></html>
"@
Set-Content -Path $OUT -Value $html -Encoding utf8
"Fleet health written: $OUT  ($nOK healthy / $nWait waiting / $nCrit attention)"
Start-Process $OUT
