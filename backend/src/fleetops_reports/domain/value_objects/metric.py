"""Metric value object.

SAD Traceability: represents metrics/KPIs persisted in MongoDB and reported in
executive documents according to sections 6 and 10.
"""

from __future__ import annotations

from dataclasses import dataclass

from fleetops_reports.domain.exceptions import InvalidMetricError


@dataclass(frozen=True)
class Metric:
    name: str
    value: float
    unit: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvalidMetricError("unknown", "metric name is required", self.name)
        if self.value != self.value:
            raise InvalidMetricError(self.name, "metric value cannot be NaN", self.value)

