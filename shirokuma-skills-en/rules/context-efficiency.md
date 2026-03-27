---
scope: default
category: general
priority: required
---

# Context Efficiency Classification

Guidelines for choosing between Agent delegation and Skill invocation based on context consumption.

## Classification Criteria

| Criterion | Route | Rationale |
|-----------|-------|-----------|
| Reading/writing many files (10+) or large files | Agent tool | Prevents main context bloat |
| External web access (WebSearch, WebFetch) | Agent tool | Web content inflates context unpredictably |
| Changes exceeding 200 lines | Agent tool | Large diffs should not occupy main context |
| Lightweight task + project rules required | Skill tool | Rules are accessible only in main context |
| git/GitHub operations only (commit, PR, status) | Agent tool | Isolated subagent keeps main context clean |
| Orchestration requiring AskUserQuestion | Skill tool | User interaction requires main context |

## Decision Flow

```
Is context consumption large (many files / web / 200+ lines)?
  Yes → Agent tool (subagent isolation)
  No  → Does the task need project-specific rules?
          Yes → Skill tool (main context)
          No  → Agent tool (preferred for isolation)
```

## Examples

| Task | Route | Reason |
|------|-------|--------|
| Implement feature (edit 5+ files) | Agent (`coding-worker`) | File I/O volume |
| Research best practices | Agent (`research-worker`) | Web access + large output |
| Config quality review | Skill (`reviewing-claude-config`) | Needs `.shirokuma/rules/` access |
| Create commit | Agent (`commit-worker`) | git ops, isolated |
| Evolve rules (impact analysis) | Agent(Explore) for Step 3 | Many files to read |
| Code review (PR) | Agent (`review-worker`) | Multi-file reads + large review output |
| Post Issue comment | Bash (inline) | Single CLI call, minimal context |
