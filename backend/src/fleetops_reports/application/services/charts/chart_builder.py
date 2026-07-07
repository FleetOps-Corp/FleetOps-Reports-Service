"""Chart builder contract.

SAD Traceability: Builder Pattern base for statistical visualizations in SAD section 10.5.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Self


class ChartBuilder(ABC):
    """Incremental SVG chart builder shared by all FleetOps graph types."""

    def __init__(self) -> None:
        self._title = ""
        self._series: list[tuple[str, float]] = []
        self._style: dict[str, str | int | float] = {
            "width": 800,
            "height": 400,
            "background": "#f7fafc",
            "bar_color": "#3182ce",
            "text_color": "#1a202c",
            "axis_color": "#cbd5e0",
        }

    def with_title(self, title: str) -> Self:
        self._title = title
        return self

    def with_series(self, series: list[tuple[str, float]]) -> Self:
        self._series = series
        return self

    def with_style(self, **kwargs: str | int | float) -> Self:
        self._style.update(kwargs)
        return self

    @abstractmethod
    def build(self) -> str:
        """Return a complete SVG document as a string."""
