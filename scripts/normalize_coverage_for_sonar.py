"""Rewrite coverage.xml paths for SonarCloud import.

coverage.py emits Cobertura paths relative to each measured source root
(for example ``value_objects/metric.py``). SonarCloud expects filenames
relative to the repository root (for example
``backend/src/fleetops_reports/domain/value_objects/metric.py``).
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPORT = Path("backend/coverage.xml")
BASE = Path("backend/src/fleetops_reports")


def resolve_sonar_path(filename: str) -> str | None:
    normalized = filename.replace("\\", "/")
    for layer in ("domain", "application"):
        candidate = BASE / layer / normalized
        if candidate.is_file():
            return candidate.as_posix()
    return None


def main() -> int:
    if not REPORT.is_file():
        print(f"Missing coverage report: {REPORT}", file=sys.stderr)
        return 1

    tree = ET.parse(REPORT)
    root = tree.getroot()

    sources = root.find("sources")
    if sources is not None:
        for source in list(sources):
            sources.remove(source)
        ET.SubElement(sources, "source").text = "."

    missing: list[str] = []
    updated = 0
    for cls in root.iter("class"):
        filename = cls.get("filename")
        if not filename or filename.startswith("backend/"):
            continue
        sonar_path = resolve_sonar_path(filename)
        if sonar_path is None:
            missing.append(filename)
            continue
        cls.set("filename", sonar_path)
        updated += 1

    if missing:
        print("Could not resolve coverage paths:", ", ".join(sorted(missing)), file=sys.stderr)
        return 1

    tree.write(REPORT, encoding="utf-8", xml_declaration=True)
    print(f"Normalized {updated} coverage entries in {REPORT} for SonarCloud")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
