# Security ↔ Reports Integration Report

Generated after aligning Reports EC2 with the deployed Security Gateway (RS256 + `/api/*` routes).

## Deployed endpoints

| Service | Public base URL | Port |
|---------|-----------------|------|
| **Security Gateway** | `http://3.237.75.68:8000` | 8000 |
| **Security Gateway (DNS)** | `https://ec2-3-237-75-68.compute-1.amazonaws.com:8000` | 8000 |
| **Reports (EC2)** | `http://18.217.5.127:8081` | 8081 |

## Security route map (deployed)

| Purpose | Security path | Upstream prefix (Security `.env`) |
|---------|---------------|-----------------------------------|
| Login | `POST /auth/login` | Auth service |
| Vehicles | `GET /api/vehicles/` | `/api/vehicles` |
| Assignments | `GET /api/assignments/` | `/api/assignments` |
| Incidents | `GET /api/incidents/` | `/api/incidents` |
| Maintenance | `GET /api/maintenance/` | `/api/maintenance` |
| Reports proxy (canonical) | `POST /api/reportes/generate` | `/api/reportes` |
| Reports proxy (legacy) | `POST /api/reports/generate` | `/api/reports` |

Reports exposes matching aliases at `/api/reportes/**` and `/api/reports/**` (in addition to `/reports/**` and `/reportes/**`).

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

## Reports EC2 configuration applied

```env
OPERATIONAL_GATEWAY_BASE_URL=http://3.237.75.68:8000
OPERATIONAL_VEHICLES_PATH=/api/vehicles/
OPERATIONAL_ASSIGNMENTS_PATH=/api/assignments/
OPERATIONAL_INCIDENTS_PATH=/api/incidents/
OPERATIONAL_MAINTENANCE_PATH=/api/maintenance/
OPERATIONAL_GATEWAY_BEARER_TOKEN=<JWT from Security login>
```

Apply on server:

```bash
cd /opt/fleetops-reports
export SECURITY_GATEWAY_URL='http://3.237.75.68:8000'
export OPERATIONAL_GATEWAY_BEARER_TOKEN='<token>'
chmod +x scripts/deploy/configure_ec2_security_integration.sh
./scripts/deploy/configure_ec2_security_integration.sh .env
docker compose -f docker-compose.prod.yml --env-file .env up -d --build backend gateway
```

## Required action on Security team

Security Gateway must forward `/api/reportes/**` (or `/api/reports/**`) to the Reports public URL:

```env
REPORTS_SERVICE_URL=http://18.217.5.127:8081
REPORTS_SERVICE_PREFIX=/api/reportes
```

Without this, `POST /api/reportes/generate` on Security will not reach Reports EC2.

Security must also register role `EMPLEADO_REPORTES` in the role service and allow it on the reports route prefix.

## Verification checklist

```powershell
# From your workstation (no token — expect 401 on protected routes)
powershell -ExecutionPolicy Bypass -File scripts/simulate/smoke_security_integration.ps1

# With JWT from Security login (do not commit tokens)
powershell -ExecutionPolicy Bypass -File scripts/simulate/smoke_security_integration.ps1 -BearerToken $token
```

To bootstrap a reports test user after Security runs `seed_admin.py`, copy
`scripts/simulate/bootstrap_security_reports_user.example.ps1` locally and pass
credentials via parameters or `FLEETOPS_*` environment variables.

```bash
# On Reports EC2 (SSH)
curl -sS http://127.0.0.1:8081/health
curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8081/api/reports
# Expect 401 when JWT middleware is active

# On Security (from any host)
curl -sS -o /dev/null -w '%{http_code}\n' http://3.237.75.68:8000/api/vehicles/
# Expect 401 without Authorization header
```

## Obtain bearer token

```powershell
$login = Invoke-RestMethod -Method Post -Uri http://3.237.75.68:8000/auth/login `
  -ContentType "application/json" `
  -Body '{"email":"<ADMINISTRADOR>","password":"<password>"}'
$token = $login.access_token
```

Set `OPERATIONAL_GATEWAY_BEARER_TOKEN=$token` in `/opt/fleetops-reports/.env` and restart the backend.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| 401 on Reports protected routes | Missing/invalid JWT or wrong public key | Copy `jwt_public.pem` → `certs/public.pem`; verify RS256 tokens from Security |
| 401 on Security `/api/*` | Missing bearer token | Login again; pass `Authorization: Bearer` |
| 404 on Security `/api/reportes` | `REPORTS_SERVICE_PREFIX` not set to `/api/reportes` | Security team sets prefix and URL |
| 403 on Reports with valid JWT | Role is `EMPLEADO` (default on register) | Admin assigns `EMPLEADO_REPORTES` via `POST /roles/assign` |
| 503 on Security `/api/reports` | `REPORTS_SERVICE_URL` not set | Security team points to `http://18.217.5.127:8081` |
| 422 on generate | Upstream microservices unreachable | Confirm Vehicles/Incidents/etc. are deployed and Security routes resolve |
