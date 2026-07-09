#!/usr/bin/env pwsh
# Download a generated report PDF from a running Reports stack into docs/reports/.
param(
    [Parameter(Mandatory = $true)][string]$ReportId,
    [string]$ReportsBase = "http://localhost:8080",
    [string]$GatewayBase = "http://localhost:8000",
    [string]$AdminEmail = "simulator@example.com",
    [string]$AdminPassword = "Simulate123",
    [string]$OutputDir = ""
)

$ErrorActionPreference = "Stop"

if (-not $OutputDir) {
    $OutputDir = Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) "docs/reports"
}
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$login = Invoke-RestMethod -Method Post -Uri "$GatewayBase/auth/login" `
    -ContentType "application/json" `
    -Body (@{ email = $AdminEmail; password = $AdminPassword } | ConvertTo-Json)

$headers = @{ Authorization = "Bearer $($login.access_token)" }
$target = Join-Path $OutputDir "$ReportId.pdf"
Invoke-WebRequest -Uri "$ReportsBase/reports/$ReportId/download" -Headers $headers -OutFile $target
Write-Host "Downloaded report to $target"
