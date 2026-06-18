@echo off
REM SAD Traceability: Windows wrapper for full validation report via Docker Python 3.12.
setlocal
set ROOT=%~dp0..\..
docker run --rm --user root ^
  -v "%ROOT%\backend:/workspace" ^
  -w /workspace ^
  --env-file "%ROOT%\.env.example" ^
  python:3.12.13-slim-bookworm ^
  bash -lc "apt-get update -qq && apt-get install -y -qq bash build-essential libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 > /dev/null && bash scripts/run_validation_report.sh"
set EXITCODE=%ERRORLEVEL%
endlocal & exit /b %EXITCODE%
