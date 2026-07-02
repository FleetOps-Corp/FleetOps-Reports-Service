"""Availability service tests.

SAD Traceability: validates logical service for SAD process 10.1.
"""

import pytest

from fleetops_reports.application.services.availability_service import AvailabilityService
from fleetops_reports.domain.exceptions import EmptyDatasetError
from fleetops_reports.domain.models.vehicle import Vehicle


def test_availability_service_calculates_kpi(sample_vehicles) -> None:
    kpi = AvailabilityService().calculate_global_kpi(sample_vehicles)

    assert kpi.name == "Fleet Availability"
    assert kpi.metric.name == "fleet_availability"
    assert kpi.metric.value == pytest.approx(66.67, abs=0.01)
    assert kpi.metric.unit == "percent"


def test_availability_service_calculates_available_vehicles_kpi() -> None:
    vehicles = [
        Vehicle("veh-001", "ABC-123", "DISPONIBLE", "bogota", "van", "2024"),
        Vehicle("veh-002", "DEF-456", "DISPONIBLE", "bogota", "car", "2023"),
        Vehicle("veh-003", "GHI-789", "MANTENIMIENTO", "medellin", "van", "2022"),
    ]

    kpi = AvailabilityService().calculate_available_vehicles_kpi(vehicles)

    assert kpi.name == "Available Vehicles"
    assert kpi.metric.name == "available_vehicles"
    assert kpi.metric.value == 2
    assert kpi.metric.unit == "vehicles"


def test_availability_service_calculates_unavailable_vehicles_kpi() -> None:
    vehicles = [
        Vehicle("veh-001", "ABC-123", "DISPONIBLE", "bogota", "van", "2024"),
        Vehicle("veh-002", "DEF-456", "ASIGNADO", "bogota", "car", "2023"),
        Vehicle("veh-003", "GHI-789", "MANTENIMIENTO", "medellin", "van", "2022"),
        Vehicle("veh-004", "JKL-012", "FUERA_SERVICIO", "medellin", "truck", "2021"),
    ]

    kpi = AvailabilityService().calculate_unavailable_vehicles_kpi(vehicles)

    assert kpi.name == "Unavailable Vehicles"
    assert kpi.metric.name == "unavailable_vehicles"
    assert kpi.metric.value == 3
    assert kpi.metric.unit == "vehicles"


def test_availability_service_calculates_unavailability_kpi() -> None:
    vehicles = [
        Vehicle("veh-001", "ABC-123", "DISPONIBLE", "bogota", "van", "2024"),
        Vehicle("veh-002", "DEF-456", "ASIGNADO", "bogota", "car", "2023"),
        Vehicle("veh-003", "GHI-789", "MANTENIMIENTO", "medellin", "van", "2022"),
        Vehicle("veh-004", "JKL-012", "FUERA_SERVICIO", "medellin", "truck", "2021"),
    ]

    kpi = AvailabilityService().calculate_unavailability_kpi(vehicles)

    assert kpi.name == "Fleet Unavailability"
    assert kpi.metric.name == "fleet_unavailability"
    assert kpi.metric.value == pytest.approx(75.0, abs=0.01)
    assert kpi.metric.unit == "percent"


def test_availability_service_raises_error_when_dataset_is_empty() -> None:
    with pytest.raises(EmptyDatasetError):
        AvailabilityService().calculate_global_kpi([])


def test_availability_service_rejects_empty_dataset_for_available_kpi() -> None:
    with pytest.raises(EmptyDatasetError):
        AvailabilityService().calculate_available_vehicles_kpi([])


def test_availability_service_rejects_empty_dataset_for_unavailable_kpi() -> None:
    with pytest.raises(EmptyDatasetError):
        AvailabilityService().calculate_unavailable_vehicles_kpi([])


def test_availability_service_raises_error_for_unavailability_kpi_when_dataset_is_empty() -> None:
    with pytest.raises(EmptyDatasetError):
        AvailabilityService().calculate_unavailability_kpi([])

def test_availability_service_lists_available_vehicles() -> None:
    vehicles = [
        Vehicle("veh-001", "ABC-123", "DISPONIBLE", "bogota", "van", "2024"),
        Vehicle("veh-002", "DEF-456", "MANTENIMIENTO", "bogota", "car", "2023"),
        Vehicle("veh-003", "GHI-789", "DISPONIBLE", "medellin", "truck", "2021"),
    ]

    available_vehicles = AvailabilityService().list_available_vehicles(vehicles)

    assert len(available_vehicles) == 2
    assert [vehicle.id_vehiculo for vehicle in available_vehicles] == [
        "veh-001",
        "veh-003",
    ]
    assert [vehicle.numero_placa for vehicle in available_vehicles] == [
        "ABC-123",
        "GHI-789",
    ]
    assert all(vehicle.estado_vehiculo == "DISPONIBLE" for vehicle in available_vehicles)


def test_availability_service_rejects_empty_dataset_for_available_vehicle_list() -> None:
    with pytest.raises(EmptyDatasetError):
        AvailabilityService().list_available_vehicles([])
