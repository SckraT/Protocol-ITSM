# Протокол совещаний — мультистейджевая сборка
# Stage 1: сборка фронтенда (Node.js)
# Stage 2: Python-бэкенд со встроенным фронтендом

# ── Stage 1: Frontend build ────────────────────────────────────────────────────
FROM node:20-alpine AS frontend

WORKDIR /app/frontend

# Копируем только package.json для кэширования слоя npm ci
COPY frontend/package*.json ./
RUN npm ci

# Копируем исходники и собираем
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Python backend ────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Копируем бэкенд целиком (app/ нужен setuptools для сборки пакета)
COPY backend/ ./backend/

# Установка пакета и зависимостей из pyproject.toml
RUN pip install --no-cache-dir ./backend

# Копируем собранный фронтенд как статику (Svelte build → dist/)
COPY --from=frontend /app/frontend/dist ./static/

# Переменные окружения (данные хранятся в PostgreSQL, локальный volume не нужен)
ENV PYTHONPATH=/app/backend

EXPOSE 8000

# Запуск сервера. Миграции применяются в lifespan приложения (единая точка,
# с прерыванием старта при сбое) — здесь повторно не запускаем.
CMD ["sh", "-c", "cd /app/backend && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
