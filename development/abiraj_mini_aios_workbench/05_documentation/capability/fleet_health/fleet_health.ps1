# Fleet Health - one page showing all 12 automated jobs at a glance.
# Primary data = Windows Task Scheduler (uniform for every job). Enriched with each job's last
# status line. Writes fleet_health.html next to this script and opens it.
# Run:  powershell -ExecutionPolicy Bypass -File fleet_health.ps1   (or double-click run_fleet_health.bat)

$ErrorActionPreference = 'SilentlyContinue'
$proj = "C:\Users\digit\OneDrive\Desktop\Abiraj_AIOS\development\abiraj_mini_aios_workbench\projects"
$OUT  = Join-Path $PSScriptRoot 'fleet_health.html'

# job -> scheduled-task name, cadence label, status file
$JOBS = @(
 @{n='DST';  task='DST_Daily_Sales_Track';            cad='Daily 09:15';   f="$proj\PRJ-2026-015_daily-sales-track\automation\dst_status.txt"}
 @{n='EBPD'; task='EBPD_Weekly_Dashboard';            cad='Mon 09:30';     f="$proj\PRJ-2026-011_ebay-account-performance-dashboard\automation\ebpd_status.txt"}
 @{n='SMAW'; task='SMAW_Weekly_StockCheck';           cad='Mon 10:00';     f="$proj\PRJ-2026-004_smaw-table5-stock-check\automation\smaw_status.txt"}
 @{n='EPC';  task='EPC_Weekly_Price_Checker';         cad='Mon 10:30';     f="$proj\PRJ-2026-010_ebay-price-checker\automation\epc_status.txt"}
 @{n='EPPA'; task='EPPA_Weekly_Pause_Report';         cad='Mon 11:00';     f="$proj\PRJ-2026-013_ebay-ppc-product-pause-automation\automation\eppa_status.json"}
 @{n='PC';   task='PC_Weekly_PausedCampaigns';        cad='Wed 09:00';     f="$proj\PRJ-2026-007_paused-campaign-report\automation\pc_status.txt"}
 @{n='T7';   task='T7_Weekly_SKU_Performance';        cad='Thu 11:00';     f="$proj\PRJ-2026-005_weekly-sku-performance-check\automation\t7_status.txt"}
 @{n='ESNM'; task='ESNM_Monthly_Slow_No_Moving';      cad='Monthly 2nd';   f="$proj\PRJ-2026-014_ebay-slow-no-moving-products\automation\esnm_status.json"}
 @{n='SEG';  task='SEG_Monthly_Segmentation';         cad='Monthly 3rd';   f="$proj\PRJ-2026-001_ph-segmentation\automation\seg_status.txt"}
 @{n='ZSFO'; task='ZSFO_Monthly_ZeroSales';           cad='Monthly 4th';   f="$proj\PRJ-2026-006_zero-sales-full-optimization\automation\zsfo_status.txt"}
 @{n='ERA';  task='ERA_Monthly_Dashboard';            cad='Monthly 5th';   f="$proj\PRJ-2026-012_ebay-return-analysis\automation\era_status.txt"}
 @{n='FRRC'; task='FRRC_Monthly_FBA_Returns_Report';  cad='Monthly 8th';   f=$null}
)

