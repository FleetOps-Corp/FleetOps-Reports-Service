"""Audit middleware tests."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fleetops_reports.presentation.api.middleware import (
    REDACTED,
    AuditLoggingMiddleware,
    _sanitize_value,
)


def test_sanitize_value_redacts_sensitive_fields_and_keeps_vehicle_plates() -> None:
    payload = {
        "placa_vehiculo": "FOP-001",
        "numero_placa": "TYX-789",
        "correo": "driver@example.com",
        "password": "super-secret",
        "profile": {
            "email": "admin@example.com",
            "history": [{"token": "jwt-token", "placa": "ABC-123"}],
        },
    }

    sanitized = _sanitize_value(payload)

    assert sanitized["placa_vehiculo"] == "FOP-001"
    assert sanitized["numero_placa"] == "TYX-789"
    assert sanitized["correo"] == REDACTED
    assert sanitized["password"] == REDACTED
    assert sanitized["profile"]["email"] == REDACTED
    assert sanitized["profile"]["history"][0]["token"] == REDACTED
    assert sanitized["profile"]["history"][0]["placa"] == "ABC-123"


def test_audit_middleware_logs_gateway_request_with_sanitized_details(caplog) -> None:
    app = FastAPI(title="FleetOps Reports")
    app.add_middleware(AuditLoggingMiddleware)

    @app.post("/reportes/generate")
    async def generate_report() -> dict[str, str]:
        return {"status": "ok", "email": "private@example.com"}

    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="fleetops_reports.audit"):
        response = client.post(
            "/reportes/generate?correo=hidden@example.com&sede=Patio+Norte",
            headers={
                "X-Forwarded-For": "10.0.0.1",
                "Authorization": "Bearer secret-token",
            },
            json={
                "report_id": "rep-001",
                "placa_vehiculo": "FOP-001",
                "correo": "hidden@example.com",
                "password": "do-not-log",
            },
        )

    assert response.status_code == 200
    audit_event = next(record.audit for record in caplog.records if hasattr(record, "audit"))

    assert audit_event["application"] == "FleetOps Reports"
    assert audit_event["request"]["method"] == "POST"
    assert audit_event["request"]["route"] == "/reportes/generate"
    assert audit_event["requested_at"]
    assert audit_event["from_api_gateway"] is True
    assert "authorization" not in audit_event["request"]["headers"]
    assert audit_event["request"]["query_params"]["correo"] == REDACTED
    assert audit_event["request"]["query_params"]["sede"] == "Patio Norte"
    assert audit_event["detail"]["placa_vehiculo"] == "FOP-001"
    assert audit_event["detail"]["correo"] == REDACTED
    assert audit_event["detail"]["password"] == REDACTED
    assert audit_event["response"]["status_code"] == 200
    assert audit_event["response"]["success"] is True
    assert audit_event["response"]["detail"]["email"] == REDACTED
    assert audit_event["errors"] is None
