#!/usr/bin/env pwsh
# Bootstrap EMPLEADO_REPORTES user on the deployed Security Gateway.
#
# Prerequisites (Security team):
#   1. Run seed_admin.py inside auth_service (creates an ADMINISTRADOR account)
#   2. Ensure role EMPLEADO_REPORTES exists in role_service and route registry
#
# Usage (pass credentials via parameters or environment variables — never commit secrets):
#   $env:FLEETOPS_ADMIN_PASSWORD = '<admin-password>'
#   $env:FLEETOPS_REPORTS_PASSWORD = '<reports-user-password>'
#   powershell -File scripts/simulate/bootstrap_security_reports_user.example.ps1 `
#     -SecurityBase http://3.237.75.68:8000 `
#     -AdminEmail admin@fleetops.com `
#     -ReportsEmail reportes@fleetops.com
#
param(
    [Parameter(Mandatory = $true)]
    [string]$SecurityBase,
    [Parameter(Mandatory = $true)]
    [string]$AdminEmail,
    [string]$AdminPassword = $env:FLEETOPS_ADMIN_PASSWORD,
    [Parameter(Mandatory = $true)]
    [string]$ReportsEmail,
    [string]$ReportsPassword = $env:FLEETOPS_REPORTS_PASSWORD
)

$ErrorActionPreference = "Stop"

if (-not $AdminPassword) {
    throw "Admin password required. Set -AdminPassword or FLEETOPS_ADMIN_PASSWORD."
}
if (-not $ReportsPassword) {
    throw "Reports user password required. Set -ReportsPassword or FLEETOPS_REPORTS_PASSWORD."
}

Write-Host "== FleetOps Security user bootstrap =="
Write-Host "Gateway: $SecurityBase"

function Invoke-SecurityJson {
    param(
        [string]$Method,
        [string]$Uri,
        [hashtable]$Body = @{},
        [hashtable]$Headers = @{}
    )
    $params = @{
        Method      = $Method
        Uri         = $Uri
        ContentType = "application/json"
        TimeoutSec  = 60
    }
    if ($Body.Count -gt 0) {
        $params.Body = ($Body | ConvertTo-Json)
    }
    if ($Headers.Count -gt 0) {
        $params.Headers = $Headers
    }
    return Invoke-RestMethod @params
}

function Get-JwtSubject([string]$Token) {
    $payload = $Token.Split(".")[1]
    $padding = "=" * ((4 - ($payload.Length % 4)) % 4)
    $json = [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($payload + $padding))
    return ($json | ConvertFrom-Json).sub
}

Write-Host "Step 1: admin login..."
$adminLogin = Invoke-SecurityJson -Method Post -Uri "$SecurityBase/auth/login" -Body @{
    email    = $AdminEmail
    password = $AdminPassword
}
$adminToken = $adminLogin.access_token
$adminUserId = Get-JwtSubject $adminToken
Write-Host "[OK] Admin token obtained."

Write-Host "Step 2: register reports user (idempotent)..."
try {
    $reportsUser = Invoke-SecurityJson -Method Post -Uri "$SecurityBase/auth/register" -Body @{
        email    = $ReportsEmail
        password = $ReportsPassword
    }
    $reportsUserId = $reportsUser.id
    Write-Host "[OK] Registered $ReportsEmail (role=$($reportsUser.role))."
} catch {
    if ($_.ErrorDetails.Message -match "already") {
        Write-Host "[SKIP] User already registered; resolving user id from JWT..."
        $reportsLoginProbe = Invoke-SecurityJson -Method Post -Uri "$SecurityBase/auth/login" -Body @{
            email    = $ReportsEmail
            password = $ReportsPassword
        }
        $reportsUserId = Get-JwtSubject $reportsLoginProbe.access_token
    } else {
        throw
    }
}

Write-Host "Step 3: assign EMPLEADO_REPORTES..."
$assignHeaders = @{ Authorization = "Bearer $adminToken" }
try {
    $assignment = Invoke-SecurityJson -Method Post -Uri "$SecurityBase/roles/assign" -Headers $assignHeaders -Body @{
        user_id     = $reportsUserId
        role_name   = "EMPLEADO_REPORTES"
        assigned_by = $adminUserId
    }
    Write-Host "[OK] Assigned $($assignment.role_name) to $ReportsEmail."
} catch {
    Write-Host "[WARN] Role assignment failed (role may not exist yet on Security):"
    Write-Host $_.Exception.Message
    if ($_.ErrorDetails.Message) { Write-Host $_.ErrorDetails.Message }
}

Write-Host "Step 4: login as reports user..."
$reportsLogin = Invoke-SecurityJson -Method Post -Uri "$SecurityBase/auth/login" -Body @{
    email    = $ReportsEmail
    password = $ReportsPassword
}
Write-Host "[OK] Reports user token ready."
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Run smoke test with the reports user token (do not commit or share tokens)."
Write-Host "  2. Set OPERATIONAL_GATEWAY_BEARER_TOKEN on Reports EC2 using an ADMINISTRADOR JWT."
