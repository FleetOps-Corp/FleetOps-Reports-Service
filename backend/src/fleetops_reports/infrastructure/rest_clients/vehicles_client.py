"""Vehicles REST client.

SAD Traceability: adapter for the Vehículos service integration required by
ADR-001 and functional processes 10.1 and 10.4, via REST Gateway.
"""

from __future__ import annotations

import httpx

from fleetops_reports.domain.models.vehicle import Vehicle
from fleetops_reports.infrastructure.rest_clients.circuit_breaker import CircuitBreaker


class RestVehiclesClient:
    def __init__(self, gateway_base_url: str, circuit_breaker: CircuitBreaker) -> None:
        self._url = f"{gateway_base_url}/vehiculos"
        self._circuit_breaker = circuit_breaker

    async def list_vehicles(self) -> list[Vehicle]:
        async def operation() -> list[Vehicle]:
            async with httpx.AsyncClient() as client:
                response = await client.get(self._url)
                response.raise_for_status()
                return [
                    Vehicle(
                        id_vehiculo=item["id_vehiculo"],
                        numero_placa=item["numero_placa"],
                        estado_vehiculo=item["estado_vehiculo"],
                        ciudad_operacion=item["ciudad_operacion"],
                        marca=item["marca"],
                        modelo=item["modelo"],
                    )
                    for item in response.json()
                ]

        return await self._circuit_breaker.call(operation)
