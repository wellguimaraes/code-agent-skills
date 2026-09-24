# code-agent-skills

Personal agent skills you can install with the [skills CLI](https://skills.sh/).

## Install

```bash
# All skills in this repo
npx skills add wellguimaraes/code-agent-skills

# One skill
npx skills add wellguimaraes/code-agent-skills --skill pick-worktree
```

## Skills

| Skill | Description |
| --- | --- |
| `cleanup-branches` | Delete local git branches and their worktrees whose GitHub PRs are already merged, with a dry-run first. |
| `multi-commit` | Split a dirty working tree into focused conventional commits authored as the user, with no agent signature. |
| `pick-worktree` | List worktrees and local branches, pick where the session should work, or create a new branch in a new worktree. |
| `review-plan` | Review a plan for mistakes, simplification, and optimization opportunities, then patch the plan without implementing it. |
| `show-me` | Explain a topic visually by rendering a markdown page with diagrams, trees, and diffs, then opening it in the browser instead of dumping diagrams in chat. |
| `simple-english` | Write or rewrite text in plain, layman-readable English in the spirit of ASD-STE100 Simplified Technical English. Adapted from AminBlg/SimpleEnglish (MIT). |
| `skill-candidate` | Audit the current session for work that could become a skill and present ranked candidates for discussion before creating anything. |
| `sync-skills` | Reconcile personal skills across Cursor, Claude Code, Codex, and Command Code so every skill exists in all agent dirs through symlinks. |
| `tailwind-properly` | Write Tailwind styling inline in components — cn() with boolean condition composition, never cva — breaking long class strings into logical multi-line groups. |

## License

MIT
