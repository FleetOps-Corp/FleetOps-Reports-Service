"""Vehicle domain model.

SAD Traceability: represents vehicle assets consumed from the Vehículos service
and analyzed for availability, traceability and criticality in section 10.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Vehicle:
    id_vehiculo: str  # UUID v4 global
    numero_placa: str  # Placa del vehículo (ej: 'TYX-789')
    estado_vehiculo: str  # 'DISPONIBLE', 'EN_MANTENIMIENTO', etc.
    ciudad_operacion: str  # Ciudad asignada
    marca: str  # Fabricante de la unidad
    modelo: str  # Modelo comercial

    @property
    def is_available(self) -> bool:
        return (
            self.estado_vehiculo == "DISPONIBLE"
        )  # O el estado equivalente de tu lógica
