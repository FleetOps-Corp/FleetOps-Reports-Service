"""Download report PDF use case."""

from __future__ import annotations

from dataclasses import dataclass

from fleetops_reports.application.ports.analytics_repository import AnalyticsRepository
from fleetops_reports.application.ports.object_storage import ObjectStorage
from fleetops_reports.domain.exceptions import ReportNotFoundError


@dataclass(frozen=True)
class DownloadReportResult:
    report_id: str
    filename: str
    content: bytes
    content_type: str = "application/pdf"


class DownloadReportUseCase:
    def __init__(
        self,
        repository: AnalyticsRepository,
        storage: ObjectStorage,
    ) -> None:
        self._repository = repository
        self._storage = storage

    async def execute(self, report_id: str) -> DownloadReportResult:
        report = await self._repository.get_report(report_id)
        if report is None or not report.document_url:
            raise ReportNotFoundError(report_id)

        content = await self._storage.download_report_pdf(report.document_url)
        return DownloadReportResult(
            report_id=report.report_id,
            filename=report.document_url,
            content=content,
        )
