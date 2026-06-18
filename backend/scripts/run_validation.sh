#!/usr/bin/env bash
# SAD Traceability: runs architectural and quality validations for the archetype.
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== Installing dependencies ==="
pip install -q -e ".[test,lint]"

echo "=== Generating protos ==="
bash scripts/generate_protos.sh

echo ""
echo "=== IMPORT LINTER ==="
lint-imports

echo ""
echo "=== MYPY ==="
mypy

echo ""
echo "=== RUFF ==="
ruff check src tests

echo ""
echo "=== PYTEST ==="
pytest -q

echo ""
echo "=== COVERAGE (domain + application) ==="
coverage run -m pytest tests/unit/domain tests/unit/application
coverage report

echo ""
echo "All validations passed."
