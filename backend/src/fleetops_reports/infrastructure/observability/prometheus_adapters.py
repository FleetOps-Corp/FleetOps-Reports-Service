"""Prometheus metrics adapters.

SAD Traceability: infrastructure implementations of application metrics ports.
"""

from __future__ import annotations

from contextlib import AbstractContextManager

from fleetops_reports.infrastructure.observability.metrics import (
    REPORT_GENERATION_SECONDS,
    REPORT_REQUESTS,
    render_metrics,
)


class PrometheusMetricsExporter:
    def render(self) -> tuple[bytes, str]:
        return render_metrics()


class PrometheusReportMetricsRecorder:
    def on_request(self) -> None:
        REPORT_REQUESTS.inc()

    def track_generation(self) -> AbstractContextManager[None]:
        return REPORT_GENERATION_SECONDS.time()
