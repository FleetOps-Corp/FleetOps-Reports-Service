# Reporte de Validación Arquitectónica — FleetOps Reports

**Fecha:** 2026-06-18  
**Referencia:** DAS FleetOps Reports (SAD 2026-05-29), sección 6 — Capas Arquitectónicas  
**Entorno de validación:** Docker `reports-backend` · Python 3.12.13 · `.env.example`

---

## 1. Estructura arquitectónica detectada

El arquetipo implementa el modelo en capas del DAS con mapeo explícito a paquetes Python:

| Capa DAS | Paquete(s) | Responsabilidad |
|----------|------------|-----------------|
| **Presentación** | `presentation/` | REST (FastAPI), DTOs Pydantic, rutas `/health`, `/metrics`, `/reports` |
| **Lógica de Negocio** | `application/`, `domain/` | Use cases, servicios lógicos (ADR-006), puertos hexagonales, modelos ricos, políticas, excepciones |
| **Acceso a Datos** | `infrastructure/` | MongoDB/Beanie, MinIO, clientes gRPC, PDF/WeasyPrint, Jinja2, observabilidad |
| **Transversal** | `config/`, `main.py` | Settings externalizados; `main.py` como composition root |

### Diagrama de capas detectado

```text
                    ┌─────────────────────────────────────┐
                    │           main.py (root)            │
                    │   lifespan · wiring · routers       │
                    └──────────────┬──────────────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────┐
│  presentation/  │    │    application/      │    │ infrastructure/ │
│  routes         │───▶│  use_cases           │◀───│  adapters       │
│  schemas (DTO)  │    │  services            │    │  mongodb/minio  │
└────────┬────────┘    │  ports (Protocol)    │    │  grpc_clients   │
         │             └──────────┬───────────┘    │  mappers        │
         │                        │                │  dependencies   │
         │                        ▼                └────────┬────────┘
         │             ┌──────────────────────┐               │
         └────────────▶│      domain/         │◀──────────────┘
                       │  models · policies   │
                       │  value_objects       │
                       │  exceptions          │
                       └──────────────────────┘
```

### Servicios lógicos del DAS (ADR-006) — presencia verificada

| Servicio DAS | Archivo |
|--------------|---------|
| Disponibilidad | `application/services/availability_service.py` |
| Mantenimiento / MTTR | `application/services/maintenance_service.py` |
| Incidentes / criticidad | `application/services/incident_service.py` |
| Trazabilidad | `application/services/traceability_service.py` |
| Gráficas (Builder) | `application/services/graph_service.py` |
| Plantillas (Template View) | `application/services/template_service.py` |
| Reportes PDF | `application/services/report_service.py` |

### Flujo transaccional verificado

`POST /reports` → `ReportMapper` → `GenerateReportUseCase` → servicios lógicos → puertos → MongoDB + MinIO (presigned URL) + WeasyPrint → respuesta `201`.

---

## 2. Resultado de cada validación

### 2.1 Import Linter — Reglas arquitectónicas

**Herramienta:** `import-linter==2.1` · Config: `backend/.importlinter`  
**Archivos analizados:** 77 · **Dependencias:** 69

| Contrato | Regla | Resultado |
|----------|-------|-----------|
| `domain-independence` | Domain no importa capas externas | ✅ KEPT |
| `application-business` | Application no importa Presentation ni Infrastructure | ✅ KEPT |
| `presentation-no-infrastructure` | Presentation no importa Infrastructure | ❌ BROKEN |
| `infrastructure-no-presentation` | Infrastructure no importa Presentation | ❌ BROKEN |
| `layers-hierarchy` | Presentation → Application → Domain | ✅ KEPT |

**Veredicto Import Linter:** ❌ **2 de 5 contratos incumplidos**

#### Violaciones detectadas

**A. Presentation → Infrastructure (4 dependencias)**

| Origen | Destino |
|--------|---------|
| `presentation.api.routes.metrics` | `infrastructure.observability.metrics` |
| `presentation.api.routes.reports` | `infrastructure.dependencies` |
| `presentation.api.routes.reports` | `infrastructure.mappers.report_mapper` |
| `presentation.api.routes.reports` | `infrastructure.observability.metrics` |

**B. Infrastructure → Presentation (1 dependencia)**

| Origen | Destino |
|--------|---------|
| `infrastructure.mappers.report_mapper` | `presentation.schemas.report_schemas` |

#### Dependencias permitidas (contratos que pasan)

