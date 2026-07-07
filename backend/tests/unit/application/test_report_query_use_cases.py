"""Report query use case tests."""

import pytest

from fleetops_reports.application.use_cases.download_report import DownloadReportUseCase
from fleetops_reports.application.use_cases.get_report import GetReportUseCase
from fleetops_reports.application.use_cases.list_reports import ListReportsQuery, ListReportsUseCase
from fleetops_reports.domain.exceptions import ReportNotFoundError
from fleetops_reports.domain.models.report import Report
from tests.conftest import FakeStorage


@pytest.mark.asyncio
async def test_list_reports_use_case_returns_saved_reports(report_period, fake_repository) -> None:
    report = Report("rep-1", "Title", report_period, [], sede_operacion="Patio Norte Bogotá")
    await fake_repository.save_report(report)
    use_case = ListReportsUseCase(fake_repository)
    results = await use_case.execute(ListReportsQuery())
    assert len(results) == 1


@pytest.mark.asyncio
async def test_list_reports_use_case_filters_by_sede(report_period, fake_repository) -> None:
    await fake_repository.save_report(
        Report("rep-1", "A", report_period, [], sede_operacion="Patio Norte Bogotá")
    )
    await fake_repository.save_report(
        Report("rep-2", "B", report_period, [], sede_operacion="Patio Cali")
    )
    use_case = ListReportsUseCase(fake_repository)
    results = await use_case.execute(ListReportsQuery(sede_operacion="Patio Cali"))
    assert len(results) == 1
    assert results[0].report_id == "rep-2"


@pytest.mark.asyncio
async def test_get_report_use_case_returns_report(report_period, fake_repository) -> None:
    await fake_repository.save_report(Report("rep-1", "Title", report_period, []))
    use_case = GetReportUseCase(fake_repository)
    report = await use_case.execute("rep-1")
    assert report.report_id == "rep-1"


@pytest.mark.asyncio
async def test_get_report_use_case_raises_when_missing(fake_repository) -> None:
    use_case = GetReportUseCase(fake_repository)
    with pytest.raises(ReportNotFoundError):
        await use_case.execute("missing")


@pytest.mark.asyncio
async def test_download_report_use_case_raises_when_document_missing(
    report_period,
    fake_repository,
) -> None:
    await fake_repository.save_report(Report("rep-1", "Title", report_period, []))
    use_case = DownloadReportUseCase(fake_repository, FakeStorage())
    with pytest.raises(ReportNotFoundError):
        await use_case.execute("rep-1")


@pytest.mark.asyncio
async def test_download_report_use_case_returns_pdf(
    report_period,
    fake_repository,
    fake_storage,
) -> None:
    report = Report("rep-1", "Title", report_period, [])
    report.mark_generated("rep-1.pdf")
    await fake_repository.save_report(report)
    use_case = DownloadReportUseCase(fake_repository, fake_storage)
    result = await use_case.execute("rep-1")
    assert result.filename == "rep-1.pdf"
    assert result.content
