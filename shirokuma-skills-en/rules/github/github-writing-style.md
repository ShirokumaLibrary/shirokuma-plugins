---
scope: default
category: github
priority: required
---

# GitHub Writing Style

Writing style for GitHub content (Issues, PRs, Discussions body and comments).

## Bullets vs Prose

| Condition | Format |
|-----------|--------|
| 3+ parallel items | Bullet list |
| Ordered steps | Numbered list |
| Cause-effect / logical argument | Prose |
| Single description | Prose |

## Formatting Rules

- **Parallel structure**: Start each item with the same part of speech / structure
- **Nesting limit**: Maximum 2 levels (3+ levels: split or convert to table)
- **List length**: 2-7 items per list (8+ items: consider grouping)
- **Lead-in sentence**: Add one sentence of context before a list

## Anti-Patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| Wall of Bullets | Everything bulleted, key points buried | Mix prose and bullets appropriately |
| Broken parallelism | Items use different grammatical structures | Rewrite with consistent structure |
| List without lead-in | Missing context, meaning unclear | Add one introductory sentence |
| Single-item list | Bullet adds no value | Convert to prose |

## Mermaid Diagrams

GitHub renders Mermaid natively. Use diagrams to explain complex structures and flows.

### When to Include

| Condition | Include Mermaid | Diagram Type |
|-----------|----------------|--------------|
| 3+ tasks with dependencies | Yes | Flowchart |
| State transitions described | Yes | State diagram |
| 2+ components interacting | Yes | Sequence diagram |
| Simple linear task list | No | — |
| Single file change | No | — |

### Style Rules

- **Node limit**: Maximum 10 nodes per diagram. Split into sub-diagrams if exceeded
- **Labels**: Keep concise (~10 characters per node)
- **Direction**: Use `graph TD` (top-down) or `graph LR` (left-right) as appropriate
- **Code block**: Wrap in ` ```mermaid `

### Anti-Patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| Diagramming what text explains well | Redundant, increases maintenance cost | Only use diagrams when conditions table applies |
| Giant diagram with 10+ nodes | Poor readability | Split into sub-diagrams |
| Diagram without explanation | Missing context | Add one sentence before/after the diagram |

## Scope

Applies to GitHub Issues / PRs / Discussions body and comments. Skill completion reports (`completion-report-style` rule) are excluded. For Claude config file structure, see the `coding-claude-config` skill.
