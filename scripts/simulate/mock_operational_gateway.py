"""Lightweight mock for FleetOps Security Gateway operational routes.

Serves static JSON fixtures for /vehiculos, /asignaciones, /incidentes and
/mantenimiento. Used for EC2 smoke tests and local integration when upstream
microservices are unavailable.

Usage:
    python scripts/simulate/mock_operational_gateway.py --port 8000
"""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = ROOT / "docs" / "simulate" / "fixtures"

ROUTE_FILES = {
    "/vehiculos": "vehiculos.json",
    "/asignaciones": "asignaciones.json",
    "/incidentes": "incidentes.json",
    "/mantenimiento": "mantenimiento.json",
}


def _load_payload(route: str) -> bytes:
    filename = ROUTE_FILES.get(route)
    if not filename:
        body = {"detail": "Not found"}
        return json.dumps(body).encode("utf-8")
    data = json.loads((FIXTURES_DIR / filename).read_text(encoding="utf-8"))
    return json.dumps(data).encode("utf-8")


class MockGatewayHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        print(f"[mock-gateway] {self.address_string()} - {format % args}")

    def _write_json(self, status: int, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        if path in ROUTE_FILES:
            self._write_json(200, _load_payload(path))
            return
        if path == "/health":
            self._write_json(
                200,
                json.dumps({"status": "ok", "service": "mock-operational-gateway"}).encode(
                    "utf-8"
                ),
            )
            return
        self._write_json(404, json.dumps({"detail": f"Unknown route: {path}"}).encode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Mock FleetOps operational gateway")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), MockGatewayHandler)
    print(f"Mock operational gateway listening on http://{args.host}:{args.port}")
    for route in ROUTE_FILES:
        print(f"  GET {route}")
    server.serve_forever()


if __name__ == "__main__":
    main()
