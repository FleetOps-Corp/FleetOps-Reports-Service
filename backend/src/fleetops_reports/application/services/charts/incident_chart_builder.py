"""Incident distribution bar chart builder.

SAD Traceability: incident severity and type breakdown from SAD section 10.3,
rendered as a grouped bar chart in SAD section 10.5.
"""

from __future__ import annotations

from collections import Counter

from fleetops_reports.application.ports.operational_clients import IncidentRecord
from fleetops_reports.application.services.charts.chart_builder import ChartBuilder
from fleetops_reports.application.services.charts.svg_primitives import render_grouped_bar_chart
from fleetops_reports.domain.exceptions import EmptyDatasetError


class IncidentChartBuilder(ChartBuilder):
    def __init__(self, incidents: list[IncidentRecord]) -> None:
        super().__init__()
        self._incidents = incidents

    def build(self) -> str:
        if not self._incidents:
            raise EmptyDatasetError("incidents")

        severity_counts: Counter[str] = Counter(
            record.severity.upper() for record in self._incidents
        )
        type_counts: Counter[str] = Counter(
            record.tipo_incidente.upper() for record in self._incidents
        )

        categories = sorted(set(severity_counts) | set(type_counts))
        severity_values = [float(severity_counts.get(category, 0)) for category in categories]
        type_values = [float(type_counts.get(category, 0)) for category in categories]

        title = self._title or "Incident Distribution by Severity and Type"
        return render_grouped_bar_chart(
            title=title,
            categories=categories,
            groups=[
                ("Severity", severity_values, "#e53e3e"),
                ("Type", type_values, "#3182ce"),
            ],
            width=int(self._style["width"]),
            height=int(self._style["height"]),
            background=str(self._style["background"]),
            text_color=str(self._style["text_color"]),
            axis_color=str(self._style["axis_color"]),
        )
