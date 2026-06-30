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
from fleetops_reports.domain.policies.criticality_policy import CriticalityPolicy
from fleetops_reports.domain.value_objects.metric import Metric


class IncidentService:
    def __init__(self, policy: CriticalityPolicy | None = None) -> None:
        self._policy = policy or CriticalityPolicy()

    # ------------------------------------------------------------------ #
    # KPI 1 — ya existente en la versión anterior, ahora usa placa_vehiculo como clave           #
    # ------------------------------------------------------------------ #
    def calculate_critical_vehicle_kpi(
        self,
        incidents: list[IncidentRecord],
        maintenance: list[MaintenanceRecord],
    ) -> KPI:
        """Cuenta vehículos cuya combinación incidentes+mantenimientos
        supera el umbral de criticidad definido en CriticalityPolicy.

        Usa placa_vehiculo como clave porque IncidentRecord no expone
        vehicle_id — la placa es el identificador estable del incidents-service.
        MaintenanceRecord sí usa vehicle_id, pero la correlación cruzada no
        es responsabilidad de este método; cada dominio cuenta por separado
        y la política evalúa los contadores individuales.
        """
        incident_counts: Counter[str] = Counter(
            record.placa_vehiculo for record in incidents
        )
        maintenance_counts: Counter[str] = Counter(
            record.vehicle_id for record in maintenance
        )

        # Universo: todas las placas con al menos un incidente
        critical_count = sum(
            1
            for placa in incident_counts
            if self._policy.classify(
                incident_counts[placa], maintenance_counts[placa]
            )
            == "critical"
        )

        metric = Metric(
            name="critical_vehicle_count",
            value=float(critical_count),
            unit="vehicles",
        )
        return KPI.create_now(
            name="Critical Vehicles", metric=metric, source="incidents"
        )

    # ------------------------------------------------------------------ #
    # KPI 2 — Tasa de incidentes graves - Permite identificar sí el el valor de la siniestralidad es leve o tiene una tendencia a eventos graves                              #
    # ------------------------------------------------------------------ #
    def calculate_high_severity_rate(
        self,
        incidents: list[IncidentRecord],
    ) -> KPI:
        """Porcentaje de incidentes clasificados como GRAVE sobre el total.

        Valor estratégico: permite al operador de flota identificar si la
        siniestralidad es mayoritariamente leve (operación normal) o si hay
        una tendencia de eventos graves que requiere intervención inmediata.
        Un valor > 40% es señal de alerta operativa según contexto FleetOps.
        """
        total = len(incidents)
        if total == 0:
            rate = 0.0
        else:
            grave_count = sum(
                1 for r in incidents if r.severity.upper() == "GRAVE"
            )
            rate = round((grave_count / total) * 100, 2)

        metric = Metric(
            name="high_severity_rate",
            value=rate,
            unit="percent",
        )
        return KPI.create_now(
            name="High Severity Rate", metric=metric, source="incidents"
        )

    # ------------------------------------------------------------------ #
    # KPI 3 — Tasa de incidentes humanos  - Identifica la raiz operativa para ambos casos Humano y mecánico.                                #
    # ------------------------------------------------------------------ #
    def calculate_human_incident_rate(
        self,
        incidents: list[IncidentRecord],
    ) -> KPI:
        """Porcentaje de incidentes de tipo HUMANO sobre el total.

        Valor estratégico: diferencia la causa raíz operativa. Una tasa alta
        de incidentes HUMANO apunta a necesidades de capacitación de
        conductores; una tasa alta de MECANICO apunta a mantenimiento
        preventivo insuficiente. Ambas señales tienen planes de acción
        distintos para FleetCorp S.A.
        """
        total = len(incidents)
        if total == 0:
            rate = 0.0
        else:
            human_count = sum(
                1 for r in incidents if r.tipo_incidente.upper() == "HUMANO"
            )
            rate = round((human_count / total) * 100, 2)

        metric = Metric(
            name="human_incident_rate",
            value=rate,
            unit="percent",
        )
        return KPI.create_now(
            name="Human Incident Rate", metric=metric, source="incidents"
        )

    # ------------------------------------------------------------------ #
    # KPI 4 — Vehículos con incidentes recurrentes  - Vehiculos con mayor frecuencia de incidentes.                      #
    # ------------------------------------------------------------------ #
    def calculate_recurrent_vehicle_kpi(
        self,
        incidents: list[IncidentRecord],
        recurrence_threshold: int = 2,
    ) -> KPI:
        """Cuenta vehículos que superan el umbral de recurrencia de incidentes.

        Valor estratégico: un vehículo con ≥2 incidentes en el período
        reportado es candidato a revisión técnica o retiro temporal de
        operación. Este KPI alimenta directamente el módulo de trazabilidad
        vehicular (SAD sección 10.4) y el ranking de vehículos de alto riesgo.
        El umbral es parametrizable para permitir configuración por período.
        """
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
            name="Recurrent Vehicles", metric=metric, source="incidents"
        )