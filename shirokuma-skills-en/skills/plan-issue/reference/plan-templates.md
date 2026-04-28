# Plan Templates

Templates for each plan depth level. Use the template matching the level determined in Step 3.

> **CLI Template**: Use `shirokuma-docs issue template plan --level {level} --output <file>` to generate a template skeleton.

## Plan Issue Approach

Plan details are created as a child issue (plan issue) linked to the parent issue.

- **Plan Issue (child issue)**: An issue whose body contains the full plan content (approach, target files, task breakdown, risks, etc.)
- **Title convention**: `Plan: {parent issue title}` format
- **Status**: `Review`
- **Labels**: `area:plan`

### Plan Issue Frontmatter Structure

```markdown
---
title: "Plan: {parent issue title}"
status: "Review"
labels: ["area:plan"]
---
```

---

## Lightweight Plan (Plan Issue Body)

```markdown
---
title: "Plan: {parent issue title}"
status: "Review"
labels: ["area:plan"]
---

## Plan

### Approach
{1-2 line description of the approach}
{Include design decisions if applicable (e.g., what to include and what to exclude).}

## Parent Issue

See #{parent-number} for the task context.
```

## Standard Plan (Plan Issue Body)

> When tasks have dependencies, include a diagram following the Mermaid guidelines in the `github-writing-style` rule.

```markdown
---
title: "Plan: {parent issue title}"
status: "Review"
labels: ["area:plan"]
---

## Plan

### Approach
{State the selected approach in 1–2 prose sentences, leading with the conclusion. Explain why this approach was chosen.}

### Target Files
- `path/to/file.ts` - {Summary of changes}

### Task Breakdown
- [ ] Task 1
- [ ] Task 2

## Parent Issue

See #{parent-number} for the task context.
```

## Detailed Plan (Plan Issue Body)

> Follow the Mermaid guidelines in the `github-writing-style` rule to include diagrams for task dependencies, state transitions, or component interactions.

```markdown
---
title: "Plan: {parent issue title}"
status: "Review"
labels: ["area:plan"]
---

## Plan

### Approach
{Compare multiple options and state the selection rationale in 1–2 prose sentences, leading with the conclusion. Optionally supplement with a comparison table or additional details.}

### Design Decisions
{Describe key decisions — what to include and what to exclude — in prose or contrast format.}

### Target Files
- `path/to/file.ts` - {Summary of changes}

### Task Breakdown
- [ ] Task 1
- [ ] Task 2

### Risks / Concerns
- {Breaking changes, performance, security, etc.}

## Parent Issue

See #{parent-number} for the task context.
```

## Epic Plan (Issues with Sub-Issues)

For issues where the target is an epic (intended to have sub-issues for actual work), use the extended template that includes sub-issue structure and integration branch.

> Follow the Mermaid guidelines in the `github-writing-style` rule to visualize sub-issue dependencies and execution order.

```markdown
---
title: "Plan: {parent issue title}"
status: "Review"
labels: ["area:plan"]
---

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

## Parent Issue

See #{parent-number} for the task context.
```

See `epic-workflow` reference for details.
