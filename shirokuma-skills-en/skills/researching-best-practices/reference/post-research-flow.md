# Post-Research Flow

Defines the conditional branching logic after research completion. The flow differs by invocation context.

## Flow by Invocation Context

### Chain (via `implement-flow`)

`implement-flow` controls the entire flow. The research skill only returns findings.

```
researching-best-practices → review-issue(research, Skill) → Discussion auto-save → chain complete
```

- Discussion save: **Required** (executed by `implement-flow`'s `researching-reference.md`)
- Next action decision: Not needed (chain ends at completion)

### Standalone

When the user directly invokes `/researching-best-practices`.

```
researching-best-practices → [Discussion save (recommended)] → next action suggestion
```

- Discussion save: **Recommended** (optional). Trivial lookups (completed in under 1 minute) do not require saving
- Next action: Determined using the conditional branching table based on findings, then suggested

## Conditional Branching Table

After research completion, determine the next action based on the nature of the findings. Conditions are listed in priority order — when multiple conditions match, prefer the higher-priority (earlier) action.

| Condition | Criteria | Next Action | Example |
|-----------|----------|-------------|---------|
| Implementation task identified | Findings contain specific work items like "should implement X" or "should add Y" | Create Issue (Backlog) | "Should add CSP headers" → Issue |
| Architecture decision needed | Multiple options with trade-off comparisons | Create ADR Discussion | "Auth: JWT vs sessions" → ADR |
| Reusable pattern confirmed | A verified implementation pattern applicable to other areas | Create Knowledge Discussion | "Drizzle soft-delete pattern" → Knowledge |
| Existing rule improvement suggested | Findings contain deficiencies or improvements for existing rules/skills | Record Evolution signal | "Current validation rule is insufficient" → Evolution Issue |
| 3+ patterns accumulated | 3 or more similar patterns exist in Knowledge Discussions | Propose Rule extraction (`managing-rules`) | 3 i18n patterns → rule extraction |
| Information only | None of the above — pure information sharing | Keep as Discussion (no additional action) | "Library X version compatibility" → as-is |

## Detailed Criteria

### "Implementation task identified"

Applies when any of the following are true:
- Findings contain specific code changes (file/function level)
- Action directives like "should", "needs to", "must" are present
- Security vulnerability or bug fix is required

### "Architecture decision needed"

Applies when any of the following are true:
- Comparison of 2+ implementation approaches exists
- Decision impact spans multiple files/modules
- Low reversibility (high cost to change later)

### "Reusable pattern confirmed"

Applies when all of the following are true:
- Generic pattern not limited to a specific use case
- Verified in actual code (not theoretical only)
- Valuable for other developers (including AI agents) to reference

## Standalone Completion Suggestion Template

```markdown
## Next Steps

Based on the research findings, we recommend the following actions:

- [Select and suggest applicable actions from the conditional branching table]
```

When multiple actions apply, suggest them in priority order.

## Related References

| Document | Content |
|----------|---------|
| `implement-flow/docs/researching-reference.md` | Research delegation guide for chain invocations |
| `discussions-usage` rule | Discussion categories and Research → Rule extraction workflow |
| `rule-evolution` rule | Evolution signal recording procedures |
