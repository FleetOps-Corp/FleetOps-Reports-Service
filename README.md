# FleetOps Reports

SAD Traceability: this archetype implements the FleetOps Reports analytical
microservice described in the Software Architecture Document dated 2026-05-29.
It follows a strict layered architecture with FastAPI presentation, application
use cases and logical services, rich domain models and policies, and
infrastructure adapters for MongoDB, MinIO, gRPC, WeasyPrint, Prometheus,
Grafana and Loki.

## Prerequisites

- Docker Engine 27.x
- Docker Compose v2.29.x
- Python 3.13.x for local development
- GNU Make 4.x or compatible
- Bash 5.x for `backend/scripts/generate_protos.sh`

## Quick Start

```bash
git clone <repository-url>
cd fleetops-reports
cp .env.example .env
make proto
make up
```

The local API Gateway exposes the backend at the port configured by
`GATEWAY_HTTP_PORT` in `.env`.

## Local Tests

### Linux

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
```

### Windows

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest
```

## Exit virtual env

```bash
deactivate
cd backend
Remove-Item -Recurse -Force .venv
```

## Development Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

This installs:

- Runtime dependencies
- Testing tools
- Import Linter
- MyPy
- Ruff
- Coverage
```

## Coverage

```bash
make coverage
```

The coverage configuration enforces 100% coverage for `domain` and
`application` layers.

## Project Structure

```text
fleetops-reports/
├─ Makefile
├─ README.md
├─ docker-compose.yml
├─ .gitignore
├─ .gitattributes
├─ .env.example
├─ docs/
│  ├─ base/
├─ gateway/
│  ├─ Dockerfile
│  └─ nginx.conf
├─ backend/
│  ├─ Dockerfile
│  ├─ pyproject.toml
│  ├─ src/fleetops_reports/
│  │  ├─ presentation/
│  │  ├─ application/
│  │  ├─ domain/
│  │  ├─ infrastructure/
│  │  └─ config/
│  └─ tests/
└─ observability/
   ├─ prometheus.yml
   ├─ grafana-dashboard.json
   ├─ loki-config.yml
   └─ promtail-config.yml
```

## Architectural Decisions

- ADR-001: gRPC and Protocol Buffers integrate with Vehicles, Assignments,
  Incidents and Maintenance services.
- ADR-002: MongoDB Atlas is the production analytical persistence store;
  Docker Compose uses MongoDB locally for development and testing.
- ADR-003: MinIO stores generated graph resources and PDF reports.
- ADR-004: the analytical reporting capability is implemented as an
  independent microservice. This ADR was absent from the provided Markdown SAD
  and was incorporated from the user-supplied correction.
- ADR-005: Circuit Breaker protects operational gRPC integrations.
- ADR-006: internal logical services separate availability, maintenance,
  incidents, traceability, graphs, templates and report generation without
  deploying them as independent microservices.

## Proto Generation

Generated gRPC files are intentionally not committed. They are build artifacts
created from `backend/protos/*.proto`:

```bash
make proto
```

The script creates
`backend/src/fleetops_reports/infrastructure/grpc_clients/generated/`, which is
ignored by Git. Docker build also runs this generation step before packaging the
backend.

## Runtime Flow

The transactional example starts at `POST /reports`, maps request DTOs to a
`GenerateReportCommand`, retrieves operational data through gRPC client ports,
calculates availability, MTTR and criticality KPIs, generates a chart resource,
creates a MinIO presigned URL for WeasyPrint, renders a PDF, stores it in MinIO
and persists report metadata in MongoDB.

## Known Limitations

- Operational gRPC clients return deterministic local sample data in the
  archetype. Replace them with generated stubs and real service calls when the
  FleetOps operational services are available.
- Authentication and authorization are represented by the local Nginx gateway
  boundary, but concrete identity integration is an infrastructure concern not
  specified by the SAD.
- MongoDB Atlas is represented locally by the official MongoDB container.
- Grafana provisioning is represented by a dashboard artifact; automatic
  datasource provisioning can be added when deployment standards are known.

## Recommended Next Steps

- Add concrete gRPC stub calls after service contracts are finalized.
- Add MongoDB indexes and retention policies for analytical snapshots.
- Add API Gateway authentication and rate-limiting policies.
- Add Grafana datasource provisioning for fully automated dashboards.
