# Personal AI Assistant

[English](README.md) | **Português** | [Español](README.es.md)

Assistente pessoal **local**, com execução real de ferramentas, SQLite, agenda, lembretes e aprovação humana para alterações sensíveis. Não é apenas um chatbot simulando ações.

## Tecnologias e arquitetura

Python 3.14 (mínimo do pacote: 3.12), FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, SQLite, httpx, pytest, Ruff, mypy e GitHub Actions. A arquitetura separa API, schemas, serviços, ferramentas, adaptador opcional de LLM, aprovações e interface. Veja o [diagrama e as decisões técnicas](docs/architecture.md).

## Instalação e execução

```bash
python -m venv .venv
source .venv/bin/activate # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
cp .env.example .env # opcional; no Windows use copy
alembic upgrade head
personal-ai-assistant
```

Interface: http://127.0.0.1:8000/ · OpenAPI: http://127.0.0.1:8000/docs · saúde: `/health`. Executa somente em localhost. Configure explicitamente o fuso IANA em `PA_TIMEZONE`; UTC é o padrão técnico, não uma inferência da localização.

## Funcionalidades e exemplos

Tarefas: criar, listar, consultar, atualizar, concluir e excluir. Agenda: criar, listar, atualizar e excluir compromissos. Lembretes: criar, listar e marcar como entregues localmente. Resumo diário, histórico limitado, catálogo de ferramentas e auditoria.

```text
create task: Revisar PR
list tasks
update task: 1 | Revisar após CI
delete task: 1
create event: Reunião | 2026-11-08T10:00:00+00:00 | 2026-11-08T11:00:00+00:00 | UTC
list events
create reminder: Verificar CI | 2026-11-08T14:00:00+00:00
list reminders
daily summary: 2026-11-08 | UTC
```

O **modo demo** aceita comandos predeterminados em inglês, mas executa serviços e persistência reais. Não possui compreensão livre de linguagem natural. O catálogo de 14 ferramentas é acessível em `GET /api/tools`. A API REST documentada pelo FastAPI inclui `/api/tasks`, `/api/events`, `/api/reminders`, `/api/chat`, `/api/summary`, `/api/history` e `/api/audit`.

## Aprovação humana e segurança

Atualizações e exclusões geram `approval_required`, com alterações propostas, validade, ID e token de uso único. A interface oferece **Approve once** e **Reject**. O LLM não tem ferramenta para aprovar nem recebe o token de confirmação. Autorizações expiradas, rejeitadas ou reutilizadas são bloqueadas. Rotas HTTP remotas são recusadas; **não publique este app sem autenticação**. Não há execução de shell, arquivos arbitrários, URLs escolhidas pelo modelo, Gmail ou Calendar reais. Histórico limitado a 30 dias por padrão, com limpeza durante novas conversas; logs não gravam parâmetros brutos.

## LLM opcional e custos

Configure `PA_MODE=openai_compatible`, `PA_LLM_BASE_URL`, `PA_LLM_MODEL` e `PA_LLM_API_KEY` somente por decisão consciente: **chamadas reais podem ser cobradas**. O adaptador usa tool calling estruturado, validação Pydantic, timeouts, limites de chamadas, custos/tokens quando fornecidos pelo provedor e falhas explícitas. Modo demo e CI não fazem chamadas pagas.

## Qualidade, testes e limitações

```bash
ruff check src tests scripts
ruff format --check src tests scripts
pytest
python scripts/evaluate.py
```

24 cenários sintéticos determinísticos em SQLite real; resultados são impressos após execução, não presumidos. O GitHub Actions valida lint, formatação, tipos dos schemas, API, aprovações, migrações, avaliações e empacotamento. Sem deploy, merge ou Codex Review automático.

**Limitações:** nenhuma notificação externa automática, integração com contas pessoais, scheduler contínuo ou SaaS multiusuário. Demo com comandos fixos. A licença é MIT (© 2026 Ramon Rodriguez).
