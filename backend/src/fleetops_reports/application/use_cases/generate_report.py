"""Generate report use case.

SAD Traceability: end-to-end transactional flow from REST entry point through
all layers to MongoDB and MinIO, matching prompt rule R2 and SAD section 10.6.
"""

from __future__ import annotations

from dataclasses import dataclass

from fleetops_reports.application.ports.metrics import (
    NoOpReportMetricsRecorder,
    ReportMetricsRecorder,
)
from fleetops_reports.application.ports.operational_clients import (
    AssignmentsClient,
    IncidentsClient,
    MaintenanceClient,
    VehiclesClient,
)
from fleetops_reports.application.services.availability_service import (
    AvailabilityService,
)
from fleetops_reports.application.services.incident_service import IncidentService
from fleetops_reports.application.services.maintenance_service import MaintenanceService
from fleetops_reports.application.services.report_service import ReportService
from fleetops_reports.domain.exceptions import DomainError, ReportGenerationError
from fleetops_reports.domain.models.report import Report
from fleetops_reports.domain.value_objects.report_period import ReportPeriod


@dataclass(frozen=True)
class GenerateReportCommand:
    report_id: str
    title: str
    period: ReportPeriod


class GenerateReportUseCase:
    def __init__(
        self,
        vehicles_client: VehiclesClient,
        assignments_client: AssignmentsClient,
        incidents_client: IncidentsClient,
        maintenance_client: MaintenanceClient,
        availability_service: AvailabilityService,
        incident_service: IncidentService,
        maintenance_service: MaintenanceService,
        report_service: ReportService,
        metrics_recorder: ReportMetricsRecorder | None = None,
    ) -> None:
        self._vehicles_client = vehicles_client
        self._assignments_client = assignments_client
        self._incidents_client = incidents_client
        self._maintenance_client = maintenance_client
        self._availability_service = availability_service
        self._incident_service = incident_service
        self._maintenance_service = maintenance_service
        self._report_service = report_service
        self._metrics_recorder = metrics_recorder or NoOpReportMetricsRecorder()

    async def execute(self, command: GenerateReportCommand) -> Report:
        self._metrics_recorder.on_request()
        try:
            with self._metrics_recorder.track_generation():
                vehicles = await self._vehicles_client.list_vehicles()
                await self._assignments_client.list_assignments()
                incidents = await self._incidents_client.list_incidents()
                maintenance = await self._maintenance_client.list_maintenance()

                kpis = [
                    self._availability_service.calculate_global_kpi(vehicles),
                    self._maintenance_service.calculate_mttr_kpi(maintenance),
                    self._incident_service.calculate_critical_vehicle_kpi(
                        incidents,
                        maintenance,
                        vehicles,
                    ),
                    self._incident_service.calculate_high_severity_rate(incidents),
                    self._incident_service.calculate_human_incident_rate(incidents),
                    self._incident_service.calculate_recurrent_vehicle_kpi(incidents),
                ]

                report = Report(
                    report_id=command.report_id,
                    title=command.title,
                    period=command.period,
                    kpis=kpis,
                )
                return await self._report_service.generate(
                    report,
                    vehicles=vehicles,
                    incidents=incidents,
                    maintenance=maintenance,
                )
        except DomainError:
            raise
        except Exception as exc:
            raise ReportGenerationError(command.report_id, str(exc)) from exc
