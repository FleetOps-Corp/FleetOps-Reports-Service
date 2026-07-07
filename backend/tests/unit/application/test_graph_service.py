"""Graph service tests.

SAD Traceability: validates Builder Pattern service for SAD process 10.5.
"""

import pytest

from fleetops_reports.application.services.availability_service import AvailabilityService
from fleetops_reports.application.services.graph_service import GraphService
from fleetops_reports.application.services.maintenance_service import MaintenanceService
from fleetops_reports.domain.exceptions import EmptyDatasetError
from fleetops_reports.domain.models.kpi import KPI
from fleetops_reports.domain.value_objects.metric import Metric


@pytest.fixture
def graph_service() -> GraphService:
    return GraphService()


@pytest.fixture
def mttr_kpi(sample_maintenance) -> KPI:
    return MaintenanceService().calculate_mttr_kpi(sample_maintenance)


def test_build_kpi_graph_returns_svg_bytes(sample_vehicles, graph_service) -> None:
    kpi = AvailabilityService().calculate_global_kpi(sample_vehicles)
    graph = graph_service.build_kpi_graph([kpi])
    assert graph.startswith(b"<svg")


def test_build_availability_chart_returns_svg_bytes(
    sample_vehicles, graph_service
) -> None:
    graph = graph_service.build_availability_chart(sample_vehicles)
    assert graph.startswith(b"<svg")
    assert b"Bogot" in graph or b"Bogota" in graph


def test_build_availability_chart_raises_on_empty_dataset(graph_service) -> None:
    with pytest.raises(EmptyDatasetError) as exc_info:
        graph_service.build_availability_chart([])
    assert exc_info.value.details["dataset_name"] == "vehicles"


def test_build_incident_chart_returns_svg_bytes(sample_incidents, graph_service) -> None:
    graph = graph_service.build_incident_chart(sample_incidents)
    assert graph.startswith(b"<svg")
    assert b"GRAVE" in graph


def test_build_incident_chart_raises_on_empty_dataset(graph_service) -> None:
    with pytest.raises(EmptyDatasetError) as exc_info:
        graph_service.build_incident_chart([])
    assert exc_info.value.details["dataset_name"] == "incidents"


def test_build_maintenance_chart_returns_svg_bytes(
    sample_maintenance, graph_service
) -> None:
    graph = graph_service.build_maintenance_chart(sample_maintenance)
    assert graph.startswith(b"<svg")
    assert b"Preventive" in graph
    assert b"Corrective" in graph


def test_build_maintenance_chart_raises_on_empty_dataset(graph_service) -> None:
    with pytest.raises(EmptyDatasetError) as exc_info:
        graph_service.build_maintenance_chart([])
    assert exc_info.value.details["dataset_name"] == "maintenance"


def test_build_mttr_chart_returns_svg_bytes(mttr_kpi, graph_service) -> None:
    graph = graph_service.build_mttr_chart(mttr_kpi)
    assert graph.startswith(b"<svg")
    assert b"MTTR" in graph or b"3.5" in graph


def test_build_mttr_chart_raises_on_empty_dataset(graph_service) -> None:
    invalid_kpi = KPI.create_now(
        name="Not MTTR",
        metric=Metric(name="fleet_availability", value=95.0, unit="percent"),
        source="vehicles",
    )
    with pytest.raises(EmptyDatasetError) as exc_info:
        graph_service.build_mttr_chart(invalid_kpi)
    assert exc_info.value.details["dataset_name"] == "mttr_kpi"


def test_build_critical_ranking_chart_returns_svg_bytes(
    sample_vehicles,
    sample_incidents,
    sample_maintenance,
    graph_service,
) -> None:
    graph = graph_service.build_critical_ranking_chart(
        sample_incidents,
        sample_maintenance,
        sample_vehicles,
    )
    assert graph.startswith(b"<svg")
    assert b"FOP-002" in graph


def test_build_critical_ranking_chart_raises_on_empty_dataset(
    sample_incidents,
    sample_maintenance,
    graph_service,
) -> None:
    with pytest.raises(EmptyDatasetError) as exc_info:
        graph_service.build_critical_ranking_chart(
            sample_incidents,
            sample_maintenance,
            [],
        )
    assert exc_info.value.details["dataset_name"] == "vehicles"
