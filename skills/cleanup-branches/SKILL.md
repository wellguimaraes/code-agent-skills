---
name: cleanup-branches
description: >-
  Delete local git branches (and their worktrees) whose GitHub PRs are already
  merged. Uses a deterministic script for the candidate list. Use when the user
  runs /cleanup-branches or asks to clean up merged branches or leftover
  worktrees.
disable-model-invocation: true
---

# Cleanup branches

Tear down local branches whose PRs already merged. Companion to
`/pick-worktree` (which creates checkouts under `<MAIN_ROOT>/.worktrees/`).

The script decides what is safe. Do not re-derive the candidate list yourself.

## 1. Preconditions

Resolve:

- `SKILL_DIR` = directory that contains this `SKILL.md`
- `MAIN_ROOT` = `git rev-parse --show-toplevel` from the session workspace

Require `gh` and an authenticated session:

```bash
gh --version
gh auth status
```

If either fails, stop and ask the user to install / `gh auth login`.

## 2. Dry-run

```bash
python3 "$SKILL_DIR/scripts/cleanup_branches.py"
```

- Human table on stderr
- Full JSON on stdout (`candidates`, `skipped`)

Never invent deletes outside that JSON.

## 3. Confirm

Zero `candidates` → summarize interesting `skipped` reasons and stop.

Otherwise show each safe row: branch, PR link, worktree path (or “no worktree”).
`AskQuestion`:

- Delete all safe candidates
- Cancel

If this window’s branch is listed under `current-worktree`, tell the user to
`/pick-worktree` onto `develop`/`main` first; the script will not remove the
open checkout.

## 4. Apply

On confirm:

```bash
python3 "$SKILL_DIR/scripts/cleanup_branches.py" --apply
```

Report `apply.deleted` and `apply.failed`. Do not push, fetch, or delete remotes.

## What the script never deletes

- default branch, plus `main` / `master` / `develop` / `staging` / `production`
- this window’s worktree (`MAIN_ROOT`)
- dirty or locked worktrees
- branches with no merged PR in the last 500 merged PRs (exact `headRefName` match)

`--apply` re-checks safety, removes the worktree (with `--force` only when
porcelain is empty), then `git branch -D` (squash-merge safe), then
`git worktree prune`.

## Anti-patterns

- Deleting branches without running the script
- `git branch -d` after squash-merge
- Removing the open window’s worktree
- Stashing to force a delete
- `npm install` / extra bootstrap
- Remote branch deletes