- `domain` → solo `domain`
- `application` → `domain` (+ tipos en `application.ports`)
- `presentation` → `application`, `domain`
- `infrastructure` → `application`, `domain`, `config` (no verificado explícitamente; permitido por diseño hexagonal)
- `main.py` → todas las capas (composition root, excluido de contratos)

---

### 2.2 MyPy — Consistencia de tipos

**Herramienta:** `mypy==1.16.1` + `pydantic.mypy` · Config: `backend/mypy.ini`  
**Archivos verificados:** 69

| Estado inicial | Tras ajustes (`pydantic.mypy`, fix WeasyPrint/Jinja) |
|----------------|------------------------------------------------------|
| 18 errores | ✅ **Success: no issues found in 69 source files** |

Errores corregidos durante esta etapa:
- `Settings()` sin plugin Pydantic → resuelto con `plugins = pydantic.mypy`
- `WeasyPrintRenderer.render` retornando `Any` → anotación explícita `pdf_bytes: bytes`
- `Path(Traversable)` en `jinja_renderer.py` → cast via `str()`

**Veredicto MyPy:** ✅ **PASS**

---

### 2.3 Ruff — Calidad estructural

**Herramienta:** `ruff==0.12.0` · Config: `backend/pyproject.toml`  
**Exclusión:** `generated/` (artefactos gRPC)

| Estado inicial (con TC rules + generated/) | Tras ajustes |
|---------------------------------------------|--------------|
| 111 errores | **18 errores** (6 auto-fixables) |

Distribución de los 18 errores restantes (código escrito a mano):

| Código | Cantidad aprox. | Naturaleza |
|--------|-----------------|------------|
| `E501` | ~12 | Líneas > 100 caracteres (tests y algunos imports) |
| `I001` | ~6 | Imports desordenados (main, reports, tests) |

**Veredicto Ruff:** ⚠️ **PARTIAL** — sin errores críticos (`F`, `B`); deuda cosmética de formato.

---

### 2.4 Pytest — Pruebas funcionales

**Herramienta:** `pytest==8.4.1` · `pytest-asyncio==1.0.0`

| Suite | Tests | Resultado |
|-------|-------|-----------|
| Completa (`tests/`) | **36** | ✅ 36 passed |
| Unit domain + application | 35 | ✅ 35 passed |
| Integración API | 1 | ✅ passed |

Fixtures verificadas: `conftest.py` (root), `tests/unit/conftest.py`, `tests/integration/api/conftest.py` — todas funcionales con fakes de puertos.

**Veredicto Pytest:** ✅ **PASS**

---

### 2.5 Cobertura (domain + application)

**Herramienta:** `coverage==7.9.1` · `fail_under = 100`

| Métrica | Valor |
|---------|-------|
| Statements | 328 |
| Miss | 0 |
| Branch partial | 0 |
| **Total** | **100%** |

**Veredicto Coverage:** ✅ **PASS**

---

## 3. Violaciones encontradas — resumen consolidado

| # | Severidad | Capa | Violación | Impacto |
|---|-----------|------|-----------|---------|
| V1 | **Alta** | Presentation → Infrastructure | Rutas importan `dependencies`, `ReportMapper`, métricas Prometheus | Rompe capa estricta Presentation → Business → Data |
| V2 | **Alta** | Infrastructure → Presentation | `ReportMapper` importa `presentation.schemas` | Inversión DTO: infraestructura acoplada a contrato REST |
| V3 | Media | Composition root | `main.py` importa directamente infrastructure | Aceptable como wiring; no es violación en hexagonal |
| V4 | Baja | Ruff E501/I001 | Líneas largas e imports sin ordenar | Calidad de código, no arquitectura |
| V5 | Info | `generated/` protos | Artefactos gRPC generados en workspace local | Correctamente en `.gitignore`; excluidos de Ruff/MyPy |

---

## 4. Recomendaciones de corrección

### Prioridad 1 — Restaurar capas estrictas (V1, V2)

1. **Mover `ReportMapper` a `presentation/mappers/`** o crear DTOs de aplicación en `application/dto/` que no dependan de Pydantic. El mapper bidireccional debe vivir en Presentación o en una capa `interfaces/` que solo conozca DTOs y dominio.

2. **Extraer métricas de presentación:** crear puerto `MetricsRecorder` en `application/ports/` con implementación en `infrastructure/observability/`. La ruta `reports.py` solo debería llamar al puerto o a un middleware, no importar `Counter` de Prometheus.

