#!/usr/bin/env bash
# SAD Traceability: runs all validations and reports exit status per tool.
set -uo pipefail

cd "$(dirname "$0")/.."
OUT="/workspace/validation_results.txt"
: > "$OUT"

log() { echo "$@" | tee -a "$OUT"; }

pip install -q -e ".[test,lint]" --root-user-action=ignore 2>>"$OUT"
bash scripts/generate_protos.sh 2>>"$OUT"

declare -i IL=0 MY=0 RF=0 PT=0 CO=0

log "=== IMPORT LINTER ==="
if lint-imports 2>&1 | tee -a "$OUT"; then log "IMPORT LINTER: PASS"; else IL=1; log "IMPORT LINTER: FAIL"; fi

log ""
log "=== MYPY ==="
if mypy 2>&1 | tee -a "$OUT"; then log "MYPY: PASS"; else MY=1; log "MYPY: FAIL"; fi

log ""
log "=== RUFF ==="
if ruff check src tests 2>&1 | tee -a "$OUT"; then log "RUFF: PASS"; else RF=1; log "RUFF: FAIL"; fi

log ""
log "=== PYTEST ==="
if pytest -q 2>&1 | tee -a "$OUT"; then log "PYTEST: PASS"; else PT=1; log "PYTEST: FAIL"; fi

log ""
log "=== COVERAGE ==="
if coverage run -m pytest tests/unit/domain tests/unit/application 2>>"$OUT" && coverage report 2>&1 | tee -a "$OUT"; then
  log "COVERAGE: PASS"
else
  CO=1
  log "COVERAGE: FAIL"
fi

log ""
log "SUMMARY import_linter=$IL mypy=$MY ruff=$RF pytest=$PT coverage=$CO"
exit $((IL + MY + RF + PT + CO))
