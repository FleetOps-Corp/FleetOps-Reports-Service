"""Domain exception tests.

SAD Traceability: validates controlled business-rule failures required by the
rich domain model and SAD section 10 error handling characteristics.
"""

from fleetops_reports.domain.exceptions import InvalidMetricError


def test_domain_error_to_dict_exposes_stable_error_payload() -> None:
    error = InvalidMetricError("availability", "value must be numeric", "n/a")

    assert error.to_dict() == {
        "code": "INVALID_METRIC",
        "message": "Invalid metric 'availability': value must be numeric",
        "details": {
            "metric_name": "availability",
            "reason": "value must be numeric",
            "value": "n/a",
        },
    }
