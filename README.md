# FleetOps Reports

[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0+-green?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Docker](https://img.shields.io/badge/Docker-27+-blue?logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-Academic-purple)](./LICENSE)
[![Code Coverage](https://img.shields.io/badge/Coverage-100%25%20(Domain%2FApp)-brightgreen)](./backend/htmlcov/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-blue?logo=github&logoColor=white)](https://github.com/features/actions)

FleetOps Reports is the analytical reporting microservice of the FleetOps platform. It exposes a REST API built with FastAPI to generate analytical reports from operational data, integrating with MongoDB, MinIO, and the FleetOps API Gateway.

> **SAD Traceability**
>
> This implementation follows the FleetOps Software Architecture Document (SAD) dated **2026-05-29**, including the architectural decisions (ADRs), deployment topology, and quality attributes defined for the analytical reporting service.

---

## Features

- REST API with FastAPI
- Layered Architecture (Clean Architecture)
- Domain-Driven Design (DDD)
- MongoDB persistence
- MinIO object storage
- PDF generation with WeasyPrint
- HTML templating with Jinja2
- Prometheus metrics
- Grafana dashboards
- Loki centralized logging
- Nginx API Gateway
- Docker Compose local environment
- CI/CD with GitHub Actions
- SonarCloud static analysis
- Trivy container scanning
- Bandit security analysis
- Import Linter architecture validation
- Pre-commit hooks

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.13 |
| Framework | FastAPI |
| Validation | Pydantic v2 |
| Database | MongoDB 7.0+ |
| Object Storage | MinIO |
| HTTP Client | HTTPX |
| Templates | Jinja2 |
| PDF Engine | WeasyPrint |
| Metrics | Prometheus |
| Dashboards | Grafana |
| Logging | Loki |
| Reverse Proxy | Nginx |
| Containerization | Docker 27+ |
| Orchestration | Docker Compose v2 |
| CI/CD | GitHub Actions |

---

## Project Structure

```text
fleetops-reports/
│
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── src/
│   │   └── fleetops_reports/
│   │       ├── presentation/          # REST controllers, DTOs, HTTP responses
│   │       ├── application/           # Use cases, commands, queries
│   │       ├── domain/                # Entities, value objects, policies
│   │       ├── infrastructure/        # MongoDB, MinIO, HTTP adapters
│   │       └── config/                # Configuration, environment setup
│   └── tests/
│       ├── unit/
│       ├── integration/
│       └── fixtures/
│
├── gateway/
│   ├── Dockerfile
│   └── nginx.conf
│
├── minio/
│   └── init-bucket.sh                 # MinIO initialization script
│
├── observability/
│   ├── prometheus.yml
│   ├── grafana-dashboard.json
│   ├── loki-config.yml
│   └── promtail-config.yml
│
├── docs/
│   ├── base/                          # Base documentation
│   ├── contracts/                     # API contracts and schemas
│   ├── format/                        # Formatting and style guides
│   ├── adr/                           # Architecture Decision Records
│   ├── SAD.md                         # Software Architecture Document
│   ├── api.md                         # API specification
│   └── deployment/                    # Production deployment guides
│
├── .github/
│   └── workflows/                     # CI/CD pipeline definitions
│
├── .gitignore
├── .gitattributes
├── .pre-commit-config.yaml            # Pre-commit hooks configuration
├── docker-compose.yml
├── Makefile
├── sonar-project.properties
├── pyproject.toml
├── README.md
├── LICENSE
└── CONTRIBUTING.md
```

---

## Prerequisites

- **Docker Engine 27+** (BuildKit support and latest features)
- **Docker Compose v2** (Simplified compose file syntax)
- **Python 3.13** (for local development only)
- **GNU Make** (for task automation)
- **Git** (for repository management)

---

## Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd fleetops-reports
```

### 2. Setup environment variables

```bash
cp .env.example .env
```

For detailed configuration options, see `.env.example`.

### 3. Start the complete stack

```bash
make up
```

The API Gateway will be available at:

```
http://localhost:8080
```

### 4. Verify the installation

```bash
curl http://localhost:8080/health
```

### 5. Stop services

```bash
make down
```

---

## Architecture

### Layered Architecture

```text
┌─────────────────────────────────────┐
│     Presentation Layer              │  REST Controllers, DTOs
├─────────────────────────────────────┤
│     Application Layer               │  Use Cases, Orchestration
├─────────────────────────────────────┤
│     Domain Layer                    │  Entities, Business Logic
├─────────────────────────────────────┤
│     Infrastructure Layer            │  Persistence, External APIs
└─────────────────────────────────────┘
```

### Runtime Flow

```
Client
  │
  ▼
API Gateway (Nginx)
  │
  ▼
FastAPI Application
  │
  ├─► Application Use Case
  │      │
  │      ▼
  │   Domain Service
  │      │
  │      ▼
  │   Infrastructure
  │      ├── MongoDB (Persistence)
  │      ├── MinIO (Object Storage)
  │      ├── REST APIs (FleetOps Gateway)
  │      └── WeasyPrint (PDF Generation)
  │
  └─► Response (JSON / PDF)
```

**Layer Responsibilities:**

- **Presentation**: Request/response mapping, DTO conversion, HTTP status codes
- **Application**: Use case orchestration, transaction management, error handling
- **Domain**: Pure business logic, entities, domain services, policies
- **Infrastructure**: Data persistence, external API integration, logging, monitoring

---

## Local Development

### Environment Setup

#### Linux / macOS

```bash
cd backend

python -m venv .venv

source .venv/bin/activate

python -m pip install --upgrade pip

pip install -e ".[dev]"
```

#### Windows

```powershell
cd backend

python -m venv .venv

.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

python -m pip install -e ".[dev]"
```

### Available Commands

#### Testing

```bash
# Run unit tests
make test

# Generate coverage report (100% required for Domain & Application)
make coverage

# View coverage report in HTML
open backend/htmlcov/index.html
```

#### Validation

```bash
# Architecture validation with Import Linter
make import-linter

# Type checking with MyPy
make mypy

# Linting with Ruff
make ruff

# Security analysis with Bandit
make security

# Run complete local validation pipeline
make validate
```

#### Docker

```bash
# Build Docker images
make build

# Start all services
make up

# Stop all services
make down

# View live logs
make logs

# Clean generated artifacts
make clean
```

---

## Observability Stack

The project includes an integrated observability solution:

| Service | URL | Purpose |
|---------|-----|---------|
| **Prometheus** | http://localhost:9090 | Metrics collection and aggregation |
| **Grafana** | http://localhost:3000 | Dashboard and visualization |
| **Loki** | http://localhost:3100 | Log aggregation and querying |
| **MinIO Console** | http://localhost:9001 | Object storage management |

### Viewing Logs

```bash
# View application logs
make logs

# View specific backend logs with tail
docker logs -f fleetops-reports-backend-1 --tail 50

# Filter logs by pattern
docker logs fleetops-reports-backend-1 | grep "ERROR"
```

---

## Code Coverage

The project enforces strict coverage metrics using **coverage.py**:

- **Domain Layer**: 100% coverage required
- **Application Layer**: 100% coverage required
- **Infrastructure & Presentation**: 80%+ recommended

Generate coverage report:

```bash
make coverage
```

Report artifacts:

```
backend/coverage.xml          # XML format for CI/CD integration
backend/htmlcov/index.html    # Interactive HTML report
```

---

## CI/CD Pipeline

GitHub Actions automatically executes:

1. **Import Linter** — Architecture compliance validation
2. **MyPy** — Static type checking
3. **Ruff** — Code linting
4. **Bandit** — Security vulnerability scanning
5. **Unit Tests** — Test suite execution
6. **Coverage** — Coverage report generation
7. **SonarCloud** — Advanced static analysis
8. **Docker Build** — Container image compilation
9. **Trivy** — Container vulnerability scanning
10. **SARIF Upload** — Results to GitHub Security

Workflow location: `.github/workflows/ci.yml`

---

## Architectural Decisions

The project follows FleetOps Architecture Decision Records (ADRs):

| ADR | Decision | Rationale |
|-----|----------|-----------|
| **ADR-001** | Layered Architecture | Separation of concerns, testability, maintainability |
| **ADR-002** | MongoDB for analytics | Schema flexibility, horizontal scalability |
| **ADR-003** | MinIO for storage | Cloud-agnostic, S3-compatible, self-hosted option |
| **ADR-004** | Independent microservice | Decoupling, independent scaling, deployment autonomy |
| **ADR-005** | REST + API Gateway | Simple integration patterns, centralized routing |
| **ADR-006** | Internal domain services | Business logic encapsulation, reusability |

For detailed information, consult the [Software Architecture Document](./docs/SAD.md).

---

## Quality Assurance

Integrated QA tooling:

| Tool | Purpose | Execution |
|------|---------|-----------|
| **Ruff** | Code linting | `make ruff` |
| **MyPy** | Type checking | `make mypy` |
| **Import Linter** | Architecture validation | `make import-linter` |
| **coverage.py** | Test coverage metrics | `make coverage` |
| **Bandit** | Security scanning | `make security` |
| **Trivy** | Container vulnerability scan | CI/CD |
| **SonarCloud** | Advanced code analysis | CI/CD |

Run complete validation locally:

```bash
make validate
```

---

## Troubleshooting

### MongoDB Connection Refused

**Issue:** `ConnectionError: [Errno 111] Connection refused`

**Solution:**

```bash
# Verify containers are running
docker ps | grep mongodb

# Restart services
make down
make up

# Check MongoDB logs
docker logs fleetops-reports-mongodb-1
```

### MinIO Connectivity Issues

**Issue:** Unable to connect to MinIO at `minio:9000`

**Solution:**

```bash
# Verify MinIO is running
docker ps | grep minio

# Access MinIO console at http://localhost:9001
# Default credentials: minioadmin / minioadmin

# Test connectivity from backend
docker exec fleetops-reports-backend-1 \
  curl -v http://minio:9000/minio/health/live
```

### Tests Pass in CI but Fail Locally

**Issue:** Tests pass in GitHub Actions but fail on local machine

**Solution:**

```bash
# Ensure dev dependencies are installed
pip install -e ".[dev]"

# Clear test cache
make clean

# Run tests with verbose output
python -m pytest -vv tests/

# Run specific test file
python -m pytest tests/test_report_service.py -vv
```

### Coverage Below Threshold

**Issue:** `Coverage below 100% in Domain/Application layers`

**Solution:**

```bash
# Generate coverage report
make coverage

# Open HTML report to identify uncovered lines
open backend/htmlcov/index.html

# Add tests for uncovered code paths
# Ensure mocks and fixtures are properly utilized
```

### Docker Permission Denied (Linux)

**Issue:** `permission denied while trying to connect to Docker daemon`

**Solution:**

```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Or use sudo
sudo make up
```

---

## Documentation

- [Software Architecture Document](./docs/SAD.md) — Architecture overview and design decisions
- [Architecture Decision Records](./docs/adr/) — Detailed ADR documentation
- [API Specification](./docs/contracts/) — REST API contracts and schemas
- [Deployment Configuration](./docs/deployment/DEPLOYMENT_CONFIGURATION.md) — CI/CD and infrastructure setup
- [Deployment Guide](./docs/deployment/DEPLOYMENT_GUIDE.md) — Step-by-step EC2 free-tier deployment
- [Contributing Guide](./CONTRIBUTING.md) — Development and contribution guidelines

---

## Pre-commit Hooks

The project uses pre-commit hooks for code quality checks. Install them:

```bash
pre-commit install
```

Hooks run automatically on `git commit`:

- Trailing whitespace removal
- End-of-file fixes
- YAML validation
- JSON validation
- Markdown linting
- Python code formatting

---

## License

This project is part of the FleetOps academic software architecture implementation.

---

## Support

For issues, questions, or discussions:

- **GitHub Issues** — For bug reports and feature requests
- **GitHub Discussions** — For general questions and ideas
- **Documentation** — See the `/docs` directory for detailed guides