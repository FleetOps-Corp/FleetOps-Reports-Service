"""Percentage value object tests.

SAD Traceability: validates availability percentages.
"""

import pytest

from fleetops_reports.domain.exceptions import InvalidMetricError
from fleetops_reports.domain.value_objects.percentage import Percentage


def test_percentage_as_ratio() -> None:
    assert Percentage(25).as_ratio() == 0.25


def test_percentage_rejects_out_of_range_value() -> None:
    with pytest.raises(InvalidMetricError):
        Percentage(101)

