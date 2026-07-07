"""SVG primitive and chart builder unit tests.

SAD Traceability: validates stdlib SVG helpers and builder fluency for SAD 10.5.
"""

from datetime import UTC, datetime

import pytest

from fleetops_reports.application.ports.operational_clients import (
    IncidentRecord,
    MaintenanceRecord,
)
from fleetops_reports.application.services.charts.availability_chart_builder import (
    AvailabilityChartBuilder,
)
from fleetops_reports.application.services.charts.empty_state_chart_builder import (
    EmptyStateChartBuilder,
)
from fleetops_reports.application.services.charts.svg_primitives import (
    render_grouped_bar_chart,
    render_horizontal_bar_chart,
    render_vertical_bar_chart,
)
from fleetops_reports.application.services.graph_service import GraphService


@pytest.fixture
def graph_service() -> GraphService:
    return GraphService()


def test_empty_state_chart_builder_renders_reason() -> None:
    svg = EmptyStateChartBuilder().with_reason(
        "Dataset 'vehicles' cannot be empty for this calculation"
    ).build()
    assert svg.startswith("<svg")
    assert "Sin datos disponibles:" in svg
    assert "vehicles" in svg


def test_chart_builder_fluent_methods(sample_vehicles) -> None:
    svg = (
        AvailabilityChartBuilder(sample_vehicles)
        .with_title("Custom Availability")
        .with_series([("ignored", 1.0)])
        .with_style(width=900, height=420)
        .build()
    )
    assert svg.startswith("<svg")
    assert "Custom Availability" in svg


def test_render_vertical_bar_chart_handles_empty_series() -> None:
    assert render_vertical_bar_chart(title="Empty", series=[]) == ""


def test_render_vertical_bar_chart_handles_zero_peak() -> None:
    svg = render_vertical_bar_chart(
        title="Zero Values",
        series=[("A", 0.0), ("B", 0.0)],
    )
    assert svg.startswith("<svg")


def test_render_horizontal_bar_chart_handles_empty_series() -> None:
    assert render_horizontal_bar_chart(title="Empty", series=[]) == ""


def test_render_horizontal_bar_chart_handles_zero_peak() -> None:
    svg = render_horizontal_bar_chart(
        title="Zero Values",
        series=[("Vehicle A", 0.0)],
    )
    assert svg.startswith("<svg")


def test_render_grouped_bar_chart_handles_empty_input() -> None:
    assert render_grouped_bar_chart(title="Empty", categories=[], groups=[]) == ""


def test_render_grouped_bar_chart_handles_zero_values() -> None:
    svg = render_grouped_bar_chart(
        title="Zero Groups",
        categories=["A"],
        groups=[("G1", [0.0], "#000"), ("G2", [0.0], "#111")],
    )
    assert svg.startswith("<svg")


def test_critical_ranking_skips_unknown_plates(
    sample_vehicles,
    sample_maintenance,
    graph_service,
) -> None:
    unknown_incident = IncidentRecord(
        incident_id="INC-UNKNOWN",
        id_conductor="11111111-1111-1111-1111-111111111111",
        placa_vehiculo="UNKNOWN-PLATE",
        tipo_incidente="MECANICO",
        severity="LEVE",
        occurred_at=datetime.now(UTC),
    )
    graph = graph_service.build_critical_ranking_chart(
        [unknown_incident],
        sample_maintenance,
        sample_vehicles,
    )
    assert graph.startswith(b"<svg")


def test_maintenance_chart_with_unrecognized_types(graph_service) -> None:
    finished_at = datetime.now(UTC)
    maintenance = [
        MaintenanceRecord(
            "8c12bda5-7482-4168-96ea-5fd3a9254c2a",
            "OTRO",
            finished_at,
            finished_at,
        )
    ]
    graph = graph_service.build_maintenance_chart(maintenance)
    assert graph.startswith(b"<svg")
