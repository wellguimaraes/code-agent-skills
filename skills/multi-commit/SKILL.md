---
name: multi-commit
description: Split a dirty working tree into focused conventional commits and author them as the user with no agent signature. Use when the user asks how to commit mixed changes, wants multiple commits, conventional commits, commit as me, no agent signature, or to split/stage a large dirty tree.
disable-model-invocation: true
---

# Multi-commit

Split mixed working-tree changes into a small set of focused conventional commits. Commit as the user only—never add an agent signature.

## Authorship and messages

- Use the existing git `user.name` / `user.email`. Never change git config.
- Conventional Commits: `type(scope): summary` with a short why-focused body when useful.
- Match recent repo style via `git log`.
- **Never** add agent/AI signatures, agent `Co-Authored-By`, “Generated with …”, or similar trailers.
- Pass the message via HEREDOC. If hooks or trailers inject unwanted footers, use:
  `git -c trailer.ifexists=doNothing commit --no-gpg-sign -m "$(cat <<'EOF' ... EOF)"`
- Only commit when the user asks to commit. If they only ask how you’d commit, propose the split and stop.

## When to split

Split when the tree mixes unrelated concerns (e.g. layout move + behavior + auth hardening + docs).

- Prefer **3–4 commits** over one mega-commit or over-fragmented noise.
- Keep mid-history buildable: do not separate shared error codes/types from the services that use them.
- Docs that describe an API change belong **after** that change, not before.

## Recommended order

1. **Mechanical refactor** — moves, path aliases, import rewrites; preserve behavior when possible.
2. **Main behavioral** `feat` / `fix`.
3. **Adjacent hardening** that isn’t the main story (e.g. auth race handling).
4. **Docs** / tiny unrelated nits last.

## Workflow

```
Progress:
- [ ] Inspect tree
- [ ] Propose split (if user asked “how”)
- [ ] Snapshot outside repo if destructive restore needed
- [ ] Stage and commit each slice in order
- [ ] Verify author/message; confirm clean status
```

### Inspect

Run in parallel:

- `git status` (including untracked)
- `git diff --stat` and skim hot files
- `git log` (recent message style)

### Stage

- Stage by path per commit.
- Use `git add -p` only when a single file truly mixes concerns.
- Do not commit secrets (`.env`, credentials, etc.).

### Snapshot safety

Before any `git reset` / `git clean`:

1. Copy the final tree to a path **outside the repo** (e.g. `/tmp/...`).
2. Never keep the only snapshot under a path `git clean` can delete.
3. Prefer `git checkout -- <paths>` / selective restore over `git reset --hard` + `git clean -fd`.

### After each commit

- Confirm `git log -1` author is the user and the message has no agent trailer.
- End with clean `git status` (or only intentional leftovers).
- Do not push unless asked.

## Anti-patterns

- One commit for ~50+ mixed files
- Docs before the API they describe
- Separating shared package errors from domain services that depend on them
- Destructive clean without an external snapshot
- Agent signature or “commit as the AI” authorship
