"""Gateway bearer token provider tests."""

from __future__ import annotations

import httpx
import pytest

from fleetops_reports.domain.exceptions import OperationalGatewayAuthError
from fleetops_reports.infrastructure.rest_clients.gateway_token_provider import (
    GatewayBearerTokenProvider,
)


@pytest.mark.asyncio
async def test_static_token_is_returned_without_login() -> None:
    provider = GatewayBearerTokenProvider(
        "http://gateway:8000",
        static_token="static-jwt-token-value-12345",
    )

    assert await provider.get_token() == "static-jwt-token-value-12345"


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
async def test_empty_static_token_uses_service_login(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"access_token": "fresh-jwt", "expires_in": 3600})

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
        static_token="   ",
        service_email="admin@example.com",
        service_password="secret",
    )

    assert await provider.get_token() == "fresh-jwt"


@pytest.mark.asyncio
async def test_service_login_401_raises_operational_gateway_auth_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(401, json={"detail": "Invalid email or password."})
    )
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
        service_password="wrong",
    )

    with pytest.raises(OperationalGatewayAuthError):
        await provider.get_token()


@pytest.mark.asyncio
async def test_missing_credentials_returns_none() -> None:
    provider = GatewayBearerTokenProvider("http://gateway:8000")

    assert await provider.get_token() is None


@pytest.mark.asyncio
async def test_inbound_request_token_is_used_before_service_login(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from fleetops_reports.application.inbound_token_context import (
        reset_inbound_bearer_token,
        set_inbound_bearer_token,
    )

    def fail_login(request: httpx.Request) -> httpx.Response:
        raise AssertionError("service login must not run when inbound JWT is present")

    transport = httpx.MockTransport(fail_login)
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
    token = set_inbound_bearer_token("inbound-user-jwt-token-value")
    try:
        assert await provider.get_token() == "inbound-user-jwt-token-value"
    finally:
        reset_inbound_bearer_token(token)


@pytest.mark.asyncio
async def test_short_static_token_is_ignored_and_service_login_runs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"access_token": "fresh-jwt", "expires_in": 3600})

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
        static_token="-",
        service_email="admin@example.com",
        service_password="secret",
    )

    assert await provider.get_token() == "fresh-jwt"
