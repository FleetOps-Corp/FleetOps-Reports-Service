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
from fleetops_reports.infrastructure.rest_clients.field_mapping import get_payload_field
from fleetops_reports.infrastructure.rest_clients.gateway_http import (
    build_gateway_resource_url,
    fetch_gateway_list,
)
from fleetops_reports.infrastructure.rest_clients.gateway_token_provider import (
    GatewayBearerTokenProvider,
)


class RestIncidentsClient:
    def __init__(
        self,
        gateway_base_url: str,
        circuit_breaker: CircuitBreaker,
        bearer_token: str | None = None,
        *,
        token_provider: GatewayBearerTokenProvider | None = None,
        resource_path: str = "/api/incidents/",
    ) -> None:
        self._url = build_gateway_resource_url(gateway_base_url, resource_path)
        self._circuit_breaker = circuit_breaker
        self._bearer_token = bearer_token
        self._token_provider = token_provider

    async def list_incidents(self) -> list[IncidentRecord]:
        async def operation() -> list[IncidentRecord]:
            items = await fetch_gateway_list(
                self._url,
                self._bearer_token,
                token_provider=self._token_provider,
            )
            return [
                IncidentRecord(
                    incident_id=get_payload_field(item, "id", "incident_id"),
                    id_conductor=get_payload_field(
                        item, "id_conductor", "driver_id"
                    ),
                    placa_vehiculo=get_payload_field(
                        item, "placa_vehiculo", "vehicle_id"
                    ),
                    tipo_incidente=get_payload_field(
                        item, "tipo_incidente", "incident_type"
                    ),
                    severity=get_payload_field(item, "gravedad", "severity"),
                    occurred_at=parse_operational_datetime(
                        get_payload_field(item, "fecha_hora", "event_date")
                    ),
                )
                for item in items
            ]

        return await self._circuit_breaker.call(operation)
