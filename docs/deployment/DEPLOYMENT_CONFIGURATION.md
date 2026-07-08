# FleetOps Reports — Deployment Configuration Reference

This document describes the deployment-related artifacts introduced for FleetOps Reports, how they relate to the existing CI pipeline, and what must be configured before the first production deployment.

---

## 1. Scope

FleetOps Reports is deployed as a **Docker Compose stack** on a single host (target: AWS EC2 free tier). The analytical service integrates with:

| Dependency | Role | Production recommendation |
|------------|------|---------------------------|
| **Nginx gateway** | Public HTTP entry point | Co-located container (`gateway`) |
| **FastAPI backend** | Report generation API | Co-located container (`backend`) |
| **MinIO** | PDF and graph object storage | Co-located container (`minio`) |
| **MongoDB** | Analytical persistence | **MongoDB Atlas M0** (free tier) |
| **FleetOps Security Gateway** | Operational data (vehicles, incidents, etc.) | External team service |
| **Observability stack** | Metrics, dashboards, logs | Optional Compose profile |

---

## 2. Files Added or Updated

### 2.1 New files

| File | Purpose |
|------|---------|
| `.github/workflows/deploy.yml` | Post-CI deployment workflow (currently disabled) |
| `docker-compose.prod.yml` | Lean production Compose definition |
| `.env.production.example` | Production environment template (placeholders only) |
| `docs/deployment/DEPLOYMENT_CONFIGURATION.md` | This document |
| `docs/deployment/DEPLOYMENT_GUIDE.md` | Operator runbook |

### 2.2 Updated files

| File | Change |
|------|--------|
| `.github/workflows/ci.yml` | Documented `TODO-FASE-DOCKER` for future image publishing |
| `Makefile` | `compose-validate` now validates both dev and prod Compose files |
| `README.md` | Links updated to the new deployment documentation |

### 2.3 Unchanged by design

| File | Reason |
|------|--------|
| `docker-compose.yml` | Remains the full local development stack (including observability) |
| `.env.example` | Remains the local development template |
| Application source code | No runtime logic changes required for deployment scaffolding |

---

## 3. Compose Topology

### 3.1 Development (`docker-compose.yml`)

Runs the complete platform for local work:

- `gateway`, `backend`, `mongodb`, `minio`
- `prometheus`, `grafana`, `loki`, `promtail`

Default public port: `${GATEWAY_HTTP_PORT}` → `8080`.

### 3.2 Production (`docker-compose.prod.yml`)

Runs a **resource-conscious** default stack suitable for free-tier EC2:

| Service | Default | Profile |
|---------|---------|---------|
| `gateway` | Enabled | — |
| `backend` | Enabled | — |
| `minio` | Enabled (internal network only) | — |
| `mongodb` | Disabled | `embedded-db` |
| Observability | Disabled | `observability` |

Production defaults:

- Gateway exposed on `${GATEWAY_HTTP_PORT}` (recommended: `8081` on EC2).
- MinIO not published to the public internet (`expose` only).
- Backend includes `extra_hosts: host.docker.internal:host-gateway` for reaching an external Security Gateway when required.

---

## 4. CI/CD Pipeline

### 4.1 Continuous Integration (`ci.yml`)

Existing pipeline (unchanged behaviour):

1. **Quality gate** — import-linter, mypy, ruff, bandit, tests, 100% domain/application coverage, SonarCloud.
2. **Build Docker** — builds and scans backend and gateway images locally in CI (`push: false`).
3. **Notify** — optional Slack failure notification.

**Important:** CI validates images but **does not publish** them to a registry yet. This is tracked as `TODO-FASE-DOCKER` in `ci.yml`.

### 4.2 Deployment workflow (`deploy.yml`)

| Property | Value |
|----------|-------|
| Triggers | `workflow_run` after CI on `main`; manual `workflow_dispatch` |
| Current state | **`if: false`** — job never executes |
| Deploy strategy | SSH to EC2 → `git pull` → `docker compose -f docker-compose.prod.yml up -d --build` |
| Registry | Not used (build on host) |

