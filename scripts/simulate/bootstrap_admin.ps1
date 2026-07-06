#!/usr/bin/env pwsh
# Promote a registered Security Gateway user to ADMINISTRADOR (local dev only).
param(
    [string]$Email = "simulator@example.com",
    [string]$Password = "Simulate123"
)

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..\..\..\FleetOps-Security-Service")

docker compose up -d postgres auth_service role_service api_gateway | Out-Null
Start-Sleep -Seconds 5

try {
    Invoke-RestMethod -Method Post -Uri "http://localhost:8000/auth/register" `
        -ContentType "application/json" `
        -Body (@{ email = $Email; password = $Password } | ConvertTo-Json) | Out-Null
} catch {}

docker compose exec -T postgres psql -U fleetops_user -d fleetops_security -c @"
UPDATE users
SET role_id = (SELECT id FROM roles WHERE name = 'ADMINISTRADOR')
WHERE email = '$Email';
"@

$login = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/auth/login" `
    -ContentType "application/json" `
    -Body (@{ email = $Email; password = $Password } | ConvertTo-Json)

Write-Host "ADMINISTRADOR token ready. Set in ReportsService/.env:"
Write-Host "OPERATIONAL_GATEWAY_BEARER_TOKEN=$($login.access_token)"
