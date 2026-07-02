"""Incidents REST client.

SAD Traceability: adapter for the Incidentes service integration required by
ADR-001 and functional processes 10.1 and 10.4, via REST Gateway.
"""

from __future__ import annotations

from fleetops_reports.application.ports.operational_clients import IncidentRecord
from fleetops_reports.infrastructure.rest_clients.circuit_breaker import CircuitBreaker
from fleetops_reports.infrastructure.rest_clients.datetime_parsing import (
    parse_operational_datetime,
)
from fleetops_reports.infrastructure.rest_clients.gateway_http import fetch_gateway_list


class RestIncidentsClient:
    def __init__(
        self,
        gateway_base_url: str,
        circuit_breaker: CircuitBreaker,
        bearer_token: str | None = None,
    ) -> None:
        self._url = f"{gateway_base_url.rstrip('/')}/incidentes"
        self._circuit_breaker = circuit_breaker
        self._bearer_token = bearer_token

    async def list_incidents(self) -> list[IncidentRecord]:
        async def operation() -> list[IncidentRecord]:
            items = await fetch_gateway_list(self._url, self._bearer_token)
            return [
                IncidentRecord(
                    incident_id=item["id"],
                    id_conductor=item["id_conductor"],
                    placa_vehiculo=item["placa_vehiculo"],
                    tipo_incidente=item["tipo_incidente"],
                    severity=item["gravedad"],
                    occurred_at=parse_operational_datetime(item["fecha_hora"]),
                )
                for item in items
            ]

        return await self._circuit_breaker.call(operation)
