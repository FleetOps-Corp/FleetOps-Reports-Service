"""Generate report use case tests.

SAD Traceability: validates the end-to-end application transaction required by
the prompt and SAD section 10.6.
"""

import pytest

from fleetops_reports.application.services.availability_service import AvailabilityService
from fleetops_reports.application.services.incident_service import IncidentService
from fleetops_reports.application.services.maintenance_service import MaintenanceService
from fleetops_reports.application.services.report_service import ReportService
from fleetops_reports.application.use_cases.generate_report import (
    GenerateReportCommand,
    GenerateReportUseCase,
)
from fleetops_reports.domain.exceptions import EmptyDatasetError, ReportGenerationError
from tests.conftest import (
    FakeAssignmentsClient,
    FakeIncidentsClient,
    FakeMaintenanceClient,
    FakeVehiclesClient,
)


@pytest.mark.asyncio
async def test_generate_report_use_case_executes_transaction(
    report_period,
    sample_vehicles,
    sample_assignments,
    sample_incidents,
    sample_maintenance,
    fake_repository,
    fake_storage,
    fake_renderer,
) -> None:
    report_service = ReportService(fake_repository, fake_storage, fake_renderer)
    use_case = GenerateReportUseCase(
        FakeVehiclesClient(sample_vehicles),
        FakeAssignmentsClient(sample_assignments),
        FakeIncidentsClient(sample_incidents),
        FakeMaintenanceClient(sample_maintenance),
        AvailabilityService(),
        IncidentService(),
        MaintenanceService(),
        report_service,
    )
    command = GenerateReportCommand("rep-001", "Executive Report", report_period)
    result = await use_case.execute(command)
    assert result.status == "generated"
    assert len(result.kpis) == 6


@pytest.mark.asyncio
async def test_generate_report_use_case_handles_empty_vehicle_dataset(
    report_period,
    sample_assignments,
    sample_incidents,
    sample_maintenance,
    fake_repository,
    fake_storage,
    fake_renderer,
) -> None:
    report_service = ReportService(fake_repository, fake_storage, fake_renderer)
    use_case = GenerateReportUseCase(
        FakeVehiclesClient([]),
        FakeAssignmentsClient(sample_assignments),
        FakeIncidentsClient(sample_incidents),
        FakeMaintenanceClient(sample_maintenance),
        AvailabilityService(),
        IncidentService(),
        MaintenanceService(),
        report_service,
    )

    command = GenerateReportCommand("rep-empty-vehicles", "Executive Report", report_period)
    result = await use_case.execute(command)
    assert result.status == "generated"
    assert result.kpis[0].metric.value == 0.0


@pytest.mark.asyncio
async def test_generate_report_use_case_reraises_domain_errors(
    report_period,
    sample_vehicles,
    fake_repository,
    fake_storage,
    fake_renderer,
) -> None:
    class FailingReportService(ReportService):
        async def generate(self, report, *, vehicles, incidents, maintenance):
            raise EmptyDatasetError("forced")

    use_case = GenerateReportUseCase(
        FakeVehiclesClient(sample_vehicles),
        FakeAssignmentsClient([]),
        FakeIncidentsClient([]),
        FakeMaintenanceClient([]),
        AvailabilityService(),
        IncidentService(),
        MaintenanceService(),
        FailingReportService(fake_repository, fake_storage, fake_renderer),
    )
    command = GenerateReportCommand("rep-domain-error", "Executive Report", report_period)
    with pytest.raises(EmptyDatasetError):
        await use_case.execute(command)


class FailingAssignmentsClient:
    async def list_assignments(self):
        raise RuntimeError("assignments service unavailable")


@pytest.mark.asyncio
async def test_generate_report_use_case_wraps_unexpected_errors(
    report_period,
    sample_vehicles,
    sample_incidents,
    sample_maintenance,
    fake_repository,
    fake_storage,
    fake_renderer,
) -> None:
    report_service = ReportService(fake_repository, fake_storage, fake_renderer)
    use_case = GenerateReportUseCase(
        FakeVehiclesClient(sample_vehicles),
        FailingAssignmentsClient(),
        FakeIncidentsClient(sample_incidents),
        FakeMaintenanceClient(sample_maintenance),
        AvailabilityService(),
        IncidentService(),
        MaintenanceService(),
        report_service,
    )

    command = GenerateReportCommand("rep-runtime-error", "Executive Report", report_period)
    with pytest.raises(ReportGenerationError) as exc_info:
        await use_case.execute(command)

    assert exc_info.value.details["report_id"] == "rep-runtime-error"
