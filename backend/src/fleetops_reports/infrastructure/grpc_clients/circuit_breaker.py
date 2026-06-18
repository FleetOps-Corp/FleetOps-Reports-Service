"""Circuit breaker for gRPC calls.

SAD Traceability: implements ADR-005 to avoid cascading failures from
operational services.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from typing import TypeVar

T = TypeVar("T")


class CircuitBreakerOpenError(RuntimeError):
    pass


class CircuitBreaker:
    def __init__(self, failure_threshold: int, recovery_seconds: int) -> None:
        self._failure_threshold = failure_threshold
        self._recovery_seconds = recovery_seconds
        self._failures = 0
        self._opened_at: datetime | None = None

    async def call(self, operation: Callable[[], Awaitable[T]]) -> T:
        if self._opened_at is not None:
            elapsed = datetime.now(UTC) - self._opened_at
            if elapsed < timedelta(seconds=self._recovery_seconds):
                raise CircuitBreakerOpenError("circuit breaker is open")
            self._opened_at = None
            self._failures = 0

        try:
            result = await operation()
        except Exception:
            self._failures += 1
            if self._failures >= self._failure_threshold:
                self._opened_at = datetime.now(UTC)
            raise
        else:
            self._failures = 0
            return result

