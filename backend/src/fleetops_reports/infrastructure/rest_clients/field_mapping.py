"""Field normalization helpers for upstream JSON payloads."""

from __future__ import annotations

from typing import Any


def get_payload_field(item: dict[str, Any], *keys: str, default: str = "") -> str:
    for key in keys:
        value = item.get(key)
        if value is not None:
            return str(value)
    return default
