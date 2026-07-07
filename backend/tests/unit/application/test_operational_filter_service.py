"""Operational filter service tests."""

from datetime import UTC, datetime

from fleetops_reports.application.ports.operational_clients import (
    IncidentRecord,
    MaintenanceRecord,
)
from fleetops_reports.application.services.operational_filter_service import (
    filter_incidents_for_vehicles,
    filter_maintenance_for_vehicles,
    filter_vehicles_by_sede,
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
