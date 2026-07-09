"""Application dependency provider tests."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

import fleetops_reports.application.dependencies as deps
from fleetops_reports.application.ports.metrics import MetricsExporter
from fleetops_reports.application.use_cases.generate_report import GenerateReportUseCase


class _FakeMetricsExporter:
    def render(self) -> tuple[bytes, str]:
        return b"metrics", "text/plain"


class _FakeUseCase:
    pass


@pytest.fixture(autouse=True)
def reset_dependency_providers() -> Iterator[None]:
    deps._generate_report_use_case_provider = None
    deps._generate_fixture_report_use_case_provider = None
    deps._list_reports_use_case_provider = None
    deps._get_report_use_case_provider = None
    deps._download_report_use_case_provider = None
    deps._metrics_exporter = None
    yield
    deps._generate_report_use_case_provider = None
    deps._generate_fixture_report_use_case_provider = None
    deps._list_reports_use_case_provider = None
    deps._get_report_use_case_provider = None
    deps._download_report_use_case_provider = None
    deps._metrics_exporter = None


def test_get_generate_report_use_case_requires_configuration() -> None:
    with pytest.raises(RuntimeError, match="Application wiring is not configured"):
        deps.get_generate_report_use_case()


def test_configure_and_get_generate_report_use_case() -> None:
    fake_use_case = _FakeUseCase()
    deps.configure_generate_report_use_case(lambda: fake_use_case)  # type: ignore[arg-type]
    assert deps.get_generate_report_use_case() is fake_use_case


def test_get_generate_fixture_report_use_case_requires_configuration() -> None:
    with pytest.raises(RuntimeError, match="Fixture report use case is not configured"):
        deps.get_generate_fixture_report_use_case()


def test_configure_and_get_generate_fixture_report_use_case() -> None:
    fake_use_case = _FakeUseCase()
    deps.configure_generate_fixture_report_use_case(lambda: fake_use_case)  # type: ignore[arg-type]
    assert deps.get_generate_fixture_report_use_case() is fake_use_case


def test_get_list_reports_use_case_requires_configuration() -> None:
    with pytest.raises(RuntimeError, match="List reports use case is not configured"):
        deps.get_list_reports_use_case()


def test_configure_and_get_list_reports_use_case() -> None:
    fake_use_case = _FakeUseCase()
    deps.configure_list_reports_use_case(lambda: fake_use_case)  # type: ignore[arg-type]
    assert deps.get_list_reports_use_case() is fake_use_case


def test_get_get_report_use_case_requires_configuration() -> None:
    with pytest.raises(RuntimeError, match="Get report use case is not configured"):
        deps.get_get_report_use_case()


def test_configure_and_get_get_report_use_case() -> None:
    fake_use_case = _FakeUseCase()
    deps.configure_get_report_use_case(lambda: fake_use_case)  # type: ignore[arg-type]
    assert deps.get_get_report_use_case() is fake_use_case


def test_get_download_report_use_case_requires_configuration() -> None:
    with pytest.raises(RuntimeError, match="Download report use case is not configured"):
        deps.get_download_report_use_case()


def test_configure_and_get_download_report_use_case() -> None:
    fake_use_case = _FakeUseCase()
    deps.configure_download_report_use_case(lambda: fake_use_case)  # type: ignore[arg-type]
    assert deps.get_download_report_use_case() is fake_use_case


def test_get_metrics_exporter_requires_configuration() -> None:
    with pytest.raises(RuntimeError, match="Metrics exporter is not configured"):
        deps.get_metrics_exporter()


def test_configure_and_get_metrics_exporter() -> None:
    exporter: MetricsExporter = _FakeMetricsExporter()
    deps.configure_metrics_exporter(exporter)
    assert deps.get_metrics_exporter() is exporter


def test_use_case_provider_type() -> None:
    def provider() -> GenerateReportUseCase:
        raise NotImplementedError

    deps.configure_generate_report_use_case(provider)
    with pytest.raises(NotImplementedError):
        deps.get_generate_report_use_case()
