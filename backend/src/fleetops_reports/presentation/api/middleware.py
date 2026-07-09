"""API middleware for request authentication and audit logging."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any
from urllib.parse import parse_qsl

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from fleetops_reports.application.inbound_token_context import (
    reset_inbound_bearer_token,
    set_inbound_bearer_token,
)
from fleetops_reports.config.security import (
    PUBLIC_PATHS,
    REPORTS_ALLOWED_ROLES,
    decode_jwt,
    get_security_settings,
)

logger = logging.getLogger("fleetops_reports.audit")

MAX_AUDIT_BODY_BYTES = 8192
REDACTED = "[REDACTED]"
SENSITIVE_FIELDS = frozenset(
    {
        "access_token",
        "api_key",
        "authorization",
        "clave",
        "contraseña",
        "contrasena",
        "correo",
        "email",
        "jwt",
        "mail",
        "minio_access_key",
        "minio_secret_key",
        "password",
        "refresh_token",
        "secret",
        "secret_key",
        "token",
    }
)
SENSITIVE_FIELD_FRAGMENTS = ("password", "secret", "token", "authorization")
SAFE_HEADERS = frozenset(
    {
        "accept",
        "accept-language",
        "content-length",
        "content-type",
        "host",
        "user-agent",
        "x-forwarded-for",
        "x-forwarded-proto",
        "x-real-ip",
        "x-request-id",
    }
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

        context_token = set_inbound_bearer_token(token)
        request.state.jwt_payload = payload
        try:
            return await call_next(request)
        finally:
            reset_inbound_bearer_token(context_token)


class AuditLoggingMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        *,
        max_body_bytes: int = MAX_AUDIT_BODY_BYTES,
    ) -> None:
        self.app = app
        self.max_body_bytes = max_body_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_started_at = datetime.now(UTC)
        body = await self._read_body(receive)
        audit_body = body[: self.max_body_bytes]
        response_status: int | None = None
        response_headers: dict[str, str] = {}
        response_body_chunks: list[bytes] = []
        response_body_size = 0
        error_detail: dict[str, str] | None = None
        body_replayed = False

        async def replay_body() -> Message:
            nonlocal body_replayed
            if body_replayed:
                return {"type": "http.request", "body": b"", "more_body": False}
            body_replayed = True
            return {"type": "http.request", "body": body, "more_body": False}

        async def send_wrapper(message: Message) -> None:
            nonlocal response_status, response_headers, response_body_size
            if message["type"] == "http.response.start":
                response_status = int(message["status"])
                response_headers = _headers_from_message(message)
            if message["type"] == "http.response.body":
                chunk = message.get("body", b"")
                if chunk and response_body_size < self.max_body_bytes:
                    remaining = self.max_body_bytes - response_body_size
                    response_body_chunks.append(chunk[:remaining])
                    response_body_size += len(chunk[:remaining])
            await send(message)

        try:
            await self.app(scope, replay_body, send_wrapper)
        except Exception as exc:
            response_status = 500
            error_detail = {
                "type": exc.__class__.__name__,
                "message": str(exc),
            }
            self._log_audit_event(
                scope,
                request_started_at,
                response_status,
                audit_body,
                response_headers,
                b"".join(response_body_chunks),
                error_detail,
            )
            raise

        status_code = response_status or 500
        response_detail = _sanitize_body(
            b"".join(response_body_chunks),
            response_headers.get("content-type", ""),
        )
        if error_detail is None and status_code >= 400:
            error_detail = {
                "type": "http_error_response",
                "message": str(response_detail or status_code),
            }

        self._log_audit_event(
            scope,
            request_started_at,
            response_status,
            audit_body,
            response_headers,
            b"".join(response_body_chunks),
            error_detail,
        )

    async def _read_body(self, receive: Receive) -> bytes:
        chunks: list[bytes] = []
        more_body = True

        while more_body:
            message = await receive()
            if message["type"] != "http.request":
                continue
            chunk = message.get("body", b"")
            if chunk:
                chunks.append(chunk)
            more_body = bool(message.get("more_body", False))

        return b"".join(chunks)

    def _log_audit_event(
        self,
        scope: Scope,
        request_started_at: datetime,
        response_status: int | None,
        body: bytes,
        response_headers: dict[str, str],
        response_body: bytes,
        error_detail: dict[str, str] | None,
    ) -> None:
        headers = _headers_from_scope(scope)
        path = str(scope.get("path", ""))
        status_code = response_status or 500
        response_detail = _sanitize_body(
            response_body,
            response_headers.get("content-type", ""),
        )
        event = {
            "event": "http_request_audit",
            "application": _application_name(scope),
            "request": {
                "method": scope.get("method"),
                "path": path,
                "route": path,
                "query_params": _sanitize_mapping(_query_params(scope)),
                "headers": _sanitize_mapping(
                    {
                        key: value
                        for key, value in headers.items()
                        if key in SAFE_HEADERS
                    }
                ),
            },
            "requested_at": request_started_at.isoformat(),
            "response": {
                "status_code": status_code,
                "success": 200 <= status_code < 400,
                "detail": response_detail,
            },
            "from_api_gateway": _is_gateway_request(path, headers),
            "errors": error_detail,
            "detail": _sanitize_body(body, headers.get("content-type", "")),
        }
        logger.info("HTTP request audit", extra={"audit": event})


def _application_name(scope: Scope) -> str:
    app = scope.get("app")
    return str(getattr(app, "title", "fleetops-reports"))


def _headers_from_scope(scope: Scope) -> dict[str, str]:
    raw_headers = scope.get("headers", [])
    return {
        key.decode("latin-1").lower(): value.decode("latin-1")
        for key, value in raw_headers
    }


def _headers_from_message(message: Message) -> dict[str, str]:
    raw_headers = message.get("headers", [])
    return {
        key.decode("latin-1").lower(): value.decode("latin-1")
        for key, value in raw_headers
    }


def _query_params(scope: Scope) -> dict[str, str]:
    raw_query = scope.get("query_string", b"").decode("latin-1")
    if not raw_query:
        return {}
    return dict(parse_qsl(raw_query, keep_blank_values=True))


def _sanitize_body(body: bytes, content_type: str) -> Any:
    if not body:
        return None
    if "application/json" not in content_type.lower():
        return {"content_type": content_type or "unknown", "captured": False}
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {"content_type": content_type, "captured": False}
    return _sanitize_value(payload)


def _sanitize_mapping(values: dict[str, Any]) -> dict[str, Any]:
    return {key: _sanitize_field(key, value) for key, value in values.items()}


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return _sanitize_mapping(value)
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value]
    return value


def _sanitize_field(key: str, value: Any) -> Any:
    normalized_key = key.strip().lower()
    if normalized_key in SENSITIVE_FIELDS or any(
        fragment in normalized_key for fragment in SENSITIVE_FIELD_FRAGMENTS
    ):
        return REDACTED
    return _sanitize_value(value)


def _is_gateway_request(path: str, headers: dict[str, str]) -> bool:
    return path.startswith("/api/reports") or any(
        header in headers
        for header in ("x-forwarded-for", "x-forwarded-proto", "x-real-ip")
    )


def register_auth_middleware(app: FastAPI) -> None:
    app.add_middleware(JWTAuthMiddleware)
    app.add_middleware(AuditLoggingMiddleware)
