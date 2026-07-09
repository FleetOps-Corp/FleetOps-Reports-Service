"""Availability policy tests.

SAD Traceability: validates domain policy for SAD process 10.1.
"""

import pytest

from fleetops_reports.domain.exceptions import (
    EmptyDatasetError,
    VehicleNotAvailableError,
)
from fleetops_reports.domain.models.vehicle import Vehicle
from fleetops_reports.domain.policies.availability_policy import AvailabilityPolicy


def test_calculate_global_availability() -> None:
    vehicles = [
        Vehicle("veh-001", "ABC-123", "DISPONIBLE", "bogota", "van", "2024"),
        Vehicle("veh-002", "DEF-456", "DISPONIBLE", "bogota", "car", "2023"),
        Vehicle("veh-003", "GHI-789", "MANTENIMIENTO", "medellin", "van", "2022"),
    ]

    percentage = AvailabilityPolicy().calculate_global_availability(vehicles)

    assert percentage.value == pytest.approx(66.67, abs=0.01)


def test_calculate_global_availability_returns_zero_for_empty_dataset() -> None:
    percentage = AvailabilityPolicy().calculate_global_availability([])
    assert percentage.value == 0.0


def test_calculate_global_unavailability() -> None:
    vehicles = [
        Vehicle("veh-001", "ABC-123", "DISPONIBLE", "bogota", "van", "2024"),
        Vehicle("veh-002", "DEF-456", "ASIGNADO", "bogota", "car", "2023"),
        Vehicle("veh-003", "GHI-789", "MANTENIMIENTO", "medellin", "van", "2022"),
        Vehicle("veh-004", "JKL-012", "FUERA_SERVICIO", "medellin", "truck", "2021"),
    ]

    percentage = AvailabilityPolicy().calculate_global_unavailability(vehicles)

    assert percentage.value == pytest.approx(75.0, abs=0.01)


def test_count_unavailable_vehicles() -> None:
    vehicles = [
        Vehicle("veh-001", "ABC-123", "DISPONIBLE", "bogota", "van", "2024"),
        Vehicle("veh-002", "DEF-456", "ASIGNADO", "bogota", "car", "2023"),
        Vehicle("veh-003", "GHI-789", "MANTENIMIENTO", "medellin", "van", "2022"),
    ]

    unavailable_count = AvailabilityPolicy().count_unavailable_vehicles(vehicles)

    assert unavailable_count == 2


def test_ensure_vehicle_available_raises_for_unavailable_vehicle() -> None:
    vehicle = Vehicle(
        "veh-001",
        "ABC-123",
        "MANTENIMIENTO",
        "bogota",
        "van",
        "2024",
    )

    with pytest.raises(VehicleNotAvailableError):
        AvailabilityPolicy().ensure_vehicle_available(vehicle)


def test_ensure_vehicle_available_accepts_operational_vehicle() -> None:
    vehicle = Vehicle(
        "veh-001",
        "ABC-123",
        "DISPONIBLE",
        "bogota",
        "van",
        "2024",
    )

    AvailabilityPolicy().ensure_vehicle_available(vehicle)

def test_filter_available_vehicles_returns_only_available_vehicles() -> None:
    vehicles = [
        Vehicle("veh-001", "ABC-123", "DISPONIBLE", "bogota", "van", "2024"),
        Vehicle("veh-002", "DEF-456", "ASIGNADO", "bogota", "car", "2023"),
        Vehicle("veh-003", "GHI-789", "DISPONIBLE", "medellin", "truck", "2021"),
    ]

    available_vehicles = AvailabilityPolicy().filter_available_vehicles(vehicles)

    assert [vehicle.id_vehiculo for vehicle in available_vehicles] == [
        "veh-001",
        "veh-003",
    ]
    assert all(vehicle.is_available for vehicle in available_vehicles)


def test_filter_available_vehicles_rejects_empty_dataset() -> None:
    with pytest.raises(EmptyDatasetError):
        AvailabilityPolicy().filter_available_vehicles([])
