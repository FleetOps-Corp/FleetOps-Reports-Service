"""Request-scoped inbound JWT for operational gateway calls."""

from __future__ import annotations

from contextvars import ContextVar, Token

_inbound_bearer_token: ContextVar[str | None] = ContextVar(
    "inbound_bearer_token",
    default=None,
)


def set_inbound_bearer_token(token: str | None) -> Token[str | None]:
    normalized = token.strip() if token and token.strip() else None
    return _inbound_bearer_token.set(normalized)


def reset_inbound_bearer_token(token: Token[str | None]) -> None:
    _inbound_bearer_token.reset(token)


def get_inbound_bearer_token() -> str | None:
    return _inbound_bearer_token.get()
