"""Incident service tests.

SAD Traceability: validates logical service for SAD process 10.3.
"""

from fleetops_reports.application.services.incident_service import IncidentService


def test_incident_service_calculates_critical_vehicle_kpi(
    sample_incidents,
    sample_maintenance,
) -> None:
    kpi = IncidentService().calculate_critical_vehicle_kpi(sample_incidents, sample_maintenance)
    assert kpi.name == "Critical Vehicles"
    assert kpi.metric.unit == "vehicles"

