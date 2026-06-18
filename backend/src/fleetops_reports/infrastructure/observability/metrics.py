"""Prometheus metrics registry.

SAD Traceability: implements Observability Pattern for API, gRPC, storage,
persistence and PDF generation metrics from SAD section 10.7.
"""

from __future__ import annotations

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

REPORT_REQUESTS = Counter(
    "fleetops_reports_generated_total",
    "Total executive report generation requests.",
)

REPORT_GENERATION_SECONDS = Histogram(
    "fleetops_report_generation_seconds",
    "Time spent generating executive reports.",
)


def render_metrics() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST

