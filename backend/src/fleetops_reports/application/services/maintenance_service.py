"""Maintenance analytics logical service.

SAD Traceability: calculates MTTR and maintenance indicators from SAD section
10.2 using a domain policy rather than infrastructure logic.
-hcarabali add preventive/corrective counts, ratio and
recurrence indicators from SAD section 10.2 using domain policies and counters.
"""

from __future__ import annotations

from collections import Counter

from fleetops_reports.application.ports.operational_clients import MaintenanceRecord
from fleetops_reports.domain.models.kpi import KPI
from fleetops_reports.domain.policies.mttr_policy import MTTRPolicy
from fleetops_reports.domain.value_objects.metric import Metric


class MaintenanceService:
    def __init__(self, policy: MTTRPolicy | None = None) -> None:
        self._policy = policy or MTTRPolicy()

    def calculate_mttr_kpi(self, records: list[MaintenanceRecord]) -> KPI:
        # Filtramos solo los registros que YA terminaron (finished_at NO es None)
        # Esto blinda el cálculo de MTTR contra errores de tipo en producción
        """Calcula el Tiempo Medio de Reparación (MTTR) en horas sobre los registros cerrados."""
        intervals = [
            (record.started_at, record.finished_at)
            for record in records
            if record.finished_at is not None
        ]

        # Si no hay órdenes cerradas, pasamos una lista vacía
        # y dejamos que la política maneje el caso base (0 horas)
        metric = self._policy.calculate_hours(intervals)
        return KPI.create_now(
            name="Mean Time To Repair", metric=metric, source="maintenance"
        )

    def calculate_preventive_count_kpi(self, records: list[MaintenanceRecord]) -> KPI:
        """Cuenta el total de mantenimientos de tipo PREVENTIVO registrados."""
        count = sum(1 for r in records if r.maintenance_type == "PREVENTIVO")
        metric = Metric(
            name="preventive_maintenance_count",
            value=float(count),
            unit="maintenances",
        )
        return KPI.create_now(
            name="Preventive Maintenance Count", metric=metric, source="maintenance"
        )

    def calculate_corrective_count_kpi(self, records: list[MaintenanceRecord]) -> KPI:
        """Cuenta el total de mantenimientos de tipo CORRECTIVO registrados."""
        count = sum(1 for r in records if r.maintenance_type == "CORRECTIVO")
        metric = Metric(
            name="corrective_maintenance_count",
            value=float(count),
            unit="maintenances",
        )
        return KPI.create_now(
            name="Corrective Maintenance Count", metric=metric, source="maintenance"
        )

    def calculate_preventive_ratio_kpi(self, records: list[MaintenanceRecord]) -> KPI:
        """Calcula el ratio preventivos/correctivos; retorna 0.0 si no hay correctivos."""
        preventivos = sum(1 for r in records if r.maintenance_type == "PREVENTIVO")
        correctivos = sum(1 for r in records if r.maintenance_type == "CORRECTIVO")
        ratio = 0.0 if correctivos == 0 else round(preventivos / correctivos, 2)
        metric = Metric(
            name="preventive_corrective_ratio",
            value=ratio,
            unit="ratio",
        )
        return KPI.create_now(
            name="Preventive to Corrective Ratio", metric=metric, source="maintenance"
        )

    def calculate_high_recurrence_vehicle_kpi(
        self,
        records: list[MaintenanceRecord],
        recurrence_threshold: int = 2,
    ) -> KPI:
        """Cuenta vehículos que superan el umbral de intervenciones de mantenimiento."""
        counts: Counter[str] = Counter(r.vehicle_id for r in records)
        high_recurrence_count = sum(
            1 for freq in counts.values() if freq >= recurrence_threshold
        )
        metric = Metric(
            name="high_recurrence_vehicle_count",
            value=float(high_recurrence_count),
            unit="vehicles",
        )
        return KPI.create_now(
            name="High Recurrence Vehicles", metric=metric, source="maintenance"
        )
