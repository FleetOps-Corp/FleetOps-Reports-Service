"""Reports API integration tests."""

import jwt

from fleetops_reports.presentation.dependencies import get_app_settings


def _auth_headers(client) -> dict[str, str]:
    token = jwt.encode(
        {"sub": "test-user", "role": "ADMINISTRADOR"},
        client.private_pem,
        algorithm="RS256",
    )
    return {"Authorization": f"Bearer {token}"}


def test_generate_report_endpoint_requires_auth(api_client) -> None:
    response = api_client.post(
        "/reports/generate",
        json={
            "report_id": "rep-001",
            "title": "Executive Report",
            "start_date": "2026-05-01",
            "end_date": "2026-05-31",
        },
    )
    assert response.status_code == 401


def test_generate_report_endpoint_rejects_non_admin_role(api_client) -> None:
    token = jwt.encode(
        {"sub": "test-user", "role": "EMPLEADO"},
        api_client.private_pem,
        algorithm="RS256",
    )
    response = api_client.post(
        "/reports/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "report_id": "rep-001",
            "title": "Executive Report",
            "start_date": "2026-05-01",
            "end_date": "2026-05-31",
        },
    )
    assert response.status_code == 403


def test_generate_report_endpoint_accepts_empleado_reportes_role(api_client) -> None:
    token = jwt.encode(
        {"sub": "reports-user", "role": "EMPLEADO_REPORTES"},
        api_client.private_pem,
        algorithm="RS256",
    )
    response = api_client.post(
        "/api/reports/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "report_id": "rep-reports-001",
            "title": "Reports Employee Report",
            "start_date": "2026-05-01",
            "end_date": "2026-05-31",
        },
    )
    assert response.status_code == 201


def test_generate_report_endpoint_accepts_valid_bearer_token(api_client) -> None:
    response = api_client.post(
        "/reports/generate",
        headers=_auth_headers(api_client),
        json={
            "report_id": "rep-001",
            "title": "Executive Report",
            "start_date": "2026-05-01",
            "end_date": "2026-05-31",
            "sede_operacion": "Patio Norte Bogotá",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "generated"
    assert body["sede_operacion"] == "Patio Norte Bogotá"
    assert len(body["kpis"]) == 6


def test_list_and_download_report_endpoints(api_client) -> None:
    headers = _auth_headers(api_client)
    api_client.post(
        "/reports/generate",
        headers=headers,
        json={
            "report_id": "rep-download-001",
            "title": "Download Test",
            "start_date": "2026-05-01",
            "end_date": "2026-05-31",
        },
    )

    list_response = api_client.get("/reports", headers=headers)
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1

    detail_response = api_client.get("/reports/rep-download-001", headers=headers)
    assert detail_response.status_code == 200

    download_response = api_client.get("/reports/rep-download-001/download", headers=headers)
    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "application/pdf"


def test_generate_fixture_report_endpoint_filters_by_city(api_client) -> None:
    response = api_client.post(
        "/reports/generate/fixture",
        headers=_auth_headers(api_client),
        json={
            "report_id": "rep-ref-bogota-202605",
            "title": "FleetOps Executive Report — Fixture Reference (Bogotá)",
            "start_date": "2026-05-01",
            "end_date": "2026-05-31",
            "ciudad_operacion": "Bogotá",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["report_id"] == "rep-ref-bogota-202605"
    assert body["ciudad_operacion"] == "Bogotá"
    assert body["status"] == "generated"
    assert len(body["kpis"]) == 6

    download_response = api_client.get(
        "/reports/rep-ref-bogota-202605/download",
        headers=_auth_headers(api_client),
    )
    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "application/pdf"


def test_generate_fixture_report_endpoint_disabled_when_flag_off(api_client, monkeypatch) -> None:
    monkeypatch.setenv("FIXTURE_REPORTS_ENABLED", "false")
    get_app_settings.cache_clear()
    response = api_client.post(
        "/reports/generate/fixture",
        headers=_auth_headers(api_client),
        json={
            "report_id": "rep-fixture-disabled",
            "title": "Disabled",
            "start_date": "2026-05-01",
            "end_date": "2026-05-31",
        },
    )
    assert response.status_code == 404
    get_app_settings.cache_clear()
