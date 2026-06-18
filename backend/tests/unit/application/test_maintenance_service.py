"""Maintenance service tests.

SAD Traceability: validates logical service for SAD process 10.2.
"""

from fleetops_reports.application.services.maintenance_service import MaintenanceService


def test_maintenance_service_calculates_mttr(sample_maintenance) -> None:
    kpi = MaintenanceService().calculate_mttr_kpi(sample_maintenance)
    assert kpi.name == "Mean Time To Repair"
    assert kpi.metric.unit == "hours"

