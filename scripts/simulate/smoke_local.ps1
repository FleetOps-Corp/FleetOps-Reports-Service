#!/usr/bin/env pwsh
# Local integration smoke test (Security Gateway + Reports + mock upstream).
param(
    [string]$GatewayBase = "http://localhost:8000",
    [string]$ReportsBase = "http://localhost:8080",
    [string]$IncidentsDirect = "http://localhost:8030",
    [string]$AdminEmail = "simulator@example.com",
    [string]$AdminPassword = "Simulate123",
    [string]$Sede = "Patio Norte Bogotá"
)

$ErrorActionPreference = "Stop"

function Invoke-Json {
    param([string]$Method = "Get", [string]$Uri, [hashtable]$Body, [hashtable]$Headers = @{})
    $params = @{ Method = $Method; Uri = $Uri; Headers = $Headers; TimeoutSec = 120 }
    if ($Body) { $params.Body = ($Body | ConvertTo-Json -Depth 6); $params.ContentType = "application/json" }
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

Write-Host "`n[3] Reports health (public route)"
$repHealth = Invoke-Json -Uri "$ReportsBase/health"
Write-Host "OK: $($repHealth | ConvertTo-Json -Compress)"

Write-Host "`n[4] Reports generate via Security Gateway (/reportes/generate)"
$reportId = "rep-local-sim-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
$reportGw = Invoke-Json -Method Post -Uri "$GatewayBase/reportes/generate" -Headers $auth -Body @{
    report_id = $reportId
    title = "Gateway Simulation Report"
    start_date = "2026-05-01"
    end_date = "2026-05-31"
    sede_operacion = $Sede
}
Write-Host "OK: status=$($reportGw.status) kpis=$($reportGw.kpis.Count) sede=$($reportGw.sede_operacion)"

Write-Host "`n[5] Reports generate (direct API with forwarded JWT)"
$directId = "$reportId-direct"
$reportDirect = Invoke-Json -Method Post -Uri "$ReportsBase/reports/generate" -Headers $auth -Body @{
    report_id = $directId
    title = "Direct Simulation Report"
    start_date = "2026-05-01"
    end_date = "2026-05-31"
    sede_operacion = $Sede
}
Write-Host "OK: status=$($reportDirect.status) document=$($reportDirect.document_url)"

Write-Host "`n[6] List reports filtered by sede"
$list = Invoke-Json -Uri "$ReportsBase/reports?sede_operacion=$([uri]::EscapeDataString($Sede))" -Headers $auth
Write-Host "OK: total=$($list.total) reports for sede '$Sede'"

Write-Host "`n[7] Download PDF to docs/reports"
$outDir = Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) "docs/reports"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$pdfPath = Join-Path $outDir "$directId.pdf"
Invoke-WebRequest -Uri "$ReportsBase/reports/$directId/download" -Headers $auth -OutFile $pdfPath
Write-Host "OK: saved $pdfPath"

Write-Host "`nAll local checks completed."
