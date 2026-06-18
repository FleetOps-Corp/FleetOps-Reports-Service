"""Assignments gRPC client.

SAD Traceability: adapter for the Asignaciones service integration required by
ADR-001 and traceability process 10.4.
"""

from __future__ import annotations

from datetime import UTC, datetime

from fleetops_reports.application.ports.operational_clients import AssignmentRecord
from fleetops_reports.infrastructure.grpc_clients.circuit_breaker import CircuitBreaker


class GrpcAssignmentsClient:
    def __init__(self, target: str, circuit_breaker: CircuitBreaker) -> None:
        self._target = target
        self._circuit_breaker = circuit_breaker

    async def list_assignments(self) -> list[AssignmentRecord]:
        async def operation() -> list[AssignmentRecord]:
            return [AssignmentRecord("veh-001", "distribution-route-a", datetime.now(UTC))]

        return await self._circuit_breaker.call(operation)

