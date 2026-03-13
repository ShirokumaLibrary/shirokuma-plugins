# Plan Templates

Templates for each plan depth level. Use the template matching the level determined in Step 3.

## Lightweight Plan

```markdown
## Plan

### Approach
{1-2 line description of the approach}
```

## Standard Plan

> When tasks have dependencies, include a diagram following the Mermaid guidelines in the `github-writing-style` rule.

```markdown
## Plan

### Approach
{Selected approach and rationale}

### Target Files
- `path/to/file.ts` - {Summary of changes}

### Task Breakdown
- [ ] Task 1
- [ ] Task 2
```

## Detailed Plan

> Follow the Mermaid guidelines in the `github-writing-style` rule to include diagrams for task dependencies, state transitions, or component interactions.

```markdown
## Plan

### Approach
{Multi-option comparison and selection rationale}

### Target Files
- `path/to/file.ts` - {Summary of changes}

### Task Breakdown
- [ ] Task 1
- [ ] Task 2

### Risks / Concerns
- {Breaking changes, performance, security, etc.}
```

## Epic Plan (Issues with Sub-Issues)

For issues where `subIssuesSummary.total > 0`, use the extended template that includes sub-issue structure and integration branch.

> Follow the Mermaid guidelines in the `github-writing-style` rule to visualize sub-issue dependencies and execution order.

```markdown
## Plan

### Approach
{Overall strategy}

### Integration Branch
`epic/{number}-{slug}`

### Sub-Issue Structure

| # | Issue | Description | Dependencies | Size |
|---|-------|-------------|--------------|------|
| 1 | #{sub1} | {summary} | — | S |
| 2 | #{sub2} | {summary} | #{sub1} | M |

### Execution Order
{Recommended order based on dependencies}

### Task Breakdown
- [ ] Create integration branch
- [ ] #{sub1}: {task summary}
- [ ] #{sub2}: {task summary}
- [ ] Final PR: integration → develop

### Risks / Concerns
- {Dependency risks between sub-issues}
```

See `epic-workflow` reference for details.
