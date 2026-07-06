"""Reports API integration tests.

SAD Traceability: validates REST DTO mapping into the report generation use
case from SAD section 10.6.
"""

import jwt


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


def test_generate_report_endpoint_accepts_valid_bearer_token(api_client) -> None:
    token = jwt.encode(
        {"sub": "test-user", "role": "admin"},
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
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "generated"
    assert len(body["kpis"]) == 6
