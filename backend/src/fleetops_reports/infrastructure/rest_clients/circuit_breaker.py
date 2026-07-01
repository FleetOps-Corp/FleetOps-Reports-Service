"""Circuit breaker for REST/HTTP calls.

SAD Traceability: implements ADR-005 to avoid cascading failures from
operational services by isolation of network-level transport exceptions.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import TypeVar

import httpx

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitBreakerState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerOpenError(RuntimeError):
    """Raised when the circuit is OPEN and proactively blocks traffic."""

    pass


class CircuitBreaker:
    def __init__(self, failure_threshold: int, recovery_seconds: int) -> None:
        self._failure_threshold = failure_threshold
        self._recovery_seconds = recovery_seconds
        self._failures = 0
        self._state = CircuitBreakerState.CLOSED
        self._opened_at: datetime | None = None

    async def call(self, operation: Callable[[], Awaitable[T]]) -> T:
        """Execute an async HTTP operation under circuit breaker protection."""
        self._check_state()

        if self._state == CircuitBreakerState.OPEN:
            raise CircuitBreakerOpenError(
                f"Circuit breaker is OPEN. Fast-failing request. "
                f"Time remaining: {self._get_remaining_recovery_time()}s"
            )

        try:
            result = await operation()
        except (
            httpx.ConnectError,
            httpx.TimeoutException,
            httpx.NetworkError,
            httpx.RemoteProtocolError,
        ) as transport_err:
            # ALINEACIÓN ADR-005: Only transport-level errors degrade the circuit.
            # HTTP 4xx/5xx are business errors and do NOT open the breaker.
            self._handle_failure()
            raise transport_err
        except Exception as app_err:
            # Mapping bugs or business errors pass through without penalizing
            # the external service's availability score.
            raise app_err
        else:
            self._handle_success()
            return result

    def _check_state(self) -> None:
        if self._state == CircuitBreakerState.OPEN and self._opened_at is not None:
            elapsed = datetime.now(UTC) - self._opened_at
            if elapsed >= timedelta(seconds=self._recovery_seconds):
                self._state = CircuitBreakerState.HALF_OPEN

    def _handle_failure(self) -> None:
        self._failures += 1
        if (
            self._state == CircuitBreakerState.HALF_OPEN
            or self._failures >= self._failure_threshold
        ):
            self._state = CircuitBreakerState.OPEN
            self._opened_at = datetime.now(UTC)
            logger.warning(f"Circuit breaker OPENED after {self._failures} failures")

    def _handle_success(self) -> None:
        self._failures = 0
        self._state = CircuitBreakerState.CLOSED
        self._opened_at = None
        logger.info("Circuit breaker CLOSED - service recovered")

    def _get_remaining_recovery_time(self) -> int:
        if self._opened_at is None:
            return 0
        elapsed = datetime.now(UTC) - self._opened_at
        remaining = self._recovery_seconds - elapsed.total_seconds()
        return max(0, int(remaining))

    @property
    def state(self) -> CircuitBreakerState:
        return self._state
