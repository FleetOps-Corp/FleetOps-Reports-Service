"""Timeline model tests.

SAD Traceability: verifies chronological vehicle traceability from SAD 10.4.
"""

from datetime import UTC, datetime

from fleetops_reports.domain.models.timeline import Timeline, TimelineEvent


def test_timeline_orders_events_chronologically() -> None:
    later = TimelineEvent(datetime(2026, 5, 2, tzinfo=UTC), "incident", "incidents", "major")
    earlier = TimelineEvent(datetime(2026, 5, 1, tzinfo=UTC), "assignment", "assignments", "route")
    timeline = Timeline("veh-001", (later, earlier))
    assert timeline.chronological_events() == (earlier, later)

