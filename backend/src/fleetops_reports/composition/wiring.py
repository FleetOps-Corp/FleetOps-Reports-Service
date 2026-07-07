"""Application wiring.

SAD Traceability: composition root that binds ports to MongoDB, MinIO, REST,
PDF and observability adapters per SAD section 6.
"""

from __future__ import annotations

from functools import lru_cache

from fleetops_reports.application.dependencies import (
    configure_download_report_use_case,
    configure_generate_report_use_case,
    configure_get_report_use_case,
    configure_list_reports_use_case,
    configure_metrics_exporter,
)
from fleetops_reports.application.services.availability_service import (
    AvailabilityService,
)
from fleetops_reports.application.services.incident_service import IncidentService
from fleetops_reports.application.services.maintenance_service import MaintenanceService
from fleetops_reports.application.services.report_service import ReportService
from fleetops_reports.application.use_cases.download_report import DownloadReportUseCase
from fleetops_reports.application.use_cases.generate_report import GenerateReportUseCase
from fleetops_reports.application.use_cases.get_report import GetReportUseCase
from fleetops_reports.application.use_cases.list_reports import ListReportsUseCase
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


def _build_repository() -> MongoAnalyticsRepository:
    return MongoAnalyticsRepository()


def _build_storage(settings: Settings) -> MinioObjectStorage:
    return MinioObjectStorage(settings)


def _build_report_service(settings: Settings) -> ReportService:
    storage = _build_storage(settings)
    renderer = WeasyPrintRenderer(JinjaRenderer(settings))
    return ReportService(
        repository=_build_repository(),
        storage=storage,
        renderer=renderer,
    )


def _build_generate_report_use_case(settings: Settings) -> GenerateReportUseCase:
    gateway_url = settings.operational_gateway_base_url
    gateway_token = settings.operational_gateway_bearer_token

    vehicles_breaker = _build_circuit_breaker(settings)
    assignments_breaker = _build_circuit_breaker(settings)
    incidents_breaker = _build_circuit_breaker(settings)
    maintenance_breaker = _build_circuit_breaker(settings)

    return GenerateReportUseCase(
        vehicles_client=RestVehiclesClient(gateway_url, vehicles_breaker, gateway_token),
        assignments_client=RestAssignmentsClient(
            gateway_url, assignments_breaker, gateway_token
        ),
        incidents_client=RestIncidentsClient(gateway_url, incidents_breaker, gateway_token),
        maintenance_client=RestMaintenanceClient(
            gateway_url, maintenance_breaker, gateway_token
        ),
        availability_service=AvailabilityService(),
        incident_service=IncidentService(),
        maintenance_service=MaintenanceService(),
        report_service=_build_report_service(settings),
        metrics_recorder=PrometheusReportMetricsRecorder(),
    )


def _build_list_reports_use_case() -> ListReportsUseCase:
    return ListReportsUseCase(_build_repository())


def _build_get_report_use_case() -> GetReportUseCase:
    return GetReportUseCase(_build_repository())


def _build_download_report_use_case(settings: Settings) -> DownloadReportUseCase:
    return DownloadReportUseCase(_build_repository(), _build_storage(settings))


def configure_application() -> None:
    settings = get_settings()
    configure_metrics_exporter(PrometheusMetricsExporter())
    configure_generate_report_use_case(lambda: _build_generate_report_use_case(settings))
    configure_list_reports_use_case(_build_list_reports_use_case)
    configure_get_report_use_case(_build_get_report_use_case)
    configure_download_report_use_case(lambda: _build_download_report_use_case(settings))
