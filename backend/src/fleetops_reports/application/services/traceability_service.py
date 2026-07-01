"""Application traceability service.

SAD Traceability: orchestrates chronological timeline generation for vehicle
events across distributed bounded contexts.
"""

from __future__ import annotations

from datetime import UTC, datetime

from fleetops_reports.application.ports.operational_clients import (
    AssignmentRecord,
    IncidentRecord,
    MaintenanceRecord,
)
from fleetops_reports.domain.models.timeline import Timeline, TimelineEvent


class TraceabilityService:
    def build_timeline(
        self,
        vehicle_id: str,  # Este ID representa el id_vehiculo inmutable
        numero_placa: str,  # ¡Agregamos la placa! Es necesaria para cruzar con incidentes
        assignments: list[AssignmentRecord],
        incidents: list[IncidentRecord],
        maintenance: list[MaintenanceRecord],
    ) -> Timeline:
        events: list[TimelineEvent] = []

        # 1. Procesamiento de Asignaciones (Argumentos posicionales sin keywords)
        events.extend(
            TimelineEvent(
                record.start_date, "assignment", "assignments", record.conductor_id
            )
            for record in assignments
            if record.vehicle_id == vehicle_id
        )

        # 2. Procesamiento de Incidentes (Argumentos posicionales y filtrado por placa)
        events.extend(
            TimelineEvent(record.occurred_at, "incident", "incidents", record.severity)
            for record in incidents
            if record.placa_vehiculo == numero_placa
        )

        # 3. Procesamiento de Mantenimientos
        # (Manejo del opcional datetime | None y .append posicional)
        for record in maintenance:
            if record.vehicle_id == vehicle_id:
                # CORRECCIÓN: Si finished_at es None (mantenimiento activo), usamos la hora actual
                event_date = (
                    record.finished_at
                    if record.finished_at is not None
                    else datetime.now(UTC)
                )

                # Modificación semántica de la descripción si sigue en el taller
                maint_detail = (
                    f"{record.maintenance_type} (En Progreso)"
                    if record.finished_at is None
                    else record.maintenance_type
                )

                events.append(
                    TimelineEvent(
                        event_date, "maintenance", "maintenance", maint_detail
                    )
                )

        timeline = Timeline(vehicle_id=vehicle_id, events=tuple(events))
        return Timeline(vehicle_id=vehicle_id, events=timeline.chronological_events())
