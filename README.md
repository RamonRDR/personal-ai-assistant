<div align="center">

# Personal AI Assistant 🧠

**Turn everyday requests into real local actions, with human approval in control.**

**🇺🇸 English** · [🇧🇷 Português](README.pt-BR.md) · [🇪🇸 Español](README.es.md)

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

> **Project status:** Implemented on [draft PR #1](https://github.com/RamonRDR/personal-ai-assistant/pull/1), with passing GitHub Actions checks on `feat/personal-ai-assistant-v1`. Awaiting owner-authorized Codex Review; **not merged, deployed or connected to personal accounts**.

A local-first personal assistant designed to demonstrate reliable **Python backend development, controlled automation, tool calling and applied AI integration**. It performs real operations through a small, auditable catalog of tools. Its offline demonstration is deterministic, while an optional LLM adapter allows structured natural-language tool calling when explicitly enabled.

## Overview

The browser and REST API share the same business services and SQLite database. Tasks, appointments, local reminders, short conversation history, human approval requests and tool outcomes are persisted. The interpreter never claims that a task was created or deleted without a real tool result.

The default demo requires no paid provider, external account or background worker. This is a **single-user local development application**, not an internet-facing SaaS.

## Features

- Create, list, retrieve, update, complete and delete tasks, with priority, optional due date and status.
- Create, list, update and delete calendar events with timezone-aware start/end values.
- Create, list and explicitly mark local reminders delivered; inspect pending reminders and daily summaries.
- Use **14 allowlisted tools**, each with Pydantic input schemas, risk classification and structured outcomes.
- Require human approval for sensitive task and event edits/deletions, with one-time tokens, expiry, rejection and audit traces.
- Use a responsive local interface with chat, tasks, events, reminders, approval buttons and recent tool audit results.
- Optionally invoke an OpenAI-compatible chat-completions endpoint through `httpx`, bounded by request timeout and tool-call count.
- Test the adapter with a simulated network provider; the demo and CI make **no paid model calls**.

## Technology stack

| Area | Technology | Verified scope |
| --- | --- | --- |
| Runtime | Python 3.14 | Used in GitHub Actions; `pyproject.toml` declares Python >=3.12 |
| API and server | FastAPI, Uvicorn | REST endpoints, ASGI server, OpenAPI/Swagger UI |
| Validation and settings | Pydantic v2, Pydantic Settings | Strict schemas, typed environment configuration |
| Persistence | SQLAlchemy 2, SQLite, Alembic | ORM models, local data, versioned migrations |
| Optional AI transport | httpx | Operator-configured, optional LLM adapter; fake provider tested |
| Browser interface | HTML, CSS, vanilla JavaScript | Responsive static interface; no React or Node build |
| Quality | pytest, Ruff, mypy | Tests; lint/format; **schema-only** type check |
| Automation | GitHub Actions, Python build | Hosted-runner CI, migrations, evaluation, packaging |

**Version interpretation:** FastAPI `0.115+` represents its declared minimum (`>=0.115,<1`), not an exact resolved version. Pydantic v2 and SQLAlchemy 2 are declared major-version ranges. Uvicorn, httpx, Pydantic Settings, SQLite and Alembic are deliberately not assigned unverified exact installed versions.

## Architecture

`Local browser / REST → FastAPI loopback gate → deterministic demo or optional LLM adapter → allowlisted tool manager → domain services → SQLAlchemy / SQLite`. Sensitive operations stop at an approval proposal until a real human confirms the one-time token. Tool execution results and bounded conversation history are stored locally.

See the [Mermaid architecture diagram, ADRs and threat model](docs/architecture.md).

## Requirements

- Python **3.14 recommended** to match CI; package requirement **Python >=3.12**.
- SQLite support (through Python) and a terminal to run local migrations.
- No Docker, PostgreSQL, Redis, cloud services, Google account or paid API required.

## Installation

~~~bash
python -m venv .venv
source .venv/bin/activate           # Linux / macOS
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
cp .env.example .env                # Optional; Windows: copy .env.example .env
alembic upgrade head
~~~

Set environment values before running the server. The default SQLite path `./assistant.db` is relative to the current working directory.

## Configuration

| Environment variable | Meaning | Default |
| --- | --- | --- |
| `PA_DATABASE_URL` | SQLAlchemy database URL | `sqlite:///./assistant.db` |
| `PA_MODE` | `demo` or `openai_compatible` | `demo` |
| `PA_TIMEZONE` | Explicit IANA timezone | `UTC` |
| `PA_HISTORY_LIMIT` | Messages loaded into model context | `12` |
| `PA_HISTORY_RETENTION_DAYS` | Prune older messages on chat writes | `30` |
| `PA_MAX_TOOL_CALLS` | Limit real LLM tool invocations per request | `4` (max 8) |
| `PA_APPROVAL_TTL_SECONDS` | Approval expiration period | `600` |
| `PA_LLM_BASE_URL` / `PA_LLM_MODEL` / `PA_LLM_API_KEY` | Optional provider settings | No API key configured |

See [.env.example](.env.example). Never commit a real `.env` file or provider credentials.

## Run locally

~~~bash
personal-ai-assistant
~~~

The CLI starts Uvicorn on `127.0.0.1:8000`, never on `0.0.0.0`.

- **Demo UI:** http://127.0.0.1:8000/
- **Interactive API docs:** http://127.0.0.1:8000/docs
- **OpenAPI JSON:** http://127.0.0.1:8000/openapi.json
- **Health:** http://127.0.0.1:8000/health

## Example demo commands

The offline demo accepts a **fixed English command grammar**, not unrestricted natural language. Inputs can contain translated task titles, but commands such as `create task:` remain in English.

~~~text
create task: Review my pull request
list tasks
get task: 1
complete task: 1
update task: 1 | Review after CI
delete task: 1
create event: Demo | 2026-11-08T10:00:00+00:00 | 2026-11-08T11:00:00+00:00 | UTC
list events
create reminder: Review CI | 2026-11-08T14:00:00+00:00
list reminders
daily summary: 2026-11-08 | UTC
~~~

Updating or deleting records returns `approval_required` until a human decides. Demo commands execute the **same real SQLite services** as the HTTP API.

## REST API and tool catalog

| Method | Endpoint | Operation |
| --- | --- | --- |
| GET | `/health`, `/docs`, `/openapi.json` | Health and API documentation |
| GET / POST | `/api/tasks` | List / create tasks |
| GET / PATCH / DELETE | `/api/tasks/{task_id}` | Retrieve / propose update / propose delete |
| POST | `/api/tasks/{task_id}/complete` | Complete task |
| GET / POST | `/api/events` | List / create local events |
| PATCH / DELETE | `/api/events/{event_id}` | Propose update / delete |
| GET / POST | `/api/reminders` | List / create local reminders |
| POST | `/api/reminders/{reminder_id}/deliver` | Mark locally delivered |
| GET | `/api/summary?day=2026-11-08&timezone=UTC` | Timezone-aware daily summary |
| GET | `/api/tools`, `/api/audit`, `/api/history` | Tool catalog, audit, conversation history |
| GET | `/api/approvals` | Pending proposals (no confirmation tokens) |
| POST | `/api/approvals/{id}/approve`, `/reject` | Human decision with one-time token |
| POST | `/api/chat` | Demo or optional LLM conversation |

~~~bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"create task: Document architecture"}'
~~~

