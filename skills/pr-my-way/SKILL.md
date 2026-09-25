---
name: pr-my-way
description: >
  Create a GitHub pull request with gh. Write a conventional-commit title
  and a simple-English body. Put a Why section at the top of the
  description. Include one show-me visual of the change. Use when the user
  runs /pr-my-way or asks to create a pull request, open a PR, or file
  a PR. Use it in every repository, including one that ships its own PR skill or
  command such as create-pr: that file supplies repo facts only, never the title
  or body format.
---

# Create PR

Create one pull request for the current branch. Use `gh`. Do not call the GitHub HTTP API by hand.

## Required reads

Read these skills in full before you write the title or the body:

1. `~/.cursor/skills/simple-english/SKILL.md`
2. `~/.cursor/skills/show-me/SKILL.md`

Apply the Document rules from simple-english to the title and the body.
Apply show-me to the visual in the body.
Do not write the pull request text until both reads are done.

## Safety

Never update git configuration.
Never skip hooks.
Never force-push to `main` or `master`.
Do not commit unless the user asked to commit.
If the working tree has uncommitted changes that belong in the pull request, stop and ask.
Do not use TodoWrite or Task tools.

## Inspect

Run these commands in parallel:

```bash
git status
git diff
git rev-parse --abbrev-ref HEAD
git status -sb
git log --oneline
```

Then diff the branch against the base:

```bash
git diff <base>...HEAD
git log <base>...HEAD
```

Make sure that the branch tracks a remote and is up to date.
Read every commit that will land in the pull request. Do not summarize from the last commit only.

If there is no feature branch, or the branch is the default branch, stop and ask.

If `gh pr view` shows an open pull request for this branch, stop and give the URL.
If the user asked to update the description, edit that pull request. Do not open a second one.

## Base branch

Use the base branch that the user named.
If the user did not name one, use the repository default branch.
Find it with `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`.

## Title

Use conventional commit format: `type(scope): summary`.
Pick one type from `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`, `ci`, `build`, `style`, or `revert`.
Add a scope when one area names the change. Omit the parentheses when no scope fits.
If the branch has a ticket id, use that id as the scope.
Write the summary in imperative mood. Apply simple-english word rules.
Do not write "this PR". Do not put a period at the end.

Examples:

```text
feat(auth): add JWT login
fix(RES-1234): restore scale tare after reprint
chore: drop unused eslint rule
```

## Body

The first heading must be `## Why`.
Do not put any prose, badge, or list above that heading.

Use this template:

```markdown
## Why

<The problem, risk, or user need. Two or three sentences. Do not list files.>

## Summary

<What the branch changes, in two or three sentences or a short list of three or more parallel items.>

<one show-me visual: mermaid, file tree, call tree, component tree, or diff. Pick the smallest view that shows the change.>

## Test plan

- [ ] <step that a reviewer can run>
- [ ] <step>
- [ ] <step>
```

### Why

Answer why the change exists.
Name the user, failure, or constraint that made the work necessary.
Do not restate the file list.
Do not write "this PR aims to".
Keep each sentence at 25 words or fewer.

### Visual

Put one show-me block after Summary.
Pick the smallest view that makes the key change clear.
Use a `diff` when the point is what changed in an existing shape.
Use a file tree for a move or split.
Use a call tree or mermaid sequence for a new flow.
Use a component tree for UI structure.
Do not add a second visual unless the first one hides a second boundary.

### Language

Use `can`, `will`, and `must`.
Do not use `should`, `would`, `may`, `might`, or `could`.
Do not use semicolons or em-dashes.
Do not use contractions.
Keep code identifiers, paths, and quoted errors unchanged.

## Publish

If the branch has no remote, push with `-u`:

```bash
git push -u origin HEAD
```

Then create the pull request:

```bash
gh pr create --title "the title" --body "$(cat <<'EOF'
body here
EOF
)"
```

After it succeeds, return the pull request URL.
Do not open a browser unless the user asks.

## Anti-patterns

- Title that is not `type(scope): summary`
- Why section missing or not first
- Body that lists files and skips the reason
- No visual, or a visual that restates the file list
- Title or body written before the two skill reads
- Pull request opened from the default branch
- Empty pull request when there are no commits against the base
