"""Operational gRPC ports.

SAD Traceability: contracts for Vehicles, Assignments, Incidents and
Maintenance service integrations from ADR-001 and deployment topology.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from fleetops_reports.domain.models.vehicle import Vehicle


@dataclass(frozen=True)
class AssignmentRecord:
    vehicle_id: str
    assignee: str
    started_at: datetime


@dataclass(frozen=True)
class IncidentRecord:
    vehicle_id: str
    severity: str
    occurred_at: datetime


@dataclass(frozen=True)
class MaintenanceRecord:
    vehicle_id: str
    maintenance_type: str
    started_at: datetime
    finished_at: datetime


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

