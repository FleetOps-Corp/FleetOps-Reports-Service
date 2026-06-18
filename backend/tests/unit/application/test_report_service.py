"""Report service tests.

SAD Traceability: validates report orchestration across graph, template, PDF,
storage and repository ports.
"""

import pytest

from fleetops_reports.application.services.availability_service import AvailabilityService
from fleetops_reports.application.services.report_service import ReportService
from fleetops_reports.domain.models.report import Report


@pytest.mark.asyncio
async def test_report_service_generates_report(
    report_period,
    sample_vehicles,
    fake_repository,
    fake_storage,
    fake_renderer,
) -> None:
    kpi = AvailabilityService().calculate_global_kpi(sample_vehicles)
    report = Report("rep-001", "Executive Report", report_period, [kpi])
    result = await ReportService(fake_repository, fake_storage, fake_renderer).generate(report)
    assert result.status == "generated"
    assert result.document_url == "rep-001.pdf"

