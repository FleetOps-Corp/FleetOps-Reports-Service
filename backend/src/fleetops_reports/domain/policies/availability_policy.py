"""Availability policy.

SAD Traceability: implements the availability calculation process described in
SAD section 10.1 and raises domain exceptions when business rules are violated.
"""

from __future__ import annotations

from fleetops_reports.domain.exceptions import (
    EmptyDatasetError,
    VehicleNotAvailableError,
)
from fleetops_reports.domain.models.vehicle import Vehicle
from fleetops_reports.domain.value_objects.percentage import Percentage


class AvailabilityPolicy:
    def calculate_global_availability(self, vehicles: list[Vehicle]) -> Percentage:
        """Calculate operational vehicle percentage using SAD availability rules."""
        self._ensure_non_empty_dataset(vehicles)

        available = self.count_available_vehicles(vehicles)
        return Percentage(round((available / len(vehicles)) * 100, 2))

    def calculate_global_unavailability(self, vehicles: list[Vehicle]) -> Percentage:
        """Calculate operational vehicle unavailability percentage."""
        self._ensure_non_empty_dataset(vehicles)

        unavailable = self.count_unavailable_vehicles(vehicles)
        return Percentage(round((unavailable / len(vehicles)) * 100, 2))

    def count_available_vehicles(self, vehicles: list[Vehicle]) -> int:
        """Count vehicles that are operationally available."""
        self._ensure_non_empty_dataset(vehicles)

        return sum(1 for vehicle in vehicles if vehicle.is_available)

    def count_unavailable_vehicles(self, vehicles: list[Vehicle]) -> int:
        """Count vehicles that are not operationally available."""
        self._ensure_non_empty_dataset(vehicles)

        return sum(1 for vehicle in vehicles if not vehicle.is_available)

    def ensure_vehicle_available(self, vehicle: Vehicle) -> None:
        """Reject vehicles that cannot participate in an operational report."""
        if not vehicle.is_available:
            raise VehicleNotAvailableError(vehicle.id_vehiculo, vehicle.estado_vehiculo)

    def _ensure_non_empty_dataset(self, vehicles: list[Vehicle]) -> None:
        if not vehicles:
            raise EmptyDatasetError("vehicles")
