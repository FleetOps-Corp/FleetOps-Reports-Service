> **Note:** This document describes the **FleetOps Reports** integration contracts as implemented in the Reports service codebase. Upstream list routes are consumed **indirectly** through the FleetOps Security Gateway. Route prefixes are configurable via environment variables to match deployed Security `*_SERVICE_PREFIX` values.

# FleetOps — Reports Service: Technical Reference

---

## 1. Architecture Overview

FleetOps Reports is a **read-only consumer** of four operational microservices. It never calls those services directly; all outbound traffic goes through the **FleetOps Security Gateway** using a service-account JWT.

```
Client ──► Security Gateway ──► Reports Service (generate / list / download)
                │
                ├── GET /api/vehicles/      ──► Vehicles
                ├── GET /api/assignments/   ──► Assignments
                ├── GET /api/incidents/     ──► Incidents
                └── GET /api/maintenance/   ──► Maintenance
```

During report generation, Reports:

1. Fetches operational lists from the four upstream services (via Security).
2. Optionally filters vehicles (and correlated incidents/maintenance) by `sede_operacion`.
3. Computes **six executive KPIs**.
4. Persists report metadata in **MongoDB** and the PDF in **MinIO**.

---

## 2. Configuration Variables

### 2.1 Outbound — Security Gateway (operational reads)

| Environment variable | Description | Local default | Deployed example |
| --- | --- | --- | --- |
| `OPERATIONAL_GATEWAY_BASE_URL` | Security Gateway base URL | `http://host.docker.internal:8000` | `http://3.237.75.68:8000` |
| `OPERATIONAL_GATEWAY_BEARER_TOKEN` | JWT for upstream `GET` calls (typically `ADMINISTRADOR`) | — | From `POST /auth/login` |
| `OPERATIONAL_VEHICLES_PATH` | Vehicles list path prefix | `/vehiculos/` | `/vehiculos/` |
| `OPERATIONAL_ASSIGNMENTS_PATH` | Assignments list path prefix | `/asignaciones/` | `/asignaciones/` |
| `OPERATIONAL_INCIDENTS_PATH` | Incidents list path prefix | `/api/incidents/` | `/api/incidents/` |
| `OPERATIONAL_MAINTENANCE_PATH` | Maintenance list path prefix | `/api/v1/mantenimientos/` | `/api/v1/mantenimientos/` |
| `OPERATIONAL_GATEWAY_SERVICE_EMAIL` | Service account for auto token refresh | — | Admin/service account email |
| `OPERATIONAL_GATEWAY_SERVICE_PASSWORD` | Service account password | — | Never commit |

**Full outbound URL pattern:**

```http
GET {OPERATIONAL_GATEWAY_BASE_URL}{OPERATIONAL_*_PATH}
Authorization: Bearer {OPERATIONAL_GATEWAY_BEARER_TOKEN}
Accept: application/json
```

> **Trailing slash:** List paths must end with `/` (e.g. `/api/vehicles/`) to avoid redirect issues.

### 2.2 Inbound — JWT validation (Reports API)

| Environment variable | Description |
| --- | --- |
| `JWT_ALGORITHM` | `RS256` (production) or `HS256` (local simulation) |
| `JWT_PUBLIC_KEY_PATH` | Path to Security public key PEM (RS256) |
| `JWT_SECRET_KEY` | Shared secret (HS256 local only; do not set with RS256) |

**Allowed JWT roles:** `ADMINISTRADOR`, `EMPLEADO_REPORTES`

**Required JWT claims:** `sub`, `role`

**Library:** PyJWT (`jwt.decode`) — not Django / `simple_jwt`.

---

## 3. Upstream Response Envelope

All four REST clients accept either:

- A **raw JSON array** of objects, or
- A **wrapped list** under one of: `data`, `results`, `items`, `content`

Any other shape raises a parsing error and fails report generation (`422`).

**Example wrapped response:**

```json
{
  "data": [
    { "id_vehiculo": "...", "numero_placa": "FOP-001" }
  ]
}
```

