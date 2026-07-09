# Deployment Testing Guide

This guide explains how to validate a deployed FleetOps Reports instance (EC2 or local production compose), including authentication, report generation, site filtering, listing, and PDF download.

## Prerequisites

- Running Reports stack (`docker-compose.prod.yml` on EC2 or local)
- FleetOps Security Gateway reachable from the Reports backend (`OPERATIONAL_GATEWAY_BASE_URL`)
- `OPERATIONAL_GATEWAY_BEARER_TOKEN` configured with an `ADMINISTRADOR` JWT
- Matching inbound JWT settings on Reports (must match how Security **signs** tokens today):
  - **HS256 (current Security Service):** `JWT_ALGORITHM=HS256` and `JWT_SECRET_KEY` identical to Security Service
  - **RS256 (future / public-key verification):** `JWT_ALGORITHM=RS256` and `JWT_PUBLIC_KEY_PATH=/app/certs/public.pem`

> **Architecture note:** FleetOps Security currently issues HS256 tokens with a shared secret.
> Reports supports both HS256 (production today) and RS256 public-key verification (see `certs/README.md`
> and `docs/token/Miniguia para verificar los tokens con llave publica.md`).

## Public routes (no JWT)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness probe |
| GET | `/metrics` | Prometheus metrics |

## Protected routes (ADMINISTRADOR JWT required)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/reports/generate` | Generate executive report |
| POST | `/api/reports/generate` | Security Gateway alias |
| GET | `/reports` | List stored reports (`?sede_operacion=` optional) |
| GET | `/api/reports` | Gateway alias for listing |
| GET | `/reports/{report_id}` | Report metadata |
| GET | `/reports/{report_id}/download` | Download PDF from MinIO |

## Request body (generate)

```json
{
  "report_id": "rep-20260707-001",
  "title": "Executive Report - Patio Norte",
  "start_date": "2026-05-01",
  "end_date": "2026-05-31",
  "sede_operacion": "Patio Norte Bogotá"
}
```

`sede_operacion` is optional. When provided, Reports filters vehicles by the `sede_operacion` / `sedeOperacion` field exposed by the Vehicles service and correlates incidents and maintenance to those vehicles.

## Step 1 — Obtain JWT from Security Gateway

```powershell
$login = Invoke-RestMethod -Method Post -Uri http://<security-host>:8000/auth/login `
  -ContentType "application/json" `
  -Body '{"email":"<admin>","password":"<password>"}'
$token = $login.access_token
```

## Step 2 — Health check

```powershell
curl http://<reports-host>:8081/health
```

Expected: `{"status":"ok","service":"fleetops-reports"}`

## Step 3 — Generate report via Security Gateway

```powershell
Invoke-RestMethod -Method Post -Uri http://<security-host>:8000/api/reports/generate `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body '{
    "report_id": "rep-deploy-001",
    "title": "Deployment Validation",
    "start_date": "2026-05-01",
    "end_date": "2026-05-31",
    "sede_operacion": "Patio Norte Bogotá"
  }'
```

## Step 4 — List reports filtered by site

```powershell
Invoke-RestMethod -Uri "http://<reports-host>:8081/reports?sede_operacion=Patio%20Norte%20Bogot%C3%A1" `
  -Headers @{ Authorization = "Bearer $token" }
```

## Step 5 — Download PDF to local docs folder

```powershell
powershell -ExecutionPolicy Bypass -File scripts/simulate/download_report.ps1 `
  -ReportId rep-deploy-001 `
  -ReportsBase http://<reports-host>:8081 `
  -GatewayBase http://<security-host>:8000
```

PDFs are saved under `docs/reports/`.

## Automated smoke tests

```powershell
# Local stack
powershell -ExecutionPolicy Bypass -File scripts/simulate/smoke_local.ps1

# EC2 deployment (requires token)
powershell -ExecutionPolicy Bypass -File scripts/simulate/smoke_ec2.ps1 -BearerToken $token
```

## Troubleshooting

| Symptom | Likely cause | Action |
|---------|--------------|--------|
| 401 on `/reports/*` | Missing or invalid JWT | Login again; verify `JWT_SECRET_KEY` matches Security |
| 401 after deploy | JWT vars missing in EC2 `.env` | Run `scripts/deploy/ensure_jwt_env.sh` (see below) |
| 403 on generate | Non-admin role | Use `ADMINISTRADOR` account |
| 422 on generate | Upstream unavailable | Verify Security Gateway routes and mock/services |
| Empty KPIs for sede | No vehicles in site | Confirm Vehicles service returns `sede_operacion` |
| Download 404 | Report not persisted | Check MongoDB URI and MinIO buckets |

## EC2 — apply JWT variables (required once)

Protected routes return **401** until Reports shares the same HS256 secret as Security Service.

On the EC2 host (`/opt/fleetops-reports`):

```bash
export JWT_SECRET_KEY='<same value as FleetOps-Security-Service>'
chmod +x scripts/deploy/ensure_jwt_env.sh
./scripts/deploy/ensure_jwt_env.sh .env
docker compose -f docker-compose.prod.yml --env-file .env up -d backend
```

Verify (from SSH on EC2, with a valid admin token):

```bash
curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8081/reports
# Expect 401 without Authorization header after JWT is configured
```

## Version

Current release: **2.1.0** (see `VERSION` and `CHANGELOG.md`).
