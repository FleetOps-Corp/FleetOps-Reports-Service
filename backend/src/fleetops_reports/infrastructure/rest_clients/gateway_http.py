"""Shared HTTP helpers for FleetOps Security Gateway REST clients."""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import httpx

from fleetops_reports.infrastructure.rest_clients.gateway_token_provider import (
    GatewayBearerTokenProvider,
)
from fleetops_reports.infrastructure.rest_clients.payload_parsing import extract_gateway_list

logger = logging.getLogger(__name__)

_DEFAULT_PAGE_SIZE = 100
_UPSTREAM_UNAVAILABLE_STATUSES = frozenset({404, 405, 501})


def build_gateway_headers(bearer_token: str | None = None) -> dict[str, str]:
    headers = {"Accept": "application/json"}
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    return headers


def build_gateway_resource_url(base_url: str, resource_path: str) -> str:
    normalized = resource_path if resource_path.startswith("/") else f"/{resource_path}"
    if not normalized.endswith("/"):
        normalized = f"{normalized}/"
    return f"{base_url.rstrip('/')}{normalized}"


def _with_query_params(url: str, params: dict[str, str | int]) -> str:
    parsed = urlparse(url)
    existing = dict(parse_qsl(parsed.query, keep_blank_values=True))
    existing.update({key: str(value) for key, value in params.items()})
    query = urlencode(existing)
    return urlunparse(parsed._replace(query=query))


async def _resolve_bearer_token(
    bearer_token: str | None,
    token_provider: GatewayBearerTokenProvider | None,
) -> str | None:
    if token_provider is not None:
        return await token_provider.get_token()
    return bearer_token


async def fetch_gateway_json(
    url: str,
    bearer_token: str | None = None,
    *,
    token_provider: GatewayBearerTokenProvider | None = None,
    params: dict[str, str | int] | None = None,
) -> Any:
    resolved_token = await _resolve_bearer_token(bearer_token, token_provider)
    headers = build_gateway_headers(resolved_token)
    request_url = _with_query_params(url, params) if params else url
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        response = await client.get(request_url, headers=headers)
        response.raise_for_status()
        return response.json()


async def fetch_gateway_list(
    url: str,
    bearer_token: str | None = None,
    *,
    token_provider: GatewayBearerTokenProvider | None = None,
    params: dict[str, str | int] | None = None,
) -> list[dict[str, Any]]:
    payload = await fetch_gateway_json(
        url,
        bearer_token,
        token_provider=token_provider,
        params=params,
    )
    return extract_gateway_list(payload)


async def fetch_gateway_list_all_pages(
    url: str,
    bearer_token: str | None = None,
    *,
    token_provider: GatewayBearerTokenProvider | None = None,
    page_size: int = _DEFAULT_PAGE_SIZE,
) -> list[dict[str, Any]]:
    """Fetch list payloads, iterating Spring-style paginated responses when present."""
    first_payload = await fetch_gateway_json(
        url,
        bearer_token,
        token_provider=token_provider,
        params={"page": 0, "size": page_size},
    )

    if isinstance(first_payload, list):
        return [item for item in first_payload if isinstance(item, dict)]

    if not isinstance(first_payload, dict):
        return extract_gateway_list(first_payload)

    if "content" not in first_payload:
        return extract_gateway_list(first_payload)

    items = [item for item in first_payload.get("content", []) if isinstance(item, dict)]
    total_pages = int(first_payload.get("totalPages", 1) or 1)
    if total_pages <= 1:
        return items

    for page in range(1, total_pages):
        page_payload = await fetch_gateway_json(
            url,
            bearer_token,
            token_provider=token_provider,
            params={"page": page, "size": page_size},
        )
        if isinstance(page_payload, dict):
            page_items = page_payload.get("content", [])
            items.extend(item for item in page_items if isinstance(item, dict))

    return items


async def fetch_gateway_list_with_fallbacks(
    urls: list[str],
    bearer_token: str | None = None,
    *,
    token_provider: GatewayBearerTokenProvider | None = None,
    unavailable_log_message: str,
) -> list[dict[str, Any]]:
    """Try multiple gateway list URLs until one responds successfully."""
    last_error: Exception | None = None
    for index, url in enumerate(urls):
        try:
            return await fetch_gateway_list(
                url,
                bearer_token,
                token_provider=token_provider,
            )
        except httpx.HTTPStatusError as exc:
            last_error = exc
            if exc.response.status_code in _UPSTREAM_UNAVAILABLE_STATUSES:
                logger.warning(
                    "%s | status=%s | url=%s",
                    unavailable_log_message,
                    exc.response.status_code,
                    url,
                )
                continue
            raise
        except httpx.RequestError as exc:
            last_error = exc
            if index < len(urls) - 1:
                logger.warning(
                    "%s | request_error=%s | url=%s",
                    unavailable_log_message,
                    exc,
                    url,
                )
                continue
            raise

    if last_error is not None:
        raise last_error
    return []


async def fetch_gateway_list_all_pages_with_fallbacks(
    urls: list[str],
    bearer_token: str | None = None,
    *,
    token_provider: GatewayBearerTokenProvider | None = None,
    unavailable_log_message: str,
    page_size: int = _DEFAULT_PAGE_SIZE,
) -> list[dict[str, Any]]:
    """Paginated list fetch with route fallbacks for upstream prefix drift."""
    last_error: Exception | None = None
    for index, url in enumerate(urls):
        try:
            return await fetch_gateway_list_all_pages(
                url,
                bearer_token,
                token_provider=token_provider,
                page_size=page_size,
            )
        except httpx.HTTPStatusError as exc:
            last_error = exc
            if exc.response.status_code in _UPSTREAM_UNAVAILABLE_STATUSES:
                logger.warning(
                    "%s | status=%s | url=%s",
                    unavailable_log_message,
                    exc.response.status_code,
                    url,
                )
                continue
            raise
        except httpx.RequestError as exc:
            last_error = exc
            if index < len(urls) - 1:
                logger.warning(
                    "%s | request_error=%s | url=%s",
                    unavailable_log_message,
                    exc,
                    url,
                )
                continue
            raise

    if last_error is not None:
        raise last_error
    return []


async def fetch_gateway_list_optional(
    url: str,
    bearer_token: str | None = None,
    *,
    token_provider: GatewayBearerTokenProvider | None = None,
    unavailable_log_message: str,
) -> list[dict[str, Any]]:
    """Return an empty list when upstream list endpoints are missing or unsupported."""
    resolved_token = await _resolve_bearer_token(bearer_token, token_provider)
    headers = build_gateway_headers(resolved_token)
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        response = await client.get(url, headers=headers)

    if response.status_code in _UPSTREAM_UNAVAILABLE_STATUSES:
        logger.warning(
            "%s | status=%s | url=%s",
            unavailable_log_message,
            response.status_code,
            url,
        )
        return []

    response.raise_for_status()
    return extract_gateway_list(response.json())
