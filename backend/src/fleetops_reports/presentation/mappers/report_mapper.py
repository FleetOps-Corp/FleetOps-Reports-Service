"""Report mapper.

SAD Traceability: bidirectional DTO to Domain mapping for the executive report
flow in SAD section 10.6.
"""

from __future__ import annotations

from fleetops_reports.application.use_cases.generate_report import GenerateReportCommand
from fleetops_reports.domain.models.kpi import KPI
from fleetops_reports.domain.models.report import Report
from fleetops_reports.domain.value_objects.report_period import ReportPeriod
from fleetops_reports.presentation.schemas.report_schemas import (
    GenerateReportRequest,
    GenerateReportResponse,
    KPIResponse,
)


class ReportMapper:
    def request_to_command(self, request: GenerateReportRequest) -> GenerateReportCommand:
        return GenerateReportCommand(
            report_id=request.report_id,
            title=request.title,
            period=ReportPeriod(start_date=request.start_date, end_date=request.end_date),
        )

    def report_to_response(self, report: Report) -> GenerateReportResponse:
        return GenerateReportResponse(
            report_id=report.report_id,
            title=report.title,
            status=report.status,
            document_url=report.document_url,
            kpis=[self.kpi_to_response(kpi) for kpi in report.kpis],
        )

    def kpi_to_response(self, kpi: KPI) -> KPIResponse:
        return KPIResponse(
            name=kpi.name,
            value=kpi.metric.value,
            unit=kpi.metric.unit,
            source=kpi.source,
        )
