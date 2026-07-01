"""Datetime parsing helpers for REST client payloads."""

from __future__ import annotations

from datetime import UTC, datetime


def parse_utc_datetime(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)
