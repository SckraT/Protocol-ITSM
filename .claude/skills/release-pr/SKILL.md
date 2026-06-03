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

## After merge — sync local main AND reconcile beta

Local `main` often has **no upstream set**, so a bare `git pull` won't fast-forward. Pull explicitly:

```bash
git checkout main
git pull origin main          # explicit — fast-forwards to the squash commit
git log --oneline -3          # confirm the squash commit is on top
git diff main..origin/beta    # содержимое должно совпасть (см. ниже про reconcile)
```

**Critical — reconcile `beta` with `main` after every squash merge.** Squash collapses all of `beta`'s commits into ONE new commit on `main`; `beta` still carries the original commits. So `beta` and `main` now have **divergent history with identical content**. If you keep committing to `beta` without reconciling, the divergence accumulates and the *next* PR fails to merge with phantom `add/add` conflicts (e.g. in `CHANGELOG.md`). Fix it immediately by recording `main` as merged into `beta` while keeping `beta`'s tree:

```bash
git checkout beta
# Сначала убедиться, что main НЕ содержит правок, которых нет в beta:
git diff beta..origin/main --stat   # ожидаем только «откат» к старому коду (то, что beta удалил)
# Влить историю main, сохранив дерево beta без изменений:
git merge -s ours origin/main -m "merge: вобрать историю main в beta (содержимое уже в beta)"
git push
```

`-s ours` keeps `beta`'s tree byte-for-byte (verify: tree hash before == after) and just marks `main` as an ancestor — so the **next** `beta → main` PR diffs cleanly. Then resume work on `beta`.

⚠️ `-s ours` is only safe when `beta` already contains all of `main`'s content (the normal case — `beta` was the source). If `git diff beta..origin/main` shows real changes `beta` lacks (e.g. a hotfix committed straight to `main`), do a **normal** `git merge origin/main` and resolve, instead of `-s ours`.

## Troubleshooting

- **`gh pr merge` → "not mergeable: the merge commit cannot be cleanly created"** — almost always the squash-divergence above. Don't hand-resolve conflicts in the PR. Instead run the reconcile (`git merge -s ours origin/main` on `beta`, push), which makes `main` an ancestor of `beta`; the PR then becomes mergeable. Re-run `gh pr merge <N> --squash`.
- **`gh pr create` transiently blocked** — retry, usually succeeds on the second attempt.

## Notes

- **Never delete `beta`** — it is the permanent staging branch (`CLAUDE.md`).
- The auto-classifier blocks direct pushes to `main`; the PR path is the only way in. That's intended.
