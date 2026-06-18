"""MTTR policy tests.

SAD Traceability: validates SAD section 10.2 maintenance efficiency rules.
"""

from datetime import UTC, datetime, timedelta

import pytest

from fleetops_reports.domain.exceptions import EmptyDatasetError, InvalidMetricError
from fleetops_reports.domain.policies.mttr_policy import MTTRPolicy


def test_calculate_mttr_hours() -> None:
    finished_at = datetime.now(UTC)
    metric = MTTRPolicy().calculate_hours([(finished_at - timedelta(hours=4), finished_at)])
    assert metric.value == 4


def test_calculate_mttr_rejects_empty_dataset() -> None:
    with pytest.raises(EmptyDatasetError):
        MTTRPolicy().calculate_hours([])


def test_calculate_mttr_rejects_invalid_interval() -> None:
    started_at = datetime.now(UTC)
    with pytest.raises(InvalidMetricError):
        MTTRPolicy().calculate_hours([(started_at, started_at - timedelta(hours=1))])

