"""In-memory operational clients backed by bundled fixtures."""

from __future__ import annotations

from fleetops_reports.application.ports.operational_clients import (
    AssignmentRecord,
    IncidentRecord,
    MaintenanceRecord,
)
from fleetops_reports.domain.models.vehicle import Vehicle
from fleetops_reports.infrastructure.fixtures.loader import (
    load_fixture_assignments,
    load_fixture_incidents,
    load_fixture_maintenance,
    load_fixture_vehicles,
)


async def _async_value[T](value: T) -> T:
    return value


class FixtureVehiclesClient:
    async def list_vehicles(self) -> list[Vehicle]:
        return await _async_value(load_fixture_vehicles())


class FixtureAssignmentsClient:
    async def list_assignments(self) -> list[AssignmentRecord]:
        return await _async_value(load_fixture_assignments())


class FixtureIncidentsClient:
    async def list_incidents(self) -> list[IncidentRecord]:
        return await _async_value(load_fixture_incidents())


class FixtureMaintenanceClient:
    async def list_maintenance(self) -> list[MaintenanceRecord]:
        return await _async_value(load_fixture_maintenance())
