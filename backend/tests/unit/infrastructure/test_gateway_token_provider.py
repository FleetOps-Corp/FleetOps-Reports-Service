"""Gateway bearer token provider tests."""

from __future__ import annotations

import httpx
import pytest

from fleetops_reports.infrastructure.rest_clients.gateway_token_provider import (
    GatewayBearerTokenProvider,
)


@pytest.mark.asyncio
async def test_static_token_is_returned_without_login() -> None:
    provider = GatewayBearerTokenProvider(
        "http://gateway:8000",
        static_token="static-jwt",
    )

    assert await provider.get_token() == "static-jwt"


@pytest.mark.asyncio
async def test_service_login_refreshes_token(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/auth/login"
        return httpx.Response(
            200,
            json={"access_token": "fresh-jwt", "expires_in": 3600},
        )

    transport = httpx.MockTransport(handler)
    real_async_client = httpx.AsyncClient

    def client_factory(*args, **kwargs):
        kwargs["transport"] = transport
        return real_async_client(*args, **kwargs)

    monkeypatch.setattr(
        "fleetops_reports.infrastructure.rest_clients.gateway_token_provider.httpx.AsyncClient",
        client_factory,
    )

    provider = GatewayBearerTokenProvider(
        "http://gateway:8000",
        service_email="admin@example.com",
        service_password="secret",
    )

    assert await provider.get_token() == "fresh-jwt"


@pytest.mark.asyncio
async def test_missing_credentials_returns_none() -> None:
    provider = GatewayBearerTokenProvider("http://gateway:8000")

    assert await provider.get_token() is None
