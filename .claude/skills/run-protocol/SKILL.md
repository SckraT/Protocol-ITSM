---
name: run-protocol
description: Run Meeting Minutes (Протокол совещания) web app with Docker and verify via smoke tests
---

# Run: Meeting Minutes (Протокол совещания) v2.0

FastAPI (async SQLAlchemy ORM) + SQLite backend with a **Svelte 5 SPA** frontend. In production a single Docker container serves both on `localhost:8000` (the built Svelte app is baked into `static/`). Data persists in a SQLite volume. Architecture is layered: `backend/app/` → routers → services → repositories → models.

**Agent path:** Run the smoke-test driver (`.claude/skills/run-protocol/driver.sh`) after launching the Docker container. It verifies `/health`, the SPA loads, and the API endpoints respond with the expected v2 shapes.

## Prerequisites

- Docker Desktop (or Docker + Docker Compose on Linux)
- Bash shell
- `curl` command-line tool

**Install (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose curl
sudo systemctl start docker
sudo usermod -aG docker $USER  # Allow docker without sudo
```

## Build & Setup

```bash
cd D:\Protocol  # or wherever the project is
docker compose build
```

This builds the image from `Dockerfile` (multi-stage):
- Stage 1 (node:20-alpine): builds the Svelte frontend → `frontend/dist`
- Stage 2 (python:3.12-slim): installs the backend package from `backend/pyproject.toml`, copies the built frontend into `static/`
- Runs Alembic migrations on startup, then `uvicorn app.main:app`
- Mounts `./data/` volume for the persistent SQLite database

## Run (Agent Path)

**1. Start the container:**
```bash
docker compose up -d
```

**2. Wait for readiness (optional, fast):**
```bash
sleep 2  # Docker usually starts in < 1 sec
```

**3. Run the smoke-test driver:**
```bash
bash .claude/skills/run-protocol/driver.sh
```

The driver checks:
- `/health` returns `{"status":"ok",...}`
- SPA loads at `http://localhost:8000/`
- `/api/items` returns a `PaginatedResponse` (`{items, total, page, page_size}`)
- `/api/departments` and `/api/executors` return reference data
- Exit code 0 on all passes

**4. Access the app:**
- **Web UI:** http://localhost:8000/
- **API base:** http://localhost:8000/api/
- **Swagger UI:** http://localhost:8000/api/docs
- **Health:** http://localhost:8000/health

**Stop the container:**
```bash
docker compose down
```

## Run (Human Path)

For manual exploration:

```bash
# Start in the background
docker compose up -d

# Watch logs
docker compose logs -f

# Open browser to http://localhost:8000
# Ctrl+C to stop logs

# Bring down
docker compose down
```

## Direct API Calls

Test specific endpoints without the UI:

```bash
# Get all tasks
curl http://localhost:8000/api/items

# Get departments (reference data)
curl http://localhost:8000/api/departments

# Get executors (reference data)
curl http://localhost:8000/api/executors

# Export as CSV
curl -o protocol.csv http://localhost:8000/api/export/csv
```

## Gotchas

1. **Container name collision:** If another app is using port 8000, the container won't start. Either `docker compose down` the other app or change `ports: ["8000:8000"]` in `docker-compose.yml`.

2. **Volume persistence:** Data in `./data/protocol.db` survives `docker compose down`. To reset:
   ```bash
   rm -f data/protocol.db
   docker compose up -d
   ```

3. **Windows path issues:** On Windows (PowerShell), use forward slashes in docker commands or prepend with `& "docker compose"`.

4. **First startup:** The database initializes on first run (migrations run automatically). This is fast (< 100ms).

5. **Dev mode with hot reload:** For active development use the dev compose file — backend on :8000 (`uvicorn --reload`), Svelte dev server on :5173 (HMR):
   ```bash
   docker compose -f docker-compose.dev.yml up
   ```
   Open http://localhost:5173 (frontend) — it proxies/calls the API on :8000.
   For production-style rebuilds: `docker compose up -d --build`.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `docker: command not found` | Install Docker Desktop or `apt-get install docker.io` |
| Container won't start / exits immediately | Check logs: `docker compose logs` |
| Port 8000 already in use | `lsof -i :8000` to find process; `docker compose down` to stop this app |
| Smoke test fails on API endpoints | Wait a moment (`sleep 3`); the container may still be initializing |
| Database locked errors in app logs | Stop all containers, remove volume, restart: `docker compose down -v && docker compose up -d` |

## Testing

The smoke-test driver (`driver.sh`) is the primary agent verification. No separate test suite is needed for basic operation checks.

For deeper testing, the backend supports CSV import/export:
```bash
curl -o test.csv http://localhost:8000/api/export/csv
curl -F file=@test.csv http://localhost:8000/api/import/csv
```
