# Guía Swagger / OpenAPI — pruebas locales

## Reports Service

1. Levanta el stack local:

   ```powershell
   docker compose -f docker-compose.yml -f docs/simulate/docker-compose.simulate.override.yml up -d
   ```

2. Abre en el navegador:

   - **Swagger UI:** http://localhost:8080/docs
   - **ReDoc:** http://localhost:8080/redoc
   - **OpenAPI JSON:** http://localhost:8080/openapi.json

3. Endpoints disponibles:

   | Método | Ruta | Descripción |
   |--------|------|-------------|
   | GET | `/health` | Liveness |
   | GET | `/metrics` | Prometheus |
   | POST | `/reports/generate` | Generar reporte |
   | POST | `/reportes/generate` | Alias compatible con Security Gateway |

4. Probar **Generate Report** desde Swagger:

   - Expande `POST /reports/generate`
   - **Try it out**
   - Body:

     ```json
     {
       "report_id": "rep-swagger-001",
       "title": "Swagger Test",
       "start_date": "2026-05-01",
       "end_date": "2026-05-31"
     }
     ```

   - **Execute** → espera **201** con 6 KPIs.

   > Requisito previo: mock upstream en `:8099`, Security Gateway en `:8000`, y `OPERATIONAL_GATEWAY_BEARER_TOKEN` configurado en `.env`.

## Security Gateway

- **Swagger:** http://localhost:8000/docs
- Rutas públicas: `/auth/register`, `/auth/login`
- Rutas proxy (requieren JWT ADMINISTRADOR): `/incidentes/**`, `/reportes/**`, etc.

Swagger **no** expone el proxy genérico completo; usa Postman/curl para rutas downstream.

## Incidents Service

Django REST no publica Swagger por defecto. Usa:

- Directo: http://localhost:8030/api/incidents/
- Gateway: http://localhost:8000/incidentes/ (con JWT)

## EC2 vía túnel SSH

```powershell
ssh -i fleetops-reports-key.pem -L 8081:127.0.0.1:8081 ubuntu@ec2-18-217-5-127.us-east-2.compute.amazonaws.com
```

Navega a http://localhost:8081/docs

## Validación rápida sin UI

```powershell
# Schema
Invoke-RestMethod http://localhost:8080/openapi.json | Select-Object openapi, info

# Health desde el schema servers
Invoke-RestMethod http://localhost:8080/health
```
