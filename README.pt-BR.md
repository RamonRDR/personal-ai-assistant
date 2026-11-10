<div align="center">

# Personal AI Assistant 🧠

**Transforme solicitações do dia a dia em ações locais reais, com aprovação humana.**

[🇺🇸 English](README.md) · **🇧🇷 Português** · [🇪🇸 Español](README.es.md)

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

> **Status do projeto:** implementado no [PR #1 em rascunho](https://github.com/RamonRDR/personal-ai-assistant/pull/1), com verificações verdes no GitHub Actions na branch `feat/personal-ai-assistant-v1`. Aguardando autorização do proprietário para Codex Review; **sem merge, deploy ou conexão com contas pessoais**.

Assistente pessoal **local-first**, desenvolvido para demonstrar **backend Python, automação controlada, uso de ferramentas e integração prática de IA**. Ele executa operações reais por um catálogo restrito e auditável. A demonstração offline é determinística; um adaptador opcional de LLM permite tool calling estruturado quando ativado explicitamente.

## Visão geral

A interface web e a API REST utilizam os mesmos serviços de negócio e banco SQLite. Tarefas, compromissos, lembretes locais, histórico limitado de conversa, solicitações de aprovação humana e resultados de ferramentas são persistidos. O interpretador não afirma que uma operação foi realizada sem receber um resultado real.

O modo demo não exige serviço pago, conta externa nem processo agendador. Trata-se de um **aplicativo local para um usuário**, não de um SaaS exposto à internet.

## Funcionalidades

- Criar, listar, consultar, atualizar, concluir e excluir tarefas, com prioridade, prazo opcional e status.
- Criar, listar, atualizar e excluir compromissos com horários de início/fim e fusos explícitos.
- Criar, listar e marcar explicitamente lembretes locais como entregues; consultar pendências e resumos diários.
- Utilizar **14 ferramentas autorizadas**, com schemas Pydantic, classificação de risco e retornos estruturados.
- Exigir aprovação humana antes de editar/excluir tarefas e compromissos; token único, expiração, rejeição e auditoria.
- Acessar interface responsiva com chat, tarefas, compromissos, lembretes, aprovação e auditoria recente.
- Opcionalmente chamar um endpoint compatível com chat completions via `httpx`, com timeout e limite de ferramentas.
- Testar o adaptador com provedor de rede simulado; demo e CI **não chamam LLM pago**.

## Stack tecnológica

| Área | Tecnologia | Escopo confirmado |
| --- | --- | --- |
| Execução | Python 3.14 | Utilizado no GitHub Actions; `pyproject.toml` declara Python >=3.12 |
| API e servidor | FastAPI, Uvicorn | API REST, ASGI, OpenAPI e Swagger UI |
| Validação e configuração | Pydantic v2, Pydantic Settings | Schemas rigorosos e variáveis tipadas |
| Persistência | SQLAlchemy 2, SQLite, Alembic | ORM, banco local e migrações |
| Transporte de IA opcional | httpx | Adaptador configurável; provedor simulado nos testes |
| Interface | HTML, CSS, JavaScript puro | Interface local responsiva, sem React ou build Node |
| Qualidade | pytest, Ruff, mypy | Testes, lint/formatação e tipagem **apenas dos schemas** |
| Automação | GitHub Actions, Python build | CI hospedado, migrações, avaliações e empacotamento |

**Sobre as versões:** FastAPI `0.115+` é o mínimo declarado (`>=0.115,<1`), não uma versão exata instalada. Pydantic v2 e SQLAlchemy 2 representam faixas de versões principais. Uvicorn, httpx, Pydantic Settings, SQLite e Alembic não recebem versões exatas sem comprovação.

## Arquitetura

`Navegador local / REST → proteção local FastAPI → demo determinística ou adaptador opcional de LLM → gerenciador de ferramentas autorizadas → serviços de domínio → SQLAlchemy / SQLite`. Alterações sensíveis param na proposta de aprovação até confirmação humana com token de uso único. Resultados e histórico limitado são armazenados localmente.

Veja o [diagrama Mermaid, as decisões e o modelo de ameaças](docs/architecture.md).

## Pré-requisitos

- Python **3.14 recomendado** para reproduzir o CI; requisito do pacote: **Python >=3.12**.
- Suporte SQLite (via Python) e terminal para migrações locais.
- Não exige Docker, PostgreSQL, Redis, nuvem, conta Google ou API paga.

## Instalação

~~~bash
python -m venv .venv
source .venv/bin/activate            # Linux / macOS
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
cp .env.example .env                 # Opcional; Windows: copy .env.example .env
alembic upgrade head
~~~

Defina variáveis de ambiente antes de iniciar o servidor. O caminho padrão `./assistant.db` do SQLite é relativo ao diretório de execução.

## Configuração

| Variável | Finalidade | Padrão |
| --- | --- | --- |
| `PA_DATABASE_URL` | URL de conexão SQLAlchemy | `sqlite:///./assistant.db` |
| `PA_MODE` | `demo` ou `openai_compatible` | `demo` |
| `PA_TIMEZONE` | Fuso IANA explícito | `UTC` |
| `PA_HISTORY_LIMIT` | Mensagens carregadas no contexto do modelo | `12` |
| `PA_HISTORY_RETENTION_DAYS` | Remoção de mensagens antigas durante novas conversas | `30` |
| `PA_MAX_TOOL_CALLS` | Limite de chamadas de ferramentas por solicitação | `4` (máx. 8) |
| `PA_APPROVAL_TTL_SECONDS` | Prazo de expiração da aprovação | `600` |
| `PA_LLM_BASE_URL` / `PA_LLM_MODEL` / `PA_LLM_API_KEY` | Provedor opcional | Sem chave de API |

Consulte [.env.example](.env.example). Nunca publique o `.env` real nem credenciais.

## Executar localmente

~~~bash
personal-ai-assistant
~~~

O comando inicia Uvicorn em `127.0.0.1:8000`, nunca em `0.0.0.0`.

- **Interface demo:** http://127.0.0.1:8000/
- **Documentação interativa:** http://127.0.0.1:8000/docs
- **OpenAPI JSON:** http://127.0.0.1:8000/openapi.json
- **Saúde:** http://127.0.0.1:8000/health

## Exemplos de comandos do modo demo

O modo offline aceita uma **gramática fixa de comandos em inglês**, não linguagem natural livre. Os títulos podem estar em português, mas `create task:` e os demais prefixos permanecem em inglês.

~~~text
create task: Revisar meu pull request
list tasks
get task: 1
complete task: 1
update task: 1 | Revisar após CI
delete task: 1
create event: Reunião | 2026-11-08T10:00:00+00:00 | 2026-11-08T11:00:00+00:00 | UTC
list events
create reminder: Verificar CI | 2026-11-08T14:00:00+00:00
list reminders
daily summary: 2026-11-08 | UTC
~~~

Atualizar ou excluir retorna `approval_required` até uma decisão humana. O modo demo executa os **mesmos serviços reais do SQLite** utilizados pela API.

## API REST e catálogo de ferramentas

| Método | Endpoint | Operação |
| --- | --- | --- |
| GET | `/health`, `/docs`, `/openapi.json` | Saúde e documentação |
| GET / POST | `/api/tasks` | Listar / criar tarefas |
| GET / PATCH / DELETE | `/api/tasks/{task_id}` | Consultar / propor atualização / propor exclusão |
| POST | `/api/tasks/{task_id}/complete` | Concluir tarefa |
| GET / POST | `/api/events` | Listar / criar compromissos locais |
| PATCH / DELETE | `/api/events/{event_id}` | Propor atualização / exclusão |
| GET / POST | `/api/reminders` | Listar / criar lembretes |
| POST | `/api/reminders/{reminder_id}/deliver` | Marcar como entregue localmente |
| GET | `/api/summary?day=2026-11-08&timezone=UTC` | Resumo diário com fuso horário |
| GET | `/api/tools`, `/api/audit`, `/api/history` | Ferramentas, auditoria, histórico |
| GET | `/api/approvals` | Propostas pendentes (sem tokens) |
| POST | `/api/approvals/{id}/approve`, `/reject` | Decisão humana com token único |
| POST | `/api/chat` | Conversa demo ou LLM opcional |

~~~bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"create task: Documentar arquitetura"}'
~~~

