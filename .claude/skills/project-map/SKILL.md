---
name: project-map
description: Compact map of the «Протокол совещаний» (Meeting Minutes) codebase — where things live, the stack, and the conventions — so you can orient without Glob/Grep/Explore sweeps. Use at the start of a task in D:\Meeting-Minutes_v3, when you need to know which file owns a feature, or when the user asks "где лежит X", "как устроен проект", "structure of the app". Read this before fanning out searches.
---

# Project map: Протокол совещаний (v2.7.0)

Self-hosted meeting-minutes web app (replaces an Excel workflow). One Docker image serves the API **and** the built Svelte SPA on `:8000`; **PostgreSQL** in a separate container (volume `protocol_postgres-data`). **Read this first** — it usually answers "where does X live?" without a search.

Repo root is `D:\Meeting-Minutes_v3` (the app lived in a `Protocol/` subfolder earlier — now it's the root). Compose project name is pinned to `protocol` (`name: protocol`), so volumes/containers are `protocol_*` regardless of folder name.

## Stack

- **Backend:** Python 3.12, FastAPI (async), SQLAlchemy 2.0 (`Mapped`/`mapped_column`, `selectinload`; **no lazy loading**), **asyncpg + PostgreSQL 16** (tests use in-memory SQLite via aiosqlite), Alembic, Pydantic v2. Package via `pyproject.toml`. Auth: python-jose JWT (HS256) + bcrypt directly (passlib is incompatible with bcrypt≥4). Rate-limit state in **Redis** (fallback in-memory).
- **Frontend:** SvelteKit, Svelte 5 **Runes** (`$state`/`$derived`/`$props`/`$bindable`/`$effect`), `adapter-static` (SPA), TypeScript, Tailwind (CSS vars + `data-theme` dark mode). Tests: **Vitest** (utils/stores/client).
- **Deploy:** multi-stage Docker (`node:20-alpine` builds frontend → `python:3.12-slim` serves). Local prod stack adds **nginx** (reverse-proxy, HTTPS via mkcert) + **redis**. See `DEPLOY.md`.

## Backend layout (`backend/app/`)

Layered: **routers → services → repositories → models**. `BaseRepository[T]` uses `flush()` not `commit()`.

| Path | Owns |
|------|------|
| `models/` | ORM tables: `item`, `status`, `department`, `executor`, `meeting`, `user`, `audit_log` + M2M `item_executor`, `meeting_participant` |
| `schemas/` | Pydantic request/response per entity + `common.py` (`PaginatedResponse`, `StateEnum`/`PriorityEnum`) |
| `repositories/` | DB queries; `_base_query()` with `selectinload`, filters, pagination |
| `services/` | Business logic: `item`, `status`, `meeting`, `department`, `executor`, `auth`, `csv`, `audit` |
| `routers/` | Endpoints under `/api`: `auth, users, departments, executors, items, meetings, statuses, export` (+ `import_router`) |
| `middleware/rate_limit.py` | Sliding-window rate-limit on `/api/auth/*`; Redis (ZSET) + in-memory fallback; real client IP from `X-Real-IP`/`X-Forwarded-For` |
| `dependencies.py` | Auth guards: `get_current_user` → `forbid_pending_password_change` → `require_editor` / `require_admin` |
| `security.py` | JWT create/decode (`iat`+`exp`+`type`), bcrypt hash/verify |
| `redis_client.py` | Lazy async Redis client (`get_redis()`/`close_redis()`); `None` when `REDIS_URL` unset |
| `logging_config.py` | Structured `logging` setup (`logger`, `configure_logging`) |
| `config.py` | `Settings` (env): `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `FIRST_ADMIN_*`, token TTLs, `ALLOWED_ORIGINS`, `RUN_MIGRATIONS_ON_STARTUP`, `DEBUG` |
| `database.py` | Async engine + `async_session` + `get_db` (commit/rollback) |
| `utils/` | `time.py` (`utcnow` naive UTC), `constants.py`, `identifiers.py` |
| `main.py` | App wiring, CORS, rate-limit middleware, router includes, `/health` + `/health/detailed`, SPA fallback, lifespan (migrations + first-admin seed + safety checks) |
| `alembic/versions/` | Migrations `0001` schema … `0007` audit_log — **idempotent** via `inspect` |

## Frontend layout (`frontend/src/`)

| Path | Owns |
|------|------|
| `lib/api/client.ts` | `apiGet/Post/Patch/Delete`, `apiPostForm`, **`apiDownload`** (authorized file download), Bearer header, 401→refresh→retry (deduped via `refreshInFlight`), `forceLogout` |
| `lib/api/{auth,items,meetings,export,...}.ts` + `types.ts` | Typed API modules + interfaces; `ROLE_LABEL` in `api/auth.ts` |
| `lib/stores/*.svelte.ts` | Runes stores: `auth`, `items` (+ `loaded` flag, bulk ops), `meetings`, `refs`, `filters`, `selection`, `theme`, `toast`, `confirm` |
| `lib/utils/` | `date`, `format`, `constants`, **`itemFilter`** (pure filter/sort logic, unit-tested) |
| `lib/components/` | `ui/` (Button, Input, Modal, Select, Loader…), `items/` (ItemsTable, ItemRow, ItemForm, ItemDrawer, Filters, BulkActions, ExecutorMultiSelect, Timeline…), `refs/`, `common/` |
| `routes/` | `+layout` (header/nav + auth-guard + reactive data-load via `$effect`), `+page` (tasks), `login/`, `change-password/`, `admin/` (users), `meetings/`, `refs/` |

## Data model (tables)

`items` (тема, ticket, priority, state, due_date, **`meeting_id`** nullable FK) · `statuses` (history, N:1) · `departments` · `executors` (`department_id`, optional `user_id` 1:1) · `meetings` (тема, дата, заметки + participants M2M) · `users` (roles, ФИО, email/phone, `must_change_password`) · `audit_log` (significant actions). Task↔executor M2M = `item_executors`; meeting↔executor = `meeting_participants`.

**The running stack has demo data** (100 items, 30 executors, 11 users — seeded via `scripts/seed_demo.py`). Don't wipe `protocol_postgres-data` without asking.

## Auth model

JWT access (30 min) + refresh (7 d, rotation) in localStorage. Roles: `viewer` (read) / `editor` (CRUD) / `admin` (+ user mgmt). Layered guards: GET → `get_current_user`; mutations → `require_editor`; whole admin router → `APIRouter(dependencies=[Depends(require_admin)])`. `forbid_pending_password_change` blocks everything except `/auth/*` until a forced password change is done. Brute-force protection: rate-limit on `/api/auth/login` (5/60) and `/refresh` (10/60) by real client IP.

## Workflow & deploy files

- **Branching:** features → `beta`, then squash-PR → `main` (stable); `beta` reset onto `main` after each release. See the `release-pr` skill. Versioning across 4 spots → the `bump-version` skill (version lives only in `main.py` `FastAPI(version=)` + `/health`, `pyproject.toml`, `package.json`). New tables/resources → the `new-entity` skill. Run/verify → the `run-protocol` skill.
- **Compose files:** `docker-compose.yml` (base, `8000:8000` + postgres + redis), `docker-compose.dev.yml` (hot reload, :5173 + :8000), `docker-compose.prod.yml` (`127.0.0.1`, `.env` required, + redis), `docker-compose.local-prod.yml` (**local prod: nginx 80/443 + HTTPS via mkcert, postgres, redis; backend not published**). Configs: `deploy/nginx.conf` (VPS), `deploy/nginx.local.conf` (local), `deploy/certs/` (mkcert, gitignored), `.env.example`, `DEPLOY.md`.
- **Verification (host has no Python/Node):** run ruff/pyright/pytest and svelte-check/vitest in throwaway Docker containers (`python:3.12-slim`, `node:20-alpine`).
- **Rules of the repo:** `CLAUDE.md` (CHANGELOG per change, Russian comments, branching, pre-PR checks). Audit & roadmap: `docs/AUDIT_v2.7.0.md`.
