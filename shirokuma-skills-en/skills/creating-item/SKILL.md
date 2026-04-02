---
name: creating-item
description: Creates GitHub Issues or Discussions with auto-inferred metadata from conversation context and provides auto-chaining to implement-flow. Triggers: "create issue", "make this an issue", "follow-up issue", "create spec", "new issue", "file an issue".
allowed-tools: Bash, AskUserQuestion, Read, Write, TaskCreate, TaskUpdate, TaskGet, TaskList
---

# Creating Items

Auto-infer Issue metadata from conversation context, delegate to `managing-github-items` for creation, and provide auto-chaining to `implement-flow`.

## Responsibility Split

| Layer | Responsibility |
|-------|---------------|
| `creating-item` | User interface. Context analysis, metadata inference, chain control |
| `managing-github-items` | Internal engine. CLI command execution, field setting, validation |

## Workflow

### Step 1: Context Analysis

Infer from conversation context:

| Field | Inference Source |
|-------|-----------------|
| Title | Concise summary from user's statement |
| Issue Type | Content keywords (see [reference/chain-rules.md](reference/chain-rules.md)) |
| Priority | Impact scope and urgency |
| Size | Work effort |
| Area labels | Affected code areas |

**Purpose Clarity Check (required)**: If the user's message only describes a "means" (what to do) without a clear "purpose" (who / what / why), present inferred purpose candidates and confirm via `AskUserQuestion`. See [reference/purpose-criteria.md](reference/purpose-criteria.md) for criteria.

### Step 2: Delegate to `managing-github-items`

After context analysis, invoke via Skill tool immediately (no pre-creation confirmation):

```
Skill: managing-github-items
Args: create-item --title "{Title}" --issue-type "{Type}" --labels "{area:label}" --priority "{Priority}" --size "{Size}"
```

### Step 3: Return to User

After creation, display next action guidance based on the default recommendation from [reference/chain-rules.md](reference/chain-rules.md):

**When Size XS/S and requirements are clear (default: start immediately):**

```markdown
Item created: #{number}
→ `/implement-flow #{number}` to start implementation directly (recommended)
→ `/prepare-flow #{number}` to start planning
→ Or keep in Backlog
```

**When Size M+ or requirements are ambiguous (default: review then plan):**

```markdown
Item created: #{number}
→ `/review-issue plan #{number}` to review requirements and spec impact (recommended)
→ `/prepare-flow #{number}` to start planning
→ `/implement-flow #{number}` to start implementation directly
→ Or keep in Backlog
```

See [reference/chain-rules.md](reference/chain-rules.md) "Review Execution Conditions" section for review recommendation details.

## Reference Documents

| Document | Content | When to Read |
|----------|---------|--------------|
| [reference/chain-rules.md](reference/chain-rules.md) | Chain decision rules and inference logic | Item creation |
| [reference/purpose-criteria.md](reference/purpose-criteria.md) | Means vs purpose criteria (JTBD-based) | Context analysis (purpose clarity check) |

## Next Steps

Based on chain-rules.md: recommend `/implement-flow` for Size XS/S with clear requirements, `/review-issue plan` then `/prepare-flow` for Size M+ or ambiguous requirements. See Step 3 for details.

## Evolution Signal Auto-Recording

At the end of the item creation completion report, auto-record Evolution signals following the "Auto-Recording Procedure at Skill Completion" in the `rule-evolution` rule.

**Skip condition:** If the created item's Issue Type is Evolution, skip the entire signal recording (the Evolution Issue itself is an improvement proposal, avoiding duplicate recording).

## GitHub Writing Rules

Issue title and body must comply with the `output-language` rule and `github-writing-style` rule. This rule also applies to the delegated `managing-github-items` skill.

## Notes

- After creation, inform the user and offer the opportunity to request modifications
- Delegate CLI execution to `managing-github-items` (don't call CLI directly)
- Detailed inference tables are available via the `managing-github-items` skill
