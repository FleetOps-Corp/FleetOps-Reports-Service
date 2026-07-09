"""OpenAPI security scheme tests for Swagger Authorize."""

from fastapi import FastAPI

from fleetops_reports.presentation.api.routes import reports


def test_openapi_declares_bearer_auth_for_report_routes() -> None:
    app = FastAPI()
    app.include_router(reports.router)
    app.include_router(reports.security_api_router)
    schema = app.openapi()
    security_schemes = schema["components"]["securitySchemes"]
    assert "HTTPBearer" in security_schemes
    assert security_schemes["HTTPBearer"]["scheme"] == "bearer"

    protected_paths = (
        "/reports/generate",
        "/reports",
        "/reports/{report_id}",
        "/reports/{report_id}/download",
        "/api/reports/generate",
        "/api/reports",
        "/api/reports/{report_id}",
        "/api/reports/{report_id}/download",
    )
    for path in protected_paths:
        for operation in schema["paths"][path].values():
            assert operation.get("security") == [{"HTTPBearer": []}]
