---
name: fastapi
description: Set up, structure, and extend the project's FastAPI backend service — project layout, routers, Pydantic schemas, settings, domain logic, repositories, and database access. Use whenever creating the initial FastAPI project structure, adding a new endpoint/router, defining a request/response schema, configuring environment-based settings, writing aggregation logic, or wiring the database session layer.
metadata:
  project-version: "0.4.0"
  project-status: "proposed"
  project-category: "technology"
  project-scope: "backend"
  agent-agnostic: "true"
---

# FastAPI

## 1. Objective

Standardize how the project's FastAPI backend is structured and configured, so any team
member or agent produces consistent, decoupled code instead of ad hoc structures — directly
addressing the separation-of-concerns requirement that motivated the move away from Django.

## 2. Scope

Use this skill to:

- scaffold the initial FastAPI project structure;
- add a new router/endpoint for a resource (avaliações, professores, disciplinas);
- define Pydantic request/response schemas;
- configure environment-based settings;
- write domain logic (aggregation rules) and repository queries;
- wire the database session/connection layer.

Do not use it to:

- define product requirements or acceptance criteria (use `requirements`);
- create or change architectural decisions (use `architecture`);
- write Dockerfiles or `docker-compose.yml` (use `docker` — the entrypoint defined here must
  match that skill's `CMD`);
- implement SIGAA scraping logic (belongs to a future `integracao-sigaa` skill);
- write frontend code.

## 3. When to use

- Setting up or extending the FastAPI project structure.
- Adding a new API route or resource.
- Adding or editing a Pydantic schema.
- Implementing aggregation or other business rules in `app/domain/`.
- Configuring or reading environment variables/settings.
- Setting up or modifying the database session layer or a migration.

## 4. When not to use

- Deciding evaluation/domain business rules that are not yet specified in `specs.md`.
- Anything covered by the `docker` skill.
- Frontend code of any kind.

## 5. Expected inputs

1. which resource/entity the endpoint concerns;
2. HTTP method and path — the API contract is defined in `specs.md`, section 8;
3. expected request and response fields;
4. the aggregation or validation rules that apply, from `specs.md`.

If a rule is not specified in `specs.md` or in `docs/requisitos.md`, do not invent it.
Stop and record the gap (see Section 13).

Database-backed work must use the synchronous SQLAlchemy session layer defined in Step 4.

## 6. Pre-conditions

1. Python 3.12 + venv already set up.
2. All prior Django-specific files removed, preserving Git history.
3. `.env` file exists with required settings and is listed in `.gitignore`.
4. Dependencies declared in `requirements.txt`: `fastapi`, `uvicorn[standard]`, `pydantic`,
   `python-decouple`, `sqlalchemy`, `alembic`, and `psycopg2-binary`.
5. `specs.md` has been read for the entity or endpoint being implemented.
6. Authentication and session work follows the validated decision in `specs.md`, Section 7 ("Regras de identificação e sessão").

## 7. Procedure

### Step 1 — Project structure

```
backend/
├── app/
│   ├── main.py
│   ├── core/           # config, security, database session
│   ├── models/         # SQLAlchemy entities
│   ├── repositories/   # queries and persistence
│   ├── domain/         # business rules; no database dependency
│   ├── services/       # use cases, orchestration
│   ├── schemas/        # Pydantic
│   ├── routers/        # endpoints
│   └── scrapers/       # SIGAA import
├── alembic/            # migrations
├── tests/
├── requirements.txt
└── .env
```

The top-level `backend/` folder, mirrored by `frontend/`, makes the front/back separation
explicit in the repository — answering the professor's original concern.

`domain/` exists so that aggregation rules are unit-testable without an active database.
Keep it free of SQLAlchemy imports.

### Step 2 — Entry point (`app/main.py`)

```python
from fastapi import FastAPI
from app.routers import avaliacoes

app = FastAPI(title="G7 - Avaliação de Professores UnB")
app.include_router(avaliacoes.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

### Step 3 — Settings (`app/core/config.py`)

```python
from decouple import config

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
DATABASE_URL = config("DATABASE_URL")
```

Never read environment variables anywhere else.

### Step 4 — Database layer — Defined

Use **SQLAlchemy** as the ORM and **Alembic** for migrations, per ADR 01 in
`docs/arquitetura.md`. This supersedes the Tortoise ORM proposal from version `0.1.0` of
this skill. Use synchronous sessions with PostgreSQL and the `psycopg2` driver, as approved
during the review of PR #55 on 2026-09-11.

Read the required `DATABASE_URL` through `app/core/config.py`; do not load the same setting
independently in the session module. Use this format:

```text
postgresql+psycopg2://usuario:senha@host:porta/banco
```

Rules:

- every schema change goes through a versioned Alembic migration, committed to Git;
- manual DDL and ad hoc scripts are not permitted;
- the session lives in `app/core/`; routers never open sessions directly.

### Step 5 — Models (`app/models/`)

One file per domain entity, matching the data model in `docs/arquitetura.md`, section 4:
`avaliacao.py`, `usuario.py`, `professor.py`, `disciplina.py`, `turma.py`.

Constraints declared in `specs.md` — notably
`UNIQUE(usuario_id, professor_id, disciplina_id)` — must exist in the migration, not only
in application code.

### Step 6 — Repositories (`app/repositories/`)

All database queries live here. No query written inline in a router or service.

### Step 7 — Domain (`app/domain/`)

Aggregation rules and other pure business logic. Input: plain data. Output: plain data.
No database, no HTTP, no framework imports. These are the most error-prone rules in the
system and must be unit-testable in isolation.

### Step 8 — Schemas (`app/schemas/`)

Pydantic models for request/response validation. Never expose ORM models directly in a
response — always map to a schema.

### Step 9 — Routers (`app/routers/`)

One `APIRouter` per resource, included in `main.py` with a prefix and tags:

```python
from fastapi import APIRouter
router = APIRouter(prefix="/avaliacoes", tags=["avaliacoes"])
```

Routers only parse input, call a service, and format output.

### Step 10 — Run locally

```bash
uvicorn app.main:app --reload
```

## 8. Expected output

A running FastAPI app exposing `/health`, a Swagger UI at `/docs`, settings loaded from
`.env`, a working session layer, and migrations under `alembic/`.

## 9. Constraints

Never:

- hardcode secrets in code — always read via `app/core/config.py`;
- return SQLAlchemy model instances directly from an endpoint — always map to a schema;
- put business logic inside a router function — delegate to `app/services/` or `app/domain/`;
- import SQLAlchemy inside `app/domain/`;
- write a query outside `app/repositories/`;
- change the database schema outside an Alembic migration;
- implement a rule that is not specified in `specs.md` or `docs/requisitos.md`;
- create a general score field, composite index, or free-text field on Avaliacao — these are
  permanent product restrictions.

## 10. Human approval

Required to:

- make this skill `Defined`;
- change the ORM, migration tool, execution model, or PostgreSQL driver;
- change the project structure conventions team-wide;
- add a structural dependency not already listed in Section 6.

## 11. Verification

1. `uvicorn app.main:app --reload` starts without errors;
2. `/docs` loads and lists all registered endpoints;
3. `/health` returns `{"status": "ok"}`;
4. `alembic upgrade head` runs cleanly against an empty database;
5. domain rules have unit tests that run without a database;
6. a sample request against a new schema is correctly validated or rejected.

## 12. Interaction with other skills

- **`requirements`**: canonical source of requirements and acceptance criteria. This skill
  implements them; it does not define them.
- **`architecture`**: owns the layered structure and the ADRs this skill applies.
- **`implementation`**: governs how an authorized change is executed.
- **`testing`**: owns test strategy and execution.
- **`docker`**: the entrypoint defined here (`app.main:app`) must match that skill's `CMD`.
- **`skill-authoring`**: governs this skill's lifecycle.

## 13. Handling uncertainty and failures

If a rule needed for implementation is not specified:

1. do not invent it;
2. implement only the part that is specified;
3. record the gap and hand it off to `requirements`.

If database initialization fails, verify that `DATABASE_URL` is present and uses the
documented SQLAlchemy PostgreSQL format. Report the exact exception rather than substituting
another ORM, driver, or URL format.

If `uvicorn` fails to start, report the exact traceback rather than guessing — most failures
at this stage are a missing environment variable or an import error from an incomplete router.

If a migration conflicts, do not edit an applied migration. Create a new one.

## 14. Verification of this skill (per `skill-authoring` checklist)

- [x] directory name (`fastapi`) matches `name` in frontmatter;
- [x] `name` and `description` present, description states purpose and trigger context;
- [x] project-specific metadata under `metadata`;
- [x] does not duplicate rules owned by another skill (requirements, ADRs and Docker
      entrypoint are referenced, not repeated);
- [x] defined and pending decisions stated explicitly (Section 15);
- [x] approval boundaries stated (Section 10).

## 15. Decision status

### Defined

- ORM/database library: synchronous SQLAlchemy with PostgreSQL and `psycopg2`.
- Schema migrations: Alembic, with every schema change represented by a versioned migration.
- `DATABASE_URL` format: `postgresql+psycopg2://usuario:senha@host:porta/banco`.

### Pending Decision

- Whether the SIGAA scraper requires browser automation, which would add a structural
  dependency to the backend image.

## 16. Change history

- `0.4.0` — synchronous SQLAlchemy with `psycopg2` and the `DATABASE_URL` format recorded
  as approved; Alembic and the conventions introduced in `0.3.0` retained. Remains `proposed`.
- `0.3.0` — authentication session decision synchronized with `specs.md`: server-side
  sessions are no longer a pending decision in this skill. Remains `proposed`.
- `0.2.0` — ORM changed from the proposed Tortoise ORM to SQLAlchemy + Alembic (ADR 01);
  structure extended with `domain/`, `repositories/` and `scrapers/`; constraints aligned
  with `specs.md`. Remains `proposed`.
- `0.1.0` — initial proposal.
