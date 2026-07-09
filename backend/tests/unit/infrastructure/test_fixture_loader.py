"""Bundled fixture loader tests."""

from fleetops_reports.infrastructure.fixtures.loader import (
    load_fixture_incidents,
    load_fixture_maintenance,
    load_fixture_vehicles,
)


def test_fixture_loader_loads_operational_datasets() -> None:
    vehicles = load_fixture_vehicles()
    incidents = load_fixture_incidents()
    maintenance = load_fixture_maintenance()

    assert len(vehicles) >= 30
    assert len(incidents) >= 10
    assert len(maintenance) >= 10
    assert {vehicle.ciudad_operacion for vehicle in vehicles} >= {"Bogotá", "Medellín", "Cali"}
