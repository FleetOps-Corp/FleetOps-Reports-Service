"""Report period value object tests.

SAD Traceability: validates report date boundaries for executive reporting.
"""

from datetime import date

import pytest

from fleetops_reports.domain.exceptions import InvalidReportPeriodError
from fleetops_reports.domain.value_objects.report_period import ReportPeriod


def test_report_period_label() -> None:
    period = ReportPeriod(date(2026, 5, 1), date(2026, 5, 31))
    assert period.label() == "2026-05-01 to 2026-05-31"


def test_report_period_rejects_inverted_dates() -> None:
    with pytest.raises(InvalidReportPeriodError):
        ReportPeriod(date(2026, 6, 1), date(2026, 5, 31))

