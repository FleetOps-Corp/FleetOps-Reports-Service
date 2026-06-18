"""Graph service tests.

SAD Traceability: validates Builder Pattern service for SAD process 10.5.
"""

from fleetops_reports.application.services.availability_service import AvailabilityService
from fleetops_reports.application.services.graph_service import GraphService


def test_graph_service_returns_svg_bytes(sample_vehicles) -> None:
    kpi = AvailabilityService().calculate_global_kpi(sample_vehicles)
    graph = GraphService().build_kpi_graph([kpi])
    assert graph.startswith(b"<svg")