**Catálogo (14):** `create_task`, `list_tasks`, `get_task`, `update_task`, `complete_task`, `delete_task`; `create_event`, `list_events`, `update_event`, `delete_event`; `get_daily_summary`; `create_reminder`, `list_reminders`, `deliver_reminder`. Os schemas e níveis de risco podem ser consultados em `GET /api/tools`.

## Aprovação humana (human-in-the-loop)

As ferramentas sensíveis (`update_task`, `delete_task`, `update_event`, `delete_event`) geram uma proposta com ID, alterações, validade e token de confirmação único. A interface local apresenta **Approve once** e **Reject**. Clientes REST enviam `{"confirmation_token":"..."}` ao endpoint da decisão. O token é armazenado como hash, não é enviado ao LLM e é consumido antes da execução. Aprovações inválidas, rejeitadas, vencidas ou reutilizadas não autorizam nova operação.

## LLM real opcional e custos

Para ativar conscientemente a seleção de ferramentas por modelo, configure:

~~~dotenv
PA_MODE=openai_compatible
PA_LLM_BASE_URL=https://api.openai.com/v1
PA_LLM_MODEL=gpt-4o-mini
PA_LLM_API_KEY=your-private-key
~~~

**O provedor poderá cobrar pelas chamadas.** O adaptador usa schemas de funções, validação dos argumentos, limite de ferramentas, timeout e informação de tokens quando fornecida. O caminho foi testado com **provedor simulado**, **não com LLM pago real**. Demo e CI obrigatórios não utilizam API paga.

