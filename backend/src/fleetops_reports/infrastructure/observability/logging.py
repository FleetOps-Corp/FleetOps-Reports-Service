"""Structured logging setup.

SAD Traceability: emits JSON logs that Promtail can collect and forward to Loki
as required by the SAD observability stack.
"""

from __future__ import annotations

import logging
from pathlib import Path

from pythonjsonlogger.json import JsonFormatter


def configure_logging(level: str, log_file_path: str | None = None) -> None:
    formatter = JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(stream_handler)
    if log_file_path:
        path = Path(log_file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(path)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
    root.setLevel(level.upper())

