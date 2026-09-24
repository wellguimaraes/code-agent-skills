---
name: skill-candidate
description: >-
  Audit the current session and surface work that could become a skill,
  ranked for discussion. Use when the user runs /skill-candidate or
  /skill:skill-candidate, or asks what in this session could become a
  skill, which patterns deserve a skill, or wants skill ideas to review
  before anything is created. For the audit-and-discuss flow, not plain
  "create a skill" requests.
---

# Skill candidate

Scan the current session, identify what could become a skill, and present
candidates for discussion. **The deliverable of this run is the discussion —
do not create a skill, memory entry, or any file until the user explicitly
approves a specific candidate in a later turn.**

If the user passed a focus argument (e.g. `/skill-candidate the deploy work`
or `/skill:skill-candidate the deploy work`), restrict the audit to that
thread of the session.

## Progress

```
- [ ] Collect the session material
- [ ] Cross-check memory
- [ ] Evaluate and classify candidates
- [ ] Present the report, open the discussion, stop
```

## 1. Collect the session material

Work primarily from the conversation already in context: every user request,
every multi-step action taken, every correction.

If parts of this session are compacted or missing from context, recover them
from this agent's on-disk transcript when it has one (all JSONL; the newest
file matching the current cwd is the current session):

- pi: `~/.pi/agent/sessions/<sanitized-cwd>/<timestamp>_<id>.jsonl`
- Claude Code: `~/.claude/projects/<sanitized-cwd>/<session-id>.jsonl`
- Codex: `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`
- Cursor: `~/.cursor/chats/` or `~/.cursor/acp-sessions/`, if present

`<sanitized-cwd>` is the cwd with slashes replaced by dashes. Locate the
session dir by eye with `ls`, then extract turns with jq or grep, e.g. for
pi:

```bash
jq -c 'select(.type=="message")' <transcript>.jsonl
```

Message lines carry role `user`/`assistant`; content may be a string or an
array of blocks (text, tool calls, tool results). If no transcript is
accessible, work from context alone and say so.

If the session has no substantive work yet, say so and stop — nothing to audit.

## 2. Cross-check memory

Check the agent's long-term memory and running notes — pi: MEMORY.md +
scratchpad; Claude Code: CLAUDE.md / memory files; Codex and Cursor:
AGENTS.md / project rules. A candidate already captured as a preference may
not need a new artifact, and some candidates are better as memory than as
skills. Note which.

## 3. Evaluate candidates

Mine the session for these signals:

- **Repeated procedure** — the same multi-step sequence executed two or more
  times, or the user marked recurrence ("again", "like last time", "every
  week", "on every PR").
- **Correction** — the user redirected how something was done ("no, do it
  this way"). The redirect encodes a convention a future session would
  otherwise relearn by failing.
- **Tribal knowledge** — the user explained domain or project context that is
  not written in the repo or its docs.
- **Command pattern** — a specific command, flag combination, ordering, or
  pipeline used deliberately more than once.
- **Recovery path** — a first attempt failed and a non-obvious workaround was
  found; the workaround is the skill.

Classify each candidate honestly:

| Verdict | When |
|---|---|
| Global skill (`~/.agents/skills/`) | Multi-step, clear trigger, recurs, not repo-specific |
| Project skill (`<repo>/.agents/skills/`) | Same, but only meaningful inside one repo |
| Memory preference | One-line always-on rule, not a procedure — MEMORY.md, not a skill |
| Scratchpad | One-off reminder, likely obsolete soon |
| Skip | One-time task, general coding competence, too vague to trigger |

Do not force candidates. If nothing qualifies, say so plainly.

## 4. Present the report

Keep it in chat — this is a discussion, not a document (at most offer a doc).
At most ~6 candidates, strongest first. For each:

1. **Name** — proposed kebab-case name.
2. **Evidence** — what happened in the session; short quotes or tight
   paraphrases.
3. **Trigger** — when the skill should activate; this becomes its
   description.
4. **Draft description** — one or two lines, phrased like a SKILL.md
   description field: what it does + when to use it.
5. **Draft outline** — step skeleton, a few bullets.
6. **Verdict + confidence** — global skill / project skill / memory /
   scratchpad / skip, with high/medium/low confidence.

End with the explicit ask: which candidates to pursue, and what to adjust
(name, trigger, scope, steps, global vs project). State that nothing was
created. Then stop and wait.

## 5. On approval, create

Only in a later turn, when the user approves a specific candidate (possibly
adjusted through discussion):

1. Draft `SKILL.md` into `~/.agents/skills/<name>/` (global) or
   `<repo>/.agents/skills/<name>/` (project), following the Agent Skills
   format: frontmatter with `name` (lowercase, hyphens, max 64 chars) and
   `description` (max 1024 chars, stating what + when). Add
   `disable-model-invocation: true` only if the user wants command-only
   activation. Keep instructions direct, checklist-first, short.
2. Show the draft and the path it was written to.
3. Global skills only: if the user keeps `~/.agents/skills/` as a
   canonical dir shared across agents, propagate links with the
   sync-skills skill if installed (`/sync-skills`; pi: `/skill:sync-skills`;
   or `python3 ~/.agents/skills/sync-skills/scripts/sync_skills.py`). One
   canonical copy then serves pi, Claude Code, Codex, Cursor, and
   Command Code.
4. Remind the user how to activate it in the current agent: pi `/reload`,
   other agents a new session.