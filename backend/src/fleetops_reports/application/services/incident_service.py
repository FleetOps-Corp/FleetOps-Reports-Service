"""Incident analytics logical service.

SAD Traceability: supports recurrence, severity and vehicle criticality
analysis from SAD section 10.3.
"""

from __future__ import annotations

from collections import Counter

from fleetops_reports.application.ports.operational_clients import (
    IncidentRecord,
    MaintenanceRecord,
)
from fleetops_reports.domain.models.kpi import KPI
from fleetops_reports.domain.models.vehicle import (
    Vehicle,
)  # Importación del modelo requerida
from fleetops_reports.domain.policies.criticality_policy import CriticalityPolicy
from fleetops_reports.domain.value_objects.metric import Metric


class IncidentService:
    def __init__(self, policy: CriticalityPolicy | None = None) -> None:
        self._policy = policy or CriticalityPolicy()

    def calculate_critical_vehicle_kpi(
        self,
        incidents: list[IncidentRecord],
        maintenance: list[MaintenanceRecord],
        vehicles: list[Vehicle],  # Recibe la lista para resolver la relación de red
    ) -> KPI:
        # 1. Creamos un mapa de indexación rápida: Placa -> vehicle_id
        placa_to_id = {
            v.numero_placa: v.id_vehiculo for v in vehicles if v.numero_placa
        }

        # 2. Contabilizamos incidentes traduciendo 'placa_vehiculo' a su 'vehicle_id' real
        incident_counts: Counter[str] = Counter()
        for record in incidents:
            v_id = placa_to_id.get(record.placa_vehiculo)
            if v_id:
                incident_counts[v_id] += 1

        # 3. Contabilizamos mantenimientos (este sí usa directamente vehicle_id en su registro)
        maintenance_counts = Counter(record.vehicle_id for record in maintenance)
        # 4. Consolidamos el universo total de IDs de vehículos afectados
        vehicle_ids = set(incident_counts) | set(maintenance_counts)
        # 5. Evaluamos la política de criticidad por cada ID unificado
        critical_count = sum(
            1
            for vehicle_id in vehicle_ids
            if self._policy.classify(
                incident_counts[vehicle_id], maintenance_counts[vehicle_id]
            )
            == "critical"
        )

        metric = Metric(
            name="critical_vehicle_count", value=float(critical_count), unit="vehicles"
        )
        return KPI.create_now(
            name="Critical Vehicles", metric=metric, source="incidents"
        )
