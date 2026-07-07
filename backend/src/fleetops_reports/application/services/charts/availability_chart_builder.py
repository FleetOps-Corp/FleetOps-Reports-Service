"""Availability bar chart builder.

SAD Traceability: availability by operation city from SAD section 10.1, rendered
as a bar chart in SAD section 10.5.
"""

from __future__ import annotations

from collections import defaultdict

from fleetops_reports.application.services.charts.chart_builder import ChartBuilder
from fleetops_reports.application.services.charts.svg_primitives import render_vertical_bar_chart
from fleetops_reports.domain.exceptions import EmptyDatasetError
from fleetops_reports.domain.models.vehicle import Vehicle


class AvailabilityChartBuilder(ChartBuilder):
    def __init__(self, vehicles: list[Vehicle]) -> None:
        super().__init__()
        self._vehicles = vehicles

    def build(self) -> str:
        if not self._vehicles:
            raise EmptyDatasetError("vehicles")

        by_location: dict[str, list[Vehicle]] = defaultdict(list)
        for vehicle in self._vehicles:
            location = vehicle.sede_operacion or vehicle.ciudad_operacion or "Unknown"
            by_location[location].append(vehicle)

        series: list[tuple[str, float]] = []
        for location in sorted(by_location):
            location_vehicles = by_location[location]
            available = sum(1 for vehicle in location_vehicles if vehicle.is_available)
            percentage = round((available / len(location_vehicles)) * 100, 2)
            series.append((location, percentage))

        title = self._title or "Availability by Operation Site"
        return render_vertical_bar_chart(
            title=title,
            series=series,
            width=int(self._style["width"]),
            height=int(self._style["height"]),
            background=str(self._style["background"]),
            bar_color=str(self._style["bar_color"]),
            text_color=str(self._style["text_color"]),
            axis_color=str(self._style["axis_color"]),
            value_suffix="%",
            max_value=100.0,
        )