**Tool catalog (14):** `create_task`, `list_tasks`, `get_task`, `update_task`, `complete_task`, `delete_task`; `create_event`, `list_events`, `update_event`, `delete_event`; `get_daily_summary`; `create_reminder`, `list_reminders`, `deliver_reminder`. Schemas and risk levels are exposed via `GET /api/tools`.

## Human-in-the-loop approval

Sensitive tools (`update_task`, `delete_task`, `update_event`, `delete_event`) first produce a proposal with an approval ID, proposed changes, expiry and a one-time confirmation token. The local browser offers **Approve once** and **Reject**. API clients send `{"confirmation_token":"..."}` to the corresponding decision endpoint. The token is hashed at rest, not sent to the LLM, and is consumed before execution. Invalid, rejected, expired and reused approvals cannot authorize a new operation.

## Optional real LLM and costs

To deliberately enable model-based tool selection, configure:

~~~dotenv
PA_MODE=openai_compatible
PA_LLM_BASE_URL=https://api.openai.com/v1
PA_LLM_MODEL=gpt-4o-mini
PA_LLM_API_KEY=your-private-key
~~~

**Provider calls may cost money.** The optional adapter uses structured function schemas, argument validation, bounded tool calls, timeout handling and token usage when reported by the provider. The code path has been tested with a **simulated provider**, **not a live paid LLM**. The default offline demo and mandatory CI avoid paid APIs.

