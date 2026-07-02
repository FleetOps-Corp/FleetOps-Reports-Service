"""Shared test fixtures.

SAD Traceability: provides functional fixtures for the analytical report flow
without calling real MongoDB, MinIO or gRPC services.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import pytest

from fleetops_reports.application.ports.operational_clients import (
    AssignmentRecord,
    IncidentRecord,
    MaintenanceRecord,
)
from fleetops_reports.domain.models.vehicle import Vehicle
from fleetops_reports.domain.value_objects.report_period import ReportPeriod


async def _async_value[T](value: T) -> T:
    return value


@pytest.fixture(autouse=True)
def test_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    values = {
        "APP_ENVIRONMENT": "test",
        "LOG_LEVEL": "INFO",
        "LOG_FILE_PATH": "",
        "MONGODB_URI": "mongodb://example.invalid:27017",
        "MONGODB_DATABASE": "fleetops_reports_test",
        "MINIO_ENDPOINT": "example.invalid:9000",
        "MINIO_ACCESS_KEY": "placeholder-access-key",
        "MINIO_SECRET_KEY": "placeholder-secret-key",
        "MINIO_SECURE": "false",
        "MINIO_REPORTS_BUCKET": "reports",
        "MINIO_GRAPHS_BUCKET": "graphs",
        "OPERATIONAL_GATEWAY_BASE_URL": "http://example.invalid:8080",
        "CIRCUIT_BREAKER_FAILURE_THRESHOLD": "3",
        "CIRCUIT_BREAKER_RECOVERY_SECONDS": "30",
    }
    for key, value in values.items():
        monkeypatch.setenv(key, value)


@pytest.fixture
def report_period() -> ReportPeriod:
    return ReportPeriod(start_date=date(2026, 5, 1), end_date=date(2026, 5, 31))


@pytest.fixture
def sample_vehicles() -> list[Vehicle]:
    return [
        Vehicle("veh-001", "FOP-001", "DISPONIBLE", "bogota", "van", "2024"),
        Vehicle("veh-002", "FOP-002", "MANTENIMIENTO", "medellin", "truck", "2023"),
        Vehicle("veh-003", "FOP-003", "DISPONIBLE", "cali", "van", "2024"),
    ]


@pytest.fixture
def sample_assignments() -> list[AssignmentRecord]:
    now = datetime.now(UTC)
    return [AssignmentRecord("asig-001", "veh-001", "cond-01", "van", now, None)]


@pytest.fixture
def sample_incidents() -> list[IncidentRecord]:
    now = datetime.now(UTC)
    return [
        IncidentRecord(
            incident_id="INC-20260601-001",
            id_conductor="cond-01",
            placa_vehiculo="FOP-002",
            tipo_incidente="MECANICO",   # era "CHOQUE"
            severity="GRAVE",            # era "critical"
            occurred_at=now,
        ),
        IncidentRecord(
            incident_id="INC-20260610-002",
            id_conductor="cond-01",
            placa_vehiculo="FOP-002",    # mismo vehículo → recurrente
            tipo_incidente="MECANICO",   # era "FALLA_MECANICA"
            severity="GRAVE",            # era "major"
            occurred_at=now,
        ),
    ]


@pytest.fixture
def sample_maintenance() -> list[MaintenanceRecord]:
    finished_at = datetime.now(UTC)
    return [
        MaintenanceRecord(
            "veh-002", "CORRECTIVO", finished_at - timedelta(hours=5), finished_at
        ),
        MaintenanceRecord(
            "veh-003", "PREVENTIVO", finished_at - timedelta(hours=2), finished_at
        ),
    ]


class FakeRepository:
    def __init__(self) -> None:
        self.saved = []

    async def save_report(self, report):
        self.saved.append(report)
        return await _async_value(report)

    async def get_report(self, report_id):
        return await _async_value(
            next((report for report in self.saved if report.report_id == report_id), None)
        )


class FakeStorage:
    async def upload_report_pdf(self, report_id: str, content: bytes) -> str:
        return await _async_value(f"{report_id}.pdf")

    async def upload_graph(self, graph_name: str, content: bytes) -> str:
        return await _async_value(graph_name)

    async def create_presigned_url(self, object_name: str, expires_seconds: int) -> str:
        return await _async_value(f"https://minio.test/{object_name}?expires={expires_seconds}")


class FakeRenderer:
    async def render(self, template_name: str, context: dict[str, object]) -> bytes:
        return await _async_value(f"PDF:{template_name}:{context['report_id']}".encode())


class FakeVehiclesClient:
    def __init__(self, vehicles) -> None:
        self._vehicles = vehicles

    async def list_vehicles(self):
        return await _async_value(self._vehicles)


class FakeAssignmentsClient:
    def __init__(self, assignments) -> None:
        self._assignments = assignments

    async def list_assignments(self):
        return await _async_value(self._assignments)


class FakeIncidentsClient:
    def __init__(self, incidents) -> None:
        self._incidents = incidents

    async def list_incidents(self):
        return await _async_value(self._incidents)


class FakeMaintenanceClient:
    def __init__(self, maintenance) -> None:
        self._maintenance = maintenance

    async def list_maintenance(self):
        return await _async_value(self._maintenance)


@pytest.fixture
def fake_repository() -> FakeRepository:
    return FakeRepository()


@pytest.fixture
def fake_storage() -> FakeStorage:
    return FakeStorage()


@pytest.fixture
def fake_renderer() -> FakeRenderer:
    return FakeRenderer()
