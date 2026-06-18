"""Traceability logical service.

SAD Traceability: builds a unified timeline for vehicle history from Vehicles,
Assignments, Incidents and Maintenance data as described in SAD section 10.4.
"""

from __future__ import annotations

from fleetops_reports.application.ports.operational_clients import (
    AssignmentRecord,
    IncidentRecord,
    MaintenanceRecord,
)
from fleetops_reports.domain.models.timeline import Timeline, TimelineEvent


class TraceabilityService:
    def build_timeline(
        self,
        vehicle_id: str,
        assignments: list[AssignmentRecord],
        incidents: list[IncidentRecord],
        maintenance: list[MaintenanceRecord],
    ) -> Timeline:
        events: list[TimelineEvent] = []
        events.extend(
            TimelineEvent(record.started_at, "assignment", "assignments", record.assignee)
            for record in assignments
            if record.vehicle_id == vehicle_id
        )
        events.extend(
            TimelineEvent(record.occurred_at, "incident", "incidents", record.severity)
            for record in incidents
            if record.vehicle_id == vehicle_id
        )
        events.extend(
            TimelineEvent(record.finished_at, "maintenance", "maintenance", record.maintenance_type)
            for record in maintenance
            if record.vehicle_id == vehicle_id
        )
        timeline = Timeline(vehicle_id=vehicle_id, events=tuple(events))
        return Timeline(vehicle_id=vehicle_id, events=timeline.chronological_events())

