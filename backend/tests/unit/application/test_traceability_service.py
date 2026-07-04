"""Traceability service tests.

SAD Traceability: validates logical service for SAD process 10.4.
"""

from datetime import UTC, datetime

from fleetops_reports.application.ports.operational_clients import MaintenanceRecord
from fleetops_reports.application.services.traceability_service import (
    TraceabilityService,
)

VEHICLE_FOP_002_ID = "9d23cea6-8593-5279-a7fb-6ge4b0365d3b"


def test_traceability_service_builds_timeline(
    sample_assignments,
    sample_incidents,
    sample_maintenance,
) -> None:
    timeline = TraceabilityService().build_timeline(
        VEHICLE_FOP_002_ID,
        "FOP-002",
        sample_assignments,
        sample_incidents,
        sample_maintenance,
    )
    assert timeline.vehicle_id == VEHICLE_FOP_002_ID
    assert len(timeline.events) >= 1


def test_traceability_service_marks_in_progress_maintenance(
    sample_assignments,
    sample_incidents,
) -> None:
    started_at = datetime(2026, 6, 24, 20, 15, tzinfo=UTC)
    active_maintenance = [
        MaintenanceRecord(
            VEHICLE_FOP_002_ID,
            "CORRECTIVO",
            started_at,
            None,
        )
    ]

    timeline = TraceabilityService().build_timeline(
        VEHICLE_FOP_002_ID,
        "FOP-002",
        sample_assignments,
        sample_incidents,
        active_maintenance,
    )

    maintenance_events = [
        event for event in timeline.events if event.event_type == "maintenance"
    ]
    assert len(maintenance_events) == 1
    assert maintenance_events[0].description == "CORRECTIVO (En Progreso)"
