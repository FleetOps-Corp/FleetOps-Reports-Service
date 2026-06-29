"""Application wiring.

SAD Traceability: composition root that binds ports to MongoDB, MinIO, REST,
PDF and observability adapters per SAD section 6.
"""

from __future__ import annotations

from functools import lru_cache

from fleetops_reports.application.dependencies import (
    configure_generate_report_use_case,
    configure_metrics_exporter,
)
from fleetops_reports.application.services.availability_service import (
    AvailabilityService,
)
from fleetops_reports.application.services.incident_service import IncidentService
from fleetops_reports.application.services.maintenance_service import MaintenanceService
from fleetops_reports.application.services.report_service import ReportService
from fleetops_reports.application.use_cases.generate_report import GenerateReportUseCase
from fleetops_reports.config.settings import Settings
from fleetops_reports.infrastructure.observability.prometheus_adapters import (
    PrometheusMetricsExporter,
    PrometheusReportMetricsRecorder,
)
from fleetops_reports.infrastructure.pdf.weasyprint_renderer import WeasyPrintRenderer
from fleetops_reports.infrastructure.persistence.mongodb.analytics_repository import (
    MongoAnalyticsRepository,
)
from fleetops_reports.infrastructure.rest_clients.assignments_client import (
    RestAssignmentsClient,
)
from fleetops_reports.infrastructure.rest_clients.circuit_breaker import CircuitBreaker
from fleetops_reports.infrastructure.rest_clients.incidents_client import (
    RestIncidentsClient,
)
from fleetops_reports.infrastructure.rest_clients.maintenance_client import (
    RestMaintenanceClient,
)
from fleetops_reports.infrastructure.rest_clients.vehicles_client import (
    RestVehiclesClient,
)
from fleetops_reports.infrastructure.storage.minio.minio_client import (
    MinioObjectStorage,
)
from fleetops_reports.infrastructure.templates.jinja_renderer import JinjaRenderer


@lru_cache
def get_settings() -> Settings:
    return Settings()


def _build_circuit_breaker(settings: Settings) -> CircuitBreaker:
    return CircuitBreaker(
        failure_threshold=settings.circuit_breaker_failure_threshold,
        recovery_seconds=settings.circuit_breaker_recovery_seconds,
    )

def _build_generate_report_use_case(settings: Settings) -> GenerateReportUseCase:
    gateway_url = settings.operational_gateway_base_url

    # ALINEACIÓN ADR-005: 4 independent circuit breakers to isolate cascading failures
    vehicles_breaker = _build_circuit_breaker(settings)
    assignments_breaker = _build_circuit_breaker(settings)
    incidents_breaker = _build_circuit_breaker(settings)
    maintenance_breaker = _build_circuit_breaker(settings)

    storage = MinioObjectStorage(settings)
    renderer = WeasyPrintRenderer(JinjaRenderer(settings))
    report_service = ReportService(
        repository=MongoAnalyticsRepository(),
        storage=storage,
        renderer=renderer,
    )

    return GenerateReportUseCase(
        vehicles_client=RestVehiclesClient(gateway_url, vehicles_breaker),
        assignments_client=RestAssignmentsClient(gateway_url, assignments_breaker),
        incidents_client=RestIncidentsClient(gateway_url, incidents_breaker),
        maintenance_client=RestMaintenanceClient(gateway_url, maintenance_breaker),
        availability_service=AvailabilityService(),
        incident_service=IncidentService(),
        maintenance_service=MaintenanceService(),
        report_service=report_service,
        metrics_recorder=PrometheusReportMetricsRecorder(),
    )


def configure_application() -> None:
    settings = get_settings()
    configure_metrics_exporter(PrometheusMetricsExporter())
    configure_generate_report_use_case(
        lambda: _build_generate_report_use_case(settings)
    )
