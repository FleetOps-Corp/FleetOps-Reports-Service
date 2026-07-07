"""Template service tests.

SAD Traceability: validates Template View context assembly for SAD process 10.6.
"""

from fleetops_reports.application.services.availability_service import AvailabilityService
from fleetops_reports.application.services.template_service import TemplateService
from fleetops_reports.domain.models.report import Report


def test_template_service_builds_context(report_period, sample_vehicles) -> None:
    """The template service should expose all data required by the Jinja template."""

    kpi = AvailabilityService().calculate_global_kpi(sample_vehicles)

    report = Report(
        report_id="rep-001",
        title="Executive Report",
        period=report_period,
        kpis=[kpi],
    )

    graph_urls = {
        "availability": "https://minio.test/rep-001-availability.svg",
        "incidents": "https://minio.test/rep-001-incidents.svg",
        "maintenance": "https://minio.test/rep-001-maintenance.svg",
        "mttr": "https://minio.test/rep-001-mttr.svg",
        "critical-ranking": "https://minio.test/rep-001-critical-ranking.svg",
        "kpi-summary": "https://minio.test/rep-001-kpi-summary.svg",
    }

    context = TemplateService().build_context(report, graph_urls)

    assert context["report_id"] == "rep-001"
    assert context["title"] == "Executive Report"
    assert context["period"] == report_period.label()
    assert context["status"] == "draft"
    assert context["graph_urls"] == graph_urls

    # New field used by the report header
    assert "created_at" in context
    assert isinstance(context["created_at"], str)

    assert len(context["kpis"]) == 1

    kpi_context = context["kpis"][0]

    assert kpi_context["name"] == kpi.name
    assert kpi_context["metric"] == kpi.metric.name
    assert kpi_context["value"] == kpi.metric.value
    assert kpi_context["unit"] == kpi.metric.unit
    assert kpi_context["source"] == kpi.source
