"""Application dependency providers.

SAD Traceability: FastAPI-compatible providers that resolve use cases and
ports without importing infrastructure from presentation.
"""

from __future__ import annotations

from collections.abc import Callable

from fleetops_reports.application.ports.metrics import MetricsExporter
from fleetops_reports.application.use_cases.generate_report import GenerateReportUseCase

_use_case_provider: Callable[[], GenerateReportUseCase] | None = None
_metrics_exporter: MetricsExporter | None = None


def configure_generate_report_use_case(provider: Callable[[], GenerateReportUseCase]) -> None:
    global _use_case_provider
    _use_case_provider = provider


def configure_metrics_exporter(exporter: MetricsExporter) -> None:
    global _metrics_exporter
    _metrics_exporter = exporter


def get_generate_report_use_case() -> GenerateReportUseCase:
    if _use_case_provider is None:
        msg = (
            "Application wiring is not configured. "
            "Call composition.wiring.configure_application()."
        )
        raise RuntimeError(msg)
    return _use_case_provider()


def get_metrics_exporter() -> MetricsExporter:
    if _metrics_exporter is None:
        msg = "Metrics exporter is not configured. Call composition.wiring.configure_application()."
        raise RuntimeError(msg)
    return _metrics_exporter
