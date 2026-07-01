"""Incident analytics logical service.

SAD Traceability: supports recurrence, severity, type breakdown and vehicle
criticality analysis from SAD section 10.3.
"""

from __future__ import annotations

from collections import Counter

from fleetops_reports.application.ports.operational_clients import (
    IncidentRecord,
    MaintenanceRecord,
)
from fleetops_reports.domain.models.kpi import KPI
from fleetops_reports.domain.models.vehicle import Vehicle
from fleetops_reports.domain.policies.criticality_policy import CriticalityPolicy
from fleetops_reports.domain.value_objects.metric import Metric


class IncidentService:
    def __init__(self, policy: CriticalityPolicy | None = None) -> None:
        self._policy = policy or CriticalityPolicy()

    def calculate_critical_vehicle_kpi(
        self,
        incidents: list[IncidentRecord],
        maintenance: list[MaintenanceRecord],
        vehicles: list[Vehicle],
    ) -> KPI:
        plate_to_vehicle_id = {
            vehicle.numero_placa: vehicle.id_vehiculo
            for vehicle in vehicles
            if vehicle.numero_placa
        }

        incident_counts: Counter[str] = Counter()
        for record in incidents:
            vehicle_id = plate_to_vehicle_id.get(record.placa_vehiculo)
            if vehicle_id:
                incident_counts[vehicle_id] += 1

        maintenance_counts: Counter[str] = Counter(
            record.vehicle_id for record in maintenance
        )

        vehicle_ids = set(incident_counts) | set(maintenance_counts)
        critical_count = sum(
            1
            for vehicle_id in vehicle_ids
            if self._policy.classify(
                incident_counts[vehicle_id],
                maintenance_counts[vehicle_id],
            )
            == "critical"
        )

        metric = Metric(
            name="critical_vehicle_count",
            value=float(critical_count),
            unit="vehicles",
        )
        return KPI.create_now(
            name="Critical Vehicles",
            metric=metric,
            source="incidents",
        )

    def calculate_high_severity_rate(
        self,
        incidents: list[IncidentRecord],
    ) -> KPI:
        total = len(incidents)
        if total == 0:
            rate = 0.0
        else:
            grave_count = sum(
                1 for record in incidents if record.severity.upper() == "GRAVE"
            )
            rate = round((grave_count / total) * 100, 2)

        metric = Metric(
            name="high_severity_rate",
            value=rate,
            unit="percent",
        )
        return KPI.create_now(
            name="High Severity Rate",
            metric=metric,
            source="incidents",
        )

    def calculate_human_incident_rate(
        self,
        incidents: list[IncidentRecord],
    ) -> KPI:
        total = len(incidents)
        if total == 0:
            rate = 0.0
        else:
            human_count = sum(
                1
                for record in incidents
                if record.tipo_incidente.upper() == "HUMANO"
            )
            rate = round((human_count / total) * 100, 2)

        metric = Metric(
            name="human_incident_rate",
            value=rate,
            unit="percent",
        )
        return KPI.create_now(
            name="Human Incident Rate",
            metric=metric,
            source="incidents",
        )

    def calculate_recurrent_vehicle_kpi(
        self,
        incidents: list[IncidentRecord],
        recurrence_threshold: int = 2,
    ) -> KPI:
        counts: Counter[str] = Counter(
            record.placa_vehiculo for record in incidents
        )
        recurrent_count = sum(
            1 for count in counts.values() if count >= recurrence_threshold
        )

        metric = Metric(
            name="recurrent_vehicle_count",
            value=float(recurrent_count),
            unit="vehicles",
        )
        return KPI.create_now(
            name="Recurrent Vehicles",
            metric=metric,
            source="incidents",
        )
