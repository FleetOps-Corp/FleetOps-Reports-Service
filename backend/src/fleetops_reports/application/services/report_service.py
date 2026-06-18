"""Report orchestration service.

SAD Traceability: coordinates Graph, Template, WeasyPrint, MinIO and MongoDB
for the executive report flow in SAD section 10.6.
"""

from __future__ import annotations

from typing import Protocol

from fleetops_reports.application.ports.analytics_repository import AnalyticsRepository
from fleetops_reports.application.ports.object_storage import ObjectStorage
from fleetops_reports.application.services.graph_service import GraphService
from fleetops_reports.application.services.template_service import TemplateService
from fleetops_reports.domain.models.report import Report


class PdfRenderer(Protocol):
    async def render(self, template_name: str, context: dict[str, object]) -> bytes:
        """Render report HTML into PDF bytes."""


class ReportService:
    def __init__(
        self,
        repository: AnalyticsRepository,
        storage: ObjectStorage,
        renderer: PdfRenderer,
        graph_service: GraphService | None = None,
        template_service: TemplateService | None = None,
    ) -> None:
        self._repository = repository
        self._storage = storage
        self._renderer = renderer
        self._graph_service = graph_service or GraphService()
        self._template_service = template_service or TemplateService()

    async def generate(self, report: Report) -> Report:
        graph_content = self._graph_service.build_kpi_graph(report.kpis)
        graph_object = await self._storage.upload_graph(f"{report.report_id}.svg", graph_content)
        graph_url = await self._storage.create_presigned_url(graph_object, expires_seconds=600)
        context = self._template_service.build_context(report, graph_url)
        pdf_content = await self._renderer.render("executive_report.html.j2", context)
        document_url = await self._storage.upload_report_pdf(report.report_id, pdf_content)
        report.mark_generated(document_url)
        return await self._repository.save_report(report)

