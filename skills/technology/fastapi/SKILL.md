---
name: fastapi
description: Set up, structure, and extend the project's FastAPI backend service — project layout, routers, Pydantic schemas, settings, and database access. Use whenever creating the initial FastAPI project structure, adding a new endpoint/router, defining a request/response schema, configuring environment-based settings, or wiring the database session layer.
metadata:
  project-version: "0.2.0"
  project-status: "proposed"
  project-category: "technology"
  project-scope: "backend"
  agent-agnostic: "true"
---

# FastAPI

## 1. Objective

Standardize how the project's FastAPI backend is structured and configured, so any team member or agent produces consistent, decoupled code instead of ad hoc structures — directly addressing the separation-of-concerns requirement that motivated the move away from Django.

## 2. Scope

Use this skill to:

- scaffold the initial FastAPI project structure;
- add a new router/endpoint for a resource (e.g. avaliações, usuários, turmas);
- define Pydantic request/response schemas;
- configure environment-based settings;
- wire the database session/connection layer.

Do not use it to:

- implement domain-specific business rules (belongs to a future `engineering`-category skill, e.g. moderation logic, rating aggregation);
- write Dockerfiles or `docker-compose.yml` (use the `docker` skill — the entrypoint defined here must match what that skill's `CMD` expects);
- implement SIGAA scraping logic (belongs to a future `integracao-sigaa` skill);
- write frontend code.

## 3. When to use

- Setting up the FastAPI project for the first time (post Django removal).
- Adding a new API route or resource.
- Adding or editing a Pydantic schema.
- Configuring or reading environment variables/settings.
- Setting up or modifying the database session layer.

## 4. When not to use

- Deciding evaluation/domain business rules unrelated to API structure.
- Anything covered by the `docker` skill.
- Frontend code of any kind.

## 5. Expected inputs

1. which resource/entity the endpoint concerns;
2. HTTP method and path;
3. whether the endpoint needs database access;
4. expected request and response fields.

Database-backed work must use the SQLAlchemy session layer defined in Step 4.

## 6. Pre-conditions

1. Python 3.12 + venv already set up.
2. All prior Django-specific files removed via a dedicated migration branch (e.g. `chore/migrate-to-fastapi`), preserving Git history.
3. `.env` file exists with required settings and is listed in `.gitignore` (project-wide convention, already `Defined`).
4. Dependencies declared in `requirements.txt`: `fastapi`, `uvicorn[standard]`, `pydantic`, `python-decouple`, `sqlalchemy`, and `psycopg2-binary`.

## 7. Procedure

### Step 1 — Project structure (Proposed)

```
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   └── services/
├── requirements.txt
└── .env
```

A top-level `backend/` folder (mirrored later by a top-level `frontend/` folder) makes the front/back separation visually explicit in the repository — directly answering the professor's original concern.

### Step 2 — Entry point (`app/main.py`)

```python
from fastapi import FastAPI
from app.routers import avaliacoes

app = FastAPI(title="G7 - Avaliação de Disciplinas")
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

### Step 4 — Database layer (`app/db/`) — Defined

Use synchronous **SQLAlchemy** models and sessions with PostgreSQL. The team approved this choice during the review of PR #55 on 2026-09-11. Read the required `DATABASE_URL` through `app/core/config.py`; do not load the same setting independently in the session module.

Use this URL format with the approved `psycopg2` driver:

```text
postgresql+psycopg2://usuario:senha@host:porta/banco
```

### Step 5 — Models (`app/models/`)

One file per domain entity, mirroring the previously agreed data model (e.g. `avaliacao.py`, `usuario.py`, `turma.py`).

### Step 6 — Schemas (`app/schemas/`)

Pydantic models for request/response validation. Never expose ORM models directly in a response — always map to a schema.

### Step 7 — Routers (`app/routers/`)

One `APIRouter` per resource, included in `main.py` with a prefix and tags:

```python
from fastapi import APIRouter
router = APIRouter(prefix="/avaliacoes", tags=["avaliacoes"])
```

### Step 8 — Run locally

```bash
uvicorn app.main:app --reload
```

## 8. Expected output

A running FastAPI app exposing `/health`, a Swagger UI at `/docs`, settings loaded from `.env`, and a working SQLAlchemy database session layer.

## 9. Constraints

Never:

- hardcode secrets in code — always read via `app/core/config.py`;
- return SQLAlchemy model instances directly from an endpoint — always map to a Pydantic schema;
- put business logic directly inside a router function — delegate to `app/services/`.

## 10. Human approval

Required to:

- make this skill `Defined`;
- confirm the `backend/` + `frontend/` top-level folder split;
- change the project structure conventions team-wide.

## 11. Verification

1. `uvicorn app.main:app --reload` starts without errors;
2. `/docs` loads and lists all registered endpoints;
3. `/health` returns `{"status": "ok"}`;
4. a sample request against a new schema is correctly validated or rejected.

## 12. Interaction with other skills

- **`docker`**: the entrypoint defined here (`app.main:app`) must match that skill's `CMD`.
- **`skill-authoring`**: governs this skill's lifecycle.
- **Future domain/engineering skill**: will define business rules inside `app/services/`.

## 13. Handling uncertainty and failures

If database initialization fails, verify that `DATABASE_URL` is present and uses
the documented SQLAlchemy PostgreSQL format. Report the exact exception rather
than substituting another ORM, driver, or URL format.

If `uvicorn` fails to start, report the exact traceback rather than guessing — most failures at this stage are a missing environment variable or an import error from an incomplete router.

## 14. Verification of this skill (per `skill-authoring` checklist)

- [x] directory name (`fastapi`) matches `name` in frontmatter;
- [x] `name` and `description` present, description states purpose and trigger context;
- [x] project-specific metadata under `metadata`;
- [x] does not duplicate rules owned by another skill (Docker entrypoint referenced, not repeated);
- [x] defined and pending decisions stated explicitly (Section 15);
- [x] approval boundaries stated (Section 10).

## 15. Decision status

### Defined

- ORM/database library: synchronous SQLAlchemy with PostgreSQL and `psycopg2`.
- `DATABASE_URL` format: `postgresql+psycopg2://usuario:senha@host:porta/banco`.

### Pending Decision

- `backend/` + `frontend/` top-level folder split (proposed, needs team sign-off).
- Naming convention: domain entities proposed in Portuguese (matching the existing data model), technical scaffolding (routers, schemas) in English (matching FastAPI/Python ecosystem convention).
