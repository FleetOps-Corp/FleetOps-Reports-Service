"""API integration fixtures."""

from __future__ import annotations

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fleetops_reports.application.dependencies import (
    get_download_report_use_case,
    get_generate_report_use_case,
    get_get_report_use_case,
    get_list_reports_use_case,
)
from fleetops_reports.application.services.availability_service import AvailabilityService
from fleetops_reports.application.services.incident_service import IncidentService
from fleetops_reports.application.services.maintenance_service import MaintenanceService
from fleetops_reports.application.services.report_service import ReportService
from fleetops_reports.application.use_cases.download_report import DownloadReportUseCase
from fleetops_reports.application.use_cases.generate_report import GenerateReportUseCase
from fleetops_reports.application.use_cases.get_report import GetReportUseCase
from fleetops_reports.application.use_cases.list_reports import ListReportsUseCase
from fleetops_reports.config.security import get_security_settings
from fleetops_reports.presentation.api.middleware import register_auth_middleware
from fleetops_reports.presentation.api.routes import reports
from tests.conftest import (
    FakeAssignmentsClient,
    FakeIncidentsClient,
    FakeMaintenanceClient,
    FakeVehiclesClient,
)


def _generate_test_rsa_keys(tmp_path: pytest.TempPathFactory) -> tuple[bytes, str]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    public_key_path = tmp_path / "jwt-public.pem"
    public_key_path.write_bytes(public_pem)
    return private_pem, str(public_key_path)


@pytest.fixture
def api_client(
    sample_vehicles,
    sample_assignments,
    sample_incidents,
    sample_maintenance,
    fake_repository,
    fake_storage,
    fake_renderer,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> TestClient:
    private_pem, public_key_path = _generate_test_rsa_keys(tmp_path)
    monkeypatch.setenv("JWT_ALGORITHM", "RS256")
    monkeypatch.setenv("JWT_PUBLIC_KEY_PATH", public_key_path)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    get_security_settings.cache_clear()

    app = FastAPI()
    register_auth_middleware(app)
    app.include_router(reports.router)

    report_service = ReportService(fake_repository, fake_storage, fake_renderer)
    use_case = GenerateReportUseCase(
        FakeVehiclesClient(sample_vehicles),
        FakeAssignmentsClient(sample_assignments),
        FakeIncidentsClient(sample_incidents),
        FakeMaintenanceClient(sample_maintenance),
        AvailabilityService(),
        IncidentService(),
        MaintenanceService(),
        report_service,
    )
    app.dependency_overrides[get_generate_report_use_case] = lambda: use_case
    app.dependency_overrides[get_list_reports_use_case] = lambda: ListReportsUseCase(
        fake_repository
    )
    app.dependency_overrides[get_get_report_use_case] = lambda: GetReportUseCase(
        fake_repository
    )
    app.dependency_overrides[get_download_report_use_case] = lambda: DownloadReportUseCase(
        fake_repository, fake_storage
    )

    client = TestClient(app)
    client.private_pem = private_pem
    client.use_case = use_case
    client.app = app
    return client
