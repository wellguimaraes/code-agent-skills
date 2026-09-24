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
| `pick-worktree` | List worktrees and local branches, pick where the session should work, or create a new branch in a new worktree. |
| `show-me` | Explain a topic visually by rendering a markdown page with diagrams, trees, and diffs, then opening it in the browser instead of dumping diagrams in chat. |
| `skill-candidate` | Audit the current session for work that could become a skill and present ranked candidates for discussion before creating anything. |

## License

MIT
