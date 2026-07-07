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


@pytest.mark.asyncio
async def test_report_service_generates_report(
    report_period,
    sample_vehicles,
    sample_incidents,
    sample_maintenance,
    fake_repository,
    fake_storage,
    fake_renderer,
) -> None:
    kpis = [
        AvailabilityService().calculate_global_kpi(sample_vehicles),
        MaintenanceService().calculate_mttr_kpi(sample_maintenance),
    ]
    report = Report("rep-001", "Executive Report", report_period, kpis)
    result = await ReportService(fake_repository, fake_storage, fake_renderer).generate(
        report,
        vehicles=sample_vehicles,
        incidents=sample_incidents,
        maintenance=sample_maintenance,
    )
    assert result.status == "generated"
    assert result.document_url == "rep-001.pdf"


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
