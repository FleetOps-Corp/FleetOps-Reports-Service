"""Vehicle model tests.

SAD Traceability: verifies vehicle availability semantics from SAD section 10.1.
"""

from fleetops_reports.domain.models.vehicle import Vehicle


def test_vehicle_reports_operational_status() -> None:
    vehicle = Vehicle("veh-001", "FOP-001", "DISPONIBLE", "bogota", "van", "2024")
    assert vehicle.estado_vehiculo == "DISPONIBLE"


def test_vehicle_reports_non_operational_status() -> None:
    vehicle = Vehicle("veh-002", "FOP-002", "MANTENIMIENTO", "bogota", "van", "2023")
    assert vehicle.estado_vehiculo == "MANTENIMIENTO"
