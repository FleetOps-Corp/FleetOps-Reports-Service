"""Report service tests.

SAD Traceability: validates report orchestration across graph, template, PDF,
storage and repository ports.
"""

import logging

import pytest

from fleetops_reports.application.services.availability_service import AvailabilityService
from fleetops_reports.application.services.maintenance_service import MaintenanceService
from fleetops_reports.application.services.report_service import ReportService
from fleetops_reports.domain.models.report import Report


class _CapturingRenderer:
    def __init__(self) -> None:
        self.last_context: dict[str, object] | None = None

    async def render(self, template_name: str, context: dict[str, object]) -> bytes:
        self.last_context = context
        return f"PDF:{template_name}:{context['report_id']}".encode()


@pytest.mark.asyncio
async def test_report_service_generates_report(
    report_period,
    sample_vehicles,
    sample_incidents,
    sample_maintenance,
    fake_repository,
    fake_storage,
) -> None:
    renderer = _CapturingRenderer()
    kpis = [
        AvailabilityService().calculate_global_kpi(sample_vehicles),
        MaintenanceService().calculate_mttr_kpi(sample_maintenance),
    ]
    report = Report("rep-001", "Executive Report", report_period, kpis)
    result = await ReportService(fake_repository, fake_storage, renderer).generate(
        report,
        vehicles=sample_vehicles,
        incidents=sample_incidents,
        maintenance=sample_maintenance,
    )
    assert result.status == "generated"
    assert result.document_url == "rep-001.pdf"
    assert renderer.last_context is not None
    graph_urls = renderer.last_context["graph_urls"]
    assert set(graph_urls) == {
        "availability",
        "incidents",
        "maintenance",
        "mttr",
        "critical-ranking",
    }


@pytest.mark.asyncio
async def test_report_service_uploads_placeholder_when_chart_dataset_is_empty(
    report_period,
    sample_vehicles,
    sample_maintenance,
    fake_repository,
    fake_storage,
    fake_renderer,
    caplog,
) -> None:
    kpi = AvailabilityService().calculate_global_kpi(sample_vehicles)
    report = Report("rep-empty-chart", "Executive Report", report_period, [kpi])

    with caplog.at_level(logging.WARNING):
        result = await ReportService(fake_repository, fake_storage, fake_renderer).generate(
            report,
            vehicles=sample_vehicles,
            incidents=[],
            maintenance=sample_maintenance,
        )

    assert result.status == "generated"
    assert any(
        "replaced with empty-state placeholder" in record.message
        for record in caplog.records
    )
