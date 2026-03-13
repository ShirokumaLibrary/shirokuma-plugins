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

For details (quality standards, PR template, interruption recovery, batch candidate detection), see `working-on-issue/reference/batch-workflow.md`.
