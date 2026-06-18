"""Availability logical service.

SAD Traceability: coordinates data retrieved through gRPC clients and applies
the AvailabilityPolicy for the process in SAD section 10.1.
"""

from __future__ import annotations

from fleetops_reports.domain.models.kpi import KPI
from fleetops_reports.domain.models.vehicle import Vehicle
from fleetops_reports.domain.policies.availability_policy import AvailabilityPolicy
from fleetops_reports.domain.value_objects.metric import Metric


class AvailabilityService:
    def __init__(self, policy: AvailabilityPolicy | None = None) -> None:
        self._policy = policy or AvailabilityPolicy()

    def calculate_global_kpi(self, vehicles: list[Vehicle]) -> KPI:
        percentage = self._policy.calculate_global_availability(vehicles)
        metric = Metric(name="fleet_availability", value=percentage.value, unit="percent")
        return KPI.create_now(name="Fleet Availability", metric=metric, source="vehicles")

