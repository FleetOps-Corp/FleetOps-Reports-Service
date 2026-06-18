"""Traceability service tests.

SAD Traceability: validates logical service for SAD process 10.4.
"""

from fleetops_reports.application.services.traceability_service import TraceabilityService


def test_traceability_service_builds_timeline(
    sample_assignments,
    sample_incidents,
    sample_maintenance,
) -> None:
    timeline = TraceabilityService().build_timeline(
        "veh-002",
        sample_assignments,
        sample_incidents,
        sample_maintenance,
    )
    assert timeline.vehicle_id == "veh-002"
    assert len(timeline.events) >= 1