$rows = ''
$nOK=0; $nFail=0; $nPending=0
foreach ($j in $JOBS) {
  $t = Get-ScheduledTask -TaskName $j.task
  $i = Get-ScheduledTaskInfo -TaskName $j.task
  if (-not $t) {
    $rows += "<tr class='fail'><td>$($j.n)</td><td>$($j.cad)</td><td colspan=5>NOT REGISTERED</td></tr>"; $nFail++; continue
  }
  $code = [int64]$i.LastTaskResult
  $cls  = switch ($code) { 0 {'ok'} 267011 {'pending'} 267009 {'run'} default {'fail'} }
  $txt  = switch ($code) {
            0 {'OK'} 267011 {'never run'} 267009 {'running'} 267014 {'terminated'}
            3221225786 {'0xC000013A (never started - OneDrive?)'} default {"FAILED (code $code)"} }
  if ($cls -eq 'ok') {$nOK++} elseif ($cls -eq 'pending') {$nPending++} elseif ($cls -eq 'fail') {$nFail++}
  $last = if ($i.LastRunTime -and $i.LastRunTime.Year -gt 2000) { $i.LastRunTime.ToString('ddd dd MMM HH:mm') } else { '&mdash;' }
  $next = if ($i.NextRunTime) { $i.NextRunTime.ToString('ddd dd MMM HH:mm') } else { '&mdash;' }
  $raw = ''
  if ($j.f -and (Test-Path $j.f)) { $ll = Get-Content $j.f -Tail 1; if ($ll) { $raw = $ll.Trim() } }
  $summary = ($raw -replace '&','&amp;' -replace '<','&lt;' -replace '>','&gt;')
  if (-not $summary) { $summary = '<span class="mut">(no status line yet)</span>' }
  $rows += "<tr class='$cls'><td class='j'>$($j.n)</td><td>$($j.cad)</td><td><span class='pill $cls'>$txt</span></td><td>$last</td><td>$next</td><td>$($t.State)</td><td class='sum'>$summary</td></tr>"
}
$stamp = (Get-Date).ToString('dddd dd MMM yyyy, HH:mm')

$html = @"
<!doctype html><html><head><meta charset="utf-8"><title>AIOS Automation Fleet Health</title>
<style>
:root{--bg:#0f1420;--card:#161d2e;--ink:#e7ecf5;--mut:#8a93a8;--line:#263149;
--ok:#2f855a;--okbg:#12331f;--fail:#c8393c;--failbg:#3a1416;--pend:#b8791b;--pendbg:#332510;--run:#3956a8;}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;padding:28px}
h1{font-size:19px;margin:0 0 2px}.sub{color:var(--mut);margin:0 0 18px;font-size:13px}
.kpis{display:flex;gap:12px;margin:0 0 18px;flex-wrap:wrap}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 16px;min-width:96px}
.kpi b{font-size:22px;display:block}.kpi span{color:var(--mut);font-size:12px}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
th,td{padding:9px 12px;text-align:left;border-bottom:1px solid var(--line);font-size:13px;vertical-align:top}
th{color:var(--mut);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.03em}
tr:last-child td{border-bottom:none}
td.j{font-weight:700}td.sum{color:var(--mut);max-width:420px}
.pill{display:inline-block;padding:2px 9px;border-radius:20px;font-size:12px;font-weight:600}
.pill.ok{background:var(--okbg);color:#57d98a}.pill.fail{background:var(--failbg);color:#ff7a7d}
.pill.pending{background:var(--pendbg);color:#e0a84e}.pill.run{background:#16233f;color:#7ea0 e6}
tr.fail{background:rgba(200,57,60,.06)}.mut{color:var(--mut)}
.foot{color:var(--mut);font-size:12px;margin-top:14px}
</style></head><body>
<h1>AIOS Automation Fleet — Health</h1>
<p class="sub">12 scheduled jobs · generated $stamp</p>
<div class="kpis">
 <div class="kpi"><b>12</b><span>jobs</span></div>
 <div class="kpi"><b style="color:#57d98a">$nOK</b><span>last run OK</span></div>
 <div class="kpi"><b style="color:#e0a84e">$nPending</b><span>not run yet</span></div>
 <div class="kpi"><b style="color:#ff7a7d">$nFail</b><span>failed</span></div>
</div>
<table><thead><tr><th>Job</th><th>Cadence</th><th>Last result</th><th>Last run</th><th>Next run</th><th>State</th><th>Last status line</th></tr></thead>
<tbody>$rows</tbody></table>
<p class="foot">Source: Windows Task Scheduler + each job's status file. "never run" = scheduled but not yet fired.
A result of 0xC000013A with an empty status line means the job never started (suspected OneDrive) — not a code failure.
Re-run this page any time: <b>run_fleet_health.bat</b>.</p>
</body></html>
"@
Set-Content -Path $OUT -Value $html -Encoding utf8
"Fleet health written: $OUT  ($nOK OK / $nPending pending / $nFail failed)"
Start-Process $OUT
