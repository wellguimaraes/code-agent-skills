---
name: review-changes
description: >-
  Review actual code changes (working tree, branch, or PR) for mistakes,
  simplification, and optimization opportunities, and check whether each
  added test earns its keep or a code comment would do. Then patch clear
  fixes into the code. Use when the user asks to review the changes, review
  the diff, review what you just did, check the implementation, or tighten
  the changes before commit or PR.
---

# Review changes

Review the actual changes: **check for mistakes, simplification and
optimization opportunities**. Then patch clear mistakes and simplifications
into the code. Do not add features.

## Workflow

```
Progress:
- [ ] Locate the changes
- [ ] Ground against the repo
- [ ] Review axes + tests vs comment
- [ ] Report findings
- [ ] Patch clear fixes into the code
```

### 1. Locate the changes

Use the target the user named (PR number, branch, commit range, paths).
Otherwise review the current branch: commits since the merge base with the
default branch, plus staged, unstaged, and untracked files.

```bash
base=$(git merge-base HEAD origin/HEAD 2>/dev/null || git merge-base HEAD main)
git diff "$base" --stat
git diff "$base"
git ls-files --others --exclude-standard
```

For a PR not checked out: `gh pr diff <n>`. Stop if the diff is empty.

Done when: you have the full diff and the list of touched files.

### 2. Ground against the repo

Read the diff hunks in their files, not in isolation. For each touched
symbol, check its callers and the nearby code that follows the same pattern.
Confirm that APIs, helpers, and config the change relies on exist and behave
as the change assumes. Run the project's existing type check, lint, and tests
for the touched area when they are cheap. Discard findings you cannot ground.

Done when: every claim you will report is backed by a file:line, a quoted
diff line, or a check output.

### 3. Review axes, then tests vs comment

Keep axes separate so one does not mask another.

**Mistakes** — bugs, wrong edge cases, broken callers, contract changes
callers do not expect, misuse of existing APIs, missing parts of the request,
conventions the repo follows that the change breaks.

**Simplification** — extra files, extra abstractions, wrappers with one
caller, speculative options or generality, code that re-does what an existing
helper already does, dead code, leftover debug output.

**Optimization** — cheaper path to the *same* outcome (reuse, fewer hops,
fewer passes, smaller surface). Not premature performance work (caches,
indexes, extra concurrency) unless the change's goal is performance.

**Tests vs comment** — for every test the diff adds, ask:

> Check if the added tests are really needed (if they'd really help when
> updating the tested code) or perhaps a simple comment in the code would be
> enough to let the one touching the code later to avoid mistakes when the
> reason behind the existing code is not obvious. If they're not really needed,
> skip them.

Decide per test:

- **Keep** — a later change could break a contract that is not visible from the
  code, and this test would go red.
- **Remove, comment instead** — the hazard is missing intent (why this exists /
  why this shape), not a behavior someone would otherwise think is safe to
  change.
- **Remove, nothing instead** — the test restates obvious behavior, mocks the
  thing it claims to test, or would churn on every real edit.

Also flag non-obvious code in the diff that has no test and no comment, where
a short comment would stop a later editor from "fixing" it.

Done when: each axis (and each added test) has been checked with evidence.

### 4. Report findings

Report in this order: Mistakes, Simplification, Optimization, Tests vs comment.
Each finding needs evidence (file:line or quoted diff line) and says whether
you will **apply** it or only **suggest** it. Empty axes say so in one line.

Done when: the user can see what you found and what you will patch vs suggest.

### 5. Patch the code

Edit the working tree:

- **Apply**: bugs with a clear fix, dead code and debug leftovers, reuse of
  existing helpers, collapsing needless wrappers or files, and tests that fail
  the tests-vs-comment check (remove them; add a comment at the relevant code
  when the why is not obvious).
- **Suggest only**: fixes that change the approach or public API, add infra or
  dependencies, trade clarity for speed, or need a product decision. Leave
  those in the report.

Do not add scope. Do not stage, commit, or push. After patching, rerun the
checks from step 2 and report their result. Then tell the user what changed.

If the target is not in the local working tree (for example a PR on another
branch), report only. Do not patch.

Done when: the working tree holds the applied fixes, checks pass or their
failures are reported, and approach-level changes remain suggestions only.

## Guardrails

- Ground first; do not rubber-stamp your own changes.
- Review the diff, not the whole file. Pre-existing issues outside the diff are
  out of scope unless the change makes them worse.
- Optimization means a cheaper same-outcome path.
- A test earns its keep only if it would help a later editor; a comment earns
  its keep when the why is not obvious.
- Patch is a fix to the change, not a rewrite of the goal.

## Anti-patterns

- Judging hunks without reading the surrounding file or the callers
- Merging axes into one ranked list
- Adding performance work the change did not ask for
- Keeping tests that only restate the code or lock an obvious shape
- Comments that restate what the code does instead of why
- Rewriting the goal or expanding scope while "simplifying"
- Committing or staging the fixes
