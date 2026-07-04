"""Shared HTTP helpers for FleetOps Security Gateway REST clients."""

from __future__ import annotations

import httpx

from fleetops_reports.infrastructure.rest_clients.payload_parsing import extract_gateway_list


def build_gateway_headers(bearer_token: str | None = None) -> dict[str, str]:
    headers = {"Accept": "application/json"}
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    return headers


async def fetch_gateway_list(url: str, bearer_token: str | None = None) -> list[dict]:
    headers = build_gateway_headers(bearer_token)
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return extract_gateway_list(response.json())
