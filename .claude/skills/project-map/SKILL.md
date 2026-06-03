---
name: project-map
description: Compact map of the «Протокол совещаний» (Meeting Minutes) codebase — where things live, the stack, and the conventions — so you can orient without Glob/Grep/Explore sweeps. Use at the start of a task in D:\Protocol, when you need to know which file owns a feature, or when the user asks "где лежит X", "как устроен проект", "structure of the app". Read this before fanning out searches.
---

# Project map: Протокол совещаний (v2.2.0)

Self-hosted meeting-minutes web app (replaces an Excel workflow). One Docker container serves the API **and** the built Svelte SPA on `:8000`. SQLite in a volume. **Read this first** — it usually answers "where does X live?" without a search.

## Stack

- **Backend:** Python 3.12, FastAPI (async), SQLAlchemy 2.0 (`Mapped`/`mapped_column`, `selectinload`; **no lazy loading**), aiosqlite, Alembic, Pydantic v2. Package via `pyproject.toml` (not requirements.txt). Auth: python-jose JWT (HS256) + bcrypt directly (passlib is incompatible with bcrypt≥4).
- **Frontend:** SvelteKit, Svelte 5 **Runes** (`$state`/`$derived`/`$props`/`$bindable`/`$effect`), `adapter-static` (SPA), TypeScript, Tailwind (CSS vars + `data-theme` dark mode).
- **Deploy:** multi-stage Docker (`node:20-alpine` builds frontend → `python:3.12-slim` serves). See `DEPLOY.md`.

## Backend layout (`backend/app/`)

Layered: **routers → services → repositories → models**. `BaseRepository[T]` uses `flush()` not `commit()`.

| Path | Owns |
|------|------|
| `models/` | ORM tables: `item`, `status`, `department`, `executor`, `meeting`, `user` + M2M `item_executor`, `meeting_participant` |
| `schemas/` | Pydantic request/response per entity + `common.py` (`PaginatedResponse`, enums) |
| `repositories/` | DB queries; `_base_query()` with `selectinload`, filters, pagination |
| `services/` | Business logic + `_serialize_*()` → response schemas |
| `routers/` | Endpoints under `/api`: `auth, users, departments, executors, items, meetings, statuses, export` |
| `dependencies.py` | Auth guards: `get_current_user` / `require_editor` / `require_admin` |
| `security.py` | JWT create/decode, bcrypt hash/verify |
| `config.py` | `Settings` (env): `SECRET_KEY`, `FIRST_ADMIN_*`, token TTLs, `DB_PATH` |
| `main.py` | App wiring, router includes, `/health`, first-admin seed on startup |
| `alembic/versions/` | Migrations `0001` schema, `0002` users, `0003` meetings — **idempotent** via `inspect` |

## Frontend layout (`frontend/src/`)

| Path | Owns |
|------|------|
| `lib/api/client.ts` | `apiGet/Post/Patch/Delete`, Bearer header, 401→refresh→retry, `forceLogout` |
| `lib/api/{auth,meetings,...}.ts` + `types.ts` | Typed API modules + interfaces; `ROLE_LABEL` lives in `api/auth.ts` |
| `lib/stores/*.svelte.ts` | Runes stores: `auth`, `items`, `meetings`, `refs`, `filters`, `theme`, `toast`, `confirm` |
| `lib/components/` | `ui/` (Button, Input, Modal, Select…), `items/` (ItemForm, ItemDrawer, Filters, ExecutorMultiSelect), `common/` |
| `routes/` | `+layout` (header/nav/auth-guard), `+page` (tasks), `login/`, `admin/` (users), `meetings/`, `refs/` |

## Data model (tables)

`items` (тема, ticket, priority, state, due_date, **`meeting_id`** nullable FK) · `statuses` (history, N:1) · `departments` · `executors` (`department_id`) · `meetings` (тема, дата, заметки + participants M2M) · `users` (roles). Task↔executor M2M = `item_executors`. **User has live data — never reset the DB.**

## Auth model

JWT access (30 min) + refresh (7 d) in localStorage. Roles: `viewer` (read) / `editor` (CRUD) / `admin` (+ user mgmt). GET → `get_current_user`; mutations → `require_editor`; whole-router admin → `APIRouter(dependencies=[Depends(require_admin)])`.

## Workflow & deploy files

- **Branching:** features → `beta`, then squash-PR → `main` (stable). See the `release-pr` skill. Versioning across 4 files → the `bump-version` skill. New tables/resources → the `new-entity` skill. Run/verify → the `run-protocol` skill.
- **Deploy:** `docker-compose.yml` (dev `8000:8000`), `docker-compose.dev.yml` (hot reload, :5173 + :8000), `docker-compose.prod.yml` (`127.0.0.1`, `.env` required), `deploy/nginx.conf`, `.env.example`, `DEPLOY.md`.
- **Rules of the repo:** `CLAUDE.md` (CHANGELOG per change, Russian comments, branching, pre-PR checks).
