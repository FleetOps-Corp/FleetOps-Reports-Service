"""API integration fixtures.

SAD Traceability: creates a FastAPI TestClient with dependency overrides for
ports and use cases.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fleetops_reports.application.dependencies import get_generate_report_use_case
from fleetops_reports.application.services.availability_service import AvailabilityService
from fleetops_reports.application.services.incident_service import IncidentService
from fleetops_reports.application.services.maintenance_service import MaintenanceService
from fleetops_reports.application.services.report_service import ReportService
from fleetops_reports.application.use_cases.generate_report import GenerateReportUseCase
from fleetops_reports.presentation.api.routes import reports
from tests.conftest import (
    FakeAssignmentsClient,
    FakeIncidentsClient,
    FakeMaintenanceClient,
    FakeVehiclesClient,
)


@pytest.fixture
def api_client(
    sample_vehicles,
    sample_assignments,
    sample_incidents,
    sample_maintenance,
    fake_repository,
    fake_storage,
    fake_renderer,
) -> TestClient:
    app = FastAPI()
    app.include_router(reports.router)
    use_case = GenerateReportUseCase(
        FakeVehiclesClient(sample_vehicles),
        FakeAssignmentsClient(sample_assignments),
        FakeIncidentsClient(sample_incidents),
        FakeMaintenanceClient(sample_maintenance),
        AvailabilityService(),
        IncidentService(),
        MaintenanceService(),
        ReportService(fake_repository, fake_storage, fake_renderer),
    )
    app.dependency_overrides[get_generate_report_use_case] = lambda: use_case
    return TestClient(app)
