"""Get report use case."""

from __future__ import annotations

from fleetops_reports.application.ports.analytics_repository import AnalyticsRepository
from fleetops_reports.domain.exceptions import ReportNotFoundError
from fleetops_reports.domain.models.report import Report


class GetReportUseCase:
    def __init__(self, repository: AnalyticsRepository) -> None:
        self._repository = repository

    async def execute(self, report_id: str) -> Report:
        report = await self._repository.get_report(report_id)
        if report is None:
            raise ReportNotFoundError(report_id)
        return report
