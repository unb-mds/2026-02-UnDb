---
name: docker
description: Write, review, and troubleshoot Dockerfiles, docker-compose files, and .dockerignore for this project's services (backend API, database, and frontend). Use whenever the team needs to containerize a service, set up a local Docker-based dev environment, debug a container build/run failure, or prepare a service for containerized deployment.
metadata:
  project-version: "0.1.1"
  project-status: "proposed"
  project-category: "technology"
  project-scope: "project-wide"
  agent-agnostic: "true"
---

# Docker

## 1. Objective

Standardize how project services are containerized so that any team member (or agent) can build, run, and debug the application in identical conditions, regardless of their host operating system.

## 2. Scope

Use this skill to:

- write a new `Dockerfile` for a project service;
- write or update `docker-compose.yml` to orchestrate multiple services (e.g. backend + database);
- write or update `.dockerignore`;
- troubleshoot container build or runtime failures;
- document the local Docker-based dev workflow.

Do not use it to:

- design CI/CD pipelines (belongs to a future `process`-category skill that will *reference* the Dockerfiles produced here);
- decide application-level architecture (routing, framework structure) — that belongs to the relevant `technology` skill for the framework in use;
- choose cloud hosting/production infrastructure, unless that decision has already been made and documented as `Defined` elsewhere.

## 3. When to use

- A service (backend, database, frontend) needs to run inside a container for the first time.
- An existing Dockerfile or compose file needs to change (new dependency, new port, new environment variable).
- `docker build` or `docker compose up` fails and needs debugging.
- Someone asks "how do I run this project with Docker?"

## 4. When not to use

- Pure application code changes with no impact on how the service is built or run.
- Questions about choosing application frameworks; consult the architectural decisions and the applicable technology skill.

## 5. Expected inputs

1. which service is being containerized (backend, database, frontend);
2. current stack for that service (e.g. Python version, framework, package manager);
3. target environment: local development or production;
4. existing `Dockerfile` / `docker-compose.yml`, if updating rather than creating;
5. required environment variables / secrets (names only, never values).

If any of these is unknown, mark it `Pending Decision` rather than assuming.

## 6. Pre-conditions

Before writing or changing container files:

1. confirm Docker Engine is installed on the machine that will build/run the containers;
2. confirm the service has a manifest listing its dependencies (e.g. `requirements.txt` or `pyproject.toml`);
3. confirm secrets are managed via `.env` and that `.env` is listed in `.gitignore` (already `Defined` project-wide — see the project's environment/secrets convention);
4. confirm which services must run together (single container vs. multi-service via Compose).

## 7. Procedure

### Step 1 — Identify the service and base image

Pick the smallest official base image that satisfies the service's runtime (e.g. `python:3.12-slim` for a Python/FastAPI backend). Avoid full/non-slim images unless a specific dependency requires it.

### Step 2 — Write the Dockerfile

Minimum structure for a Python backend service:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Adjust the `CMD` entrypoint to match the actual FastAPI app module once the project structure is defined.

### Step 3 — Write `.dockerignore`

Exclude at minimum: `venv/`, `__pycache__/`, `*.pyc`, `.git/`, `.env`, `*.log`.

### Step 4 — Write `docker-compose.yml` for multi-service setups

Example for backend + PostgreSQL:

```yaml
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - db

  db:
    image: postgres:16
    env_file: .env
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

The frontend stack is Next.js + Tailwind CSS, approved in #28 (ADR 02).
For execution/containerization and its approval state, consult
[`docs/arquitetura.md`, ADR 08](../../../docs/arquitetura.md#adr-08--execução-e-containerização-do-frontend)
and #36. Inspect the actual root Compose and Dockerfiles before applying this example;
the example is not the current project configuration.

### Step 5 — Build and run locally

```bash
docker compose up --build
```

### Step 6 — Verify

Confirm the backend responds on its expected port and, if applicable, that it can reach the database service by its service name (e.g. `db`, not `localhost`).

### Step 7 — Document

Add or update run instructions in the project `README.md` so any team member can start the environment with a single command.

## 8. Expected output

A working `Dockerfile` per service, a `.dockerignore`, and (when more than one service is involved) a `docker-compose.yml` — plus a short README section describing how to run them.

## 9. Constraints

Never:

- hardcode secrets or credentials inside a `Dockerfile` or `docker-compose.yml` (always use `env_file: .env`);
- commit `.env` to the repository;
- run multiple unrelated processes inside a single container without explicit justification;
- use a non-slim/non-official base image without a documented reason.

## 10. Human approval

Human approval is required to:

- make this skill `Defined` (authoritative);
- change the chosen base images project-wide;
- add a production-targeted Dockerfile/Compose file (as opposed to a local-dev one);
- change the database engine or its containerized configuration.

## 11. Verification

Before considering the work done:

1. `docker build` completes without errors;
2. `docker compose up` starts all defined services without crash loops;
3. the application is reachable on the expected port;
4. `docker history <image>` shows no secret values baked into layers;
5. `.env` is not present inside the built image.

## 12. Interaction with other skills

- **`skill-authoring`**: governs the lifecycle of this skill itself.
- **`fastapi`** (`technology`): consult its current status and guidance for the backend structure that the Dockerfile `CMD` must match.
- **Future CI/CD skill** (`process`, not yet created): will reference the Dockerfile(s) produced here to build images in GitHub Actions.

## 13. Handling uncertainty and failures

If the backend framework or frontend stack is not yet `Defined`:

1. do not invent the missing decision;
2. write only the Dockerfile(s) for services that are already decided;
3. mark the missing service's containerization as `Pending Decision`;
4. state clearly which human decision unblocks it.

If a container fails to build or run, report the exact error output rather than guessing at a fix, and check first whether the failure is due to a missing environment variable, a missing dependency in the manifest, or a port conflict.

## 14. Verification of this skill (per `skill-authoring` checklist)

- [x] directory name (`docker`) matches `name` in frontmatter;
- [x] `name` and `description` present;
- [x] `description` states both purpose and trigger context;
- [x] project-specific metadata is under `metadata`;
- [x] does not duplicate rules owned by another skill (env/secrets convention is referenced, not repeated);
- [x] pending decisions stated explicitly (Section 15);
- [x] approval boundaries stated (Section 10).

## 15. Open decisions (Pending Decision)

- Frontend execution/containerization: tracked only in #36 for epics #11 and #13; #32 was closed as duplicate. The stack is approved in #28; the implementation and architectural approval state are recorded in ADR 08. Do not infer approval from the presence of container files or promote this skill automatically.
- Whether a separate production Dockerfile/Compose file is needed before the November 25 release, or whether the dev configuration will be reused.
