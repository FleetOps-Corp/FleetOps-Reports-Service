"""Vehicles REST client.

SAD Traceability: adapter for the Vehículos service integration required by
ADR-001 and functional processes 10.1 and 10.4, via REST Gateway.
"""

from __future__ import annotations

from fleetops_reports.domain.models.vehicle import Vehicle
from fleetops_reports.infrastructure.rest_clients.circuit_breaker import CircuitBreaker
from fleetops_reports.infrastructure.rest_clients.gateway_http import fetch_gateway_list


class RestVehiclesClient:
    def __init__(
        self,
        gateway_base_url: str,
        circuit_breaker: CircuitBreaker,
        bearer_token: str | None = None,
    ) -> None:
        self._url = f"{gateway_base_url.rstrip('/')}/vehiculos/"
        self._circuit_breaker = circuit_breaker
        self._bearer_token = bearer_token

    async def list_vehicles(self) -> list[Vehicle]:
        async def operation() -> list[Vehicle]:
            items = await fetch_gateway_list(self._url, self._bearer_token)
            return [
                Vehicle(
                    id_vehiculo=item["id_vehiculo"],
                    numero_placa=item["numero_placa"],
                    estado_vehiculo=item["estado_vehiculo"],
                    ciudad_operacion=item["ciudad_operacion"],
                    marca=item["marca"],
                    modelo=item["modelo"],
                )
                for item in items
            ]

        return await self._circuit_breaker.call(operation)
