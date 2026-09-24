---
name: sync-skills
description: Reconcile personal skills across Cursor, Claude Code, Codex, and Command Code so every skill exists in all agent dirs. Use when the user runs /sync-skills or asks to sync, unify, deduplicate, or fix missing/broken skills across agents.
disable-model-invocation: true
---

# Sync skills

Single source of truth: `~/.agents/skills/`. Each global agent dir holds only
symlinks into it (plus agent-owned extras like Codex's `.system/`, which are
never touched):

- `~/.cursor/skills/`
- `~/.codex/skills/`
- `~/.claude/skills/`
- `~/.commandcode/skills/` (Command Code global skills)

Command Code also supports project skills at `.commandcode/skills/`; this
script only syncs the **global** `~/.commandcode/skills/` tree. Copy or
symlink project skills manually if needed.

## Procedure

1. Run the deterministic sync and read its report:

   `python3 ~/.agents/skills/sync-skills/scripts/sync_skills.py`

   The script already handles the mechanical cases: it moves unique skills
   into the canonical dir, deduplicates byte-identical copies, relinks
   broken symlinks whose content exists, and attempts reinstall of lost
   skills listed in `~/.agents/.skill-lock.json` (`sourceUrl` + `skillPath`).

2. If it reports a **conflict** (same skill name, different content in two
   places), diff them, keep the better version at
   `~/.agents/skills/<name>/`, delete the loser, and rerun the script.

3. If it reports **missing** content it could not reinstall (no lock entry
   or offline), ask the user for the source and install it into the
   canonical dir manually. Then rerun the script.

4. Repeat until the script reports all in sync with no broken links.
