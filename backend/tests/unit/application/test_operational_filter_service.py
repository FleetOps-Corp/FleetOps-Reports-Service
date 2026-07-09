"""Operational filter service tests."""

from datetime import UTC, date, datetime

from fleetops_reports.application.ports.operational_clients import (
    IncidentRecord,
    MaintenanceRecord,
)
from fleetops_reports.application.services.operational_filter_service import (
    filter_incidents_by_period,
    filter_incidents_for_vehicles,
    filter_maintenance_by_period,
    filter_maintenance_for_vehicles,
    filter_vehicles_by_ciudad,
    filter_vehicles_by_sede,
    filter_vehicles_for_report,
)
from fleetops_reports.domain.models.vehicle import Vehicle


def test_filter_vehicles_by_sede_is_case_insensitive() -> None:
    vehicles = [
        Vehicle("1", "A", "DISPONIBLE", "Bogotá", "X", "Y", "Patio Norte Bogotá"),
        Vehicle("2", "B", "DISPONIBLE", "Cali", "X", "Y", "Patio Cali"),
    ]
    filtered = filter_vehicles_by_sede(vehicles, "patio norte bogotá")
    assert len(filtered) == 1
    assert filtered[0].id_vehiculo == "1"


def test_filter_vehicles_by_ciudad_is_case_insensitive() -> None:
    vehicles = [
        Vehicle("1", "A", "DISPONIBLE", "Bogotá", "X", "Y", "Patio Norte Bogotá"),
        Vehicle("2", "B", "DISPONIBLE", "Cali", "X", "Y", "Patio Cali"),
    ]
    filtered = filter_vehicles_by_ciudad(vehicles, "cali")
    assert len(filtered) == 1
    assert filtered[0].id_vehiculo == "2"


def test_filter_vehicles_for_report_applies_sede_and_ciudad() -> None:
    vehicles = [
        Vehicle("1", "A", "DISPONIBLE", "Bogotá", "X", "Y", "Patio Norte Bogotá"),
        Vehicle("2", "B", "DISPONIBLE", "Bogotá", "X", "Y", "Patio Sur Bogotá"),
        Vehicle("3", "C", "DISPONIBLE", "Cali", "X", "Y", "Patio Cali"),
    ]
    filtered = filter_vehicles_for_report(
        vehicles,
        sede_operacion="Patio Norte Bogotá",
        ciudad_operacion="Bogotá",
    )
    assert len(filtered) == 1
    assert filtered[0].id_vehiculo == "1"


def test_filter_incidents_for_vehicles() -> None:
    vehicles = [Vehicle("1", "FOP-001", "DISPONIBLE", "Bogotá", "X", "Y", "Sede A")]
    now = datetime.now(UTC)
    incidents = [
        IncidentRecord("1", "c1", "FOP-001", "MECANICO", "GRAVE", now),
        IncidentRecord("2", "c2", "FOP-999", "MECANICO", "GRAVE", now),
    ]
    filtered = filter_incidents_for_vehicles(incidents, vehicles)
    assert len(filtered) == 1
    assert filtered[0].incident_id == "1"


def test_filter_maintenance_for_vehicles() -> None:
    vehicles = [Vehicle("veh-1", "FOP-001", "DISPONIBLE", "Bogotá", "X", "Y", "Sede A")]
    now = datetime.now(UTC)
    maintenance = [
        MaintenanceRecord("veh-1", "CORRECTIVO", now, now),
        MaintenanceRecord("veh-2", "CORRECTIVO", now, now),
    ]
    filtered = filter_maintenance_for_vehicles(maintenance, vehicles)
    assert len(filtered) == 1
    assert filtered[0].vehicle_id == "veh-1"


def test_filter_incidents_by_period() -> None:
    incidents = [
        IncidentRecord(
            "1",
            "c1",
            "FOP-001",
            "MECANICO",
            "GRAVE",
            datetime(2026, 5, 10, tzinfo=UTC),
        ),
        IncidentRecord(
            "2",
            "c2",
            "FOP-002",
            "MECANICO",
            "GRAVE",
            datetime(2026, 6, 10, tzinfo=UTC),
        ),
    ]
    filtered = filter_incidents_by_period(
        incidents,
        start_date=date(2026, 5, 1),
        end_date=date(2026, 5, 31),
    )
    assert len(filtered) == 1
    assert filtered[0].incident_id == "1"


def test_filter_maintenance_by_period() -> None:
    maintenance = [
        MaintenanceRecord(
            "veh-1",
            "CORRECTIVO",
            datetime(2026, 5, 10, tzinfo=UTC),
            datetime(2026, 5, 11, tzinfo=UTC),
        ),
        MaintenanceRecord(
            "veh-2",
            "CORRECTIVO",
            datetime(2026, 6, 10, tzinfo=UTC),
            datetime(2026, 6, 11, tzinfo=UTC),
        ),
    ]
    filtered = filter_maintenance_by_period(
        maintenance,
        start_date=date(2026, 5, 1),
        end_date=date(2026, 5, 31),
    )
    assert len(filtered) == 1
    assert filtered[0].vehicle_id == "veh-1"


def test_to_utc_datetime_passthrough_datetime() -> None:
    from fleetops_reports.application.services import operational_filter_service as module

    dt = datetime(2026, 5, 1, tzinfo=UTC)
    assert module._to_utc_datetime(dt) is dt
