# Инструкции по проекту «Протокол совещаний»

## Версионирование

При выпуске новой версии (новая запись в `CHANGELOG.md`) **обязательно** обновлять версию во всех местах:

- `backend/app/main.py` — `FastAPI(version="X.Y.Z")` **и** строка в эндпоинте `/health` (`{"status": "ok", "version": "X.Y.Z"}`)
- `backend/pyproject.toml` — `version = "X.Y.Z"`
- `frontend/package.json` — `"version": "X.Y.Z"`

Версия в `/health` должна соответствовать последней версии из `CHANGELOG.md`.

## Рабочий процесс

- На каждое изменение — запись в `CHANGELOG.md`.
- Комментарии в коде на русском, минимализм.
- Крупные изменения — через PR в `main` (squash-мердж, как #4/#5/#7).
- Проверка перед мерджем: `svelte-check` без ошибок, `docker compose build` + контейнер healthy.
