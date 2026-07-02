"""Payload parsing helpers for FleetOps Security Gateway responses."""

from __future__ import annotations

from typing import Any

_LIST_KEYS = ("data", "results", "items", "content")


def extract_gateway_list(payload: Any) -> list[dict[str, Any]]:
    """Normalize list payloads returned directly or wrapped by upstream services."""
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    if isinstance(payload, dict):
        for key in _LIST_KEYS:
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]

    raise ValueError("Gateway response does not contain a JSON list payload")