---

## 4. Upstream Microservice Contracts

### 4.1 Vehicles

| Item | Value |
| --- | --- |
| **Security Gateway route (deployed)** | `GET {OPERATIONAL_GATEWAY_BASE_URL}/vehiculos/` |
| **Security Gateway route (local default)** | `GET {OPERATIONAL_GATEWAY_BASE_URL}/vehiculos/` |
| **REST client** | `RestVehiclesClient` |
| **Domain model** | `Vehicle` |
| **KPI usage** | Fleet Availability (`vehicles` source); vehicle inventory table in PDF |

#### JSON list item (fields consumed)

```json
{
  "id_vehiculo": "0e295003-ccc2-489b-b6d9-e23867eb2cf1",
  "numero_placa": "FOP-001",
  "estado_vehiculo": "DISPONIBLE",
  "ciudad_operacion": "Bogotá",
  "sede_operacion": "Patio Norte Bogotá",
  "marca": "Freightliner",
  "modelo": "Cascadia"
}
```

| Field | Type | Mapped to | Notes |
| --- | --- | --- | --- |
| `id_vehiculo` | UUID string | `Vehicle.id_vehiculo` | Also accepts camelCase alias `idVehiculo` |
| `numero_placa` | string | `Vehicle.numero_placa` | Also accepts `numeroPlaca`; used to join incidents |
| `estado_vehiculo` | string | `Vehicle.estado_vehiculo` | Also accepts `estadoVehiculo` |
| `ciudad_operacion` | string | `Vehicle.ciudad_operacion` | Also accepts `ciudadOperacion` |
| `sede_operacion` | string | `Vehicle.sede_operacion` | Also accepts `sedeOperacion`; optional filter on generate |
| `marca` | string | `Vehicle.marca` | Manufacturer |
| `modelo` | string | `Vehicle.modelo` | Model |

**Availability rule:** `estado_vehiculo == "DISPONIBLE"` counts as available for the Fleet Availability KPI.

**Common status values:** `DISPONIBLE`, `EN_RUTA`, `ASIGNADO`, `EN_MANTENIMIENTO`, `FUERA_DE_SERVICIO`

---

### 4.2 Assignments

| Item | Value |
| --- | --- |
| **Security Gateway route (deployed)** | `GET {OPERATIONAL_GATEWAY_BASE_URL}/asignaciones/` |
| **Security Gateway route (local default)** | `GET {OPERATIONAL_GATEWAY_BASE_URL}/asignaciones/` |
| **REST client** | `RestAssignmentsClient` |
| **Domain model** | `AssignmentRecord` |
| **KPI usage** | Fetched during generation; **not** mapped into the current six-KPI set (integration readiness / upstream health) |

#### JSON list item (fields consumed)

Aligned with FleetOps Assignments Flyway schema (`asignaciones` table):

```json
{
  "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "conductor_id": "11111111-1111-1111-1111-111111111111",
  "vehiculo_id": "0e295003-ccc2-489b-b6d9-e23867eb2cf1",
  "tipo_vehiculo": "CAMION",
  "fecha_inicio": "2026-07-01",
  "fecha_fin": "2026-07-10",
  "creada_en": "2026-05-18T15:30:00Z"
}
```

| Field | Type | Mapped to | Notes |
| --- | --- | --- | --- |
| `id` | UUID string | `AssignmentRecord.assignment_id` | Assignment primary key |
| `conductor_id` | UUID string | `AssignmentRecord.conductor_id` | FK → `conductores.id` |
| `vehiculo_id` | UUID string \| null | `AssignmentRecord.vehicle_id` | Nullable while SAGA is pending |
| `tipo_vehiculo` | string | `AssignmentRecord.tipo_vehiculo` | e.g. `CAMION` |
| `fecha_inicio` | date \| datetime | `AssignmentRecord.start_date` | ISO date or datetime |
| `fecha_fin` | date \| datetime \| null | `AssignmentRecord.end_date` | Null if assignment is still active |
| `creada_en` | datetime | — | **Ignored** by Reports mapper (upstream metadata only) |

