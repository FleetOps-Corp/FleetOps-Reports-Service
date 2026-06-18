"""Metric value object tests.

SAD Traceability: validates analytical metric integrity for KPIs.
"""

import pytest

from fleetops_reports.domain.exceptions import InvalidMetricError
from fleetops_reports.domain.value_objects.metric import Metric


def test_metric_accepts_valid_value() -> None:
    metric = Metric("mttr", 2.5, "hours")
    assert metric.value == 2.5


def test_metric_rejects_blank_name() -> None:
    with pytest.raises(InvalidMetricError):
        Metric("", 1.0, "count")


def test_metric_rejects_nan() -> None:
    with pytest.raises(InvalidMetricError):
        Metric("invalid", float("nan"), "count")

