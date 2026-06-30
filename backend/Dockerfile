# SAD Traceability: containerizes the FastAPI analytical microservice from ADR-004.
FROM python:3.13-slim-bookworm AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /build

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY src ./src

RUN python -m pip wheel --wheel-dir /wheels .[test]

FROM python:3.13-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/app/.local/bin:${PATH}"

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 app \
    && mkdir -p /var/log/fleetops-reports \
    && chown -R app:app /var/log/fleetops-reports

COPY --from=builder /wheels /wheels
RUN python -m pip install --no-cache-dir /wheels/*.whl \
    && rm -rf /wheels

USER app

EXPOSE 8000

CMD ["uvicorn", "fleetops_reports.main:app", "--host", "0.0.0.0", "--port", "8000"]
