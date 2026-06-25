from pathlib import Path
from grpc_tools import protoc

generated_dir = Path(
    "src/fleetops_reports/infrastructure/grpc_clients/generated"
)

generated_dir.mkdir(parents=True, exist_ok=True)
(generated_dir / "__init__.py").touch(exist_ok=True)

protoc.main(
    [
        "",
        "-I",
        "protos",
        "--python_out=src/fleetops_reports/infrastructure/grpc_clients/generated",
        "--grpc_python_out=src/fleetops_reports/infrastructure/grpc_clients/generated",
        "protos/vehicles.proto",
        "protos/assignments.proto",
        "protos/incidents.proto",
        "protos/maintenance.proto",
    ]
)