"""Application-layer fixtures for incident service tests.

SAD Traceability: data set with deliberate HUMANO/MECANICO and GRAVE/LEVE
mix to exercise all branches in IncidentService (SAD section 10.3).
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from fleetops_reports.application.ports.operational_clients import IncidentRecord


@pytest.fixture
def sample_incidents() -> list[IncidentRecord]:
    """Sobreescribe el fixture raíz para este scope.

    Distribución intencional:
      - 3 incidentes total
      - 2 GRAVE, 1 LEVE  → high_severity_rate = 66.67%
      - 1 HUMANO, 2 MECANICO → human_incident_rate = 33.33%
      - FOP-002 aparece 2 veces → recurrent_vehicle_count = 1
      - FOP-002 tiene 2 incidentes → supera umbral criticidad → critical_count = 1
    """
    now = datetime.now(UTC)
    return [
        IncidentRecord(
            incident_id="INC-20260601-001",
            id_conductor="cond-01",
            placa_vehiculo="FOP-002",
            tipo_incidente="MECANICO",
            severity="GRAVE",
            occurred_at=now,
        ),
        IncidentRecord(
            incident_id="INC-20260610-002",
            id_conductor="cond-01",
            placa_vehiculo="FOP-002",
            tipo_incidente="MECANICO",
            severity="GRAVE",
            occurred_at=now,
        ),
        IncidentRecord(
            incident_id="INC-20260615-003",
            id_conductor="cond-02",
            placa_vehiculo="FOP-003",
            tipo_incidente="HUMANO",
            severity="LEVE",
            occurred_at=now,
        ),
    ]