> **Design note:** `vehiculo_id` may be `null` at creation time until Vehicles confirms via the choreographed SAGA (`VehiculoConfirmadoEvent`). Reports tolerates null vehicle references.

---

### 4.3 Incidents

| Item | Value |
| --- | --- |
| **Security Gateway route (deployed)** | `GET {OPERATIONAL_GATEWAY_BASE_URL}/api/incidents/` |
| **Security Gateway route (local default)** | `GET {OPERATIONAL_GATEWAY_BASE_URL}/api/incidents/` |
| **REST client** | `RestIncidentsClient` |
| **Domain model** | `IncidentRecord` |
| **KPI usage** | Critical Vehicles, High Severity Rate, Human Incident Rate, Recurrent Vehicles |

#### JSON list item (fields consumed)

```json
{
  "id": "INC-202605-001-0",
  "id_conductor": "11111111-1111-1111-1111-111111111111",
  "placa_vehiculo": "FOP-002",
  "tipo_incidente": "HUMANO",
  "gravedad": "GRAVE",
  "fecha_hora": "2026-05-02T08:30:00Z"
}
```

| Field | Type | Mapped to | Notes |
| --- | --- | --- | --- |
| `id` | string | `IncidentRecord.incident_id` | e.g. `INC-YYYYMMDD-XXXX` |
| `id_conductor` | string | `IncidentRecord.id_conductor` | Driver involved |
| `placa_vehiculo` | string | `IncidentRecord.placa_vehiculo` | Joined to `Vehicle.numero_placa` (not UUID) |
| `tipo_incidente` | string | `IncidentRecord.tipo_incidente` | `HUMANO`, `MECANICO`, etc. |
| `gravedad` | string | `IncidentRecord.severity` | High-severity KPI uses exact match `GRAVE` |
| `fecha_hora` | datetime | `IncidentRecord.occurred_at` | ISO 8601 |

> **Important:** Incident-to-vehicle correlation uses **license plate** (`placa_vehiculo` → `numero_placa`), not vehicle UUID.

---

### 4.4 Maintenance

| Item | Value |
| --- | --- |
| **Security Gateway route (deployed)** | `GET {OPERATIONAL_GATEWAY_BASE_URL}/api/v1/mantenimientos/` |
| **Security Gateway route (local default)** | `GET {OPERATIONAL_GATEWAY_BASE_URL}/api/v1/mantenimientos/` |
| **REST client** | `RestMaintenanceClient` |
| **Domain model** | `MaintenanceRecord` |
| **KPI usage** | Mean Time To Repair (MTTR); inputs critical-vehicle classification |

#### JSON list item (fields consumed)

```json
{
  "id_vehiculo": "0e295003-ccc2-489b-b6d9-e23867eb2cf1",
  "tipo_mantenimiento": 0,
  "fecha_inicio_mantenimiento": "2026-05-01T08:00:00Z",
  "fecha_fin_mantenimiento": "2026-05-01T10:00:00Z"
}
```

| Field | Type | Mapped to | Notes |
| --- | --- | --- | --- |
| `id_vehiculo` | UUID string | `MaintenanceRecord.vehicle_id` | Vehicle under maintenance |
| `tipo_mantenimiento` | int \| string | `MaintenanceRecord.maintenance_type` | `0` or `"CORRECTIVO"`; `1` or `"PREVENTIVO"` |
| `fecha_inicio_mantenimiento` | datetime | `MaintenanceRecord.started_at` | MTTR interval start |
| `fecha_fin_mantenimiento` | datetime \| null | `MaintenanceRecord.finished_at` | Null if still open; excluded from MTTR |

**Maintenance type mapping:**

| Upstream value | Domain value |
| --- | --- |
| `0` | `CORRECTIVO` |
| `1` | `PREVENTIVO` |
| `"CORRECTIVO"` / `"PREVENTIVO"` | Uppercased string |

---

## 5. Identifier Formats

