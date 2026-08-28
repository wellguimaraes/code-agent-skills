---
name: pick-worktree
description: >-
  List existing git worktrees and recent local branches, let the user pick
  where this agent session should work, and optionally create a new branch in
  a new worktree. Use when the user runs /pick-worktree or asks to choose a
  branch, worktree, or checkout for the rest of the session.
disable-model-invocation: true
---

# Pick worktree

Retarget this session onto a git checkout. Native `/worktree` only creates a
new tree; this skill **lists** existing worktrees and branches as choices.

The IDE window stays on the folder Cursor opened. After a pick, pin
`TARGET_ROOT` and use that path for every later Read / Write / Glob / Grep /
Shell (`working_directory`). Never edit a different checkout.

## 1. Discover

From the workspace repo:

```bash
git rev-parse --show-toplevel
git worktree list --porcelain
git branch --list --sort=-committerdate
git status -sb
```

`MAIN_ROOT` = the worktree whose path is this window’s workspace (session
Workspace Path). Other listed worktrees (`.worktrees/`, `~/.cursor/worktrees`,
siblings) are extra checkouts.

Local branches already checked out in some worktree must not appear a second
time. Cap leftover branches to the 15 most recently committed; `Other` covers
an older name.

## 2. Ask

`AskQuestion`, prompt like: `This window is on <branch>. Where should this session work?`

Options, in order:

| Kind | Label |
| --- | --- |
| Create | `✨ New branch in a NEW worktree (auto-naming)` — always first |
| This window’s worktree | `<branch> (this window)` — no emoji, no path |
| Any other worktree | `🌴 <branch>` — branch name only |
| Local branch with no worktree | `<branch>` — no emoji |

Never offer “new branch in the main worktree”. New branches always get their
own worktree.

Detached HEAD: use the short SHA as the “branch” in the label.

### Branch with no worktree

Second `AskQuestion`:

- Switch the main checkout to it (`git switch` in `MAIN_ROOT`)
- New worktree for this existing branch

Dirty `MAIN_ROOT`: do not `git switch`. Show status and stop, or offer a new
worktree instead. Do not stash unless the user asks.

### ✨ New branch in a NEW worktree (auto-naming)

Do **not** ask for a name unless the user already typed one.

1. Infer from this chat (ticket, feature, bug). If the repo uses Linear IDs
   like `RES-1234`, prefer `feature/RES-xxxx-slug`.
2. If nothing is clear, use `wip/untitled-YYYYMMDD-HHMMSS` (local time).

Then create. See step 3.

## 3. Create a worktree

Path: `<MAIN_ROOT>/.worktrees/<slug>` — not under `~/.cursor/worktrees`.
`<slug>` = last `/` segment of the branch name, filesystem-safe. If that
directory exists, append `-2`, `-3`, …

New branch:

```bash
mkdir -p "$MAIN_ROOT/.worktrees"
git -C "$MAIN_ROOT" worktree add -b <name> .worktrees/<slug> <base>
```

`<base>` = the branch currently checked out in `MAIN_ROOT` (often `develop`
or `main`).

Existing branch, new worktree (no `-b`):

```bash
git -C "$MAIN_ROOT" worktree add .worktrees/<slug> <branch>
```

Then copy ignored env files from the main tree. Set `SKILL_DIR` to the
directory that contains this `SKILL.md` (wherever the agent installed the
skill — e.g. `.cursor/skills/pick-worktree`, `.agents/skills/pick-worktree`,
`.claude/skills/pick-worktree`):

```bash
bash "$SKILL_DIR/scripts/copy-worktreeinclude.sh" "$MAIN_ROOT" "<new-worktree-path>"
```

The script reads `<MAIN_ROOT>/.worktreeinclude` (relative paths, `#` comments
and blanks skipped). Missing sources are skipped. Existing dest files are not
overwritten. No `.worktreeinclude` → no-op.

`TARGET_ROOT` = the new worktree path.

## 4. Pin and continue

State once:

- branch
- `TARGET_ROOT` (absolute)

If the branch is `wip/untitled-…`, renaming is **required** later, not
optional.

Then continue the user’s original task in `TARGET_ROOT`. Do not wait for a
new prompt if they already said what to do.

Do not run `cursor --new-window` unless they ask to open the folder.

## 5. Rename a temp branch

When the session’s subject becomes clear, **before the first push**:

```bash
git -C "$TARGET_ROOT" branch -m <final>
```

Say the new name once. Do **not** rename the worktree directory.

If the temp name was already pushed, do not rename unless the user asks
(that needs a remote delete + push).

## Anti-patterns

- Creating a branch in `MAIN_ROOT`
- Asking for a branch name when ✨ was chosen and context is empty (use the
  temp name)
- Full paths or last-path-segment in picker labels
- Palm emoji on this window’s checkout
- Editing files under a checkout that is not `TARGET_ROOT`
- `npm install` / extra bootstrap unless the user asks
