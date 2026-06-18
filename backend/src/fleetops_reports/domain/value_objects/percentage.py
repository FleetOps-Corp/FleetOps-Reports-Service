"""Percentage value object.

SAD Traceability: supports availability and ratio indicators in SAD sections
10.1 and 10.2.
"""

from __future__ import annotations

from dataclasses import dataclass

from fleetops_reports.domain.exceptions import InvalidMetricError


@dataclass(frozen=True)
class Percentage:
    value: float

    def __post_init__(self) -> None:
        if self.value < 0 or self.value > 100:
            raise InvalidMetricError("percentage", "value must be between 0 and 100", self.value)

    def as_ratio(self) -> float:
        return self.value / 100

