# Deployment Artifact - pinned MinIO image with non-root runtime.
# SAD Traceability: MinIO object storage for graph resources and PDF reports per ADR-003.
FROM minio/minio:RELEASE.2025-04-22T22-12-26Z

USER root
RUN mkdir -p /data \
    && chown -R 10001:10001 /data

USER 10001:10001

