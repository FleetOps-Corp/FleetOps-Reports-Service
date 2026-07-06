# FleetOps Reports — Simulation & Integration Testing

Guía maestra para reproducir las pruebas de integración del **Reports Service** contra:

1. **Despliegue EC2** (producción simulada)
2. **Stack local** (Security Gateway + Incidents + Reports + mock upstream)

## Índice

| Documento | Contenido |
|-----------|-----------|
| [01-deployed-ec2.md](./01-deployed-ec2.md) | Rama desplegada, smoke tests EC2, mock gateway |
| [02-local-integration.md](./02-local-integration.md) | Stack local, prueba incidents→gateway, reports→gateway |
| [03-postman-guide.md](./03-postman-guide.md) | Colección Postman y variables |
| [04-swagger-docs-guide.md](./04-swagger-docs-guide.md) | Probar desde `/docs` en local |
| [05-failure-report.md](./05-failure-report.md) | Fallos encontrados y mitigaciones |
| [artifacts/local-smoke-output.txt](./artifacts/local-smoke-output.txt) | Salida real de la última prueba local |

## Scripts ejecutables

Desde la raíz de `ReportsService`:

```powershell
# Mock upstream (vehículos, asignaciones, incidentes, mantenimiento)
python scripts/simulate/mock_operational_gateway.py --port 8099

# Bootstrap ADMINISTRADOR en Security Gateway local
powershell -ExecutionPolicy Bypass -File scripts/simulate/bootstrap_admin.ps1

# Smoke test EC2
powershell -ExecutionPolicy Bypass -File scripts/simulate/smoke_ec2.ps1

# Smoke test local (requiere stacks levantados)
powershell -ExecutionPolicy Bypass -File scripts/simulate/smoke_local.ps1
```

## Puertos de referencia (local)

| Servicio | URL base |
|----------|----------|
| Security Gateway | http://localhost:8000 |
| Reports API (Nginx) | http://localhost:8080 |
| Incidents directo | http://localhost:8030 |
| Mock upstream | http://localhost:8099 |

## Resultado ejecutado en esta sesión

- **Local:** todas las comprobaciones de `smoke_local.ps1` **OK** (ver artifacts).
- **EC2:** `/health` OK en rama `aquiceno`; generación de reportes requiere mock gateway en el host (pasos en `01-deployed-ec2.md`).
