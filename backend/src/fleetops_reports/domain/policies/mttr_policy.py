"""MTTR policy.

SAD Traceability: implements the maintenance efficiency metric from section
10.2, including validation for invalid repair intervals.
"""

from __future__ import annotations

from datetime import datetime

from fleetops_reports.domain.exceptions import EmptyDatasetError, InvalidMetricError
from fleetops_reports.domain.value_objects.metric import Metric


class MTTRPolicy:
    def calculate_hours(self, repair_intervals: list[tuple[datetime, datetime]]) -> Metric:
        """Calculate Mean Time To Repair in hours from closed maintenance intervals."""
        if not repair_intervals:
            raise EmptyDatasetError("repair_intervals")

        total_hours = 0.0
        for started_at, finished_at in repair_intervals:
            if finished_at < started_at:
                raise InvalidMetricError("mttr", "finish time cannot precede start time")
            total_hours += (finished_at - started_at).total_seconds() / 3600

        return Metric(name="MTTR", value=total_hours / len(repair_intervals), unit="hours")

