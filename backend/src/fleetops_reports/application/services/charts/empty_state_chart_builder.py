"""Empty-state placeholder chart builder.

SAD Traceability: visual placeholder for missing chart datasets in SAD section
10.5, keeping report layout stable when operational data is unavailable.
"""

from __future__ import annotations

from typing import Self

from fleetops_reports.application.services.charts.chart_builder import ChartBuilder
from fleetops_reports.application.services.charts.svg_primitives import (
    escape_text,
    svg_background,
    svg_label,
    svg_open,
)


class EmptyStateChartBuilder(ChartBuilder):
    def __init__(self) -> None:
        super().__init__()
        self._reason = ""

    def with_reason(self, reason: str) -> Self:
        self._reason = reason
        return self

    def build(self) -> str:
        width = int(self._style["width"])
        height = int(self._style["height"])
        background = str(self._style["background"])
        text_color = str(self._style["text_color"])
        message = f"Sin datos disponibles: {self._reason}"

        return (
            f"{svg_open(width, height)}"
            f"{svg_background(width, height, background)}"
            f"<rect x='40' y='40' width='{width - 80}' height='{height - 80}' "
            f"fill='#edf2f7' stroke='#cbd5e0' stroke-width='2' rx='8'/>"
            f"{svg_label(width // 2, height // 2 - 8, message, text_color, size=18)}"
            f"<text x='{width // 2}' y='{height // 2 + 20}' font-family='Arial' "
            f"font-size='13' fill='#718096' text-anchor='middle'>"
            f"{escape_text('FleetOps Reports')}</text>"
            f"</svg>"
        )
