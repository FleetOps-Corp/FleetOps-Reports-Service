"""Critical vehicle ranking horizontal bar chart builder.

SAD Traceability: vehicle criticality ranking from SAD section 10.3, rendered
as a horizontal bar chart in SAD section 10.5.
"""

from __future__ import annotations

from collections import Counter

from fleetops_reports.application.ports.operational_clients import (
    IncidentRecord,
    MaintenanceRecord,
)
from fleetops_reports.application.services.charts.chart_builder import ChartBuilder
from fleetops_reports.application.services.charts.svg_primitives import render_horizontal_bar_chart
from fleetops_reports.domain.exceptions import EmptyDatasetError
from fleetops_reports.domain.models.vehicle import Vehicle
from fleetops_reports.domain.policies.criticality_policy import CriticalityPolicy


def _plate_to_vehicle_id(vehicles: list[Vehicle]) -> dict[str, str]:
    # TODO: duplicated from IncidentService plate-to-vehicle mapping; extract a
    # shared helper if more services need the same normalization.
    return {
        vehicle.numero_placa: vehicle.id_vehiculo
        for vehicle in vehicles
        if vehicle.numero_placa
    }


class CriticalRankingChartBuilder(ChartBuilder):
    def __init__(
        self,
        incidents: list[IncidentRecord],
        maintenance: list[MaintenanceRecord],
        vehicles: list[Vehicle],
        policy: CriticalityPolicy | None = None,
    ) -> None:
        super().__init__()
        self._incidents = incidents
        self._maintenance = maintenance
        self._vehicles = vehicles
        self._policy = policy or CriticalityPolicy()

    def build(self) -> str:
        if not self._vehicles:
            raise EmptyDatasetError("vehicles")

        plate_to_vehicle_id = _plate_to_vehicle_id(self._vehicles)

        incident_counts: Counter[str] = Counter()
        for record in self._incidents:
            vehicle_id = plate_to_vehicle_id.get(record.placa_vehiculo)
            if vehicle_id:
                incident_counts[vehicle_id] += 1

        maintenance_counts: Counter[str] = Counter(
            record.vehicle_id for record in self._maintenance
        )

        rankings: list[tuple[str, float, str]] = []
        for vehicle in self._vehicles:
            incident_count = incident_counts[vehicle.id_vehiculo]
            maintenance_count = maintenance_counts[vehicle.id_vehiculo]
            score = float(incident_count * 2 + maintenance_count)
            classification = self._policy.classify(incident_count, maintenance_count)
            label = f"{vehicle.numero_placa} ({classification})"
            rankings.append((label, score, classification))

        rankings.sort(key=lambda item: item[1], reverse=True)
        series = [(label, score) for label, score, _ in rankings]

        color_by_class = {
            "critical": "#e53e3e",
            "warning": "#dd6b20",
            "normal": "#3182ce",
        }
        top_classification = rankings[0][2] if rankings else "normal"
        bar_color = color_by_class.get(top_classification, "#3182ce")

        title = self._title or "Vehicle Criticality Ranking"
        return render_horizontal_bar_chart(
            title=title,
            series=series,
            width=int(self._style["width"]),
            height=max(int(self._style["height"]), 120 + len(series) * 28),
            background=str(self._style["background"]),
            bar_color=bar_color,
            text_color=str(self._style["text_color"]),
            axis_color=str(self._style["axis_color"]),
        )
