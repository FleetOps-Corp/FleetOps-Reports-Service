"""Application dependency providers.

SAD Traceability: FastAPI-compatible providers that resolve use cases and
ports without importing infrastructure from presentation.
"""

from __future__ import annotations

from collections.abc import Callable

from fleetops_reports.application.ports.metrics import MetricsExporter
from fleetops_reports.application.use_cases.download_report import DownloadReportUseCase
from fleetops_reports.application.use_cases.generate_report import GenerateReportUseCase
from fleetops_reports.application.use_cases.get_report import GetReportUseCase
from fleetops_reports.application.use_cases.list_reports import ListReportsUseCase

_generate_report_use_case_provider: Callable[[], GenerateReportUseCase] | None = None
_generate_fixture_report_use_case_provider: Callable[[], GenerateReportUseCase] | None = None
_list_reports_use_case_provider: Callable[[], ListReportsUseCase] | None = None
_get_report_use_case_provider: Callable[[], GetReportUseCase] | None = None
_download_report_use_case_provider: Callable[[], DownloadReportUseCase] | None = None
_metrics_exporter: MetricsExporter | None = None


def configure_generate_report_use_case(provider: Callable[[], GenerateReportUseCase]) -> None:
    global _generate_report_use_case_provider
    _generate_report_use_case_provider = provider


def configure_generate_fixture_report_use_case(
    provider: Callable[[], GenerateReportUseCase],
) -> None:
    global _generate_fixture_report_use_case_provider
    _generate_fixture_report_use_case_provider = provider


def configure_list_reports_use_case(provider: Callable[[], ListReportsUseCase]) -> None:
    global _list_reports_use_case_provider
    _list_reports_use_case_provider = provider


def configure_get_report_use_case(provider: Callable[[], GetReportUseCase]) -> None:
    global _get_report_use_case_provider
    _get_report_use_case_provider = provider


def configure_download_report_use_case(
    provider: Callable[[], DownloadReportUseCase],
) -> None:
    global _download_report_use_case_provider
    _download_report_use_case_provider = provider


def configure_metrics_exporter(exporter: MetricsExporter) -> None:
    global _metrics_exporter
    _metrics_exporter = exporter


def get_generate_report_use_case() -> GenerateReportUseCase:
    if _generate_report_use_case_provider is None:
        msg = (
            "Application wiring is not configured. "
            "Call composition.wiring.configure_application()."
        )
        raise RuntimeError(msg)
    return _generate_report_use_case_provider()


def get_generate_fixture_report_use_case() -> GenerateReportUseCase:
    if _generate_fixture_report_use_case_provider is None:
        msg = "Fixture report use case is not configured."
        raise RuntimeError(msg)
    return _generate_fixture_report_use_case_provider()


def get_list_reports_use_case() -> ListReportsUseCase:
    if _list_reports_use_case_provider is None:
        msg = "List reports use case is not configured."
        raise RuntimeError(msg)
    return _list_reports_use_case_provider()


def get_get_report_use_case() -> GetReportUseCase:
    if _get_report_use_case_provider is None:
        msg = "Get report use case is not configured."
        raise RuntimeError(msg)
    return _get_report_use_case_provider()


def get_download_report_use_case() -> DownloadReportUseCase:
    if _download_report_use_case_provider is None:
        msg = "Download report use case is not configured."
        raise RuntimeError(msg)
    return _download_report_use_case_provider()


def get_metrics_exporter() -> MetricsExporter:
    if _metrics_exporter is None:
        msg = "Metrics exporter is not configured. Call composition.wiring.configure_application()."
        raise RuntimeError(msg)
    return _metrics_exporter
