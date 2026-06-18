"""Reports API integration tests.

SAD Traceability: validates REST DTO mapping into the report generation use
case from SAD section 10.6.
"""


def test_generate_report_endpoint(api_client) -> None:
    response = api_client.post(
        "/reports",
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
    assert len(body["kpis"]) == 3

