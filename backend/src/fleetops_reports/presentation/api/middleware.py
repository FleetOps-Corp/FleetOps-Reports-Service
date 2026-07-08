"""API middleware for request authentication."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from fleetops_reports.config.security import (
    PUBLIC_PATHS,
    REPORTS_ALLOWED_ROLES,
    decode_jwt,
    get_security_settings,
)


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Any) -> Any:
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        authorization = request.headers.get("authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        token = authorization.split(" ", 1)[1]
        settings = get_security_settings()
        if not settings.jwt_public_key_path and not settings.jwt_secret_key:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        try:
            payload = decode_jwt(token, settings)
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

        if str(payload.get("role", "")).upper() not in REPORTS_ALLOWED_ROLES:
            return JSONResponse(
                status_code=403,
                content={
                    "detail": (
                        "Reports access requires ADMINISTRADOR or EMPLEADO_REPORTES role."
                    ),
                },
            )

        request.state.jwt_payload = payload
        return await call_next(request)


def register_auth_middleware(app: FastAPI) -> None:
    app.add_middleware(JWTAuthMiddleware)
