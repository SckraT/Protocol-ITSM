---
name: new-entity
description: Scaffold a new domain entity (table + CRUD API + frontend) in «Протокол совещаний» following the project's strict layered pattern. Use whenever adding a new backend model/table with endpoints, a new resource like the existing Meeting/Item/Executor, or when the user says "добавь сущность", "новая модель", "новая таблица с CRUD", "add entity/resource". Saves re-reading the existing layers to infer the convention.
---

# New entity scaffold

The backend is rigidly layered: **`model → schema → repository → service → router → migration → registration`**. The frontend mirrors it: **`types → api → store → route`**. `Meeting` (v2.2) is the cleanest end-to-end reference — read those files as the template instead of guessing. This skill is the checklist so nothing is missed and you don't re-derive the pattern each time.

## Conventions that bite if ignored

- SQLAlchemy 2.0 style: `Mapped[...]` / `mapped_column`. **Lazy loading is forbidden** — eager-load relations with `selectinload` in the repository's `_base_query()`.
- `BaseRepository[T]` uses `flush()`, never `commit()` (the request/session lifecycle commits).
- Auth on every endpoint: **GET → `Depends(get_current_user)`**, **mutations → `Depends(require_editor)`**. A whole admin-only router → `APIRouter(dependencies=[Depends(require_admin)])` (see `routers/users.py`).
- Migrations are **idempotent**: guard with `inspect(bind).get_table_names()` / `get_columns()` before create/add. SQLite can't `ALTER ADD` an FK — add a plain column and rely on the ORM-level FK (see migration `0003`).
- Pydantic v2 response schemas: build them in the service's `_serialize_*()`; reuse `ExecutorInItem` etc. where it fits.

## Backend steps (reference files in parentheses)

1. **Model** — `backend/app/models/<entity>.py` (`models/meeting.py`). M2M? add a `Table` like `models/meeting_participant.py`.
2. **Register model** — import + `__all__` in `backend/app/models/__init__.py`.
3. **Schema** — `backend/app/schemas/<entity>.py` with `<Entity>Create` / `<Entity>Update` (all-optional) / `<Entity>Response` (`schemas/meeting.py`).
4. **Repository** — `backend/app/repositories/<entity>_repository.py` extending `BaseRepository`, with `_base_query()` (+ `selectinload`), `get_with_relations`, `list_with_filters` (`repositories/meeting_repository.py`).
5. **Service** — `backend/app/services/<entity>_service.py` with `_serialize_<entity>()` + CRUD (`services/meeting_service.py`).
6. **Router** — `backend/app/routers/<entity>.py`, `prefix="/<entities>"`, auth deps per method (`routers/meetings.py`).
7. **Register router** — import + `app.include_router(..., prefix="/api")` in `backend/app/main.py`.
8. **Migration** — `backend/alembic/versions/YYYYMMDD_000N_add_<entities>.py`, `down_revision` = previous, idempotent (`versions/20260603_0003_add_meetings.py`).
9. **FK on another table?** add the column + `selectinload` to that table's model/repo, plus its schema/serialize (how `Item.meeting_id` was added).

## Frontend steps

1. **Types** — add `<Entity>`, `<Entity>CreatePayload`, `<Entity>UpdatePayload` to `frontend/src/lib/api/types.ts`.
2. **API module** — `frontend/src/lib/api/<entities>.ts` using `apiGet/apiPost/apiPatch/apiDelete` from `client.ts` (`api/meetings.ts`). Don't hand-roll fetch.
3. **Store** — `frontend/src/lib/stores/<entities>.svelte.ts`, Runes class with `all = $state([])`, `load/create/update/remove`, toasts (`stores/meetings.svelte.ts`).
4. **Route** — `frontend/src/routes/<entities>/+page.svelte` (CRUD UI; `routes/meetings/+page.svelte`). Add to `navItems` in `+layout.svelte` and load the store in the layout's `onMount`.
5. Reuse UI: `Modal`, `Button`, `Input`, `confirmStore` (not native `confirm`), `ExecutorMultiSelect` (has a `label` prop).

## Finish

- `## [Unreleased]` entry in `CHANGELOG.md`.
- Verify: `cd frontend && npm run check` (0 errors) + `docker compose up -d --build` healthy + smoke test (see the `run-protocol` skill).
- Commit on `beta` (see the `release-pr` skill for the path to `main`).
