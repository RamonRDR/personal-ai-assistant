<div align="center">

# Personal AI Assistant 🧠

**Convierte solicitudes cotidianas en acciones locales reales, con aprobación humana.**

[🇺🇸 English](README.md) · [🇧🇷 Português](README.pt-BR.md) · [🇪🇸 Español](README.es.md)

[![CI](https://github.com/RamonRDR/personal-ai-assistant/actions/workflows/ci.yml/badge.svg?branch=feat%2Fpersonal-ai-assistant-v1)](https://github.com/RamonRDR/personal-ai-assistant/actions/workflows/ci.yml)
[![Python 3.14](https://img.shields.io/badge/Python-3.14-blue)](https://www.python.org/)
[![MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

![FastAPI 0.115+](https://img.shields.io/badge/FastAPI-0.115%2B-009688)
![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-E92063)
![Pydantic Settings](https://img.shields.io/badge/Pydantic-Settings-B72867)
![SQLAlchemy 2](https://img.shields.io/badge/SQLAlchemy-2-red)
![SQLite](https://img.shields.io/badge/SQLite-local%20database-003B57)
![Alembic](https://img.shields.io/badge/Alembic-migrations-555555)
![Uvicorn](https://img.shields.io/badge/Uvicorn-ASGI-4051B5)
![httpx](https://img.shields.io/badge/httpx-HTTP%20client-2A6FB1)
![HTML & CSS](https://img.shields.io/badge/HTML%20%26%20CSS-local%20UI-E34F26)
![Vanilla JavaScript](https://img.shields.io/badge/JavaScript-vanilla%20UI-F7DF1E)

![Tool Calling](https://img.shields.io/badge/Tool%20Calling-structured-6959CD)
![LLM Adapter Optional](https://img.shields.io/badge/LLM%20Adapter-optional-7C5AA3)
![Human Approval](https://img.shields.io/badge/Human%20Approval-enforced-15803D)
![Demo Mode](https://img.shields.io/badge/Demo%20Mode-offline-64748B)

[![pytest 29 passing](https://img.shields.io/badge/pytest-29%20passing-0A9EDC)](https://github.com/RamonRDR/personal-ai-assistant/actions/runs/42477081665)
![Ruff lint & format](https://img.shields.io/badge/Ruff-lint%20%26%20format-D7FF64)
![mypy schemas checked](https://img.shields.io/badge/mypy-schemas%20checked-2A6DB4)
![OpenAPI & Swagger UI](https://img.shields.io/badge/OpenAPI-Swagger%20UI-6BA539)
[![Synthetic Evals 24/24](https://img.shields.io/badge/Synthetic%20Evals-24%2F24%20passing-14815D)](https://github.com/RamonRDR/personal-ai-assistant/actions/runs/42477081665)
![Package Build](https://img.shields.io/badge/Package%20Build-CI%20verified-475569)

</div>

> **Estado del proyecto:** implementado en el [PR #1 en borrador](https://github.com/RamonRDR/personal-ai-assistant/pull/1), con verificaciones verdes en GitHub Actions en `feat/personal-ai-assistant-v1`. Esperando autorización del propietario para Codex Review; **sin merge, despliegue ni conexión a cuentas personales**.

Asistente personal **local-first** que demuestra **backend Python, automatización controlada, uso de herramientas e integración aplicada de IA**. Ejecuta operaciones reales mediante un catálogo limitado y auditable. La demostración offline es determinista; un adaptador opcional de LLM permite tool calling estructurado cuando se habilita expresamente.

## Descripción general

La interfaz web y la API REST comparten los servicios de negocio y la base SQLite. Las tareas, citas, recordatorios locales, historial limitado de conversaciones, solicitudes de aprobación humana y resultados de herramientas se almacenan de forma persistente. El intérprete nunca afirma que una operación se completó sin recibir el resultado real.

La demo predeterminada no requiere proveedores de pago, cuentas externas ni procesos programadores. Es una **aplicación local para un usuario**, no un SaaS expuesto a internet.

## Funcionalidades

- Crear, listar, consultar, actualizar, completar y eliminar tareas, con prioridad, fecha de vencimiento opcional y estado.
- Crear, listar, actualizar y eliminar eventos con inicio/fin y zona horaria explícitos.
- Crear, listar y marcar explícitamente recordatorios locales como entregados; consultar pendientes y resúmenes diarios.
- Utilizar **14 herramientas permitidas**, con esquemas Pydantic, clasificación de riesgo y respuestas estructuradas.
- Exigir aprobación humana para editar/eliminar tareas y eventos, con token de uso único, vencimiento, rechazo y auditoría.
- Utilizar una interfaz local adaptable con chat, tareas, eventos, recordatorios, botones de aprobación y auditoría reciente.
- Invocar opcionalmente un endpoint compatible con chat completions mediante `httpx`, con límite de llamadas y timeout.
- Probar el adaptador con proveedor de red simulado; la demo y CI **no llaman a un LLM de pago**.

## Tecnologías

| Área | Tecnología | Alcance comprobado |
| --- | --- | --- |
| Ejecución | Python 3.14 | Utilizado en GitHub Actions; `pyproject.toml` declara Python >=3.12 |
| API y servidor | FastAPI, Uvicorn | API REST, ASGI, OpenAPI y Swagger UI |
| Validación y configuración | Pydantic v2, Pydantic Settings | Esquemas estrictos y variables tipadas |
| Persistencia | SQLAlchemy 2, SQLite, Alembic | ORM, base de datos local y migraciones |
| Transporte de IA opcional | httpx | Adaptador configurable; pruebas con proveedor simulado |
| Interfaz | HTML, CSS, JavaScript puro | UI local adaptable, sin React ni compilación Node |
| Calidad | pytest, Ruff, mypy | Pruebas, lint/formato y tipos **solo de los esquemas** |
| Automatización | GitHub Actions, Python build | CI alojado, migraciones, evaluación y empaquetado |

**Sobre versiones:** FastAPI `0.115+` representa la versión mínima declarada (`>=0.115,<1`), no una instalación exacta. Pydantic v2 y SQLAlchemy 2 son rangos de versiones principales. Uvicorn, httpx, Pydantic Settings, SQLite y Alembic no reciben versiones exactas sin evidencia.

## Arquitectura

`Navegador local / REST → protección local de FastAPI → demo determinista o adaptador opcional de LLM → gestor de herramientas permitidas → servicios de negocio → SQLAlchemy / SQLite`. Las mutaciones sensibles se detienen en una propuesta hasta recibir aprobación humana con token de un solo uso. Los resultados y el historial limitado se almacenan localmente.

Consulta el [diagrama Mermaid, las decisiones y el modelo de amenazas](docs/architecture.md).

## Requisitos

- Python **3.14 recomendado** para reproducir CI; requisito del paquete: **Python >=3.12**.
- Compatibilidad con SQLite (a través de Python) y terminal para migraciones.
- No requiere Docker, PostgreSQL, Redis, nube, cuenta Google ni API de pago.

## Instalación

~~~bash
python -m venv .venv
source .venv/bin/activate            # Linux / macOS
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
cp .env.example .env                 # Opcional; Windows: copy .env.example .env
alembic upgrade head
~~~

Configura las variables antes de iniciar el servidor. La ruta SQLite predeterminada `./assistant.db` es relativa al directorio de trabajo.

## Configuración

| Variable | Significado | Predeterminado |
| --- | --- | --- |
| `PA_DATABASE_URL` | URL SQLAlchemy | `sqlite:///./assistant.db` |
| `PA_MODE` | `demo` o `openai_compatible` | `demo` |
| `PA_TIMEZONE` | Zona horaria IANA explícita | `UTC` |
| `PA_HISTORY_LIMIT` | Mensajes cargados en el contexto del modelo | `12` |
| `PA_HISTORY_RETENTION_DAYS` | Eliminar historial antiguo al conversar | `30` |
| `PA_MAX_TOOL_CALLS` | Límite de herramientas por solicitud LLM | `4` (máx. 8) |
| `PA_APPROVAL_TTL_SECONDS` | Caducidad de las aprobaciones | `600` |
| `PA_LLM_BASE_URL` / `PA_LLM_MODEL` / `PA_LLM_API_KEY` | Proveedor opcional | Sin clave de API |

Consulta [.env.example](.env.example). Nunca publiques tu archivo `.env` real ni credenciales.

## Ejecución local

~~~bash
personal-ai-assistant
~~~

La CLI inicia Uvicorn en `127.0.0.1:8000`, nunca en `0.0.0.0`.

- **Interfaz de demostración:** http://127.0.0.1:8000/
- **Documentación interactiva:** http://127.0.0.1:8000/docs
- **OpenAPI JSON:** http://127.0.0.1:8000/openapi.json
- **Estado:** http://127.0.0.1:8000/health

## Ejemplos de comandos de la demo

El modo offline acepta una **gramática fija de comandos en inglés**, no lenguaje natural abierto. Los títulos pueden estar en español, pero los prefijos como `create task:` siguen en inglés.

~~~text
create task: Revisar mi pull request
list tasks
get task: 1
complete task: 1
update task: 1 | Revisar después de CI
delete task: 1
create event: Reunión | 2026-11-08T10:00:00+00:00 | 2026-11-08T11:00:00+00:00 | UTC
list events
create reminder: Revisar CI | 2026-11-08T14:00:00+00:00
list reminders
daily summary: 2026-11-08 | UTC
~~~

Las actualizaciones o eliminaciones devuelven `approval_required` hasta una decisión humana. La demo ejecuta los **mismos servicios reales de SQLite** que la API.

## API REST y catálogo de herramientas

| Método | Endpoint | Operación |
| --- | --- | --- |
| GET | `/health`, `/docs`, `/openapi.json` | Estado y documentación |
| GET / POST | `/api/tasks` | Listar / crear tareas |
| GET / PATCH / DELETE | `/api/tasks/{task_id}` | Consultar / proponer actualización / eliminación |
| POST | `/api/tasks/{task_id}/complete` | Completar tarea |
| GET / POST | `/api/events` | Listar / crear eventos locales |
| PATCH / DELETE | `/api/events/{event_id}` | Proponer actualización / eliminación |
| GET / POST | `/api/reminders` | Listar / crear recordatorios |
| POST | `/api/reminders/{reminder_id}/deliver` | Marcar entregado localmente |
| GET | `/api/summary?day=2026-11-08&timezone=UTC` | Resumen diario con zona horaria |
| GET | `/api/tools`, `/api/audit`, `/api/history` | Herramientas, auditoría, historial |
| GET | `/api/approvals` | Propuestas pendientes (sin tokens) |
| POST | `/api/approvals/{id}/approve`, `/reject` | Decisión humana con token único |
| POST | `/api/chat` | Conversación demo o LLM opcional |

~~~bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "X-Local-Request: 1" \
  -d '{"message":"create task: Documentar arquitectura"}'
~~~

**Catálogo (14):** `create_task`, `list_tasks`, `get_task`, `update_task`, `complete_task`, `delete_task`; `create_event`, `list_events`, `update_event`, `delete_event`; `get_daily_summary`; `create_reminder`, `list_reminders`, `deliver_reminder`. Esquemas y riesgos disponibles en `GET /api/tools`.

## Aprobación humana (human-in-the-loop)

Las herramientas sensibles (`update_task`, `delete_task`, `update_event`, `delete_event`) proponen una acción con ID, cambios, vencimiento y token de confirmación único. La UI ofrece **Approve once** y **Reject**. Clientes REST envían `{"confirmation_token":"..."}` al endpoint correspondiente. El token se guarda como hash, no se transmite al LLM y se consume antes de la operación. Una aprobación inválida, rechazada, caducada o reutilizada no sirve para autorizar una nueva ejecución.

## LLM real opcional y costos

Para habilitar explícitamente la selección de herramientas mediante el modelo, configura:

~~~dotenv
PA_MODE=openai_compatible
PA_LLM_BASE_URL=https://api.openai.com/v1
PA_LLM_MODEL=gpt-4o-mini
PA_LLM_API_KEY=your-private-key
~~~

**El proveedor puede cobrar por las llamadas.** El adaptador usa esquemas de funciones, validación de argumentos, límite de herramientas, timeout e información de tokens cuando está disponible. Se probó la ruta con **proveedor simulado**, **no con un LLM de pago real**. Ni la demo ni el CI obligatorio realizan llamadas pagadas.

## Pruebas automatizadas y GitHub Actions

~~~bash
ruff check src tests scripts
ruff format --check src tests scripts
mypy src/personal_ai_assistant/schemas.py
pytest --junitxml=pytest-results.xml
python scripts/check_readme_badges.py pytest-results.xml
python scripts/evaluate.py
alembic upgrade head
python -m build
~~~

La reversión de migraciones (`alembic downgrade base`) se realiza en una base **desechable de CI**; no la ejecutes sobre datos importantes.

**Evidencia:** la [ejecución #42477081665](https://github.com/RamonRDR/personal-ai-assistant/actions/runs/42477081665) registró **29 aprobadas, 0 fallidas, 0 omitidas, 1 advertencia** y **24/24 escenarios sintéticos aprobados**. La advertencia de deprecación procede de una dependencia Starlette/httpx usada en las pruebas.

**Mantenimiento de badges:** `pytest 29 passing` es una **instantánea estática**, no un contador en tiempo real. CI genera `pytest-results.xml` y ejecuta `scripts/check_readme_badges.py` para comparar el conteo con los **tres READMEs** y validar la igualdad de badges y el número de escenarios. Si cambia la suite, actualiza los tres documentos mediante un PR revisado; CI **no crea commits**. El badge de estado CI es dinámico y rastrea `feat/personal-ai-assistant-v1`, ya que `main` todavía no contiene el workflow. Tras un merge autorizado, cambia el badge a `main`.

GitHub Actions comprueba Ruff lint/formato, mypy en `schemas.py`, pytest de API/seguridad, migraciones Alembic, evaluación determinista, build y presencia de la UI en el paquete. No solicita revisiones ni hace despliegues, publicaciones o merges automáticos.

## Seguridad y privacidad

Solo se aceptan conexiones locales y cabeceras Host permitidas, y la CLI escucha en localhost. Las mutaciones HTTP requieren `X-Local-Request: 1`; se bloquean Origin, Referer y Fetch Metadata de otros orígenes. Las eliminaciones aprobadas desvinculan recordatorios sin borrar sus mensajes ni horarios. Las aprobaciones se vinculan a la identidad inmutable del registro. La aplicación **carece de autenticación** y **no debe publicarse**. No existen shell, archivos arbitrarios, herramientas HTTP con URLs escogidas por el modelo, acciones financieras, Gmail ni Google Calendar reales. Una herramienta LLM no puede concederse aprobación humana. La auditoría guarda resultados, no argumentos completos; las propuestas permanecen en SQLite local. La retención predeterminada de 30 días se aplica **cuando llegan nuevas conversaciones**. Protege el archivo SQLite y sus copias.

Consulta las [notas técnicas de arquitectura y seguridad](docs/architecture.md).

## Limitaciones conocidas

- Demo de comandos fijos, **no es IA conversacional abierta**.
- Proveedor real opcional **no validado independientemente** en esta versión.
- Recordatorios locales consultables, **sin envío automático en segundo plano**.
- Sin autenticación de producción, multitenencia, planificador, hosting remoto ni cifrado en reposo.
- Un build correcto no prueba visualmente todo el navegador ni demuestra un despliegue.

## Estructura del repositorio

| Ruta | Responsabilidad |
| --- | --- |
| `src/personal_ai_assistant/api.py` | Rutas HTTP, control local y OpenAPI |
| `assistant.py`, `prompts/system.txt` | Parser demo y orquestación LLM opcional |
| `tools.py`, `services.py` | Restricciones de herramientas y reglas de negocio |
| `schemas.py`, `models.py`, `db.py`, `config.py` | Validación, modelos SQLAlchemy, sesiones y configuración |
| `static/index.html`, `cli.py` | Interfaz local y arranque del servidor |
| `alembic/` | Migraciones |
| `tests/`, `evals/`, `scripts/` | Pruebas, escenarios y validación de badges |
| `.github/workflows/ci.yml` | CI con permisos de solo lectura |
| `docs/architecture.md` | Mermaid, decisiones y amenazas |

## Posibles mejoras futuras

La autenticación y las integraciones externas opcionales podrían abordarse **solo en una versión futura con revisión independiente**. No están implementadas actualmente.

## Contribuciones

Se aceptan issues y cambios propuestos. Ejecuta las comprobaciones locales antes de enviar un pull request; nunca incluyas claves reales ni conjuntos de datos personales.

## Licencia

[MIT](LICENSE) · Copyright (c) 2026 Ramon Rodriguez.
