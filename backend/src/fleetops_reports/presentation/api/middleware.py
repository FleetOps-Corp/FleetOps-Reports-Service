"""API middleware for request authentication."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import jwt
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from fleetops_reports.config.security import get_security_settings


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Any) -> Any:
        authorization = request.headers.get("authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        token = authorization.split(" ", 1)[1]
        settings = get_security_settings()
        public_key_value = settings.jwt_public_key_path
        if not public_key_value:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        public_key = public_key_value
        candidate_paths = [Path(public_key_value)]
        if not candidate_paths[0].is_absolute():
            candidate_paths.append(Path(__file__).resolve().parents[3] / public_key_value)
            candidate_paths.append(Path(__file__).resolve().parents[4] / public_key_value)

        for candidate_path in candidate_paths:
            if candidate_path.exists():
                public_key = candidate_path.read_text(encoding="utf-8")
                break

        try:
            jwt.decode(
                token,
                public_key,
                algorithms=[settings.jwt_algorithm],
                options={"require": ["sub"]},
            )
        except jwt.InvalidTokenError:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        return await call_next(request)


def register_auth_middleware(app: FastAPI) -> None:
    app.add_middleware(JWTAuthMiddleware)
