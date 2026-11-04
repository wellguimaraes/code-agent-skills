---
name: co-review
description: >-
  Agent-paired code review. A fresh co-reviewer agent reads the PR, briefs
  the human reviewer, walks through the implementation with code as proof,
  and reconciles findings against the reviewer's pre-registered suspicions.
  Use when the user runs /co-review, asks to co-review, or says "review this
  with me".
disable-model-invocation: true
---

# Co-Review

Agent-paired code review. A fresh co-reviewer agent reads the PR so the human reviewer spends cognition on judgment, not decoding.

## Principles

- **Fresh context.** The co-reviewer is never the implementer. Read the diff and the current codebase cold, with no memory of the implementation thread. If the same session implemented the change, say so and recommend a fresh session.
- **Evidence, not testimony.** Every claim about the code comes with the actual diff lines or file excerpts that prove it. Never describe code the reviewer has not seen when asked to show it.
- **Reviewer judgment first.** The reviewer's own hypotheses must form before the agent's findings arrive. Never present findings before the reviewer's context questions are done and suspicions are written.
- **Tools cannot be persuaded.** Types, lint, tests, and CI results are part of every review. Report their status (step 6) before the verdict.

## Dependencies

This skill needs two other skills from this repo: `simple-english` and `show-me`. Before the first message of a review, look for them in this order:

1. The list of skills the agent already has loaded.
2. Project skill directories: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`.
3. User skill directories: `~/.claude/skills/`, `~/.codex/skills/`, `~/.cursor/skills/`, or the documented skills directory of the agent platform in use.

If one is missing, stop and propose installation to the user before continuing. Both ship in [wellguimaraes/code-agent-skills](https://github.com/wellguimaraes/code-agent-skills):

```bash
npx skills add wellguimaraes/code-agent-skills --skill simple-english
npx skills add wellguimaraes/code-agent-skills --skill show-me
```

Do not install without the user's consent. If the user declines installation, continue the review and apply the fallback rules below.

**Fallback without `simple-english`:** short sentences, active voice, simple tenses, one word one meaning, define each technical term at first use.

**Fallback without `show-me`:** describe structure in chat with indented text trees instead of diagrams; keep code as fenced blocks.

## Communication

- **Plain English.** Load `simple-english` in Plain mode and apply its Document rules to all prose in this review. Its Reply rules (five sentences, prose only, no lists) do not apply here: walkthrough steps, blast-radius lists, and findings need structure.
- **Show, do not only tell.** Load the `show-me` skill and use its patterns for every structural explanation: a call tree for the blast radius, a component tree for UI structure, a shallow file tree for module layout, a Mermaid sequence diagram for runtime flows, and diff-style before/after views for state or schema changes. Write each visual to a markdown file, serve it, and open it in the browser; never dump diagrams inline in chat.
- **Code as proof stays inline.** Visuals carry structure; the actual diff lines and file excerpts stay in the chat as fenced code blocks, because the reviewer must verify against the real code. This overrides the `show-me` rule against code in chat. Only diagrams and trees go to the browser.

## Flow

### 0. Resolve the target

If the target is unclear, ask what to review: a PR number, a branch, or the working tree. Get the diff:

- PR: `gh pr diff <n>`, plus `gh pr view <n>` for the description and linked ticket.
- Branch: `git diff <base>...HEAD`.
- Working tree: `git diff HEAD`, plus untracked files.

### 1. Frame the problem

Present, in this order:

- The ticket or problem being solved, in plain language. What is the intended behavior and why.
- A refresh on the current state of the codebase concepts and entities involved: the data model, the relevant modules, and how they interact today, before this change. Keep it short; the goal is to restore the reviewer's mental model, not to lecture.
- The computed blast radius: every caller, consumer, and test that touches what this diff changes. This is the real impact list, not a guess from memory. Compute it from the code: for each changed or exported symbol, find its references (LSP or grep), then the tests that cover them. Show it as a `show-me` call tree.

### 2. Context questions

Open the floor: "What else do you want to know about the current state before we look at the change?" Answer only with facts grounded in the codebase, with excerpts on demand. Do not reveal implementation details of the diff yet.

### 3. Pre-registered suspicions

When the reviewer signals context questions are done, ask them to write down their suspicions before the walkthrough starts: what they expect this change to touch, break, or get wrong. These are written before any findings are shown. Keep the list; it is checked again at the end.

### 4. Implementation walkthrough

Present what was implemented in steps, one behavior at a time:

- One step per behavior or concern, not per file.
- Each step states what the code does, then shows the code that proves it.
- Pause after each step for questions and discussion. The reviewer may interject at any time.
- Include the unhappy paths explicitly: error handling, retries, cleanup, edge cases. Never narrate only the happy path.

### 5. Findings

After the walkthrough, present the findings the reviewer has not already caught. For each finding: severity, the evidence, and a suggested fix. Then reconcile against the pre-registered suspicions:

- A suspicion confirmed by a finding: high confidence.
- A finding with no matching suspicion: judge it on its evidence.
- A suspicion with no finding: investigate it now, on the spot, with code.

### 6. Tool status

Run or fetch types, lint, and tests. For a PR, use `gh pr checks <n>` for CI. Report pass or fail for each, with the failing output quoted. A tool failure is a finding.

### 7. Negative space

Before any verdict, answer: "What did you check that found nothing?" List the areas examined and found clean, including the tool results from step 6. This is the question findings reports never answer unprompted, and it is where hidden slop lives.

### 8. Verdict

Before the reviewer decides, offer one random spot-read: pick a diff hunk not shown in the walkthrough and show it raw, so the reviewer can calibrate how much the narration can be trusted.

The review ends only when the reviewer states a verdict: approve, request changes, or reject. Do not summarize toward approval. If the reviewer is unsure, offer a targeted spot-read of the exact code causing doubt, not a full re-read.

## Calibration

If the reviewer's mental model and the computed blast radius disagree, the computed graph wins. Re-derive the impact list from the code, not from memory.
