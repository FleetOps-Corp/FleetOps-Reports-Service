"""Template service tests.

SAD Traceability: validates Template View context assembly for SAD process 10.6.
"""

from fleetops_reports.application.services.availability_service import AvailabilityService
from fleetops_reports.application.services.template_service import TemplateService
from fleetops_reports.domain.models.report import Report


def test_template_service_builds_context(report_period, sample_vehicles) -> None:
    kpi = AvailabilityService().calculate_global_kpi(sample_vehicles)
    report = Report("rep-001", "Executive Report", report_period, [kpi])
    context = TemplateService().build_context(report, "https://minio.test/graph.svg")
    assert context["report_id"] == "rep-001"
    assert len(context["kpis"]) == 1

