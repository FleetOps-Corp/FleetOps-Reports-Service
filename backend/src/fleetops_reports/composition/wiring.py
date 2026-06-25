"""Application wiring.

SAD Traceability: composition root that binds ports to MongoDB, MinIO, gRPC,
PDF and observability adapters per SAD section 6.
"""

from __future__ import annotations

import asyncio
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

# Mantenemos tus nombres de archivos confirmados en infrastructure/grpc_clients/
from fleetops_reports.infrastructure.grpc_clients.assignments_client import (
    GrpcAssignmentsClient,
)
from fleetops_reports.infrastructure.grpc_clients.circuit_breaker import CircuitBreaker
from fleetops_reports.infrastructure.grpc_clients.incidents_client import (
    GrpcIncidentsClient,
)
from fleetops_reports.infrastructure.grpc_clients.maintenance_client import (
    GrpcMaintenanceClient,
)
from fleetops_reports.infrastructure.grpc_clients.vehicles_client import (
    GrpcVehiclesClient,
)
from fleetops_reports.infrastructure.observability.prometheus_adapters import (
    PrometheusMetricsExporter,
    PrometheusReportMetricsRecorder,
)
from fleetops_reports.infrastructure.pdf.weasyprint_renderer import WeasyPrintRenderer
from fleetops_reports.infrastructure.persistence.mongodb.analytics_repository import (
    MongoAnalyticsRepository,
)
from fleetops_reports.infrastructure.storage.minio.minio_client import (
    MinioObjectStorage,
)
from fleetops_reports.infrastructure.templates.jinja_renderer import JinjaRenderer

# Referencias globales para la liberación ordenada de sockets y recursos de red en el apagado
_vehicles_client: GrpcVehiclesClient | None = None
_assignments_client: GrpcAssignmentsClient | None = None
_incidents_client: GrpcIncidentsClient | None = None
_maintenance_client: GrpcMaintenanceClient | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


def _build_circuit_breaker(settings: Settings) -> CircuitBreaker:
    """Helper para instanciar cortocircuitos independientes por cada cliente de red."""
    return CircuitBreaker(
        failure_threshold=settings.circuit_breaker_failure_threshold,
        recovery_seconds=settings.circuit_breaker_recovery_seconds,
    )


def _build_generate_report_use_case(settings: Settings) -> GenerateReportUseCase:
    global _vehicles_client, _assignments_client, _incidents_client, _maintenance_client

    # ALINEACIÓN ADR-005: Creamos 4 instancias independientes
    # para aislar por completo los fallos en cascada
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

    # Asignación a las referencias globales para poder llamarlas en el shutdown
    _vehicles_client = GrpcVehiclesClient(
        settings.vehicles_grpc_target, vehicles_breaker
    )
    _assignments_client = GrpcAssignmentsClient(
        settings.assignments_grpc_target, assignments_breaker
    )
    _incidents_client = GrpcIncidentsClient(
        settings.incidents_grpc_target, incidents_breaker
    )
    _maintenance_client = GrpcMaintenanceClient(
        settings.maintenance_grpc_target, maintenance_breaker
    )

    return GenerateReportUseCase(
        # Cada cliente gRPC recibe exclusivamente su Circuit Breaker dedicado
        vehicles_client=_vehicles_client,
        assignments_client=_assignments_client,
        incidents_client=_incidents_client,
        maintenance_client=_maintenance_client,
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


async def shutdown_application() -> None:
    """Libera de forma ordenada todos los canales asíncronos gRPC activos al apagar el servidor."""
    shutdown_tasks = []

    if _vehicles_client is not None:
        shutdown_tasks.append(_vehicles_client.close())
    if _assignments_client is not None:
        shutdown_tasks.append(_assignments_client.close())
    if _incidents_client is not None:
        shutdown_tasks.append(_incidents_client.close())
    if _maintenance_client is not None:
        shutdown_tasks.append(_maintenance_client.close())

    if shutdown_tasks:
        # Ejecuta concurrentemente el cierre de los stubs abiertos
        # para mitigar pérdidas de sockets (TIME_WAIT)
        await asyncio.gather(*shutdown_tasks, return_exceptions=True)
