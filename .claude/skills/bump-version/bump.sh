#!/bin/bash
# Поднять версию проекта во всех обязательных местах (см. CLAUDE.md).
# Использование: bash bump.sh X.Y.Z
set -e

NEW="$1"
if ! [[ "$NEW" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "✗ Версия должна быть в формате X.Y.Z (получено: '$NEW')"
  exit 1
fi

# Корень репозитория (скрипт лежит в .claude/skills/bump-version/)
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
MAIN="$ROOT/backend/app/main.py"
PYPROJECT="$ROOT/backend/pyproject.toml"
PKG="$ROOT/frontend/package.json"
CHANGELOG="$ROOT/CHANGELOG.md"

SEMVER='[0-9]+\.[0-9]+\.[0-9]+'

# 1. backend/app/main.py — FastAPI(version=...) и /health "version": "..."
sed -i -E "s/(version=\")$SEMVER(\")/\1$NEW\2/" "$MAIN"
sed -i -E "s/(\"version\": \")$SEMVER(\")/\1$NEW\2/" "$MAIN"

# 2. backend/pyproject.toml — version = "..." (строго в начале строки, чтобы не задеть target-version)
sed -i -E "s/^version = \"$SEMVER\"/version = \"$NEW\"/" "$PYPROJECT"

# 3. frontend/package.json — "version": "..."
sed -i -E "s/(\"version\": \")$SEMVER(\")/\1$NEW\2/" "$PKG"

echo "=== Обновлённые строки ($NEW) ==="
grep -nE "version.*$NEW" "$MAIN" || true
grep -nE "^version = \"$NEW\"" "$PYPROJECT" || true
grep -nE "\"version\": \"$NEW\"" "$PKG" || true

# 4. Проверка соответствия CHANGELOG (верхняя запись ## [X.Y.Z])
TOP_CL="$(grep -m1 -oE '## \[[0-9]+\.[0-9]+\.[0-9]+\]' "$CHANGELOG" | grep -oE "$SEMVER" || true)"
echo "=== Проверка CHANGELOG ==="
if [ "$TOP_CL" = "$NEW" ]; then
  echo "✓ Верхняя запись CHANGELOG = $NEW — /health соответствует."
else
  echo "⚠ Верхняя версия в CHANGELOG: '${TOP_CL:-нет}', а bump = $NEW."
  echo "  Допишите '## [$NEW] — YYYY-MM-DD' в CHANGELOG.md (правило /health = последняя версия)."
fi
