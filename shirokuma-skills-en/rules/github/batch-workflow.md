---
scope:
  - main
category: github
priority: required
---

# Batch Workflow

Process multiple small issues in a single branch and PR when they share a common area or theme.

## Eligibility Criteria

| Criterion | Requirement |
|-----------|-------------|
| Size | XS or S only (M+ requires individual processing) |
| Relatedness | Same `area:*` label, or affecting the same file group |
| Independence | No blocking dependencies between issues |
| Upper limit | 5 issues or fewer per batch (recommended) |

**Not eligible:** Issues requiring TDD (each needs its own test cycle), different `area:*` labels with no file overlap.

## Branch Naming

```
{type}/{issue-numbers}-batch-{slug}
```

Default to `chore` when types are mixed. Issue numbers are hyphen-separated, sorted ascending.

## Status Management

At batch start, move all issues to In Progress in bulk (exception to `project-items` rule).

## Parallel Batch Mode (Experimental)

> Parallel processing using `isolation: worktree`. Activated with the `--parallel` flag.

Process issues that operate on completely independent file sets in parallel using worktree isolation.

### Sequential vs Parallel

| Condition | Mode |
|-----------|------|
| Issues sharing common files | Sequential batch (1 branch, 1 PR) |
| Issues with completely independent file sets | Parallel batch (each issue gets its own PR) |

### Parallel Batch Eligibility

In addition to sequential batch criteria:

| Criterion | Requirement |
|-----------|-------------|
| File independence | No overlapping changed files between issues |
| Concurrency | Default 3, max 5 (set via `--parallel=N`) |

### Aggregation Pattern

Each issue creates its own independent PR (PR-based aggregation). No batch branch is created.

Details (workflow, error handling, verification procedures) are auto-loaded when the `implement-flow` skill is executed.
