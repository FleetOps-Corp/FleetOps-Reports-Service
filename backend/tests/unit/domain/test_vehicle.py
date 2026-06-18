"""Vehicle model tests.

SAD Traceability: verifies vehicle availability semantics from SAD section 10.1.
"""

from fleetops_reports.domain.models.vehicle import Vehicle


def test_vehicle_reports_operational_status() -> None:
    vehicle = Vehicle("veh-001", "FOP-001", "operational", "bogota", "van")
    assert vehicle.is_operational() is True


def test_vehicle_reports_non_operational_status() -> None:
    vehicle = Vehicle("veh-002", "FOP-002", "maintenance", "bogota", "van")
    assert vehicle.is_operational() is False

