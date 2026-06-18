#!/usr/bin/env bash
# SAD Traceability: generates gRPC artifacts from Protocol Buffer contracts
# for ADR-001 without committing *_pb2.py or *_pb2_grpc.py files.

set -euo pipefail

PROTO_DIR="protos"
GENERATED_DIR="src/fleetops_reports/infrastructure/grpc_clients/generated"

mkdir -p "${GENERATED_DIR}"
touch "${GENERATED_DIR}/__init__.py"

python -m grpc_tools.protoc \
  -I "${PROTO_DIR}" \
  --python_out="${GENERATED_DIR}" \
  --grpc_python_out="${GENERATED_DIR}" \
  "${PROTO_DIR}/vehicles.proto" \
  "${PROTO_DIR}/assignments.proto" \
  "${PROTO_DIR}/incidents.proto" \
  "${PROTO_DIR}/maintenance.proto"