## Automated tests and GitHub Actions

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

The migration rollback check (`alembic downgrade base`) is run against a **throwaway CI database**; do not execute it against a database containing data you need.

**Evidence:** [CI run #42477081665](https://github.com/RamonRDR/personal-ai-assistant/actions/runs/42477081665) on the development branch recorded **29 passed, 0 failed, 0 skipped, 1 warning** and **24/24 synthetic scenarios passed**. The warning comes from a third-party Starlette/httpx test-client deprecation notice.

**Badge maintenance:** The `pytest 29 passing` badge is a **static snapshot** of that run, not a live test counter. CI generates `pytest-results.xml` and runs `scripts/check_readme_badges.py` to compare the observed passing count with **all three READMEs**. It also checks that badge sets and scenario counts match. Future changes to the test suite require updating the badges together in a reviewed PR; CI does **not** commit to the repository. The CI status badge is dynamic and currently points to `feat/personal-ai-assistant-v1` because `main` has not received this workflow. Once merged, update the badge to track `main`.

GitHub-hosted CI runs Ruff lint/format, mypy on `schemas.py`, pytest API/security tests, Alembic upgrade/downgrade/re-upgrade, deterministic evaluation, package build and packaged UI verification. No automatic review, deploy, publication or merge occurs.

## Security and privacy

Only loopback peers are accepted, and the CLI binds localhost. The app **has no login/authentication**, so it must **not** be exposed publicly. No shell execution, arbitrary file access, user-directed HTTP tools, banking actions, real Gmail or Google Calendar integrations exist. Human approval cannot be granted by an LLM tool. Audit logs record operation outcomes rather than raw arguments; pending approval proposals are stored in the local database. Chat retention defaults to 30 days and is pruned **when new chat exchanges occur**. Secure the local DB file and backup copies yourself.

See [architecture and security notes](docs/architecture.md).

## Known limitations

- Offline demo is a limited command interpreter, **not open-ended AI**.
- Live provider calls are optional and **not independently validated** in this version.
- Reminders are local and pollable, **not automatically pushed** in the background.
- No production authentication, multi-user tenancy, scheduler, remote hosting or encrypted-at-rest store.
- A successful package build is not an end-to-end visual browser test or a deployment.

## Repository structure

| Path | Responsibility |
| --- | --- |
| `src/personal_ai_assistant/api.py` | HTTP routes, local access control, OpenAPI |
| `assistant.py`, `prompts/system.txt` | Deterministic parser and optional LLM orchestration |
| `tools.py`, `services.py` | Tool risk gates and domain operations |
| `schemas.py`, `models.py`, `db.py`, `config.py` | Validation, SQLAlchemy models, sessions and settings |
| `static/index.html`, `cli.py` | Local interface and server entry point |
| `alembic/` | Database migrations |
| `tests/`, `evals/`, `scripts/` | Tests, scenarios, reproducible badge verification |
| `.github/workflows/ci.yml` | Read-only, hosted-runner validation |
| `docs/architecture.md` | Mermaid diagram, decisions, threat model |

## Possible future improvements

Authentication and opt-in external integrations could be explored **only in a separately reviewed release**. Neither is implemented here.

## Contributions

Issues and proposed changes are welcome. Run the local checks before submitting a pull request; do not commit real credentials or personal datasets.

## License

[MIT](LICENSE) · Copyright (c) 2026 Ramon Rodriguez.
