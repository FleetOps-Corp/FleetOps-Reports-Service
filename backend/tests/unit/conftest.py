"""Unit-level fixtures.

SAD Traceability: supplies fake ports for application service tests without
real database, object storage or gRPC calls.
"""

from __future__ import annotations

import pytest

from fleetops_reports.application.services.availability_service import AvailabilityService
from fleetops_reports.application.services.incident_service import IncidentService
from fleetops_reports.application.services.maintenance_service import MaintenanceService
from fleetops_reports.application.services.report_service import ReportService
from fleetops_reports.application.use_cases.generate_report import GenerateReportUseCase
from tests.conftest import (
    FakeAssignmentsClient,
    FakeIncidentsClient,
    FakeMaintenanceClient,
    FakeVehiclesClient,
)


@pytest.fixture
def unit_report_service(fake_repository, fake_storage, fake_renderer) -> ReportService:
    """ReportService wired with fake ports for application-layer unit tests."""
    return ReportService(fake_repository, fake_storage, fake_renderer)


@pytest.fixture
def unit_generate_report_use_case(
    sample_vehicles,
    sample_assignments,
    sample_incidents,
    sample_maintenance,
    unit_report_service,
) -> GenerateReportUseCase:
    """Use case fixture that exercises all application ports without infrastructure."""
    return GenerateReportUseCase(
        FakeVehiclesClient(sample_vehicles),
        FakeAssignmentsClient(sample_assignments),
        FakeIncidentsClient(sample_incidents),
        FakeMaintenanceClient(sample_maintenance),
        AvailabilityService(),
        IncidentService(),
        MaintenanceService(),
        unit_report_service,
    )

