# Pruebas locales — Security Gateway + Incidents + Reports

## Objetivo

Validar el flujo completo:

1. **Incidents → Security Gateway** (`GET /incidentes/`)
2. **Incidents directo (develop)** (`GET /api/incidents/`)
3. **Reports → Security Gateway** (consumo upstream + `POST /reportes/generate`)
4. **Reports directo** (`POST /reports/generate`)

## 1. Levantar mock upstream (fixtures)

Terminal A — desde `ReportsService`:

```powershell
python scripts/simulate/mock_operational_gateway.py --port 8099
```

Sirve JSON en `/vehiculos/`, `/asignaciones/`, `/incidentes/`, `/mantenimiento/`.

## 2. Security Gateway

Terminal B — `FleetOps-Security-Service`:

Asegura en `.env`:

```env
VEHICLES_SERVICE_URL=http://host.docker.internal:8099
ASSIGNMENTS_SERVICE_URL=http://host.docker.internal:8099
INCIDENTS_SERVICE_URL=http://host.docker.internal:8030
MAINTENANCE_SERVICE_URL=http://host.docker.internal:8099
REPORTS_SERVICE_URL=http://host.docker.internal:8080
```

```powershell
docker compose up -d --build
```

> Si `entrypoint.sh` falla en Windows, convierte CRLF→LF (ver `05-failure-report.md` F-004).

Bootstrap admin:

```powershell
cd ..\ReportsService
powershell -ExecutionPolicy Bypass -File scripts\simulate\bootstrap_admin.ps1
```

Copia el token a `ReportsService/.env`:

```env
OPERATIONAL_GATEWAY_BEARER_TOKEN=<token>
```

## 3. Incidents Service

Terminal C — `FleetOps-Incidents-Service`:

```powershell
docker compose up -d --build
docker compose exec incidents-service python manage.py migrate
```

Puerto publicado: **8030** (mapeo `8030:8000`).

## 4. Reports Service (develop local)

Terminal D — `ReportsService`:

```powershell
docker compose -f docker-compose.yml -f docs/simulate/docker-compose.simulate.override.yml up -d --build
```

El override usa MongoDB embebido del compose (no Atlas) para evitar SSL desde Docker.

## 5. Ejecutar smoke test

```powershell
powershell -ExecutionPolicy Bypass -File scripts\simulate\smoke_local.ps1
```

## Resultado ejecutado (2026-07-02)

```
[1] Security Gateway liveness (GET /docs)          OK
[2] Register/login admin                           OK
[3] Incidents direct (/api/incidents/)             OK (0 registros)
[4] Incidents via Security Gateway (/incidentes/)  OK (0 registros)
[5] Reports health                                 OK
[6] Reports generate (direct API)                  OK — 6 KPIs, PDF generado
[7] Reports via Security Gateway (/reportes/generate) OK — 6 KPIs
```

Salida completa: [artifacts/local-smoke-output.txt](./artifacts/local-smoke-output.txt)

## Pruebas manuales curl

### A. Incidents directo (develop)

```powershell
curl http://localhost:8030/health
curl http://localhost:8030/api/incidents/
```

### B. Incidents vía Security Gateway

```powershell
# Obtener JWT
$login = Invoke-RestMethod -Method Post -Uri http://localhost:8000/auth/login `
  -ContentType application/json `
  -Body '{"email":"simulator@example.com","password":"Simulate123"}'
$token = $login.access_token

curl -H "Authorization: Bearer $token" http://localhost:8000/incidentes/
```

### C. Crear incidente (gateway, payload español)

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/incidentes/create/ `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType application/json `
  -Body '{
    "id_conductor": "11111111-1111-1111-1111-111111111111",
    "placa_vehiculo": "FOP-002",
    "tipo_incidente": "MECANICO",
    "gravedad": "GRAVE",
    "descripcion": "Falla de motor en ruta",
    "fecha_hora": "2026-05-15T10:30:00Z"
  }'
```

### D. Generar reporte directo

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8080/reports/generate `
  -ContentType application/json `
  -Body '{
    "report_id": "rep-manual-001",
    "title": "Manual Test",
    "start_date": "2026-05-01",
    "end_date": "2026-05-31"
  }'
```

### E. Generar reporte vía Security Gateway

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/reportes/generate `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType application/json `
  -Body '{
    "report_id": "rep-gw-manual-001",
    "title": "Gateway Manual Test",
    "start_date": "2026-05-01",
    "end_date": "2026-05-31"
  }'
```

## Detener servicios

```powershell
# Reports
docker compose -f docker-compose.yml -f docs/simulate/docker-compose.simulate.override.yml down

# Incidents
cd ..\FleetOps-Incidents-Service; docker compose down

# Security Gateway
cd ..\FleetOps-Security-Service; docker compose down
```

Mock upstream: Ctrl+C en Terminal A.
