# Project Overview

FleetOps Reports is the **analytical reporting microservice** of the FleetOps platform. It aggregates operational data from distributed services, computes fleet KPIs, and produces executive PDF reports with embedded charts.

## Role in the ecosystem

```text
Operational microservices          FleetOps Security Gateway
(vehicles, assignments,      →    (JWT + RBAC proxy)
 incidents, maintenance)                  ↓
                                    Reports backend
                                          ↓
                              PDF + SVG + KPI JSON + MongoDB record
```

Reports is a **consumer** of operational data and a **producer** of analytical artifacts. It does not own fleet master data.

---

## Internal services (Docker Compose)

| Service | Technology | Responsibility |
|---------|------------|----------------|
| **gateway** | Nginx | Public HTTP entry point; reverse-proxies all routes to the backend |
| **backend** | FastAPI (Python 3.13) | Report generation API, KPI computation, PDF rendering orchestration |
| **mongodb** | MongoDB 7 | Analytical persistence for generated report metadata |
| **minio** | MinIO | Object storage for PDF documents and SVG chart assets |
| **prometheus** | Prometheus | Scrapes backend `/metrics` (dev / optional prod profile) |
| **grafana** | Grafana | Dashboards over Prometheus data (dev / optional prod profile) |
| **loki** + **promtail** | Grafana Loki stack | Centralized JSON log collection (dev / optional prod profile) |

Production (`docker-compose.prod.yml`) runs a lean subset by default: **gateway**, **backend**, **minio**. MongoDB is typically **Atlas M0**; observability is an optional profile.

---

## External dependencies

| Dependency | Direction | Purpose |
|------------|-----------|---------|
| **FleetOps Security Gateway** | Outbound | Source of truth for vehicles, assignments, incidents, maintenance |
| **MongoDB Atlas** (production) | Outbound | Report metadata storage |
| **Client / Security Gateway** | Inbound | Trigger report generation |

Reports does **not** embed business logic from upstream services; it maps their JSON into domain records and applies analytical policies locally.

---

## Who consumes Reports

| Consumer | Access pattern | Auth |
|----------|----------------|------|
| **Administrators / clients** | Direct: `POST /reports/generate` via Reports Nginx gateway | Expected at corporate gateway layer (local Nginx does not enforce JWT) |
| **FleetOps Security Gateway** | Proxy: `POST /reportes/generate` → Reports backend | Gateway validates JWT (`ADMINISTRADOR` role) before forwarding |
| **Operators** | `GET /health`, `GET /metrics` | Unauthenticated health; metrics for observability stack |

No other FleetOps microservice is required to call Reports for the platform to operate; Reports is an on-demand analytical endpoint.

---

## What Reports produces

### 1. HTTP JSON response

On successful `POST /reports/generate`:

- `status`: `"generated"`
- `document_url`: MinIO object key (e.g. `rep-001.pdf`), not a presigned URL
- `kpis`: array of **six** KPI objects:

| KPI | Source domain | Unit |
|-----|---------------|------|
| Fleet Availability | vehicles | percent |
| Mean Time To Repair | maintenance | hours |
| Critical Vehicles | incidents + maintenance + vehicles | vehicles |
| High Severity Rate | incidents | percent |
| Human Incident Rate | incidents | percent |
| Recurrent Vehicles | incidents | vehicles |

### 2. PDF executive report

- Rendered with **WeasyPrint** from Jinja2 HTML templates
- Stored in MinIO bucket: `MINIO_REPORTS_BUCKET` (default `fleetops-reports`)
- Object name: `{report_id}.pdf`

### 3. SVG KPI chart

- Built by `GraphService` from KPI names/values
- Stored in MinIO bucket: `MINIO_GRAPHS_BUCKET` (default `fleetops-graphs`)
- Object name: `{report_id}.svg`
- Embedded in the PDF via a short-lived presigned URL during render

### 4. MongoDB document

Report aggregate (metadata, period, KPIs, generation status) persisted through `AnalyticsRepository` for audit and retrieval.

---

## Public API surface

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness probe |
| GET | `/metrics` | Prometheus metrics |
| POST | `/reports/generate` | Generate consolidated operational report |
| POST | `/reportes/generate` | Gateway-compatible alias |
| GET | `/docs` | OpenAPI Swagger UI (FastAPI) |

Default local URL: `http://localhost:8080` (Nginx gateway port).

---

## Configuration highlights

| Variable | Role |
|----------|------|
| `OPERATIONAL_GATEWAY_BASE_URL` | Security Gateway base URL for upstream reads |
| `OPERATIONAL_GATEWAY_BEARER_TOKEN` | JWT with `ADMINISTRADOR` role |
| `MONGODB_URI` / `MONGODB_DATABASE` | Analytical database |
| `MINIO_*` | Object storage connection and bucket names |
| `GATEWAY_HTTP_PORT` | Host port for the Nginx gateway |

See `.env.example` and `.env.production.example` for the full list.

---

## Architecture layers (backend)

| Layer | Responsibility |
|-------|----------------|
| **presentation** | REST routes, Pydantic schemas, HTTP error mapping |
| **application** | Use cases, KPI services, report orchestration |
| **domain** | Entities, policies, business rules |
| **infrastructure** | MongoDB, MinIO, REST clients, WeasyPrint, observability |

Upstream integration adapters live in `infrastructure/rest_clients/` and are wired through `composition/wiring.py`.