| Source | Identifier | Format |
| --- | --- | --- |
| Vehicles | `id_vehiculo` | UUID v4 |
| Assignments | `id`, `conductor_id`, `vehiculo_id` | UUID v4 |
| Incidents | `id` | String (e.g. `INC-202605-001-0`) |
| Incidents ↔ Vehicles | `placa_vehiculo` | Plate string (e.g. `FOP-002`) |
| Maintenance | `id_vehiculo` | UUID v4 |
| Reports (generated) | `report_id` | Client-supplied string (unique per report) |

---

## 6. Reports Service Endpoints

This section documents **every HTTP route exposed by FleetOps Reports**, including public probes, operational aliases, authentication rules, and expected responses.

### 6.1 Route prefix overview

Reports registers the **same four business operations** under two English prefixes (`/reports` and `/api/reports`).

| OpenAPI tag | Prefix | Authentication | Purpose |
| --- | --- | --- | --- |
| `health` | `/health` | **Public** | Liveness probe for Docker / load balancers |
| `metrics` | `/metrics` | **Public** | Prometheus metrics exposition |
| `Reports` | `/reports` | JWT required | Native service routes (direct access) |
| `Reports (Security /api/reports)` | `/api/reports` | JWT required | Security Gateway prefix |

**Recommended paths:**

| Access pattern | Path to use |
| --- | --- |
| Client → Security Gateway → Reports (production) | `/api/reports/*` |
| Client → Reports EC2 directly (testing) | `/reports/*` or `/api/reports/*` |

### 6.2 Public endpoints

#### `GET /health`

| Property | Value |
| --- | --- |
| **Auth** | None |
| **Description** | Confirms the Reports backend process is running. Used by Docker health checks and deployment probes. |
| **Success status** | `200 OK` |

**Response body:**

```json
{
  "status": "ok",
  "service": "fleetops-reports"
}
```

---

#### `GET /metrics`

| Property | Value |
| --- | --- |
| **Auth** | None |
| **Description** | Exposes Prometheus-compatible metrics for observability (request counts, generation latency, etc.). |
| **Success status** | `200 OK` |
| **Content-Type** | Prometheus text format |

---

### 6.3 Protected report endpoints

All routes below require:

```http
Authorization: Bearer <JWT>
```

**Allowed roles:** `ADMINISTRADOR`, `EMPLEADO_REPORTES`

Each operation is available at **`/reports`** and **`/api/reports`**. Replace `{prefix}` in the tables below with either prefix.

---

#### `POST {prefix}/generate`

| Property | Value |
| --- | --- |
| **Auth** | JWT required |
| **Description** | Generates a consolidated executive operational report. Fetches data from all four upstream microservices via Security Gateway, computes six KPIs, renders a PDF, uploads it to MinIO, and persists metadata in MongoDB. |
| **Success status** | `201 Created` |
| **Error statuses** | `401` (missing/invalid token), `403` (wrong role), `422` (validation or upstream failure) |

**Example paths:**

| Context | Full path |
| --- | --- |
| Via Security Gateway (recommended) | `POST /api/reports/generate` |
| Direct to Reports service | `POST /reports/generate` |

**Request body:**

