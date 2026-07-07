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
    }

    context = TemplateService().build_context(report, graph_urls, vehicles=sample_vehicles)

    assert context["report_id"] == "rep-001"
    assert context["title"] == "Executive Report"
    assert context["period"] == report_period.label()
    assert context["status"] == "draft"
    assert context["graph_urls"] == graph_urls
    assert len(context["vehicles"]) == len(sample_vehicles)
    assert context["vehicles"][0]["status"] == "DISPONIBLE"

    # New field used by the report header
    assert "created_at" in context
    assert isinstance(context["created_at"], str)

    assert len(context["kpis"]) == 1

    kpi_context = context["kpis"][0]

    assert kpi_context["name"] == kpi.name
    assert kpi_context["description"] == "Share of fleet units that are operational and ready for dispatch."
    assert kpi_context["value"] == kpi.metric.value
    assert kpi_context["unit"] == kpi.metric.unit
    assert kpi_context["source"] == kpi.source


def test_template_service_sorts_available_vehicles_first(report_period) -> None:
    from fleetops_reports.domain.models.vehicle import Vehicle

    vehicles = [
        Vehicle("1", "FOP-003", "EN_MANTENIMIENTO", "Bogotá", "A", "M1", "Sede"),
        Vehicle("2", "FOP-001", "DISPONIBLE", "Bogotá", "B", "M2", "Sede"),
        Vehicle("3", "FOP-002", "FUERA_DE_SERVICIO", "Bogotá", "C", "M3", "Sede"),
    ]
    report = Report("rep-sort", "Sort Test", report_period, kpis=[])
    rows = TemplateService().build_context(report, {}, vehicles=vehicles)["vehicles"]
    assert [row["plate"] for row in rows] == ["FOP-001", "FOP-003", "FOP-002"]
