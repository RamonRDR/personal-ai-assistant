# Personal AI Assistant

[English](README.md) | [Português](README.pt-BR.md) | **Español**

Asistente personal **local**, con ejecución real de herramientas, SQLite, calendario, recordatorios y aprobación humana para operaciones sensibles. No es un chatbot que simula acciones.

## Tecnologías y arquitectura

Python 3.14 (mínimo del paquete: 3.12), FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, SQLite, httpx, pytest, Ruff, mypy y GitHub Actions. Separamos API, esquemas, servicios, herramientas, adaptador opcional de LLM, aprobaciones e interfaz. Consulta el [diagrama y las decisiones](docs/architecture.md).

## Instalación y ejecución

```bash
python -m venv .venv
source .venv/bin/activate # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
cp .env.example .env # opcional; en Windows, copy
alembic upgrade head
personal-ai-assistant
```

Interfaz: http://127.0.0.1:8000/ · OpenAPI: http://127.0.0.1:8000/docs · estado: `/health`. Sólo se ejecuta en localhost. Configura explícitamente la zona horaria IANA con `PA_TIMEZONE`; UTC es un valor técnico predeterminado, no una suposición sobre la ubicación.

## Funciones y ejemplos

Tareas: crear, listar, consultar, actualizar, completar y eliminar. Calendario: crear, listar, actualizar y eliminar eventos. Recordatorios: crear, listar y marcar como entregados localmente. Resumen diario, historial limitado, catálogo de herramientas y auditoría.

```text
create task: Revisar PR
list tasks
update task: 1 | Revisar tras CI
delete task: 1
create event: Reunión | 2026-11-08T10:00:00+00:00 | 2026-11-08T11:00:00+00:00 | UTC
list events
create reminder: Revisar CI | 2026-11-08T14:00:00+00:00
list reminders
daily summary: 2026-11-08 | UTC
```

El **modo demo** sólo acepta comandos predeterminados en inglés, pero sí ejecuta servicios y persistencia reales; no interpreta lenguaje natural abierto. Catálogo de 14 herramientas: `GET /api/tools`. OpenAPI documenta `/api/tasks`, `/api/events`, `/api/reminders`, `/api/chat`, `/api/summary`, `/api/history` y `/api/audit`.

## Aprobación humana, seguridad y privacidad

Actualizar o eliminar genera `approval_required`, con cambios propuestos, vencimiento, ID y token de un solo uso. La interfaz permite **Approve once** y **Reject**. El LLM nunca puede aprobar por sí solo ni recibe el token. Se bloquean aprobaciones vencidas, rechazadas o reutilizadas. Se rechaza HTTP remoto: **no publiques este proyecto sin autenticación**. No se implementan shell, archivos arbitrarios, URLs escogidas por el modelo, Gmail ni Google Calendar. Historial limitado por defecto a 30 días y limpiado al conversar; auditorías sin argumentos completos.

## LLM opcional y costos

Configura `PA_MODE=openai_compatible`, `PA_LLM_BASE_URL`, `PA_LLM_MODEL` y `PA_LLM_API_KEY` solamente si autorizas su uso. **Las llamadas al proveedor pueden tener costos**. Hay tool calling estructurado, validación Pydantic, tiempo máximo, límites de herramientas, tokens cuando el proveedor los facilita y manejo explícito de errores. La demo y CI no consumen API de pago.

## Pruebas y limitaciones

```bash
ruff check src tests scripts
ruff format --check src tests scripts
pytest
python scripts/evaluate.py
```

24 escenarios sintéticos deterministas con SQLite real; las métricas se calculan al ejecutar, no se inventan. GitHub Actions comprueba lint, formato, tipos de esquemas, API, aprobaciones, migraciones, evaluación y empaquetado. No hay despliegue, merge ni Codex Review automático.

**Limitaciones:** no existen notificaciones externas automáticas, integraciones con cuentas reales, scheduler permanente ni SaaS multiusuario. Demo con comandos fijos. Licencia MIT (© 2026 Ramon Rodriguez).
