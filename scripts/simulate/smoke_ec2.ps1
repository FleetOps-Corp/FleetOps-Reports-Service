#!/usr/bin/env pwsh
# Smoke test against EC2 Reports deployment (run from ReportsService root).
param(
    [string]$HostIp = "18.217.5.127",
    [int]$Port = 8081,
    [string]$PemPath = "..\fleetops-reports-key.pem",
    [string]$SshHost = "ubuntu@ec2-18-217-5-127.us-east-2.compute.amazonaws.com"
)

$ErrorActionPreference = "Stop"
$base = "http://${HostIp}:${Port}"

Write-Host "== EC2 deployed smoke test =="
Write-Host "Target: $base"

try {
    $health = Invoke-RestMethod -Uri "$base/health" -TimeoutSec 20
    Write-Host "[OK] GET /health -> $($health | ConvertTo-Json -Compress)"
} catch {
    Write-Host "[FAIL] GET /health -> $($_.Exception.Message)"
}

$payload = @{
    report_id  = "rep-ec2-sim-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    title      = "EC2 Simulation Report"
    start_date = "2026-05-01"
    end_date   = "2026-05-31"
} | ConvertTo-Json

try {
    $report = Invoke-RestMethod -Method Post -Uri "$base/reports/generate" `
        -ContentType "application/json" -Body $payload -TimeoutSec 120
    Write-Host "[OK] POST /reports/generate -> status=$($report.status) kpis=$($report.kpis.Count)"
} catch {
    Write-Host "[FAIL] POST /reports/generate -> $($_.Exception.Message)"
    if ($_.ErrorDetails.Message) { Write-Host $_.ErrorDetails.Message }
}

Write-Host "`n== EC2 in-server checks (SSH) =="
ssh -i $PemPath -o ConnectTimeout=25 -o StrictHostKeyChecking=no $SshHost @"
cd /opt/fleetops-reports
git log -1 --oneline
docker compose -f docker-compose.prod.yml --env-file .env ps
curl -sS -m 10 http://127.0.0.1:8081/openapi.json | head -c 200
echo
"@
