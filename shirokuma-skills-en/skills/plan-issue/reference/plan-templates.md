# Plan Templates

Templates for each plan depth level. Use the template matching the level determined in Step 3.

## Comment-Link Structure

Plan details are posted as a comment, and only a summary link is written to the Issue body (comment-link pattern).

- **Comment (detailed)**: Full plan content (approach, target files, task breakdown, risks, etc.)
- **Body (summary link)**: Link to the plan comment + 1-2 line approach summary

### Body Summary Link Format

```markdown
## Plan

> Details: {comment_url}

### Approach
{1-2 line description of the approach}
```

`{comment_url}` is obtained from the `comment_url` field returned by `shirokuma-docs items add comment`.

---

## Lightweight Plan (Comment Content)

```markdown
## Plan

### Approach
{1-2 line description of the approach}
```

For lightweight plans, posting a comment is also required. The body contains only the summary link (`> Details: {url}`).

## Standard Plan (Comment Content)

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

## Detailed Plan (Comment Content)

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
