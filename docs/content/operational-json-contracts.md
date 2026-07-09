# Operational JSON Contracts

FleetOps Reports does **not** call operational microservices directly. All inbound operational data is fetched through the **FleetOps Security Gateway** using a service account JWT (`OPERATIONAL_GATEWAY_BEARER_TOKEN` with `ADMINISTRADOR` role).

## Security Gateway access pattern

| Property | Value |
|----------|-------|
| Base URL | `OPERATIONAL_GATEWAY_BASE_URL` (e.g. `http://host.docker.internal:8000`) |
| HTTP method | `GET` only (list endpoints) |
| Auth header | `Authorization: Bearer <JWT>` |
| Accept header | `application/json` |
| Trailing slash | **Required** on list routes (e.g. `/vehiculos/`) to avoid 301 redirects |

### Response envelope

The backend accepts either:

- A **raw JSON array** of objects, or
- A **wrapped list** under one of: `data`, `results`, `items`, `content`

Any other shape raises a parsing error and fails report generation.

---

## 1. Vehicles

| Item | Value |
|------|-------|
| Security Gateway route | `GET {OPERATIONAL_GATEWAY_BASE_URL}/vehiculos/` |
| REST client | `RestVehiclesClient` |
| Used for KPIs | Fleet Availability (`vehicles` source) |

### Expected list item (fields consumed)

Only the fields below are mapped into the domain model. Additional upstream fields are ignored.

```json
{
  "id_vehiculo": "8c12bda5-7482-4168-96ea-5fd3a9254c2a",
  "numero_placa": "TYX-789",
  "estado_vehiculo": "DISPONIBLE",
  "ciudad_operacion": "Bogotá",
  "marca": "Kenworth",
  "modelo": "T800"
}
```

| Field | Type | Notes |
|-------|------|-------|
| `id_vehiculo` | string (UUID) | Primary vehicle identifier |
| `numero_placa` | string | Normalized plate; used to correlate incidents |
| `estado_vehiculo` | string | e.g. `DISPONIBLE`, `EN_MANTENIMIENTO`, `FUERA_DE_SERVICIO` |
| `ciudad_operacion` | string | Operational city |
| `marca` | string | Manufacturer |
| `modelo` | string | Model name |

**Important:** Availability KPI treats `estado_vehiculo == "DISPONIBLE"` as available.

---

## 2. Assignments

| Item | Value |
|------|-------|
| Security Gateway route | `GET {OPERATIONAL_GATEWAY_BASE_URL}/asignaciones/` |
| REST client | `RestAssignmentsClient` |
| Used for KPIs | Fetched during generation; reserved for traceability / future analytics |

### Expected list item (fields consumed)

```json
{
  "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "conductor_id": "11111111-1111-1111-1111-111111111111",
  "vehiculo_id": "8c12bda5-7482-4168-96ea-5fd3a9254c2a",
  "tipo_vehiculo": "CAMION",
  "fecha_inicio": "2026-07-01",
  "fecha_fin": "2026-07-10"
}
```

| Field | Type | Notes |
|-------|------|-------|
| `id` | string (UUID) | Assignment identifier |
| `conductor_id` | string | Driver reference |
| `vehiculo_id` | string \| null | May be null while assignment is pending |
| `tipo_vehiculo` | string | e.g. `CAMION` |
| `fecha_inicio` | string | ISO date or datetime |
| `fecha_fin` | string \| null | Null if assignment is still active |

**Important:** Date-only values (`YYYY-MM-DD`) are parsed as UTC midnight.

---

## 3. Incidents

| Item | Value |
|------|-------|
| Security Gateway route | `GET {OPERATIONAL_GATEWAY_BASE_URL}/incidentes/` |
| REST client | `RestIncidentsClient` |
| Used for KPIs | Critical Vehicles, High Severity Rate, Human Incident Rate, Recurrent Vehicles (`incidents` source) |

### Expected list item (fields consumed)

```json
{
  "id": "INC-20260601-001",
  "id_conductor": "11111111-1111-1111-1111-111111111111",
  "placa_vehiculo": "FOP-002",
  "tipo_incidente": "MECANICO",
  "gravedad": "GRAVE",
  "fecha_hora": "2026-05-15T10:30:00Z"
}
```

| Field | Type | Allowed values |
|-------|------|----------------|
| `id` | string | Incident identifier |
| `id_conductor` | string | Driver involved |
| `placa_vehiculo` | string | Vehicle plate; joined to `numero_placa` |
| `tipo_incidente` | string | `HUMANO`, `MECANICO` |
| `gravedad` | string | `LEVE`, `GRAVE` |
| `fecha_hora` | string | ISO 8601 datetime |

**Important:** Incident-to-vehicle correlation uses **plate** (`placa_vehiculo` → `numero_placa`), not UUID.

---

## 4. Maintenance

| Item | Value |
|------|-------|
| Security Gateway route | `GET {OPERATIONAL_GATEWAY_BASE_URL}/mantenimiento/` |
| REST client | `RestMaintenanceClient` |
| Used for KPIs | Mean Time To Repair (`maintenance` source); also inputs critical-vehicle logic |

### Expected list item (fields consumed)

```json
{
  "id_vehiculo": "9d23cea6-8593-5279-a7fb-6ge4b0365d3b",
  "tipo_mantenimiento": 0,
  "fecha_inicio_mantenimiento": "2026-05-10T08:00:00Z",
  "fecha_fin_mantenimiento": "2026-05-10T13:00:00Z"
}
```

| Field | Type | Notes |
|-------|------|-------|
| `id_vehiculo` | string (UUID) | Vehicle under maintenance |
| `tipo_mantenimiento` | int \| string | `0` or `"CORRECTIVO"`; `1` or `"PREVENTIVO"` |
| `fecha_inicio_mantenimiento` | string | ISO datetime; MTTR start |
| `fecha_fin_mantenimiento` | string \| null | ISO datetime; null if still open |

**Important:** MTTR only considers records with a non-null `fecha_fin_mantenimiento`.

---

## Inbound API — Reports own request/response

Reports exposes its own JSON contract (not via Security Gateway for direct access):

| Route | Method | Body |
|-------|--------|------|
| `/reports/generate` | POST | See below |
| `/api/reports/generate` | POST | Alias for Security Gateway proxy compatibility |

### Request body

```json
{
  "report_id": "rep-001",
  "title": "Executive Report",
  "start_date": "2026-05-01",
  "end_date": "2026-05-31"
}
```

### Success response (`201 Created`)

```json
{
  "report_id": "rep-001",
  "title": "Executive Report",
  "status": "generated",
  "document_url": "rep-001.pdf",
  "kpis": [
    {
      "name": "Fleet Availability",
      "value": 66.67,
      "unit": "percent",
      "source": "vehicles"
    }
  ]
}
```

The response always includes **six KPIs** when generation succeeds. See [project-overview.md](./project-overview.md) for the full KPI list.

---

## Resilience notes

| Mechanism | Behavior |
|-----------|----------|
| Circuit breaker | Per upstream service; opens after repeated transport failures |
| HTTP 4xx/5xx | Propagates as `REPORT_GENERATION_ERROR` (422) |
| Missing JWT | Upstream calls fail; report cannot be generated |
| Empty lists | Valid; KPIs degrade to zero or domain defaults where applicable |

---

## Related references

- Fixture examples: [../simulate/fixtures/](../simulate/fixtures/)
- Extended field catalogs: [../format/](../format/)
- Gateway env vars: [../deployment/DEPLOYMENT_CONFIGURATION.md](../deployment/DEPLOYMENT_CONFIGURATION.md#7-security-gateway-integration)
