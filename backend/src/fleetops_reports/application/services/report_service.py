"""Report orchestration service.

SAD Traceability: coordinates Graph, Template, WeasyPrint, MinIO and MongoDB
for the executive report flow in SAD section 10.6.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Protocol

from fleetops_reports.application.ports.analytics_repository import AnalyticsRepository
from fleetops_reports.application.ports.object_storage import ObjectStorage
from fleetops_reports.application.ports.operational_clients import (
    IncidentRecord,
    MaintenanceRecord,
)
from fleetops_reports.application.services.graph_service import GraphService
from fleetops_reports.application.services.template_service import TemplateService
from fleetops_reports.domain.exceptions import EmptyDatasetError
from fleetops_reports.domain.models.report import Report
from fleetops_reports.domain.models.vehicle import Vehicle

logger = logging.getLogger(__name__)


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

    async def generate(
        self,
        report: Report,
        *,
        vehicles: list[Vehicle],
        incidents: list[IncidentRecord],
        maintenance: list[MaintenanceRecord],
    ) -> Report:
        graph_urls: dict[str, str] = {}

        chart_builders: list[tuple[str, Callable[[], bytes]]] = [
            (
                "availability",
                lambda: self._graph_service.build_availability_chart(vehicles),
            ),
            (
                "incidents",
                lambda: self._graph_service.build_incident_chart(incidents),
            ),
            (
                "maintenance",
                lambda: self._graph_service.build_maintenance_chart(maintenance),
            ),
            ("mttr", lambda: self._build_mttr_chart(report)),
            (
                "critical-ranking",
                lambda: self._graph_service.build_critical_ranking_chart(
                    incidents,
                    maintenance,
                    vehicles,
                ),
            ),
        ]

        for chart_key, build_chart in chart_builders:
            graph_content = self._build_chart_or_placeholder(chart_key, build_chart)
            object_name = f"{report.report_id}-{chart_key}.svg"
            graph_object = await self._storage.upload_graph(object_name, graph_content)
            graph_urls[chart_key] = await self._storage.create_presigned_url(
                graph_object, expires_seconds=600
            )

        # TODO: remove legacy kpi-summary chart once executive template no longer needs it.
        # TODO: handle empty report.kpis with empty-state placeholder instead of failing here.
        kpi_summary_content = self._graph_service.build_kpi_graph(report.kpis)
        kpi_summary_object = await self._storage.upload_graph(
            f"{report.report_id}-kpi-summary.svg",
            kpi_summary_content,
        )
        graph_urls["kpi-summary"] = await self._storage.create_presigned_url(
            kpi_summary_object, expires_seconds=600
        )

        context = self._template_service.build_context(report, graph_urls)
        pdf_content = await self._renderer.render("executive_report.html.j2", context)
        document_url = await self._storage.upload_report_pdf(report.report_id, pdf_content)
        report.mark_generated(document_url)
        return await self._repository.save_report(report)

    def _build_mttr_chart(self, report: Report) -> bytes:
        mttr_kpi = next((kpi for kpi in report.kpis if kpi.metric.name == "MTTR"), None)
        if mttr_kpi is None:
            raise EmptyDatasetError("mttr_kpi")
        return self._graph_service.build_mttr_chart(mttr_kpi)

    def _build_chart_or_placeholder(
        self,
        chart_key: str,
        build_chart: Callable[[], bytes],
    ) -> bytes:
        try:
            return build_chart()
        except EmptyDatasetError as exc:
            logger.warning(
                "Chart '%s' replaced with empty-state placeholder: %s",
                chart_key,
                exc,
            )
            return self._graph_service.build_empty_state_chart(reason=str(exc))
