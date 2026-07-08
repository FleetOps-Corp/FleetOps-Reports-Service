"""Vehicles REST client.

SAD Traceability: adapter for the Vehículos service integration required by
ADR-001 and functional processes 10.1 and 10.4, via REST Gateway.
"""

from __future__ import annotations

from fleetops_reports.domain.models.vehicle import Vehicle
from fleetops_reports.infrastructure.rest_clients.circuit_breaker import CircuitBreaker
from fleetops_reports.infrastructure.rest_clients.field_mapping import get_payload_field
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
                    id_vehiculo=get_payload_field(item, "id_vehiculo", "idVehiculo"),
                    numero_placa=get_payload_field(item, "numero_placa", "numeroPlaca"),
                    estado_vehiculo=get_payload_field(
                        item, "estado_vehiculo", "estadoVehiculo"
                    ),
                    ciudad_operacion=get_payload_field(
                        item, "ciudad_operacion", "ciudadOperacion"
                    ),
                    sede_operacion=get_payload_field(
                        item, "sede_operacion", "sedeOperacion"
                    ),
                    marca=get_payload_field(item, "marca"),
                    modelo=get_payload_field(item, "modelo"),
                )
                for item in items
            ]

        return await self._circuit_breaker.call(operation)
