---
name: squash-and-merge
description: >
  Squash-merge a GitHub pull request with gh. Write a conventional-commit
  subject and a simple-English body for the squash commit. Do not use the
  GitHub default commit dump. Use when the user runs /squash-and-merge or
  asks to squash and merge a PR, squash merge, or set the squashed commit
  title and description.
disable-model-invocation: true
---

# Squash and merge

Squash-merge one open pull request. Use `gh`. Pass an explicit subject and body for the squash commit. Do not accept the GitHub default message.

## Required reads

Read this file in full before you merge:

1. `~/.cursor/skills/simple-english/SKILL.md`

Apply the Document rules from simple-english to the squash commit subject and body.

## Safety

Never update git configuration.
Never skip hooks.
Never force-push.
Never use `--admin` unless the user asked to override merge rules.
Never merge `main` or `master` as the head branch.
If the user did not name a pull request, use the open pull request for the current branch.
If there is no open pull request, stop and ask.
Do not merge a pull request from a different author unless the user named that pull request.
Do not use TodoWrite or Task tools.

## Inspect

Run these in parallel:

```bash
gh pr view --json number,title,body,url,state,isDraft,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup,commits,baseRefName,headRefName,headRefOid,author
git log --oneline
```

Then read the full change that will land:

```bash
gh pr diff
gh pr view --json commits --jq '.commits[] | {oid, messageHeadline, messageBody}'
```

If the pull request is a draft, stop.
If `state` is not `OPEN`, stop.
If `mergeable` is `CONFLICTING`, stop and report the conflict.
If required checks fail, stop and report the failures.
If `reviewDecision` is `CHANGES_REQUESTED`, stop and report it.
If `reviewDecision` is `REVIEW_REQUIRED`, stop unless the user asked to merge anyway.

Read the pull request Why and Summary. Read every commit that will squash. Do not write the squash message from the last commit only.

## Subject

Use conventional commit format: `type(scope): summary`.
Pick one type from `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`, `ci`, `build`, `style`, or `revert`.
If the branch or pull request has a ticket id, use that id as the scope.
Write the summary in imperative mood.
Do not put a period at the end.
Append `(#<number>)` when the subject does not already contain the pull request number.

Use the pull request title when it already matches this format.
If the pull request title is vague or is not a conventional commit, rewrite it from the diff.

Do not concatenate commit subjects.
Do not use the GitHub default "commit messages" squash template.

Examples:

```text
feat(RES-7257): show default material price next to list price (#4120)
fix(auth): restore session refresh on 401 (#3991)
chore: drop unused eslint rule (#4012)
```

## Body

Write a git commit body. Do not copy the pull request Test plan. Do not copy mermaid diagrams or file trees.

Use this shape:

```text
<Why the change exists. One or two sentences.>

<What the squash contains. Two or three sentences, or a short list of three or more parallel items.>
```

Answer why first. Name the user, failure, or constraint.
Then say what landed.
Do not list every file.
Do not dump the commit log.
Keep each sentence at 25 words or fewer.
Use `can`, `will`, and `must`.
Do not use `should`, `would`, `may`, `might`, or `could`.
Do not use semicolons or em-dashes.
Do not use contractions.

## Merge

Pass `--subject` and `--body` on every merge. If either flag is missing, stop.
Pass `--match-head-commit` with the `headRefOid` from inspect.

```bash
gh pr merge <number> --squash --delete-branch --match-head-commit "<headRefOid>" --subject "the subject" --body "$(cat <<'EOF'
body here
EOF
)"
```

If GitHub enables auto-merge because checks still run, report that and stop. Do not poll unless the user asked to wait.

If `--delete-branch` fails on the local branch because this worktree is still on it, that is fine. Do not switch worktrees. Do not delete local worktrees. The cleanup-branches skill handles leftover local branches.

After a successful merge, return the pull request URL and the squash subject.

## Anti-patterns

- Merge without `--subject` and `--body`
- Squash body that pastes every commit message
- Subject that is not `type(scope): summary`
- Merge of a draft, a failing check, or a changes-requested review
- `--admin` without an explicit ask
- Local `git merge --squash` when `gh pr merge --squash` is available
