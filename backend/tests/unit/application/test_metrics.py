"""Metrics port tests."""

from __future__ import annotations

from fleetops_reports.application.ports.metrics import NoOpReportMetricsRecorder


def test_noop_report_metrics_recorder() -> None:
    recorder = NoOpReportMetricsRecorder()
    recorder.on_request()
    with recorder.track_generation():
        recorder.on_request()
