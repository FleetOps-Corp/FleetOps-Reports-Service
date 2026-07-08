#!/usr/bin/env pwsh
# Validate connectivity between deployed Security Gateway and Reports EC2.
param(
    [string]$SecurityBase = "http://3.237.75.68:8000",
    [string]$ReportsBase = "http://18.217.5.127:8081",
    [string]$BearerToken = ""
)

$ErrorActionPreference = "Stop"

Write-Host '== Security <-> Reports integration smoke =='
Write-Host "Security: $SecurityBase"
Write-Host "Reports:  $ReportsBase"

function Test-Status {
    param([string]$Label, [string]$Uri, [int[]]$Expected = @(200, 401, 403))
    try {
        $response = Invoke-WebRequest -Uri $Uri -TimeoutSec 20 -SkipHttpErrorCheck
        $ok = $Expected -contains $response.StatusCode
        $mark = if ($ok) { "OK" } else { "WARN" }
        Write-Host ('[{0}] {1} -> HTTP {2}' -f $mark, $Label, $response.StatusCode)
        return $response.StatusCode
    } catch {
        Write-Host ('[FAIL] {0} -> {1}' -f $Label, $_.Exception.Message)
        return -1
    }
}

Test-Status "Security OpenAPI" "$SecurityBase/openapi.json" @(200) | Out-Null
Test-Status "Security /api/vehicles (auth required)" "$SecurityBase/api/vehicles/" @(401, 403) | Out-Null
Test-Status "Security /api/reports (auth required)" "$SecurityBase/api/reports/" @(401, 403) | Out-Null
Test-Status "Reports /health (public)" "$ReportsBase/health" @(200) | Out-Null
Test-Status "Reports /reports (JWT required)" "$ReportsBase/reports" @(401) | Out-Null
Test-Status "Reports /api/reports (JWT required)" "$ReportsBase/api/reports" @(401) | Out-Null

if (-not $BearerToken) {
    Write-Host '[SKIP] Authenticated generate tests require -BearerToken from Security /auth/login'
    exit 0
}

$headers = @{ Authorization = "Bearer $BearerToken" }
$reportId = "rep-sec-int-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

try {
    $viaSecurity = Invoke-RestMethod -Method Post -Uri "$SecurityBase/api/reports/generate" `
        -Headers $headers -ContentType "application/json" -TimeoutSec 120 -Body (@{
            report_id = $reportId
            title = "Security Integration Report"
            start_date = "2026-05-01"
            end_date = "2026-05-31"
        } | ConvertTo-Json)
    Write-Host ('[OK] Security POST /api/reports/generate -> status={0}' -f $viaSecurity.status)
} catch {
    Write-Host ('[FAIL] Security POST /api/reports/generate -> {0}' -f $_.Exception.Message)
    if ($_.ErrorDetails.Message) { Write-Host $_.ErrorDetails.Message }
}

try {
    $direct = Invoke-RestMethod -Method Post -Uri "$ReportsBase/api/reports/generate" `
        -Headers $headers -ContentType "application/json" -TimeoutSec 120 -Body (@{
            report_id = "$reportId-direct"
            title = "Direct Reports API Test"
            start_date = "2026-05-01"
            end_date = "2026-05-31"
        } | ConvertTo-Json)
    Write-Host ('[OK] Reports POST /api/reports/generate -> status={0}' -f $direct.status)
} catch {
    Write-Host ('[FAIL] Reports POST /api/reports/generate -> {0}' -f $_.Exception.Message)
    if ($_.ErrorDetails.Message) { Write-Host $_.ErrorDetails.Message }
}
