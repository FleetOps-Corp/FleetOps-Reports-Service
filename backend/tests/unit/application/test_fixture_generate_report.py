"""Fixture-backed report generation tests."""

from datetime import date

import pytest

from fleetops_reports.application.services.availability_service import AvailabilityService
from fleetops_reports.application.services.incident_service import IncidentService
from fleetops_reports.application.services.maintenance_service import MaintenanceService
from fleetops_reports.application.services.operational_filter_service import (
    filter_vehicles_for_report,
)
from fleetops_reports.application.services.report_service import ReportService
from fleetops_reports.application.use_cases.generate_report import (
    GenerateReportCommand,
    GenerateReportUseCase,
)
from fleetops_reports.domain.value_objects.report_period import ReportPeriod
from fleetops_reports.infrastructure.fixtures.clients import (
    FixtureAssignmentsClient,
    FixtureIncidentsClient,
    FixtureMaintenanceClient,
    FixtureVehiclesClient,
)
from fleetops_reports.infrastructure.fixtures.loader import load_fixture_vehicles


@pytest.fixture
def fixture_use_case(fake_repository, fake_storage, fake_renderer) -> GenerateReportUseCase:
    return GenerateReportUseCase(
        FixtureVehiclesClient(),
        FixtureAssignmentsClient(),
        FixtureIncidentsClient(),
        FixtureMaintenanceClient(),
        AvailabilityService(),
        IncidentService(),
        MaintenanceService(),
        ReportService(fake_repository, fake_storage, fake_renderer),
    )


@pytest.mark.asyncio
async def test_fixture_generate_filters_by_city(fixture_use_case, fake_repository) -> None:
    report = await fixture_use_case.execute(
        GenerateReportCommand(
            report_id="rep-fixture-bogota",
            title="Fixture Bogotá",
            period=ReportPeriod(start_date=date(2026, 5, 1), end_date=date(2026, 5, 31)),
            ciudad_operacion="Bogotá",
        )
    )

    assert report.status == "generated"
    assert report.ciudad_operacion == "Bogotá"
    assert report.sede_operacion is None
    assert len(report.kpis) == 6
    assert fake_repository.saved[-1].report_id == "rep-fixture-bogota"


def test_fixture_vehicles_city_filter_matches_bogota_scope() -> None:
    vehicles = filter_vehicles_for_report(
        load_fixture_vehicles(),
        ciudad_operacion="Bogotá",
    )
    assert len(vehicles) == 26
    assert all(vehicle.ciudad_operacion == "Bogotá" for vehicle in vehicles)
