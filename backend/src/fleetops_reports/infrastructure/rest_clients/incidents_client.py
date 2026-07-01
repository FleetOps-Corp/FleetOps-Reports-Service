"""Incidents REST client.

SAD Traceability: adapter for the Incidentes service integration required by
ADR-001 and functional processes 10.1 and 10.4, via REST Gateway.
"""

from __future__ import annotations

from datetime import datetime

import httpx

from fleetops_reports.application.ports.operational_clients import IncidentRecord
from fleetops_reports.infrastructure.rest_clients.circuit_breaker import CircuitBreaker


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class RestIncidentsClient:
    def __init__(self, gateway_base_url: str, circuit_breaker: CircuitBreaker) -> None:
        self._url = f"{gateway_base_url}/incidentes"
        self._circuit_breaker = circuit_breaker

    async def list_incidents(self) -> list[IncidentRecord]:
        async def operation() -> list[IncidentRecord]:
            async with httpx.AsyncClient() as client:
                response = await client.get(self._url)
                response.raise_for_status()
                return [
                    IncidentRecord(
                        incident_id=item["id"],
                        id_conductor=item["id_conductor"],
                        placa_vehiculo=item["placa_vehiculo"],
                        tipo_incidente=item["tipo_incidente"],
                        severity=item["gravedad"],
                        occurred_at=_parse_dt(item["fecha_hora"]),
                    )
                    for item in response.json()
                ]

        return await self._circuit_breaker.call(operation)
