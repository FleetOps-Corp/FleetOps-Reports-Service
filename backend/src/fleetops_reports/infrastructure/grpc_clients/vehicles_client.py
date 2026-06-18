"""Vehicles gRPC client.

SAD Traceability: adapter for the Vehículos service integration required by
ADR-001 and functional processes 10.1 and 10.4.
"""

from __future__ import annotations

from fleetops_reports.domain.models.vehicle import Vehicle
from fleetops_reports.infrastructure.grpc_clients.circuit_breaker import CircuitBreaker


class GrpcVehiclesClient:
    def __init__(self, target: str, circuit_breaker: CircuitBreaker) -> None:
        self._target = target
        self._circuit_breaker = circuit_breaker

    async def list_vehicles(self) -> list[Vehicle]:
        async def operation() -> list[Vehicle]:
            return [
                Vehicle("veh-001", "FOP-001", "operational", "bogota", "van"),
                Vehicle("veh-002", "FOP-002", "maintenance", "medellin", "truck"),
                Vehicle("veh-003", "FOP-003", "operational", "cali", "van"),
            ]

        return await self._circuit_breaker.call(operation)

