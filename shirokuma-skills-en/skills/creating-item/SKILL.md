---
name: creating-item
description: Creates GitHub Issues or Discussions with auto-inferred metadata from conversation context and provides auto-chaining to working-on-issue. Triggers: "create issue", "make this an issue", "follow-up issue", "create spec", "new issue", "file an issue".
allowed-tools: Bash, AskUserQuestion, Read, Write, TodoWrite
---

# Creating Items

Auto-infer Issue metadata from conversation context, delegate to `managing-github-items` for creation, and provide auto-chaining to `working-on-issue`.

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

After creation, display next action guidance:

```markdown
Item created: #{number}
→ `/preparing-on-issue #{number}` to start planning
→ `/working-on-issue #{number}` to start implementation directly
→ Or keep in Backlog
```

See [reference/chain-rules.md](reference/chain-rules.md) for chain decision details.

## Reference Documents

| Document | Content | When to Read |
|----------|---------|--------------|
| [reference/chain-rules.md](reference/chain-rules.md) | Chain decision rules and inference logic | Item creation |
| [reference/purpose-criteria.md](reference/purpose-criteria.md) | Means vs purpose criteria (JTBD-based) | Context analysis (purpose clarity check) |

## Next Steps

```
Item created: #{number}
→ `/preparing-on-issue #{number}` to start planning
→ `/working-on-issue #{number}` to start implementation directly
→ Or keep in Backlog
```

## Evolution Signal Auto-Recording

At the end of the item creation completion report, auto-record Evolution signals following the "Auto-Recording Procedure at Skill Completion" in the `rule-evolution` rule.

**Skip condition:** If the created item's Issue Type is Evolution, skip the entire signal recording (the Evolution Issue itself is an improvement proposal, avoiding duplicate recording).

## GitHub Writing Rules

Issue title and body must comply with the `output-language` rule and `github-writing-style` rule. This rule also applies to the delegated `managing-github-items` skill.

## Notes

- After creation, inform the user and offer the opportunity to request modifications
- Delegate CLI execution to `managing-github-items` (don't call CLI directly)
- Detailed inference tables are in `managing-github-items`'s `reference/create-item.md`
