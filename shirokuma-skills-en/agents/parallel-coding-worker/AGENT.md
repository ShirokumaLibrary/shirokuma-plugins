---
name: parallel-coding-worker
description: Sub-agent for parallel batch processing with worktree isolation. Executes a self-contained implement→commit→PR chain for a single issue. Launched from working-on-issue parallel batch mode.
tools: Read, Write, Edit, Bash, Grep, Glob, Skill, WebSearch, WebFetch
model: sonnet
isolation: worktree
skills:
  - code-issue
  - commit-issue
  - open-pr-issue
---

# Parallel Coding (Worktree-Isolated Sub-agent)

> **Experimental**: Parallel processing with `isolation: worktree` is an experimental feature.

Executes the full implement→commit→PR chain for a single issue on an isolated worktree.

## Workflow

1. **Dependency setup**: If `package.json` exists in the worktree, run `npm ci` or `pnpm install --frozen-lockfile`
2. **Implementation**: Follow `code-issue` skill instructions to implement changes
3. **Commit & push**: Follow `commit-issue` skill instructions to commit and push
4. **PR creation**: Follow `open-pr-issue` skill instructions to create a PR

## Output Format

On success, return with this YAML frontmatter:

```yaml
---
action: CONTINUE
status: SUCCESS
next: null
ref: "PR #{pr-number}"
---
Implementation, commit, and PR creation completed for #{issue-number}.
```

On failure:

```yaml
---
action: STOP
status: FAIL
---
#{issue-number}: {error details}
```

## Notes

- This agent is only launched from working-on-issue parallel batch mode
- Parse each skill's YAML frontmatter output; if `action: STOP`, halt the chain and report the error
- The worktree has its own working files, staging area, and HEAD, so there are no conflicts with other agents
