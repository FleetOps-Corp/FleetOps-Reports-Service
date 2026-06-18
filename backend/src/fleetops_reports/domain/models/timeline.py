"""Timeline domain model.

SAD Traceability: represents the unified vehicle traceability timeline from
the Trazabilidad Histórica del Vehículo process in section 10.4.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TimelineEvent:
    occurred_at: datetime
    event_type: str
    source: str
    description: str


@dataclass(frozen=True)
class Timeline:
    vehicle_id: str
    events: tuple[TimelineEvent, ...]

    def chronological_events(self) -> tuple[TimelineEvent, ...]:
        return tuple(sorted(self.events, key=lambda event: event.occurred_at))

