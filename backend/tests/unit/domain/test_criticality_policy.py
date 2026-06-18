"""Criticality policy tests.

SAD Traceability: validates SAD section 10.3 critical vehicle classification.
"""

import pytest

from fleetops_reports.domain.exceptions import InvalidMetricError
from fleetops_reports.domain.policies.criticality_policy import CriticalityPolicy


def test_classify_critical_vehicle() -> None:
    assert CriticalityPolicy().classify(4, 1) == "critical"


def test_classify_warning_vehicle() -> None:
    assert CriticalityPolicy().classify(2, 0) == "warning"


def test_classify_normal_vehicle() -> None:
    assert CriticalityPolicy().classify(0, 1) == "normal"


def test_classify_rejects_negative_counts() -> None:
    with pytest.raises(InvalidMetricError):
        CriticalityPolicy().classify(-1, 0)

