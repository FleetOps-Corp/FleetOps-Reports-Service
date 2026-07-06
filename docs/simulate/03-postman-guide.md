# Guía Postman — FleetOps Reports Simulation

## Importar colección

1. Abre Postman.
2. **Import** → selecciona `docs/simulate/postman/FleetOps-Simulation.postman_collection.json`.
3. Crea un **Environment** con las variables siguientes.

## Variables de entorno

| Variable | Local | EC2 |
|----------|-------|-----|
| `reports_base` | `http://localhost:8080` | `http://18.217.5.127:8081` |
| `gateway_base` | `http://localhost:8000` | N/A (no desplegado en EC2) |
| `incidents_direct` | `http://localhost:8030` | N/A |
| `admin_email` | `simulator@example.com` | — |
| `admin_password` | `Simulate123` | — |
| `gateway_token` | *(vacío; se llena tras Login)* | — |

## Orden recomendado (local)

### Carpeta `0 - Auth`

1. **Register Admin** — opcional si el usuario ya existe.
2. **Login Admin** — guarda `access_token` en `gateway_token` (Tests script incluido).

### Carpeta `1 - Health`

3. **Reports Health** → `GET {{reports_base}}/health`
4. **Gateway Docs** → `GET {{gateway_base}}/docs`
5. **Incidents Health** → `GET {{incidents_direct}}/health`

### Carpeta `2 - Incidents`

6. **Incidents Direct List** → `GET {{incidents_direct}}/api/incidents/`
7. **Incidents Gateway List** → `GET {{gateway_base}}/incidentes/` + Bearer
8. **Incidents Gateway Create** → `POST {{gateway_base}}/incidentes/create/` + body español

### Carpeta `3 - Reports`

9. **Generate Report Direct** → `POST {{reports_base}}/reports/generate`
10. **Generate Report via Gateway** → `POST {{gateway_base}}/reportes/generate` + Bearer

### Carpeta `4 - EC2 Deployed`

11. **EC2 Health** → `GET {{reports_base}}/health` (con `reports_base` apuntando a EC2)
12. **EC2 Generate Report** → requiere mock gateway en EC2 (ver `01-deployed-ec2.md`)

## Headers comunes

| Header | Valor |
|--------|-------|
| `Content-Type` | `application/json` |
| `Authorization` | `Bearer {{gateway_token}}` *(solo rutas gateway protegidas)* |

## Body ejemplo — Generate Report

```json
{
  "report_id": "rep-postman-001",
  "title": "Postman Simulation",
  "start_date": "2026-05-01",
  "end_date": "2026-05-31"
}
```

## Body ejemplo — Create Incident (gateway)

```json
{
  "id_conductor": "11111111-1111-1111-1111-111111111111",
  "placa_vehiculo": "FOP-002",
  "tipo_incidente": "MECANICO",
  "gravedad": "GRAVE",
  "descripcion": "Prueba Postman",
  "fecha_hora": "2026-05-15T10:30:00Z"
}
```

## Respuestas esperadas

| Request | HTTP | Campo clave |
|---------|------|-------------|
| Reports Health | 200 | `"status":"ok"` |
| Generate Report | 201 | `"status":"generated"`, `"kpis"` length 6 |
| Incidents Gateway List | 200 | array JSON |
| Login | 200 | `access_token` |

## Troubleshooting rápido

| Síntoma | Acción |
|---------|--------|
| 401 en `/incidentes/` | Ejecuta Login y verifica `gateway_token` |
| 422 en report generate | Revisa mock upstream (:8099) y JWT en `.env` del backend |
| 301/redirect en report | Asegura URLs con trailing slash (fix incluido en clients) |
| EC2 timeout | Usa túnel SSH o prueba desde el servidor |
