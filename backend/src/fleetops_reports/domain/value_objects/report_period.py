"""ReportPeriod value object.

SAD Traceability: defines temporal boundaries for executive reporting and
historical metrics in SAD sections 10.2, 10.4 and 10.6.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from fleetops_reports.domain.exceptions import InvalidReportPeriodError


@dataclass(frozen=True)
class ReportPeriod:
    start_date: date
    end_date: date

    def __post_init__(self) -> None:
        if self.start_date > self.end_date:
            raise InvalidReportPeriodError(
                self.start_date.isoformat(),
                self.end_date.isoformat(),
            )

    def label(self) -> str:
        return f"{self.start_date.isoformat()} to {self.end_date.isoformat()}"

