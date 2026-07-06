# Pruebas contra despliegue EC2

## Rama y commit desplegados

| Campo | Valor |
|-------|-------|
| Repositorio remoto | `https://github.com/FleetOps-Corp/report-service.git` |
| Rama en EC2 | **`aquiceno`** |
| Commit | **`54c0bc8`** — `Merge branch 'develop' into aquiceno` |
| Ruta en servidor | `/opt/fleetops-reports` |
| API pública | `http://18.217.5.127:8081` |

**Conclusión:** el despliegue corresponde a la **misma rama y commit** que el workspace local actual (`aquiceno` @ `54c0bc8`).

## Stack en EC2

```text
Cliente → Nginx gateway :8081 → FastAPI backend :8000
                              ↓
                    OPERATIONAL_GATEWAY (host:8000)
                              ↓
              vehiculos / asignaciones / incidentes / mantenimiento
```

En EC2 **no** corre el Security Gateway real; el backend usa `OPERATIONAL_GATEWAY_BASE_URL=http://host.docker.internal:8000` para consumir datos operativos.

## Paso 1 — Health check (sin gateway)

En el servidor:

```bash
curl -sS http://127.0.0.1:8081/health
# {"status":"ok","service":"fleetops-reports"}

curl -sS http://127.0.0.1:8081/metrics | head
```

Desde tu máquina (si la red lo permite):

```bash
curl -sS http://18.217.5.127:8081/health
```

> **Nota:** redes institucionales (p. ej. Univalle) pueden bloquear IPs AWS; valida siempre desde SSH en EC2.

## Paso 2 — Simular upstream operacional (mock gateway)

Archivos en el servidor: `/opt/fleetops-reports/simulate/`

```bash
cd /opt/fleetops-reports/simulate
pkill -f mock_operational_gateway.py || true
nohup python3 mock_operational_gateway.py --port 8000 > /tmp/mock-gateway.log 2>&1 &

curl -sS http://127.0.0.1:8000/health
curl -sS http://127.0.0.1:8000/vehiculos/
```

## Paso 3 — Configurar token y reiniciar backend

```bash
cd /opt/fleetops-reports
# Token simbólico; el mock no valida JWT
sed -i 's|^OPERATIONAL_GATEWAY_BEARER_TOKEN=.*|OPERATIONAL_GATEWAY_BEARER_TOKEN=simulate-token|' .env
docker compose -f docker-compose.prod.yml --env-file .env up -d backend
```

## Paso 4 — Generar reporte (simula payload desde gateway corporativo)

El Security Gateway reenviaría a Reports un POST equivalente a:

```bash
curl -sS -X POST http://127.0.0.1:8081/reports/generate \
  -H "Content-Type: application/json" \
  -d '{
    "report_id": "rep-ec2-sim-001",
    "title": "EC2 Simulation Report",
    "start_date": "2026-05-01",
    "end_date": "2026-05-31"
  }'
```

**Respuesta esperada (201):**

```json
{
  "report_id": "rep-ec2-sim-001",
  "title": "EC2 Simulation Report",
  "status": "generated",
  "document_url": "rep-ec2-sim-001.pdf",
  "kpis": [ "... 6 elementos ..." ]
}
```

## Paso 5 — Script automatizado (Windows)

```powershell
cd ReportsService
powershell -ExecutionPolicy Bypass -File scripts\simulate\smoke_ec2.ps1
```

## Estado en esta sesión

| Prueba | Resultado |
|--------|-----------|
| SSH + rama `aquiceno` | OK |
| GET `/health` en EC2 | OK |
| Mock + POST `/reports/generate` | **Pendiente** — SSH intermitente al final de la sesión; archivos mock ya copiados a `/opt/fleetops-reports/simulate/` |

Cuando SSH esté estable, ejecuta los pasos 2–4 o `smoke_ec2.ps1`.

## OpenAPI en EC2

```bash
curl -sS http://127.0.0.1:8081/openapi.json | head -c 300
# O abrir en navegador (túnel SSH): http://127.0.0.1:8081/docs
```

Túnel SSH desde Windows:

```powershell
ssh -i fleetops-reports-key.pem -L 8081:127.0.0.1:8081 ubuntu@ec2-18-217-5-127.us-east-2.compute.amazonaws.com
# Luego: http://localhost:8081/docs
```
