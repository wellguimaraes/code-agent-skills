---
name: review-plan
description: >-
  Review a plan for mistakes, simplification, and optimization opportunities.
  Use when the user asks to review your plan, review the plan, check a plan,
  or tighten a plan before implementation.
---

# Review plan

Review the active plan: **check for mistakes, simplification and optimization
opportunities**. Then patch clear mistakes and simplifications into the plan.
Do not implement code.

## Workflow

```
Progress:
- [ ] Locate the plan
- [ ] Ground against the repo
- [ ] Review axes + tests vs comment
- [ ] Report findings
- [ ] Patch clear fixes into the plan
```

### 1. Locate the plan

Use the plan file from this conversation (`CreatePlan` URI), a path the user
named, or the plan still in the thread. Stop if none exists.

Done when: you have the plan text (and path, if it is a file).

### 2. Ground against the repo

Before judging, re-read cited files, confirm named APIs/symbols/paths exist, and
check the change against nearby conventions. Discard findings you cannot ground.

Done when: every claim you will report is backed by a file, path, or quoted
plan line you checked.

### 3. Review axes, then tests vs comment

Keep axes separate so one does not mask another.

**Mistakes** — wrong files, invented APIs, contradictions, missing constraints
from the request or repo, steps that cannot work as written.

**Simplification** — extra files, extra abstractions, extra passes, speculative
generality, work the existing code already does.

**Optimization** — cheaper path to the *same* outcome (reuse, fewer hops,
smaller surface). Not premature performance work (caches, indexes, extra
concurrency) unless the plan's goal is performance.

**Tests vs comment** — for every test the plan adds, ask:

> Check if the added tests are really needed (if they'd really help when
> updating the tested code) or perhaps a simple comment in the code would be
> enough to let the one touching the code later to avoid mistakes when the
> reason behind the existing code is not obvious. If they're not really needed,
> skip them.

Decide per test:

- **Keep** — a later change could break a contract that is not visible from the
  code, and this test would go red.
- **Skip, comment instead** — the hazard is missing intent (why this exists /
  why this shape), not a behavior someone would otherwise think is safe to
  change.
- **Skip, nothing instead** — the test restates obvious behavior or would churn
  on every real edit.

Done when: each axis (and each proposed test) has been checked with evidence.

### 4. Report findings

Report in this order: Mistakes, Simplification, Optimization, Tests vs comment.
Each finding needs evidence (file/path or quoted plan line). No finding without
a grounding check. Empty axes say so in one line.

Done when: the user can see what you found and what you will patch vs suggest.

### 5. Patch the plan

Edit the plan file:

- **Apply**: factual errors, dead steps, reuse of existing helpers, collapsing
  redundant phases, and tests that fail the tests-vs-comment check (skip them;
  add a comment at the relevant code when the why is not obvious).
- **Suggest only**: optimizations that change the approach, add infra, or trade
  clarity for speed. Leave those in the report; do not rewrite the plan for them.

Do not add scope. After patching, the plan is the source of truth; tell the
user what changed.

Done when: the plan file (or thread plan) reflects applied fixes, and
speculative optimizations remain suggestions only.

## Guardrails

- Ground first; do not rubber-stamp your own plan.
- Optimization means a cheaper same-outcome path.
- A test earns its keep only if it would help a later editor; a comment earns
  its keep when the why is not obvious.
- Patch is an edit to the plan, not a rewrite of the goal.
- Never implement code as part of this skill.

## Anti-patterns

- Reviewing without re-reading cited paths
- Merging axes into one ranked list
- Adding performance work the plan did not ask for
- Keeping tests that only restate the code or lock an obvious shape
- Rewriting the goal or expanding scope while "simplifying"
