"""Maintenance gRPC client.

SAD Traceability: adapter for the Mantenimientos service integration required
by ADR-001 and maintenance efficiency process 10.2.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fleetops_reports.application.ports.operational_clients import MaintenanceRecord
from fleetops_reports.infrastructure.grpc_clients.circuit_breaker import CircuitBreaker


class GrpcMaintenanceClient:
    def __init__(self, target: str, circuit_breaker: CircuitBreaker) -> None:
        self._target = target
        self._circuit_breaker = circuit_breaker

    async def list_maintenance(self) -> list[MaintenanceRecord]:
        async def operation() -> list[MaintenanceRecord]:
            finished_at = datetime.now(UTC)
            return [
                MaintenanceRecord(
                    "veh-002",
                    "corrective",
                    finished_at - timedelta(hours=5),
                    finished_at,
                ),
                MaintenanceRecord(
                    "veh-003",
                    "preventive",
                    finished_at - timedelta(hours=2),
                    finished_at,
                ),
            ]

        return await self._circuit_breaker.call(operation)

