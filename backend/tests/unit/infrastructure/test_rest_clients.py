"""REST client tests aligned with FleetOps Security Gateway payloads."""

from __future__ import annotations

from datetime import UTC

import httpx
import pytest

from fleetops_reports.infrastructure.rest_clients.assignments_client import (
    RestAssignmentsClient,
)
from fleetops_reports.infrastructure.rest_clients.circuit_breaker import CircuitBreaker
from fleetops_reports.infrastructure.rest_clients.gateway_http import build_gateway_headers
from fleetops_reports.infrastructure.rest_clients.incidents_client import RestIncidentsClient
from fleetops_reports.infrastructure.rest_clients.maintenance_client import (
    RestMaintenanceClient,
)
from fleetops_reports.infrastructure.rest_clients.payload_parsing import extract_gateway_list
from fleetops_reports.infrastructure.rest_clients.vehicles_client import RestVehiclesClient


def test_build_gateway_headers_includes_bearer_token() -> None:
    headers = build_gateway_headers("admin-token")

    assert headers["Authorization"] == "Bearer admin-token"
    assert headers["Accept"] == "application/json"


def test_extract_gateway_list_accepts_raw_array() -> None:
    payload = [{"id": "1"}]

    assert extract_gateway_list(payload) == payload


def test_extract_gateway_list_accepts_wrapped_payload() -> None:
    payload = {"data": [{"id": "1"}, {"id": "2"}]}

    assert len(extract_gateway_list(payload)) == 2


def test_extract_gateway_list_rejects_invalid_payload() -> None:
    with pytest.raises(ValueError, match="JSON list payload"):
        extract_gateway_list({"status": "ok"})


@pytest.mark.asyncio
async def test_vehicles_client_maps_gateway_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = [
        {
            "id_vehiculo": "8c12bda5-7482-4168-96ea-5fd3a9254c2a",
            "numero_placa": "TYX-789",
            "estado_vehiculo": "DISPONIBLE",
            "ciudad_operacion": "Bogotá",
            "marca": "Kenworth",
            "modelo": "T800",
        }
    ]

    async def fake_fetch(url: str, bearer_token: str | None = None):
        assert url == "http://gateway:8000/vehiculos/"
        assert bearer_token == "admin-token"
        return payload

    monkeypatch.setattr(
        "fleetops_reports.infrastructure.rest_clients.vehicles_client.fetch_gateway_list",
        fake_fetch,
    )

    client = RestVehiclesClient(
        "http://gateway:8000",
        CircuitBreaker(failure_threshold=1, recovery_seconds=1),
        bearer_token="admin-token",
    )
    vehicles = await client.list_vehicles()

    assert len(vehicles) == 1
    assert vehicles[0].numero_placa == "TYX-789"
    assert vehicles[0].estado_vehiculo == "DISPONIBLE"


@pytest.mark.asyncio
async def test_assignments_client_maps_date_only_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = [
        {
            "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            "conductor_id": "11111111-1111-1111-1111-111111111111",
            "vehiculo_id": None,
            "tipo_vehiculo": "CAMION",
            "fecha_inicio": "2026-07-01",
            "fecha_fin": "2026-07-10",
        }
    ]

    async def fake_fetch(url: str, bearer_token: str | None = None):
        assert url == "http://gateway:8000/asignaciones/"
        return payload

    monkeypatch.setattr(
        "fleetops_reports.infrastructure.rest_clients.assignments_client.fetch_gateway_list",
        fake_fetch,
    )

    client = RestAssignmentsClient(
        "http://gateway:8000",
        CircuitBreaker(failure_threshold=1, recovery_seconds=1),
    )
    assignments = await client.list_assignments()

    assert assignments[0].vehicle_id is None
    assert assignments[0].start_date.tzinfo == UTC
    assert assignments[0].end_date is not None


@pytest.mark.asyncio
async def test_incidents_client_maps_gateway_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = [
        {
            "id": "INC-MEC-GRV-20260621-a3f9",
            "fecha_hora": "2026-06-21T22:00:00",
            "id_conductor": "CONDUCTOR-001",
            "placa_vehiculo": "ABC-123",
            "tipo_incidente": "MECANICO",
            "gravedad": "GRAVE",
        }
    ]

    async def fake_fetch(url: str, bearer_token: str | None = None):
        assert url == "http://gateway:8000/incidentes/"
        return payload

    monkeypatch.setattr(
        "fleetops_reports.infrastructure.rest_clients.incidents_client.fetch_gateway_list",
        fake_fetch,
    )

    client = RestIncidentsClient(
        "http://gateway:8000",
        CircuitBreaker(failure_threshold=1, recovery_seconds=1),
    )
    incidents = await client.list_incidents()

    assert incidents[0].severity == "GRAVE"
    assert incidents[0].tipo_incidente == "MECANICO"


@pytest.mark.asyncio
async def test_maintenance_client_uses_gateway_route_prefix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = [
        {
            "id_mantenimiento": "9e11fc4a-11bc-4e88-b223-38fa918bca44",
            "id_vehiculo": "8c12bda5-7482-4168-96ea-5fd3a9254c2a",
            "tipo_mantenimiento": 0,
            "fecha_inicio_mantenimiento": "2026-06-24T20:15:00Z",
            "fecha_fin_mantenimiento": "2026-06-25T02:00:00Z",
        }
    ]

    async def fake_fetch(url: str, bearer_token: str | None = None):
        assert url == "http://gateway:8000/mantenimiento/"
        return payload

    monkeypatch.setattr(
        "fleetops_reports.infrastructure.rest_clients.maintenance_client.fetch_gateway_list",
        fake_fetch,
    )

    client = RestMaintenanceClient(
        "http://gateway:8000",
        CircuitBreaker(failure_threshold=1, recovery_seconds=1),
    )
    maintenance = await client.list_maintenance()

    assert maintenance[0].maintenance_type == "CORRECTIVO"
    assert maintenance[0].finished_at is not None


@pytest.mark.asyncio
async def test_fetch_gateway_list_sends_authorization_header(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["authorization"] = request.headers.get("Authorization", "")
        return httpx.Response(200, json=[{"id": "1"}])

    transport = httpx.MockTransport(handler)
    real_async_client = httpx.AsyncClient

    def client_factory(*args, **kwargs):
        kwargs["transport"] = transport
        return real_async_client(*args, **kwargs)

    monkeypatch.setattr(
        "fleetops_reports.infrastructure.rest_clients.gateway_http.httpx.AsyncClient",
        client_factory,
    )

    from fleetops_reports.infrastructure.rest_clients.gateway_http import fetch_gateway_list

    result = await fetch_gateway_list("http://gateway:8000/vehiculos", "jwt-token")

    assert captured["authorization"] == "Bearer jwt-token"
    assert result == [{"id": "1"}]
