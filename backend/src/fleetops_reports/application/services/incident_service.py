"""Incident analytics logical service.

SAD Traceability: supports recurrence, severity and vehicle criticality
analysis from SAD section 10.3.
"""

from __future__ import annotations

from collections import Counter

from fleetops_reports.application.ports.operational_clients import IncidentRecord, MaintenanceRecord
from fleetops_reports.domain.models.kpi import KPI
from fleetops_reports.domain.policies.criticality_policy import CriticalityPolicy
from fleetops_reports.domain.value_objects.metric import Metric


class IncidentService:
    def __init__(self, policy: CriticalityPolicy | None = None) -> None:
        self._policy = policy or CriticalityPolicy()

    def calculate_critical_vehicle_kpi(
        self,
        incidents: list[IncidentRecord],
        maintenance: list[MaintenanceRecord],
    ) -> KPI:
        incident_counts = Counter(record.vehicle_id for record in incidents)
        maintenance_counts = Counter(record.vehicle_id for record in maintenance)
        vehicle_ids = set(incident_counts) | set(maintenance_counts)
        critical_count = sum(
            1
            for vehicle_id in vehicle_ids
            if self._policy.classify(incident_counts[vehicle_id], maintenance_counts[vehicle_id])
            == "critical"
        )
        metric = Metric(name="critical_vehicle_count", value=float(critical_count), unit="vehicles")
        return KPI.create_now(name="Critical Vehicles", metric=metric, source="incidents")