#### Why deployment is disabled today

The deploy job contains an explicit guard:

```yaml
if: false
```

GitHub Actions will **never** run deployment until this condition is replaced, regardless of trigger type.

#### How to enable deployment

1. Provision EC2 and complete the one-time host setup (see [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)).
2. Create the required GitHub Secrets (Section 5).
3. Replace `if: false` with:

```yaml
if: |
  (github.event_name == 'workflow_dispatch') ||
  (github.event_name == 'workflow_run' &&
   github.event.workflow_run.conclusion == 'success' &&
   github.event.workflow_run.head_branch == 'main')
```

4. Merge to `main` or run the workflow manually from the Actions tab.

---

## 5. GitHub Secrets

### 5.1 Required (when deployment is enabled)

| Secret | Description |
|--------|-------------|
| `EC2_HOST` | Public IP or DNS name of the EC2 instance |
| `EC2_USER` | SSH user (e.g. `ubuntu`, `ec2-user`) |
| `EC2_SSH_KEY` | Private key contents (PEM format) |

### 5.2 Optional

| Secret | Description | Default if unset |
|--------|-------------|------------------|
| `DEPLOY_PATH` | Remote directory containing the cloned repository | `/opt/fleetops-reports` |

### 5.3 Reserved for a future registry phase

These secrets are documented in `deploy.yml` but **not used** today:

| Secret | Future purpose |
|--------|----------------|
| `GHCR_USERNAME` | GitHub Container Registry login |
| `GHCR_TOKEN` | Registry authentication token |
| `DOCKER_IMAGE` | Image reference to pull |
| `DOCKER_TAG` | Image tag (e.g. commit SHA) |

---

## 6. Environment Variables

Never commit populated `.env` files. Use templates:

| Template | Audience |
|----------|----------|
| `.env.example` | Local development |
| `.env.production.example` | EC2 / production |

Critical production variables (placeholders only in templates):

| Variable | Notes |
|----------|-------|
| `MONGODB_URI` | Prefer Atlas M0 connection string on free tier |
| `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` | Strong random values; MinIO runs locally on EC2 |
| `OPERATIONAL_GATEWAY_BASE_URL` | URL of FleetOps Security Gateway |
| `OPERATIONAL_GATEWAY_BEARER_TOKEN` | JWT with `ADMINISTRADOR` role |
| `JWT_ALGORITHM` | Must match Security Service (`HS256` by default) |
| `JWT_SECRET_KEY` | Same secret as Security Service — required for inbound JWT on protected routes |
| `GATEWAY_HTTP_PORT` | Host port for public API access |

---

## 7. Security Gateway Integration

Reports fetches operational data exclusively through the FleetOps Security Gateway:

| Client route | Security Gateway prefix |
|--------------|-------------------------|
| Vehicles | `/vehiculos` |
| Assignments | `/asignaciones` |
| Incidents | `/incidentes` |
| Maintenance | `/mantenimiento` |

The backend sends `Authorization: Bearer <token>` on every outbound request. Without a valid token and reachable upstream microservices, report generation will fail even if the Reports stack itself is healthy.

---

## 8. Validation

Local validation covers both Compose files:

```bash
make compose-validate
make validate
```

`compose-validate` renders:

- `docker-compose.yml` with `.env.example`
- `docker-compose.prod.yml` with `.env.production.example`

---

## 9. Known Limitations and Next Steps

| Item | Status |
|------|--------|
| Image publishing to GHCR | Planned (`TODO-FASE-DOCKER`) |
| Automated deploy job | Scaffolded, disabled (`if: false`) |
| Observability on free-tier EC2 | Optional profile; disabled by default |
| Embedded MongoDB on EC2 | Optional profile; Atlas M0 recommended |
| Security Gateway + operational microservices | External dependency; must be reachable from EC2 |

---

## 10. Related Documentation

- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) — Step-by-step operator instructions
- [README.md](../../README.md) — Project overview and developer commands
- [.env.production.example](../../.env.production.example) — Production variable template
