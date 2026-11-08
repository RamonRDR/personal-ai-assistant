# Personal AI Assistant

[![CI](https://github.com/RamonRDR/personal-ai-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/RamonRDR/personal-ai-assistant/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.14-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**English** | [Português](README.pt-BR.md) | [Español](README.es.md)

A **local-first tool-using assistant**, not a pretend chatbot. It persists tasks, calendar events, reminders, approval requests and a limited message history in SQLite. Sensitive mutations are proposed, never applied, until a human approves them with a single-use expiring token.

## Features

- FastAPI REST/OpenAPI with SQLAlchemy 2, Pydantic v2 and Alembic migrations.
- 14 allowlisted tools with runtime schemas and risk classification.
- Real task and event CRUD; reminders are **local records**, not push notifications.
- Human-in-the-loop for edit/delete, including reject, expiry, one-time consumption and audit entries.
- Deterministic interactive demo without credentials, plus an **optional** OpenAI-compatible HTTP tool-calling adapter.
- Python 3.14 GitHub Actions: Ruff, mypy schema check, pytest API integration, migrations, synthetic evaluation, packaging.
- Loopback-only HTTP middleware and a loopback-bound CLI. **Do not deploy this as a public service.**

## Quick start

Requires Python 3.14 (package minimum: Python 3.12) and a local environment:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
cp .env.example .env          # Optional; Windows: copy .env.example .env
alembic upgrade head
personal-ai-assistant
```

Open **http://127.0.0.1:8000/** for a responsive demo, **/docs** for OpenAPI and **/health** for health status. The server listens on 127.0.0.1 only. Set `PA_TIMEZONE` explicitly to your IANA timezone; default UTC is a system convention, not a guess about the user.

## Demo conversation (real SQLite operations)

```text
create task: Review my pull request
list tasks
update task: 1 | Review after CI       # Requires human approval
delete task: 1                        # Requires human approval
create event: Demo | 2026-11-08T10:00:00+00:00 | 2026-11-08T11:00:00+00:00 | UTC
list events
create reminder: Review results | 2026-11-08T14:00:00+00:00
list reminders
daily summary: 2026-11-08 | UTC
```

Demo mode supports only listed patterns. It **does not** understand arbitrary natural language; for that, configure a real LLM adapter. Demo requests still call the same actual business services and persist to disk.

## REST and tool calling

Typical REST endpoints: `GET/POST /api/tasks`, `PATCH/DELETE /api/tasks/{id}`, `GET/POST /api/events`, `GET/POST /api/reminders`, `POST /api/chat`, `GET /api/tools`, `GET /api/summary?day=2026-11-08&timezone=UTC`, `GET /api/audit`, `GET /api/history`.

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"create task: Document architecture"}'
```

Tool registry: `create_task`, `list_tasks`, `get_task`, `update_task`, `complete_task`, `delete_task`, `create_event`, `list_events`, `update_event`, `delete_event`, `get_daily_summary`, `create_reminder`, `list_reminders`, `deliver_reminder`. Schemas are Pydantic-generated. All tools validate arguments and return structured status and actual data.

## Human approval

`update_task`, `delete_task`, `update_event`, `delete_event` return `approval_required` with the proposed changes, expiry, approval ID and a one-time human confirmation token. The browser renders **Approve once** / **Reject**; the API accepts `POST /api/approvals/{id}/approve` or `/reject` with `{"confirmation_token":"..."}`. No LLM tool has access to these approval routes or their confirmation tokens. Approval claims are atomically consumed before a sensitive operation; expired, rejected, repeated and invalid-token attempts cannot execute.

## Optional real LLM

Only deliberately opting in and supplying an API credential enables model calls:

```dotenv
PA_MODE=openai_compatible
PA_LLM_BASE_URL=https://api.openai.com/v1
PA_LLM_MODEL=gpt-4o-mini
PA_LLM_API_KEY=your-private-key
```

**Real LLM requests may incur provider charges.** No such calls occur in the demo or CI. Provider responses use explicit `tools` definitions, JSON argument validation, timeouts, a maximum of four tool calls (configurable up to eight), usage fields when provided, and sanitized failures. The provider endpoint is an operator setting, never a user/model tool argument. The browser shows real tool outcomes. If the provider fails, the system reports failure.

## Security and privacy

The local demo has **no user authentication**. HTTP requests from remote peers are rejected. No Gmail, Google Calendar, bank account, shell, arbitrary filesystem or untrusted-URL network tools are implemented. The model can never authorize itself. Tool invocations and outcomes are recorded without raw arguments in audit logs; pending approvals contain proposed arguments and message history is limited to 30 days by default, pruned on chat interactions. SQLite and local backups remain under your control. Do not store sensitive real-world information in a public demo.

Threat model, architecture and known limitations: [Technical notes](docs/architecture.md).

## Tests, migrations and evaluation

```bash
ruff check src tests scripts
ruff format --check src tests scripts
pytest
python scripts/evaluate.py
alembic downgrade base && alembic upgrade head  # destructive to local data
python -m build
```

`evals/scenarios.json` has **24 synthetic cases**, run against actual local tools in fresh SQLite databases. The evaluation script prints results when executed; this README does not claim any unevaluated score. CI uses standard GitHub-hosted runners, no paid credentials, no automatic deployment or merge. The final Codex Review is intentionally **not** part of CI and must be explicitly requested by the repository owner.

### Current limitations

- Only local tasks/events/reminders, no integration with real personal accounts.
- No automatic external reminder delivery or always-on scheduler. Reminders are polled in the UI and can be marked delivered.
- Deterministic demo is a fixed command interpreter, not conversational AI.
- Not hardened as a multi-user SaaS; no authentication, encryption at rest, distributed locking or production hosting.
- LLM evaluation requires a separately authorized provider and is not claimed by deterministic CI.

## License

MIT. Copyright © 2026 Ramon Rodriguez.
