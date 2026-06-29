"""Operational REST client ports.

SAD Traceability: contracts for Vehicles, Assignments, Incidents and
Maintenance service integrations via REST Gateway and deployment topology.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from fleetops_reports.domain.models.vehicle import Vehicle


@dataclass(frozen=True)
class AssignmentRecord:
    assignment_id: str  # id de la asignación (UUID string)
    vehicle_id: str | None  # Puede ser None si está pendiente en la SAGA
    conductor_id: str  # Relación con el operador (UUID string)
    tipo_vehiculo: str  # ej: 'CAMION'
    start_date: datetime  # Mapeo de fecha_inicio
    end_date: datetime | None  # Mapeo de fecha_fin (puede ser None si la asignación sigue activa)


@dataclass(frozen=True)
class IncidentRecord:
    incident_id: str  # Cambiado para alinearse al formato 'INC-YYYYMMDD-XXXX'
    id_conductor: str  # ID del conductor involucrado
    placa_vehiculo: str  # Placa normalizada (ej: 'ABC-123')
    tipo_incidente: str  # 'HUMANO' o 'MECANICO'
    severity: str  # 'LEVE' o 'GRAVE'
    occurred_at: datetime  # fecha_hora del incidente mapeada a datetime


@dataclass(frozen=True)
class MaintenanceRecord:
    vehicle_id: str  # id_vehiculo (UUID string)
    maintenance_type: (
        str  # Traducido de SMALLINT (0 -> 'CORRECTIVO', 1 -> 'PREVENTIVO')
    )
    started_at: datetime  # fecha_inicio_mantenimiento
    finished_at: (
        datetime | None
    )  # fecha_fin_mantenimiento (puede ser nulo si sigue en taller)


class VehiclesClient(Protocol):
    async def list_vehicles(self) -> list[Vehicle]:
        """Fetch vehicle inventory from the operational Vehicles service."""


class AssignmentsClient(Protocol):
    async def list_assignments(self) -> list[AssignmentRecord]:
        """Fetch assignment history from the operational Assignments service."""


class IncidentsClient(Protocol):
    async def list_incidents(self) -> list[IncidentRecord]:
        """Fetch incident history from the operational Incidents service."""


class MaintenanceClient(Protocol):
    async def list_maintenance(self) -> list[MaintenanceRecord]:
        """Fetch maintenance history from the operational Maintenance service."""
