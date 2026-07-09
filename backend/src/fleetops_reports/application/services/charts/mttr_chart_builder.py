"""MTTR bar chart builder.

SAD Traceability: Mean Time To Repair indicator from SAD section 10.2, rendered
as a bar chart in SAD section 10.5.

Note: a true temporal MTTR evolution chart would require persisted historical
snapshots or querying AnalyticsRepository; that is out of scope for this iteration.
"""

from __future__ import annotations

from fleetops_reports.application.services.charts.chart_builder import ChartBuilder
from fleetops_reports.application.services.charts.svg_primitives import render_vertical_bar_chart
from fleetops_reports.domain.exceptions import EmptyDatasetError
from fleetops_reports.domain.models.kpi import KPI


class MTTRChartBuilder(ChartBuilder):
    def __init__(self, mttr_kpi: KPI) -> None:
        super().__init__()
        self._mttr_kpi = mttr_kpi

    def build(self) -> str:
        if self._mttr_kpi.metric.name != "MTTR":
            raise EmptyDatasetError("mttr_kpi")

        title = self._title or "Mean Time To Repair (MTTR)"
        return render_vertical_bar_chart(
            title=title,
            series=[("Current MTTR", float(self._mttr_kpi.metric.value))],
            width=int(self._style["width"]),
            height=int(self._style["height"]),
            background=str(self._style["background"]),
            bar_color="#38a169",
            text_color=str(self._style["text_color"]),
            axis_color=str(self._style["axis_color"]),
            value_suffix=f" {self._mttr_kpi.metric.unit}",
        )