## Testes automatizados e GitHub Actions

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

A reversão de migração (`alembic downgrade base`) ocorre com banco **descartável no CI**; não faça isso em banco que contenha dados importantes.

**Evidência:** a [execução #42477081665](https://github.com/RamonRDR/personal-ai-assistant/actions/runs/42477081665) registrou **29 aprovados, 0 falhas, 0 ignorados, 1 aviso** e **24/24 cenários sintéticos aprovados**. O aviso de depreciação vem de uma dependência de testes Starlette/httpx.

**Manutenção dos badges:** `pytest 29 passing` é um **registro estático** de execução confirmada. O CI gera `pytest-results.xml` e executa `scripts/check_readme_badges.py` para comparar a contagem real com os **três READMEs** e conferir a igualdade de badges e a quantidade de cenários. Se os testes mudarem, atualize os badges nas três traduções em um PR revisado; o CI **não comita** automaticamente. O badge de status do CI é dinâmico e aponta para `feat/personal-ai-assistant-v1` porque a `main` ainda não recebeu o workflow. Após o merge autorizado, ajuste o badge para `main`.

O CI usa runners do GitHub e verifica Ruff lint/format, mypy em `schemas.py`, pytest de API/segurança, Alembic upgrade/downgrade/re-upgrade, avaliações determinísticas, build e presença da UI no pacote. Sem revisão, deploy, publicação ou merge automático.

## Segurança e privacidade

Apenas conexões locais são permitidas, e a CLI escuta em localhost. O aplicativo **não tem autenticação** e **não deve ser exposto publicamente**. Não existem execução de shell, acesso arbitrário a arquivos, chamadas HTTP definidas pelo modelo, movimentações financeiras, Gmail nem Google Calendar reais. Uma ferramenta do LLM não pode conceder aprovação humana. Logs registram resultados, não argumentos brutos; propostas de aprovação ficam no SQLite local. O histórico padrão de 30 dias é limpo **durante novas mensagens**. Proteja o arquivo SQLite e seus backups.

Veja as [notas de arquitetura e segurança](docs/architecture.md).

## Limitações conhecidas

- Demo com comandos fixos, **não é IA conversacional aberta**.
- LLM externo é opcional e **não foi validado com provedor real** nesta versão.
- Lembretes são locais e consultáveis, **sem envio automático em segundo plano**.
- Não há autenticação de produção, multiusuário, scheduler, hospedagem remota ou criptografia em repouso.
- Build aprovado não equivale a teste visual completo em navegador nem a deploy.

## Estrutura do repositório

| Caminho | Responsabilidade |
| --- | --- |
| `src/personal_ai_assistant/api.py` | Rotas HTTP, proteção local e OpenAPI |
| `assistant.py`, `prompts/system.txt` | Interpretador demo e orquestração opcional do LLM |
| `tools.py`, `services.py` | Políticas das ferramentas e regras de negócio |
| `schemas.py`, `models.py`, `db.py`, `config.py` | Validação, modelos SQLAlchemy, sessões e configurações |
| `static/index.html`, `cli.py` | Interface local e inicialização do servidor |
| `alembic/` | Migrações |
| `tests/`, `evals/`, `scripts/` | Testes, cenários e verificação dos badges |
| `.github/workflows/ci.yml` | CI com permissão somente de leitura |
| `docs/architecture.md` | Mermaid, decisões e modelo de ameaças |

## Possíveis evoluções

Autenticação e integrações externas opcionais só deverão ser consideradas em uma **versão futura e revisada separadamente**. Nada disso está implementado aqui.

## Contribuições

Issues e propostas são bem-vindas. Execute os checks locais antes do pull request; não publique credenciais nem bases pessoais.

## Licença

[MIT](LICENSE) · Copyright (c) 2026 Ramon Rodriguez.
