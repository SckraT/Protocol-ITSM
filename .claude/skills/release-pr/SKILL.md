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

## After merge — sync local and return to beta

Local `main` often has **no upstream set**, so a bare `git pull` won't fast-forward. Pull explicitly, then go back to `beta` to keep working:

```bash
git checkout main
git pull origin main          # explicit — fast-forwards to the squash commit
git log --oneline -3          # confirm the squash commit is on top
git diff main..origin/beta    # should be EMPTY — branches now equal

git checkout beta             # resume work here
```

## Notes

- **Never delete `beta`** — it is the permanent staging branch (`CLAUDE.md`).
- The auto-classifier blocks direct pushes to `main`; the PR path is the only way in. That's intended.
- If `gh pr create` is transiently blocked, retry — it usually succeeds on the second attempt.
