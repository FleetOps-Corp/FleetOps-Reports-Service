"""Health endpoint.

SAD Traceability: supports deployment health checks for the backend and API
Gateway described in SAD section 11.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "fleetops-reports"}

