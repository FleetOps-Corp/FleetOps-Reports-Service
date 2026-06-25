"""Assignments gRPC client.

SAD Traceability: adapter for the Asignaciones service integration required by
ADR-001 and traceability process 10.4.
"""

from __future__ import annotations

from datetime import UTC, datetime

import grpc

from fleetops_reports.application.ports.operational_clients import AssignmentRecord
from fleetops_reports.infrastructure.grpc_clients.circuit_breaker import CircuitBreaker

# Importación de stubs autogenerados correspondientes al contrato de Asignaciones
from fleetops_reports.infrastructure.grpc_clients.protos import (
    asignaciones_pb2,
    asignaciones_pb2_grpc,
)


class GrpcAssignmentsClient:
    def __init__(self, target: str, circuit_breaker: CircuitBreaker) -> None:
        self._target = target
        self._circuit_breaker = circuit_breaker
        # Inicialización del canal de comunicación gRPC asíncrono
        self._channel = grpc.aio.insecure_channel(self._target)
        self._stub = asignaciones_pb2_grpc.AsignacionesServiceStub(self._channel)

    async def list_assignments(self) -> list[AssignmentRecord]:

        async def operation() -> list[AssignmentRecord]:
            # Petición gRPC para consultar el listado total o histórico
            request = asignaciones_pb2.ListAssignmentsRequest()

            # Llamada real por red encapsulada de manera asíncrona
            response = await self._stub.ListAllAssignments(request)

            records: list[AssignmentRecord] = []
            for item in response.assignments:
                # Conversión segura de campos DATE string (YYYY-MM-DD) a objetos datetime nativos
                start_dt = datetime.fromisoformat(item.fecha_inicio).replace(tzinfo=UTC)
                end_dt = datetime.fromisoformat(item.fecha_fin).replace(tzinfo=UTC)

                # Tratamiento seguro del vehiculo_id
                # (puede venir vacío en Protobuf si es nulo en DB)
                vehiculo_uuid = item.vehiculo_id if item.vehiculo_id else None

                records.append(
                    AssignmentRecord(
                        assignment_id=str(item.id),  # UUID de la asignación
                        vehicle_id=vehiculo_uuid,  # UUID del vehículo o None
                        conductor_id=str(item.conductor_id),  # UUID del conductor
                        tipo_vehiculo=str(item.tipo_vehiculo),  # 'CAMION'
                        start_date=start_dt,
                        end_date=end_dt,
                    )
                )
            return records

        # Ejecución controlada a través del Circuit Breaker de resiliencia
        return await self._circuit_breaker.call(operation)

    async def close(self) -> None:
        """Cierre ordenado del canal de red."""
        await self._channel.close()
