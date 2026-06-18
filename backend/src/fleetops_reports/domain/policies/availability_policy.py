"""Availability policy.

SAD Traceability: implements the availability calculation process described in
SAD section 10.1 and raises domain exceptions when business rules are violated.
"""

from __future__ import annotations

from fleetops_reports.domain.exceptions import EmptyDatasetError, VehicleNotAvailableError
from fleetops_reports.domain.models.vehicle import Vehicle
from fleetops_reports.domain.value_objects.percentage import Percentage


class AvailabilityPolicy:
    def calculate_global_availability(self, vehicles: list[Vehicle]) -> Percentage:
        """Calculate operational vehicle percentage using SAD availability rules."""
        if not vehicles:
            raise EmptyDatasetError("vehicles")
        available = sum(1 for vehicle in vehicles if vehicle.is_operational())
        return Percentage((available / len(vehicles)) * 100)

    def ensure_vehicle_available(self, vehicle: Vehicle) -> None:
        """Reject vehicles that cannot participate in an operational report."""
        if not vehicle.is_operational():
            raise VehicleNotAvailableError(vehicle.vehicle_id, vehicle.status)

