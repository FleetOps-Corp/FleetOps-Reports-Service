"""Metrics ports.

SAD Traceability: observability abstractions for Prometheus metrics without
coupling application or presentation layers to infrastructure.
"""

from __future__ import annotations

from contextlib import AbstractContextManager, nullcontext
from typing import Protocol


class MetricsExporter(Protocol):
    def render(self) -> tuple[bytes, str]: ...


class ReportMetricsRecorder(Protocol):
    def on_request(self) -> None: ...

    def track_generation(self) -> AbstractContextManager[None]: ...


class NoOpReportMetricsRecorder:
    def on_request(self) -> None:
        return None

    def track_generation(self) -> AbstractContextManager[None]:
        return nullcontext()
