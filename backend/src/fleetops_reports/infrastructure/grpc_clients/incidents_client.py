"""Incidents gRPC client.

SAD Traceability: adapter for the Incidentes service integration required by
ADR-001 and criticality process 10.3.
"""

# Archivos generados que deben coincidir con la especificación de Incidentes
from __future__ import annotations

from datetime import UTC, datetime

import grpc

from fleetops_reports.application.ports.operational_clients import IncidentRecord
from fleetops_reports.infrastructure.grpc_clients.circuit_breaker import CircuitBreaker
from fleetops_reports.infrastructure.grpc_clients.protos import incidentes_pb2, incidentes_pb2_grpc


class GrpcIncidentsClient:
    def __init__(self, target: str, circuit_breaker: CircuitBreaker) -> None:
        self._target = target
        self._circuit_breaker = circuit_breaker
        # Inicialización del canal asíncrono hacia el servicio de incidentes
        self._channel = grpc.aio.insecure_channel(self._target)
        self._stub = incidentes_pb2_grpc.IncidentesServiceStub(self._channel)

    async def list_incidents(self) -> list[IncidentRecord]:

        async def operation() -> list[IncidentRecord]:
            # Petición gRPC según los filtros admitidos por el microservicio
            request = incidentes_pb2.IncidentQueryRequest()

            # Llamada asíncrona real por red
            response = await self._stub.GetIncidents(request)

            records: list[IncidentRecord] = []
            for item in response.incidents:
                # Conversión segura del formato ISO 8601 string o Timestamp gRPC a datetime nativo
                # Si el protobuf envía un string ISO (ej: '2026-06-21T22:00:00')
                occurred_at_dt = datetime.fromisoformat(item.fecha_hora).replace(
                    tzinfo=UTC
                )

                # Construcción del Record alineado con la base de datos real
                records.append(
                    IncidentRecord(
                        incident_id=str(item.id),  # 'INC-20260621-a3f9'
                        id_conductor=str(item.id_conductor),  # 'CONDUCTOR-001'
                        placa_vehiculo=str(item.placa_vehiculo),  # 'ABC-123'
                        tipo_incidente=str(
                            item.tipo_incidente
                        ),  # 'MECANICO' / 'HUMANO'
                        severity=str(item.gravedad),  # 'LEVE' / 'GRAVE'
                        occurred_at=occurred_at_dt,
                    )
                )
            return records

        # Delegación controlada al Circuit Breaker para evitar caídas en cascada
        return await self._circuit_breaker.call(operation)

    async def close(self) -> None:
        """Ordenly shutdown of network channels."""
        await self._channel.close()
