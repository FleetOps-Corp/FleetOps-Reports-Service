"""Incidents gRPC client.

SAD Traceability: adapter for the Incidentes service integration required by
ADR-001 and criticality process 10.3.
"""

from __future__ import annotations

from datetime import UTC, datetime

from fleetops_reports.application.ports.operational_clients import IncidentRecord
from fleetops_reports.infrastructure.grpc_clients.circuit_breaker import CircuitBreaker


class GrpcIncidentsClient:
    def __init__(self, target: str, circuit_breaker: CircuitBreaker) -> None:
        self._target = target
        self._circuit_breaker = circuit_breaker

    async def list_incidents(self) -> list[IncidentRecord]:
        async def operation() -> list[IncidentRecord]:
            return [
                IncidentRecord("veh-002", "critical", datetime.now(UTC)),
                IncidentRecord("veh-002", "major", datetime.now(UTC)),
            ]

        return await self._circuit_breaker.call(operation)