3. **Relocalizar `dependencies.py`:** renombrar a `composition/wiring.py` fuera de `infrastructure/` o documentar como **Archetype Convention Addition** — módulo de composición FastAPI que no pertenece a ninguna capa estricta del DAS.

4. **Patrón recomendado para FastAPI + hexagonal:**
   ```text
   presentation/routes/reports.py
     → Depends(get_use_case)  # provider en composition/dependencies.py
     → application/use_cases/
   composition/dependencies.py  # NO en infrastructure/
     → instancia adaptadores concretos
   ```

### Prioridad 2 — Calidad (V4)

5. Ejecutar `ruff check --fix src tests` para corregir imports (`I001`).
6. Ajustar líneas largas en tests o elevar `line-length` a 120 en `pyproject.toml` si el equipo lo prefiere.

### Prioridad 3 — Mantenimiento

7. Añadir `make validate` al CI con: `lint-imports`, `mypy`, `ruff check`, `pytest`, `coverage report`.
8. Documentar en README que `docker compose up` requiere `.env` o usa defaults de `.env.example`.

---

## 4.1 Correcciones aplicadas en esta etapa de revisión

| Archivo | Cambio |
|---------|--------|
| `backend/.importlinter` | **Nuevo** — 5 contratos de capas |
| `backend/mypy.ini` | **Nuevo** — plugin Pydantic, exclude generated |
| `backend/pyproject.toml` | Dependencias `lint`, config Ruff, exclude generated |
| `backend/scripts/run_validation_report.sh` | **Nuevo** — script de validación completa |
| `Makefile` | Targets `lint`, `import-linter`, `mypy`, `ruff`, `validate` |
| `domain/__init__.py` | **Nuevo** — paquete domain reconocible por Import Linter |
| `jinja_renderer.py`, `weasyprint_renderer.py` | Fixes MyPy |
| `tests/conftest.py` | Eliminado import `os` no usado |

Ver detalle de la etapa anterior en [`CORRECCIONES_REALIZADAS.md`](CORRECCIONES_REALIZADAS.md).

---

## 5. Veredicto final

| Dimensión | Estado | Nota |
|-----------|--------|------|
| Estructura de capas (presencia) | ✅ Cumple | Las 3 capas DAS existen con trazabilidad SAD |
| Aislamiento Domain | ✅ Cumple | Sin dependencias externas |
| Aislamiento Application | ✅ Cumple | Solo depende de Domain |
| Capa Presentation (estricta) | ❌ No cumple | Importa Infrastructure directamente |
| Capa Infrastructure (estricta) | ❌ No cumple | Importa Presentation schemas |
| Jerarquía Presentation → Application → Domain | ✅ Cumple | Contrato `layers-hierarchy` OK |
| Tipos (MyPy) | ✅ Cumple | 69 archivos sin errores |
| Calidad (Ruff) | ⚠️ Parcial | 18 issues cosméticos en código manual |
| Tests + cobertura | ✅ Cumple | 36 tests, 100% domain+application |
| Despliegue end-to-end | ✅ Cumple | Gateway → Backend → MongoDB/MinIO verificado |

### Veredicto global

> **⚠️ CUMPLIMIENTO PARCIAL — 75%**

El arquetipo **refleja fielmente la estructura y responsabilidades del DAS** (servicios lógicos, puertos hexagonales, flujo transaccional, observabilidad, ADRs). Las capas **Domain** y **Application** están correctamente aisladas.

Sin embargo, el patrón de inyección FastAPI actual **acopla Presentation e Infrastructure**, violando el flujo unidireccional estricto del DAS (*Presentación → Lógica de Negocio → Acceso a Datos*). Esto es una desviación **consciente y común** en microservicios FastAPI, pero debe corregirse o documentarse formalmente como convención del arquetipo antes de producción.

**Recomendación:** Aprobar el arquetipo para desarrollo académico/evolutivo; aplicar las correcciones de Prioridad 1 antes de considerarlo production-ready bajo el DAS estricto.

---

## Comandos de reproducción

```bash
# Validación completa (Docker + Python 3.12)
docker run --rm --user root \
  -v "$(pwd)/backend:/workspace" -w /workspace \
  --env-file .env.example \
  reports-backend bash scripts/run_validation_report.sh

# Individual (local, requiere Python 3.12)
make import-linter
make mypy
make ruff
make test
make coverage
```

Resultados crudos: `backend/validation_results.txt`
