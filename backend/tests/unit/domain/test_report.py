"""Report model tests.

SAD Traceability: validates executive report state transitions from SAD 10.6.
"""

import pytest

from fleetops_reports.domain.exceptions import ReportGenerationError
from fleetops_reports.domain.models.report import Report


def test_report_mark_generated_sets_status(report_period) -> None:
    report = Report("rep-001", "Executive Report", report_period, [])
    report.mark_generated("rep-001.pdf")
    assert report.status == "generated"
    assert report.document_url == "rep-001.pdf"


def test_report_mark_generated_requires_url(report_period) -> None:
    report = Report("rep-001", "Executive Report", report_period, [])
    with pytest.raises(ReportGenerationError):
        report.mark_generated("")

