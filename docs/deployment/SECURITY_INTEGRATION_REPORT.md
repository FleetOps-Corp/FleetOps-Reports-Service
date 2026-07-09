# Security ↔ Reports Integration Report

Generated after aligning Reports EC2 with the deployed Security Gateway (RS256 + microservice route prefixes).

## Deployed endpoints

| Service | Public base URL | Port |
|---------|-----------------|------|
| **Security Gateway** | `http://3.237.75.68:8000` | 8000 |
| **Security Gateway (DNS)** | `https://ec2-3-237-75-68.compute-1.amazonaws.com:8000` | 8000 |
| **Reports (EC2)** | `http://18.217.5.127:8081` | 8081 |

## Aligned route map (Gateway prefix = microservice path)

The Gateway forwards `{upstream}{path}` without rewrite. Security `*_SERVICE_PREFIX` and Reports `OPERATIONAL_*_PATH` must match the microservice internal routes:

| Purpose | Gateway / Reports path | Microservice internal route |
|---------|------------------------|----------------------------|
| Login | `POST /auth/login` | Auth `POST /login` |
| Vehicles | `GET /vehiculos/` | Vehicles `@RequestMapping("/vehiculos")` |
| Assignments | `GET /asignaciones/` | Assignments `@RequestMapping("/asignaciones")` (list may be unavailable) |
| Incidents | `GET /api/incidents/` | Incidents Django `/api/incidents/` |
| Maintenance | `GET /api/v1/mantenimientos/` | Maintenance Chi `/api/v1/mantenimientos` |
| Reports (canonical) | `POST /api/reportes/generate` | Reports `/api/reportes/generate` |
| Reports (legacy) | `POST /api/reports/generate` | Reports `/api/reports/generate` |

Reports exposes matching aliases at `/api/reportes/**`, `/api/reports/**`, `/reportes/**`, and `/reports/**`.

Inbound JWT roles accepted by Reports: `ADMINISTRADOR`, `EMPLEADO_REPORTES`.

## JWT model (RS256)

| Role | Key material | Where |
|------|--------------|-------|
| Security Auth | **Private key** (signs tokens) | Security server only — never in Reports |
| Reports | **Public key** (`jwt_public.pem`) | `certs/public.pem` → `/app/certs/public.pem` |

Reports `.env` on EC2:

```env
JWT_ALGORITHM=RS256
JWT_PUBLIC_KEY_PATH=/app/certs/public.pem
```

Do **not** set `JWT_SECRET_KEY` on Reports when using RS256.

## Reports EC2 configuration

```env
OPERATIONAL_GATEWAY_BASE_URL=http://3.237.75.68:8000
OPERATIONAL_VEHICLES_PATH=/vehiculos/
OPERATIONAL_ASSIGNMENTS_PATH=/asignaciones/
OPERATIONAL_INCIDENTS_PATH=/api/incidents/
OPERATIONAL_MAINTENANCE_PATH=/api/v1/mantenimientos/

# Option A — static JWT (~60 min TTL):
OPERATIONAL_GATEWAY_BEARER_TOKEN=

# Option B — service account auto-login (recommended):
OPERATIONAL_GATEWAY_SERVICE_EMAIL=<admin-or-service-account>
OPERATIONAL_GATEWAY_SERVICE_PASSWORD=<password>
```

Apply on server:

```bash
cd /opt/fleetops-reports
git pull origin aquiceno
export SECURITY_GATEWAY_URL='http://3.237.75.68:8000'
export OPERATIONAL_GATEWAY_SERVICE_EMAIL='<email>'
export OPERATIONAL_GATEWAY_SERVICE_PASSWORD='<password>'
chmod +x scripts/deploy/configure_ec2_security_integration.sh
./scripts/deploy/configure_ec2_security_integration.sh .env
docker compose -f docker-compose.prod.yml --env-file .env up -d --build backend gateway
```

## Required action on Security team

Security Gateway must register aligned prefixes and forward `/api/reportes/**` to Reports:

```env
VEHICLES_SERVICE_PREFIX=/vehiculos
ASSIGNMENTS_SERVICE_PREFIX=/asignaciones
INCIDENTS_SERVICE_PREFIX=/api/incidents
MAINTENANCE_SERVICE_PREFIX=/api/v1/mantenimientos
REPORTS_SERVICE_URL=http://18.217.5.127:8081
REPORTS_SERVICE_PREFIX=/api/reportes
```

Security must also register role `EMPLEADO_REPORTES` and allow it on the reports route prefix.

## Verification checklist

```powershell
powershell -ExecutionPolicy Bypass -File scripts/simulate/smoke_security_integration.ps1
powershell -ExecutionPolicy Bypass -File scripts/simulate/smoke_security_integration.ps1 -BearerToken $token
```

```bash
curl -sS http://127.0.0.1:8081/health
curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8081/api/reportes
curl -sS -o /dev/null -w '%{http_code}\n' http://3.237.75.68:8000/vehiculos/
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| 401 on Reports protected routes | Missing/invalid JWT or wrong public key | Copy `jwt_public.pem` → `certs/public.pem`; verify RS256 tokens |
| 401 on Security upstream routes | Missing outbound token | Set service account credentials or `OPERATIONAL_GATEWAY_BEARER_TOKEN` |
| 404 on Security `/api/reportes` | Reports route not registered | Security sets `REPORTS_SERVICE_PREFIX=/api/reportes` |
| 404 on `/vehiculos/` via Gateway | Prefix mismatch | Security `VEHICLES_SERVICE_PREFIX=/vehiculos` |
| 403 on Reports with valid JWT | Role not allowed | Admin assigns `EMPLEADO_REPORTES` |
| 422 on generate | Upstream unreachable or field mismatch | Confirm aligned paths; check backend logs |
