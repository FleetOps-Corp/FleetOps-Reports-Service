"""KPI model tests.

SAD Traceability: verifies analytical KPI creation.
"""

from fleetops_reports.domain.models.kpi import KPI
from fleetops_reports.domain.value_objects.metric import Metric


def test_kpi_create_now_sets_fields() -> None:
    metric = Metric("availability", 90.0, "percent")
    kpi = KPI.create_now("Availability", metric, "vehicles")
    assert kpi.name == "Availability"
    assert kpi.metric == metric
    assert kpi.source == "vehicles"