```json
{
  "report_id": "rep-20260708-001",
  "title": "Executive Operational Report",
  "start_date": "2026-05-01",
  "end_date": "2026-05-31",
  "sede_operacion": "Patio Norte Bogotá"
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `report_id` | string | Yes | Unique client-provided identifier |
| `title` | string | Yes | Report title shown in the PDF header |
| `start_date` | date (`YYYY-MM-DD`) | Yes | Reporting period start |
| `end_date` | date (`YYYY-MM-DD`) | Yes | Reporting period end |
| `sede_operacion` | string | No | Filters vehicles and correlated incidents/maintenance by operation site |

**Success response (`201`):**

```json
{
  "report_id": "rep-20260708-001",
  "title": "Executive Operational Report",
  "status": "generated",
  "document_url": "rep-20260708-001.pdf",
  "sede_operacion": "Patio Norte Bogotá",
  "kpis": [
    { "name": "Fleet Availability", "value": 66.67, "unit": "percent", "source": "vehicles" },
    { "name": "Mean Time To Repair", "value": 2.5, "unit": "hours", "source": "maintenance" },
    { "name": "Critical Vehicles", "value": 3.0, "unit": "vehicles", "source": "incidents" },
    { "name": "High Severity Rate", "value": 25.0, "unit": "percent", "source": "incidents" },
    { "name": "Human Incident Rate", "value": 40.0, "unit": "percent", "source": "incidents" },
    { "name": "Recurrent Vehicles", "value": 2.0, "unit": "vehicles", "source": "incidents" }
  ]
}
```

---

#### `GET {prefix}`

| Property | Value |
| --- | --- |
| **Auth** | JWT required |
| **Description** | Lists all generated reports stored in MongoDB. Supports optional filtering by operation site. |
| **Success status** | `200 OK` |
| **Query parameters** | `sede_operacion` (optional, string) — filter by site name |

**Example paths:**

| Context | Full path |
| --- | --- |
| Via Security Gateway | `GET /api/reports?sede_operacion=Patio Norte Bogotá` |
| Direct to Reports service | `GET /reports` |

**Success response (`200`):**

```json
{
  "reports": [
    {
      "report_id": "rep-20260708-001",
      "title": "Executive Operational Report",
      "status": "generated",
      "document_url": "rep-20260708-001.pdf",
      "sede_operacion": "Patio Norte Bogotá",
      "start_date": "2026-05-01",
      "end_date": "2026-05-31",
      "created_at": "2026-07-08T14:30:00Z"
    }
  ],
  "total": 1
}
```

---

#### `GET {prefix}/{report_id}`

| Property | Value |
| --- | --- |
| **Auth** | JWT required |
| **Description** | Returns metadata for a single report by its `report_id`. Does not return the PDF binary. |
| **Success status** | `200 OK` |
| **Error statuses** | `404` if `report_id` does not exist |

**Example paths:**

| Context | Full path |
| --- | --- |
| Via Security Gateway | `GET /api/reports/rep-20260708-001` |
| Direct to Reports service | `GET /reports/rep-20260708-001` |

**Success response (`200`):**

```json
{
  "report_id": "rep-20260708-001",
  "title": "Executive Operational Report",
  "status": "generated",
  "document_url": "rep-20260708-001.pdf",
  "sede_operacion": "Patio Norte Bogotá",
  "start_date": "2026-05-01",
  "end_date": "2026-05-31",
  "created_at": "2026-07-08T14:30:00Z"
}
```

---

#### `GET {prefix}/{report_id}/download`

| Property | Value |
| --- | --- |
| **Auth** | JWT required |
| **Description** | Downloads the generated PDF file from MinIO. Returns the binary PDF with a `Content-Disposition: attachment` header. |
| **Success status** | `200 OK` |
| **Content-Type** | `application/pdf` |
| **Error statuses** | `404` if `report_id` does not exist or PDF was not stored |

**Example paths:**

| Context | Full path |
| --- | --- |
| Via Security Gateway | `GET /api/reports/rep-20260708-001/download` |
| Direct to Reports service | `GET /reports/rep-20260708-001/download` |

---

### 6.4 Complete endpoint matrix

All paths below require JWT unless marked **Public**.

| Method | `/reports` | `/api/reports` | Auth | Description |
| --- | --- | --- | --- | --- |
| `GET` | `/health` | — | Public | Liveness probe |
| `GET` | `/metrics` | — | Public | Prometheus metrics |
| `POST` | `/reports/generate` | `/api/reports/generate` | JWT | Generate executive report |
| `GET` | `/reports` | `/api/reports` | JWT | List generated reports |
| `GET` | `/reports/{id}` | `/api/reports/{id}` | JWT | Get report metadata |
| `GET` | `/reports/{id}/download` | `/api/reports/{id}/download` | JWT | Download PDF |

### 6.5 HTTP error reference

| Status | Cause | Typical fix |
| --- | --- | --- |
| `401` | Missing or invalid JWT | Login via Security; pass `Authorization: Bearer` |
| `403` | Role is not `ADMINISTRADOR` or `EMPLEADO_REPORTES` | Assign correct role via `POST /roles/assign` |
| `404` | Report ID not found | Verify `report_id` exists via list endpoint |
| `422` | Invalid request body or upstream service failure | Check dates, IDs, and Security Gateway connectivity |

---

## 7. Generated KPI Catalog

Every successful generation returns **exactly six KPIs**:

| # | Display name | Metric key | Unit | Source service | Business meaning |
| --- | --- | --- | --- | --- | --- |
| 1 | Fleet Availability | `fleet_availability` | percent | Vehicles | Share of fleet units operational and ready for dispatch |
| 2 | Mean Time To Repair | `MTTR` | hours | Maintenance | Average time to close corrective maintenance orders |
| 3 | Critical Vehicles | `critical_vehicle_count` | vehicles | Incidents + Maintenance | Vehicles classified as critical by incident/maintenance policy |
| 4 | High Severity Rate | `high_severity_rate` | percent | Incidents | Percentage of incidents with `gravedad == "GRAVE"` |
| 5 | Human Incident Rate | `human_incident_rate` | percent | Incidents | Percentage of incidents with `tipo_incidente == "HUMANO"` |
| 6 | Recurrent Vehicles | `recurrent_vehicle_count` | vehicles | Incidents | Vehicles with ≥ 2 incidents in the filtered set |

---

## 8. Persistence — MongoDB (`reports` collection)

| Field | Type | Description |
| --- | --- | --- |
| `report_id` | string | Primary business key |
| `title` | string | Report title |
| `period` | object | `{ "start_date", "end_date" }` |
| `status` | string | e.g. `generated` |
| `document_url` | string \| null | MinIO object key / filename |
| `sede_operacion` | string \| null | Optional site filter applied |
| `kpis` | array | Serialized KPI snapshot |
| `created_at` | datetime | UTC timestamp |

PDF binaries are stored in MinIO (`MINIO_REPORTS_BUCKET`); chart SVGs in `MINIO_GRAPHS_BUCKET`.

---

## 9. Data Flow During Generation

```
POST /api/reports/generate
        │
        ├─► GET /api/vehicles/       ──► filter by sede_operacion (optional)
        ├─► GET /api/assignments/    ──► upstream health (not in KPI set today)
        ├─► GET /api/incidents/      ──► filter by vehicle plates in fleet
        ├─► GET /api/maintenance/    ──► filter by vehicle IDs in fleet
        │
        ├─► Compute 6 KPIs
        ├─► Render PDF (Jinja2 + WeasyPrint)
        ├─► Upload PDF + charts to MinIO
        └─► Persist metadata to MongoDB
```

---

## 10. Resilience

| Mechanism | Behavior |
| --- | --- |
| Circuit breaker | Per upstream client; opens after repeated transport failures (`CIRCUIT_BREAKER_*` env vars) |
| HTTP 4xx/5xx from upstream | Surfaces as `422` report generation error |
| Missing outbound JWT | Upstream calls fail; report cannot be generated |
| Empty upstream lists | Valid; KPIs degrade to zero or domain defaults |

---

## 11. Related References

| Resource | Location |
| --- | --- |
| Assignments upstream contract | [asignaciones.md](./asignaciones.md) |
| Local simulation fixtures | [../simulate/fixtures/](../simulate/fixtures/) |
| Security integration report | [../deployment/SECURITY_INTEGRATION_REPORT.md](../deployment/SECURITY_INTEGRATION_REPORT.md) |
| Operational JSON summary | [../content/operational-json-contracts.md](../content/operational-json-contracts.md) |
| REST client implementations | `backend/src/fleetops_reports/infrastructure/rest_clients/` |
| Route definitions | `backend/src/fleetops_reports/presentation/api/routes/reports.py` |
