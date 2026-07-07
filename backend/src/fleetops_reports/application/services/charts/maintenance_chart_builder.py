"""Maintenance type comparison bar chart builder.

SAD Traceability: preventive vs corrective maintenance counts from SAD section
10.2, rendered as a bar chart in SAD section 10.5.
"""

from __future__ import annotations

from collections import Counter

from fleetops_reports.application.ports.operational_clients import MaintenanceRecord
from fleetops_reports.application.services.charts.chart_builder import ChartBuilder
from fleetops_reports.application.services.charts.svg_primitives import render_vertical_bar_chart
from fleetops_reports.domain.exceptions import EmptyDatasetError


class MaintenanceChartBuilder(ChartBuilder):
    def __init__(self, maintenance: list[MaintenanceRecord]) -> None:
        super().__init__()
        self._maintenance = maintenance

    def build(self) -> str:
        if not self._maintenance:
            raise EmptyDatasetError("maintenance")

        counts = Counter(record.maintenance_type.upper() for record in self._maintenance)
        series = [
            ("Preventive", float(counts.get("PREVENTIVO", 0))),
            ("Corrective", float(counts.get("CORRECTIVO", 0))),
        ]

        title = self._title or "Preventive vs Corrective Maintenance"
        return render_vertical_bar_chart(
            title=title,
            series=series,
            width=int(self._style["width"]),
            height=int(self._style["height"]),
            background=str(self._style["background"]),
            bar_color=str(self._style["bar_color"]),
            text_color=str(self._style["text_color"]),
            axis_color=str(self._style["axis_color"]),
        )
