# Changelog

All notable changes to FleetOps Reports are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.3] - 2026-07-09

### Fixed
- Map operational Security Gateway auth failures to **503** with `OPERATIONAL_GATEWAY_AUTH_FAILED` instead of misleading **422**.
- Treat empty `OPERATIONAL_GATEWAY_BEARER_TOKEN` as unset so service-account login is attempted.

## [2.2.2] - 2026-07-08

### Added
- Swagger `/docs` **Authorize** button via `HTTPBearer` on `/reports` and `/api/reports` routes.

## [2.2.1] - 2026-07-08

### Changed
- Removed Spanish route aliases (`/reportes`, `/api/reportes`); English prefixes only (`/reports`, `/api/reports`).

## [2.2.0] - 2026-07-08

### Added
- Automatic Security Gateway service-token refresh via `OPERATIONAL_GATEWAY_SERVICE_EMAIL` / `OPERATIONAL_GATEWAY_SERVICE_PASSWORD`.
- Optional `ciudad_operacion` filter on report generation and listing.
- Date-range filtering for incidents and maintenance during report generation.
- Spring pagination support when fetching vehicles through the Gateway.
- Resilient assignments client (continues when list endpoint is missing).
- Dual-field mapping for deployed Incidents (English) and Maintenance payloads.

### Changed
- Operational upstream paths aligned with microservice routes: `/vehiculos/`, `/asignaciones/`, `/api/incidents/`, `/api/v1/mantenimientos/`.
- EC2 integration script and production env template updated for aligned paths and service-account login.

## [2.1.3] - 2026-07-07

### Added
- `/api/reportes/**` route aliases matching Security convention `api/<servicio>/...`.
- JWT middleware accepts `EMPLEADO_REPORTES` in addition to `ADMINISTRADOR` for report endpoints.

### Changed
- Security integration smoke test covers `/api/reportes` on both Security Gateway and Reports EC2.

## [2.1.2] - 2026-07-07

### Added
- Configurable Security Gateway operational paths (`OPERATIONAL_*_PATH`) for deployed `/api/*` routes.
- `/api/reports/**` route aliases matching Security `REPORTS_SERVICE_PREFIX`.
- RS256 production configuration, EC2 deploy script, and Security integration smoke test.
- `docs/deployment/SECURITY_INTEGRATION_REPORT.md`.

### Changed
- Production `.env` template defaults to RS256 + public key verification against deployed Security.
- Operational REST clients accept configurable resource paths via environment variables.

## [2.1.1] - 2026-07-07

### Added
- Fleet inventory table in executive PDF (plate, brand/model, status, operation site) sorted with available units first.
- KPI table **Description** column replacing internal metric identifiers.
- Expanded local simulation fixtures (32 vehicles, 36 incidents, 39 maintenance records) for richer charts.
- `certs/README.md` and deployment script `scripts/deploy/ensure_jwt_env.sh` for JWT configuration on EC2.

### Changed
- Chart section titles in PDF use human-readable labels.
- Default JWT algorithm setting aligned to HS256 (current Security Service signing mode).
- Environment templates document dual JWT modes: HS256 shared secret (today) and RS256 public key (target).

### Fixed
- Jinja2 component templates packaged correctly for Docker PDF generation (`html/**/*.j2`).
- Local simulation routes operational reads to mock gateway for complete sede-filtered datasets.

## [2.1.0] - 2026-07-07

### Added
- Report listing, metadata retrieval, and PDF download endpoints (`GET /reports`, `GET /reports/{id}`, `GET /reports/{id}/download`) with Security Gateway aliases under `/reportes`.
- Optional `sede_operacion` filter aligned with the Vehicles service field for report generation and listing.
- JWT inbound validation with public-route exemptions for health and metrics probes.
- Dual JWT verification modes: HS256 shared secret (Security Gateway compatibility) and RS256 public key verification.
- Operational payload field normalization for camelCase and snake_case upstream JSON.
- Empty-state handling for KPI and chart generation when upstream datasets are missing.
- Simulation scripts for authenticated smoke tests and PDF export to `docs/reports/`.
- Deployment testing guide and version documentation (`VERSION`, `CHANGELOG`, `LICENSE`).

### Changed
- Availability and MTTR policies return zero values instead of failing when datasets are empty.
- Availability charts group by operation site (`sede_operacion`) with city fallback.
- Executive PDF template includes operation site metadata.
- Updated fixtures, README, and simulation documentation for version 2.1.0.

### Fixed
- JWT middleware no longer blocks Docker health checks on `/health` and `/metrics`.
- Vehicle REST client mapping for `sedeOperacion` / `sede_operacion` and camelCase vehicle fields.
- Report generation resilience when filtered operational data is empty for a selected site.

## [2.0.0] - 2026-06-01

### Added
- REST-based report generation microservice with FastAPI, MongoDB, MinIO, and WeasyPrint.
- CI/CD pipeline with GitHub Actions, SonarCloud, and EC2 deployment workflow.
- Local Docker Compose stack with Nginx gateway and observability profile.
- Integration simulation tooling and operational JSON contract documentation.

## [1.0.0] - 2026-04-01

### Added
- Initial gRPC-based analytical prototype for FleetOps Reports (superseded by REST architecture in 2.0.0).

[2.1.0]: https://github.com/FleetOps-Corp/report-service/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/FleetOps-Corp/report-service/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/FleetOps-Corp/report-service/releases/tag/v1.0.0
