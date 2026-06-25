"""Circuit breaker for gRPC calls.

SAD Traceability: implements ADR-005 to avoid cascading failures from
operational services by isolation of network-level RPC exceptions.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import TypeVar

import grpc  # <--- Crucial para interceptar fallos reales de infraestructura

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitBreakerState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerOpenError(RuntimeError):
    """Lanzada cuando el circuito está ABIERTO y bloquea el tráfico proactivamente."""

    pass


class CircuitBreaker:
    def __init__(self, failure_threshold: int, recovery_seconds: int) -> None:
        self._failure_threshold = failure_threshold
        self._recovery_seconds = recovery_seconds
        self._failures = 0
        self._state = CircuitBreakerState.CLOSED
        self._opened_at: datetime | None = None

    async def call(self, operation: Callable[[], Awaitable[T]]) -> T:
        """Ejecuta una operación gRPC asíncrona bajo la protección del breaker."""
        self._check_state()

        if self._state == CircuitBreakerState.OPEN:
            raise CircuitBreakerOpenError(
                f"Circuit breaker is OPEN. Fast-failing request. "
                f"Time remaining: {self._get_remaining_recovery_time()}s"
            )

        try:
            result = await operation()
        except grpc.RpcError as rpc_err:
            # 1. ALINEACIÓN ADR-005: Solo los errores de red/gRPC degradan el circuito
            self._handle_failure()
            raise rpc_err
        except Exception as app_err:
            # Errores de mapeo o bugs internos pasan derecho
            # sin penalizar la disponibilidad del servicio externo
            raise app_err
        else:
            # Si la petición es exitosa, restauramos el circuito por completo
            self._handle_success()
            return result

    def _check_state(self) -> None:
        """Evalúa si el circuito ha cumplido su tiempo de cuarentena para pasar a HALF_OPEN."""
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
            logger.warning(
                f"Circuit breaker OPENED after {self._failures} failures"
            )  # ← Add this

    def _handle_success(self) -> None:
        self._failures = 0
        self._state = CircuitBreakerState.CLOSED
        self._opened_at = None
        logger.info("Circuit breaker CLOSED - service recovered")  # ← Add this

    def _get_remaining_recovery_time(self) -> int:
        """Calcula los segundos restantes para que el circuito intente reabrirse."""
        if self._opened_at is None:
            return 0
        elapsed = datetime.now(UTC) - self._opened_at
        remaining = self._recovery_seconds - elapsed.total_seconds()
        return max(0, int(remaining))

    @property
    def state(self) -> CircuitBreakerState:
        """Permite monitorear el estado actual del componente desde logs o métricas."""
        return self._state
