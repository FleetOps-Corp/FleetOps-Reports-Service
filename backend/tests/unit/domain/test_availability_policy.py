"""Availability policy tests.

SAD Traceability: validates SAD section 10.1 availability rules.
"""

import pytest

from fleetops_reports.domain.exceptions import EmptyDatasetError, VehicleNotAvailableError
from fleetops_reports.domain.models.vehicle import Vehicle
from fleetops_reports.domain.policies.availability_policy import AvailabilityPolicy


def test_calculate_global_availability(sample_vehicles) -> None:
    result = AvailabilityPolicy().calculate_global_availability(sample_vehicles)
    assert round(result.value, 2) == 66.67


def test_calculate_global_availability_rejects_empty_dataset() -> None:
    with pytest.raises(EmptyDatasetError):
        AvailabilityPolicy().calculate_global_availability([])


def test_ensure_vehicle_available_raises_for_unavailable_vehicle() -> None:
    vehicle = Vehicle("veh-002", "FOP-002", "MANTENIMIENTO", "bogota", "truck", "2023")
    with pytest.raises(VehicleNotAvailableError):
        AvailabilityPolicy().ensure_vehicle_available(vehicle)


def test_ensure_vehicle_available_accepts_operational_vehicle() -> None:
    vehicle = Vehicle("veh-001", "FOP-001", "DISPONIBLE", "bogota", "van", "2024")
    AvailabilityPolicy().ensure_vehicle_available(vehicle)

