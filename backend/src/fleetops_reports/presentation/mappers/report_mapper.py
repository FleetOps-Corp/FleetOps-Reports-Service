"""Report mapper.

SAD Traceability: bidirectional DTO to Domain mapping for the executive report
flow in SAD section 10.6.
"""

from __future__ import annotations

from fleetops_reports.application.use_cases.generate_report import GenerateReportCommand
from fleetops_reports.application.use_cases.list_reports import ListReportsQuery
from fleetops_reports.domain.models.kpi import KPI
from fleetops_reports.domain.models.report import Report
from fleetops_reports.domain.value_objects.report_period import ReportPeriod
from fleetops_reports.presentation.schemas.report_schemas import (
    GenerateReportRequest,
    GenerateReportResponse,
    KPIResponse,
    ReportListResponse,
    ReportSummaryResponse,
)


class ReportMapper:
    def request_to_command(self, request: GenerateReportRequest) -> GenerateReportCommand:
        return GenerateReportCommand(
            report_id=request.report_id,
            title=request.title,
            period=ReportPeriod(start_date=request.start_date, end_date=request.end_date),
            sede_operacion=request.sede_operacion,
            ciudad_operacion=request.ciudad_operacion,
        )

    def list_query(
        self,
        sede_operacion: str | None,
        ciudad_operacion: str | None = None,
    ) -> ListReportsQuery:
        return ListReportsQuery(
            sede_operacion=sede_operacion,
            ciudad_operacion=ciudad_operacion,
        )

    def report_to_response(self, report: Report) -> GenerateReportResponse:
        return GenerateReportResponse(
            report_id=report.report_id,
            title=report.title,
            status=report.status,
            document_url=report.document_url,
            sede_operacion=report.sede_operacion,
            ciudad_operacion=report.ciudad_operacion,
            kpis=[self.kpi_to_response(kpi) for kpi in report.kpis],
        )

    def report_to_summary(self, report: Report) -> ReportSummaryResponse:
        return ReportSummaryResponse(
            report_id=report.report_id,
            title=report.title,
            status=report.status,
            document_url=report.document_url,
            sede_operacion=report.sede_operacion,
            ciudad_operacion=report.ciudad_operacion,
            start_date=report.period.start_date,
            end_date=report.period.end_date,
            created_at=report.created_at,
        )

    def reports_to_list_response(self, reports: list[Report]) -> ReportListResponse:
        summaries = [self.report_to_summary(report) for report in reports]
        return ReportListResponse(reports=summaries, total=len(summaries))

    def kpi_to_response(self, kpi: KPI) -> KPIResponse:
        return KPIResponse(
            name=kpi.name,
            value=kpi.metric.value,
            unit=kpi.metric.unit,
            source=kpi.source,
        )
