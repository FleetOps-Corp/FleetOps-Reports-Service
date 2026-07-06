#!/usr/bin/env pwsh
# Local integration smoke test (Security Gateway + Incidents + Reports + mock upstream).
param(
    [string]$GatewayBase = "http://localhost:8000",
    [string]$ReportsBase = "http://localhost:8080",
    [string]$IncidentsDirect = "http://localhost:8030",
    [string]$AdminEmail = "simulator@example.com",
    [string]$AdminPassword = "Simulate123"
)

$ErrorActionPreference = "Stop"

function Invoke-Json {
    param([string]$Method = "Get", [string]$Uri, [hashtable]$Body, [hashtable]$Headers = @{})
    $params = @{ Method = $Method; Uri = $Uri; Headers = $Headers; TimeoutSec = 60 }
    if ($Body) { $params.Body = ($Body | ConvertTo-Json); $params.ContentType = "application/json" }
    return Invoke-RestMethod @params
}

Write-Host "== Local integration smoke test =="

Write-Host "`n[1] Security Gateway liveness (GET /docs)"
$docsStatus = (Invoke-WebRequest -Uri ($GatewayBase + "/docs") -TimeoutSec 20).StatusCode
Write-Host "OK: GET /docs -> HTTP $docsStatus"

Write-Host "`n[2] Register/login admin (ignore register conflict)"
try {
    Invoke-Json -Method Post -Uri "$GatewayBase/auth/register" -Body @{
        email = $AdminEmail; password = $AdminPassword
    } | Out-Null
} catch { Write-Host "Register skipped (user may exist)" }

$tokenResp = Invoke-Json -Method Post -Uri "$GatewayBase/auth/login" -Body @{
    email = $AdminEmail; password = $AdminPassword
}
$token = $tokenResp.access_token
$auth = @{ Authorization = "Bearer $token" }
Write-Host "OK: JWT acquired (expires_in=$($tokenResp.expires_in)s)"

Write-Host "`n[3] Incidents direct (/api/incidents/)"
$direct = Invoke-Json -Uri "$IncidentsDirect/api/incidents/"
Write-Host "OK: direct incidents count=$($direct.Count)"

Write-Host "`n[4] Incidents via Security Gateway (/incidentes/)"
$viaGw = Invoke-Json -Uri "$GatewayBase/incidentes/" -Headers $auth
Write-Host "OK: gateway incidents count=$($viaGw.Count)"

Write-Host "`n[5] Reports health"
$repHealth = Invoke-Json -Uri "$ReportsBase/health"
Write-Host "OK: $($repHealth | ConvertTo-Json -Compress)"

Write-Host "`n[6] Reports generate (direct API)"
$reportId = "rep-local-sim-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
$report = Invoke-Json -Method Post -Uri "$ReportsBase/reports/generate" -Body @{
    report_id = $reportId; title = "Local Simulation Report"
    start_date = "2026-05-01"; end_date = "2026-05-31"
}
Write-Host "OK: status=$($report.status) kpis=$($report.kpis.Count) document=$($report.document_url)"

Write-Host "`n[7] Reports via Security Gateway (/reportes/generate)"
$reportGw = Invoke-Json -Method Post -Uri "$GatewayBase/reportes/generate" -Headers $auth -Body @{
    report_id = "$reportId-gw"; title = "Gateway Simulation Report"
    start_date = "2026-05-01"; end_date = "2026-05-31"
}
Write-Host "OK: status=$($reportGw.status) kpis=$($reportGw.kpis.Count)"

Write-Host "`nAll local checks completed."
