# ADR Templates

## Standard ADR

Based on Michael Nygard's original format with MADR enhancements.

```markdown
**Status:** {Proposed | Accepted | Deprecated | Superseded}
**Date:** {YYYY-MM-DD}
[**Supersedes:** ADR-{NNN}]
[**Superseded by:** ADR-{NNN}]

## Context

{What is the issue that we're seeing that is motivating this decision or change?
Describe the forces at play: technical, business, social, project constraints.}

## Decision

{What is the change that we're proposing and/or doing?
State the decision clearly and concisely.}

## Alternatives Considered

### {Alternative 1}
- **Pros:** {advantages}
- **Cons:** {disadvantages}

### {Alternative 2}
- **Pros:** {advantages}
- **Cons:** {disadvantages}

[### {Alternative N}
- **Pros:** {advantages}
- **Cons:** {disadvantages}]

## Consequences

### Positive
- {Benefit 1}
- {Benefit 2}

### Negative
- {Trade-off 1}
- {Trade-off 2}

[### Risks
- {Risk and mitigation}]

## Related Decisions
- {ADR-NNN: brief description of relationship}
```

## Lightweight ADR

For small, low-risk, easily reversible decisions.

```markdown
**Status:** {Proposed | Accepted}
**Date:** {YYYY-MM-DD}

## Context

{Brief description of the problem or need — 1-3 sentences.}

## Decision

{What we decided — 1-2 sentences.}

## Consequences

- {Key consequence 1}
- {Key consequence 2}
```

## Template Selection Guide

| Criterion | Standard | Lightweight |
|-----------|----------|-------------|
| Reversibility | Hard to reverse | Easy to reverse |
| Blast radius | Multiple components | Single component |
| Alternatives | 2+ considered | Obvious choice |
| Stakeholders | Multiple teams | Single team/person |
| Risk level | Medium-High | Low |

## Writing Tips

### Context Section
- Describe the problem, not the solution
- Include relevant constraints (timeline, budget, team skills)
- Reference related issues or discussions

### Decision Section
- State the decision in active voice: "We will use X" not "X was chosen"
- Be specific: "PostgreSQL 16" not "a relational database"
- Include scope: what this applies to and what it doesn't

### Alternatives Section
- Include at least 2 alternatives for standard ADRs
- "Do nothing" is a valid alternative
- Be fair in pros/cons — avoid strawman alternatives

### Consequences Section
- Separate positive and negative consequences
- Be honest about trade-offs
- Include operational consequences (deployment, monitoring, maintenance)
