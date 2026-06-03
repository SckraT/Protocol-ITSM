---
name: bump-version
description: Bump the project version of «Протокол совещаний» across all required files (backend main.py FastAPI version + /health, backend pyproject.toml, frontend package.json) and verify it matches the latest CHANGELOG entry. Use whenever releasing a new version, cutting a release, or when the user says "подними версию", "bump version", "новая версия X.Y.Z", or asks to sync version numbers.
---

# Bump version

Per `CLAUDE.md`, a release must update the version in **four** places, and `/health` must equal the latest `CHANGELOG.md` version. Missing one is the classic mistake — the bundled script does all four atomically so you don't have to read each file to find the version string.

## The four locations (why each matters)

| File | What | Why |
|------|------|-----|
| `backend/app/main.py` | `FastAPI(version="X.Y.Z")` | OpenAPI/Swagger version |
| `backend/app/main.py` | `/health` → `{"status": "ok", "version": "X.Y.Z"}` | runtime version probe; **must match CHANGELOG** |
| `backend/pyproject.toml` | `version = "X.Y.Z"` | Python package version |
| `frontend/package.json` | `"version": "X.Y.Z"` | frontend package version |

## Agent path (use the script)

```bash
bash .claude/skills/bump-version/bump.sh 2.3.0
```

The script:
1. Validates the argument is a semver (`X.Y.Z`).
2. Regex-replaces the version in all four spots (file-scoped, so no false hits).
3. Prints every changed line for confirmation.
4. Warns if the new version is **not** the top `## [X.Y.Z]` heading in `CHANGELOG.md` (the `/health` rule).

It does **not** edit `CHANGELOG.md` — write the changelog entry yourself first (the human decides the notes), then run the script so the heading and `/health` line line up.

## Typical release flow

1. Add the `## [X.Y.Z] — YYYY-MM-DD` section to `CHANGELOG.md` (move items out of `[Unreleased]` if present).
2. `bash .claude/skills/bump-version/bump.sh X.Y.Z`
3. Eyeball the printed lines, commit on `beta`.

## Manual fallback

If the script can't run, edit the four locations above by hand and grep to confirm exactly four files/lines carry the new version.
