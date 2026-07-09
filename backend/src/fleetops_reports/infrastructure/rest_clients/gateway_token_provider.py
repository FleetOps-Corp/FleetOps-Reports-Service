"""Bearer token resolution for outbound Security Gateway calls."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any

import httpx

from fleetops_reports.domain.exceptions import OperationalGatewayAuthError

logger = logging.getLogger(__name__)

_DEFAULT_REFRESH_MARGIN_SECONDS = 300


@dataclass
class _CachedToken:
    value: str
    expires_at: float


class GatewayBearerTokenProvider:
    """Resolves JWT for upstream Gateway calls via static token or service login."""

    def __init__(
        self,
        gateway_base_url: str,
        *,
        static_token: str | None = None,
        service_email: str | None = None,
        service_password: str | None = None,
        refresh_margin_seconds: int = _DEFAULT_REFRESH_MARGIN_SECONDS,
    ) -> None:
        self._gateway_base_url = gateway_base_url.rstrip("/")
        self._static_token = static_token.strip() if static_token and static_token.strip() else None
        self._service_email = service_email
        self._service_password = service_password
        self._refresh_margin_seconds = refresh_margin_seconds
        self._cached: _CachedToken | None = None
        self._lock = asyncio.Lock()

    async def get_token(self) -> str | None:
        if self._static_token:
            return self._static_token

        if not self._service_email or not self._service_password:
            logger.warning(
                "No operational gateway token configured "
                "(set OPERATIONAL_GATEWAY_BEARER_TOKEN or service account credentials)"
            )
            return None

        async with self._lock:
            if self._cached and not self._is_expiring(self._cached):
                return self._cached.value

            token, expires_at = await self._login()
            self._cached = _CachedToken(value=token, expires_at=expires_at)
            return token

    def _is_expiring(self, cached: _CachedToken) -> bool:
        return time.time() >= cached.expires_at - self._refresh_margin_seconds

    async def _login(self) -> tuple[str, float]:
        login_url = f"{self._gateway_base_url}/auth/login"
        payload = {
            "email": self._service_email,
            "password": self._service_password,
        }
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            try:
                response = await client.post(login_url, json=payload)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 401:
                    raise OperationalGatewayAuthError(
                        "Service account login to Security Gateway /auth/login was rejected "
                        f"(email={self._service_email}). Ask Security to run seed_admin.py or "
                        "set OPERATIONAL_GATEWAY_BEARER_TOKEN with a valid ADMINISTRADOR JWT."
                    ) from exc
                raise OperationalGatewayAuthError(
                    f"Security Gateway /auth/login returned HTTP {exc.response.status_code}."
                ) from exc
            except httpx.RequestError as exc:
                raise OperationalGatewayAuthError(
                    f"Security Gateway /auth/login is unreachable: {exc}"
                ) from exc
            body: dict[str, Any] = response.json()

        token = str(body.get("access_token") or body.get("token") or "")
        if not token:
            raise ValueError("Security Gateway login response did not include access_token")

        expires_at = time.time() + float(body.get("expires_in", 3600))
        logger.info("Operational gateway service token refreshed via /auth/login")
        return token, expires_at
