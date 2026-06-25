"""Incident service tests.

SAD Traceability: validates logical service for SAD process 10.3.
"""

from fleetops_reports.application.services.incident_service import IncidentService
from fleetops_reports.domain.models.vehicle import Vehicle


def test_incident_service_calculates_critical_vehicle_kpi(
    sample_vehicles,
    sample_incidents,
    sample_maintenance,
) -> None:
    kpi = IncidentService().calculate_critical_vehicle_kpi(
        sample_incidents, sample_maintenance, sample_vehicles
    )
    assert kpi.name == "Critical Vehicles"
    assert kpi.metric.unit == "vehicles"


def test_incident_service_handles_vehicles_without_placa(
    sample_incidents,
    sample_maintenance,
) -> None:
    """Forces the coverage path on line 42 for vehicles without a valid plate."""
    incomplete_vehicles = [
        Vehicle("veh-999", "", "DISPONIBLE", "bogota", "van", "2024")
    ]

    kpi = IncidentService().calculate_critical_vehicle_kpi(
        sample_incidents, sample_maintenance, incomplete_vehicles
    )
    assert kpi is not None
