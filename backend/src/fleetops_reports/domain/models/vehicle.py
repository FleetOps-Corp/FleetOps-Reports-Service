"""Vehicle domain model.

SAD Traceability: represents vehicle assets consumed from the Vehículos service
and analyzed for availability, traceability and criticality in section 10.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Vehicle:
    vehicle_id: str
    plate: str
    status: str
    site: str
    category: str

    def is_operational(self) -> bool:
        return self.status.lower() == "operational"

