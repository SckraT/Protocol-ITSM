---
name: release-pr
description: Run the «Протокол совещаний» release flow — verify the beta branch, then open and squash-merge a PR from beta into main. Use when the user says "влей в main", "сделай PR в main", "выкати релиз", "merge beta to main", "принимаем в main", or otherwise wants to promote tested work from beta to the stable branch. Encodes the project's gh commands and pre-merge checklist so they aren't re-derived each time.
---

# Release: beta → main

Per `CLAUDE.md`, all features land on **`beta`** first, get tested, then are promoted to **`main`** (the stable/deploy branch) via a **squash-merged PR**. `gh` is authorized on this machine — create and merge PRs without the user. This skill is the fixed sequence so you don't reassemble it from memory.

## Pre-merge checklist (do before opening the PR)

1. On `beta`, working tree clean, pushed: `git status -sb`.
2. **Frontend typecheck:** `cd frontend && npm run check` → 0 errors.
3. **Container healthy:** `docker compose up -d --build` then confirm `healthy` (or run the `run-protocol` smoke test).
4. **CHANGELOG:** the changes are recorded. If this promotion is a tagged release, close `[Unreleased]` into `## [X.Y.Z] — YYYY-MM-DD` and run the `bump-version` skill so version + `/health` match.

## Open and merge the PR

```bash
# Inspect what's being promoted
git log --oneline main..beta
git diff --stat main..beta

# Create the PR (title/body in Russian, summarize the changes)
gh pr create --base main --head beta \
  --title "<краткое описание релиза>" \
  --body "<что входит + как проверено>"

# Squash-merge (keep beta — it's the permanent working branch)
gh pr merge <N> --squash --delete-branch=false
```

## After merge — sync main, then RESET beta onto main

Squash merge puts all of `beta`'s changes as **one new commit** on `main`; `beta`'s original commits become orphaned history. A permanent branch reused after a squash **always diverges**, and the *next* PR then fails with phantom conflicts. Avoid it entirely: **reset `beta` onto `main` after every release.** At this point `beta`'s content already equals `main` (everything was just merged), so nothing is lost.

```bash
git checkout main
git pull origin main             # explicit (main часто без upstream); fast-forward к squash-коммиту
git log --oneline -3

git checkout beta
git diff origin/main..beta --stat   # ДОЛЖНО быть пусто — всё влито.
                                    # Если НЕ пусто → там невлитое, НЕ сбрасывать (доведи до релиза).
git reset --hard origin/main
git push --force-with-lease
```

`beta` теперь стартует следующий цикл байт-в-байт как `main`, поэтому следующий `beta → main` PR — тривиальный чистый мердж. Никаких reconcile, `-s ours` и фантомных конфликтов.

**Почему reset, а не merge:** squash + долгоживущая переиспользуемая ветка — известный анти-паттерн (squash рассчитан на короткие ветки, которые удаляют). Reset держит истории `beta` и `main` идентичными каждый цикл. Безопасно здесь, потому что: (a) `beta` ведёт один мейнтейнер; (b) сброс делается только сразу после релиза, когда в `beta` нет невлитого; (c) `--force-with-lease` не затрёт неожиданные изменения на remote.

## Troubleshooting

- **`gh pr merge` → "not mergeable: the merge commit cannot be cleanly created"** — значит `beta` не сбросили после прошлого релиза и истории разошлись. Разовое восстановление (когда содержимое `beta` уже равно `main`): `git checkout beta && git reset --hard origin/main && git push --force-with-lease`, затем пересоздать/смерджить PR. (Если в `beta` есть реальные невлитые коммиты — вместо reset сделать `git merge origin/main`, разрешить, запушить.)
- **`gh pr create` transiently blocked** — повторить, обычно проходит со второй попытки.

## Notes

- **Never delete `beta`** — это постоянная staging-ветка (`CLAUDE.md`); после релиза её сбрасывают на `main`, а не удаляют.
- Auto-classifier блокирует прямой push в `main`; путь только через PR. Так задумано.
