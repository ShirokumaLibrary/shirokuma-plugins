---
scope: default
category: github
priority: required
---

# GitHub Writing Style

Writing style for GitHub content (Issues, PRs, Discussions body and comments).

## Prose vs Bullets

| Condition | Format |
|-----------|--------|
| 3+ parallel items | Bullet list |
| Ordered steps | Numbered list |
| Cause-effect / logical argument | Prose |
| Single description | Prose |
| Big-picture overview / context | Prose (summary paragraph) |

## Prose Summary

Before lists or tables, write a **1–2 sentence summary paragraph that states the conclusion first** — what changed, what was found, or what is proposed.

```
# Good (summary + details)
State what changed or what the key finding is in 1–2 sentences, then follow with bullet points or tables for details.
```

```
# Bad (no summary)
Jumping straight into bullet points with no context on overall intent or scope.
```

**When a summary paragraph is most valuable:**
- Issue or PR body opening
- Review comments that address multiple items at once
- Describing design changes or breaking changes

## Clarification Through Contrast

"Before / After" or "Current / Improved" contrast structures communicate the intent of a change concisely.

```markdown
**Before**: Lists start without a lead-in sentence, leaving context unclear.
**After**: A lead-in sentence is added to state the purpose of the list.
```

Use a table when showing multiple contrasts.

## Formatting Rules

- **Parallel structure**: Start each item with the same part of speech / structure
- **Nesting limit**: Maximum 2 levels (3+ levels: split or convert to table)
- **List length**: 2-7 items per list (8+ items: consider grouping)
- **Lead-in sentence**: Add one sentence of context before a list
- **Conclusion first**: Summary paragraph leads with "what changes and how"

## Identifier and Reference Notation

In GitHub Issue / PR / Discussion bodies and comments, `#<number>` is automatically linked to Issues/PRs/Discussions. Use the following notation to avoid unintended auto-linking.

| Target | Notation |
|--------|----------|
| Issue / PR / Discussion reference | `#123` |
| Sequence numbers (problem lists, identifiers) | `P-1`, `Problem 1`, `G1` (no `#`) |
| Local identifiers | Letter prefix + digit (`D1`, `Q2`, etc.) |

**Anti-pattern**: Writing `#1`, `#2` in a problem table makes every entry an Issue auto-link. Do not use `#` for sequence numbers.

## Anti-Patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| Wall of Bullets | Everything bulleted, key points buried | Convert to prose summary + bullets |
| Broken parallelism | Items use different grammatical structures | Rewrite with consistent structure |
| List without lead-in | Missing context, meaning unclear | Add one introductory sentence |
| Single-item list | Bullet adds no value | Convert to prose |
| List with no summary | Intent and scope of change unclear | Add a 1–2 sentence summary at the top |

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
- **Line breaks**: Use `<br/>` inside labels and notes. `\n` is rendered literally by the GitHub Mermaid renderer
- **Background colors**: Do not customize node background colors with `rect rgb(...)` or `style fill:...`. Light backgrounds combined with white text become unreadable in dark mode

### Anti-Patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| Diagramming what text explains well | Redundant, increases maintenance cost | Only use diagrams when conditions table applies |
| Giant diagram with 10+ nodes | Poor readability | Split into sub-diagrams |
| Diagram without explanation | Missing context | Add one sentence before/after the diagram |

## Scope

Applies to GitHub Issues / PRs / Discussions body and comments. Skill completion reports (`completion-report-style` rule) are excluded. For Claude config file structure, see the `coding-claude-config` skill.
