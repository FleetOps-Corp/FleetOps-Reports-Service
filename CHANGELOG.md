# Changelog

All notable changes to FleetOps Reports are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
