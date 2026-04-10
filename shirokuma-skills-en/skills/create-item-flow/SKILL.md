---
name: create-item-flow
description: Creates GitHub Issues or Discussions with auto-inferred metadata from conversation context, automatically runs requirements review, and routes to the next flow. Triggers: "create issue", "make this an issue", "follow-up issue", "create spec", "new issue", "file an issue".
allowed-tools: Bash, Skill, AskUserQuestion, Read, Write, TaskCreate, TaskUpdate, TaskGet, TaskList
---

# Creating Items

Auto-infer Issue metadata from conversation context and delegate creation to `managing-github-items`. For Issues, automatically run `review-issue requirements` after creation and route to the next flow (`/design-flow`, `/prepare-flow`, `/implement-flow`) based on the review result (`**Review result:**`) and design assessment (`**Design assessment:**`). For Discussions, skip the review and present next action candidates.

## Responsibility Split

| Layer | Responsibility |
|-------|---------------|
| `create-item-flow` | User interface. Context analysis, metadata inference, chain control |
| `managing-github-items` | Internal engine. CLI command execution, field setting, validation |

## Task Registration (Required)

**Before starting work**, register all chain steps via TaskCreate.

| # | content | activeForm | Skill |
|---|---------|------------|-------|
| 1 | Analyze context and infer metadata | Analyzing context | Manager direct |
| 1b | Search for similar issues and suggest linking | Searching for similar issues | Manager direct: `shirokuma-docs items search` |
| 2 | Delegate creation to managing-github-items | Creating the item | `managing-github-items` (Skill) |
| 2b | [Issue only] Run requirements review and design assessment | Running requirements review | `review-issue` (Skill, requirements role) |
| 3 | Return next action candidates to user | Presenting next actions | Manager direct |

Dependencies: step 1b blockedBy 1, step 2 blockedBy 1b, step 2b blockedBy 2 (conditional: only for Issue creation), step 3 blockedBy 2 or 2b.

Update each step to `in_progress` at start and `completed` on finish via TaskUpdate. Step 2b is skipped when creating a Discussion (may be omitted from the task list).

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

### Step 1b: Search for Similar Issues and Suggest Linking

After context analysis, search for similar existing Issues/Discussions before creation to identify duplicates or linking opportunities.

```bash
shirokuma-docs items search "<keyword>" --limit 5
```

- If similar Issues found: present to user and ask whether to create a new issue or consolidate into an existing one (`AskUserQuestion`)
- If related Issues found: suggest setting parent-child relationship with `items parent` after creation
- If nothing found: proceed to the next step

### Step 2: Delegate to `managing-github-items`

After context analysis, invoke via Skill tool immediately (no pre-creation confirmation):

```
Skill: managing-github-items
Args: create-item --title "{Title}" --issue-type "{Type}" --labels "{area:label}" --priority "{Priority}" --size "{Size}"
```

### Step 2b: Requirements Review and Design Assessment (invoke review-issue requirements)

**Scope**: Execute only when the created item's type is `issue`. Skip for `discussion` and present next action candidates in Step 3 as usual.

Leverage the context immediately after Issue creation to invoke `review-issue requirements #{issue-number}` via the Skill tool.

```
Skill: review-issue
Args: requirements #{issue-number}
```

`review-issue requirements` may additionally perform a Project Requirement Consistency check (ADR reference) based on Issue keywords and labels. See [../review-issue/roles/requirements.md](../review-issue/roles/requirements.md#project-requirement-consistency) for trigger conditions and output fields.

#### Expected Output Fields

Scan the Issue comment posted by `review-issue` for the following strings:
- `**Review result:**` — PASS or NEEDS_REVISION (always output)
- `**Design assessment:**` — NEEDED or NOT_NEEDED (always output)
- `**Project Requirement Consistency:**` — PASS or NEEDS_REVISION (only when ADR check is performed)
- `**Referenced ADRs:**` — ADR number list (only when ADR check is performed)

#### Handling on Check Failure

When `Review result` is `NEEDS_REVISION` (revision loop): Present the issues to the user and request corrections to the Issue body. Invoke `review-issue requirements` again after corrections (maximum 2 revision loops; on the 3rd NEEDS_REVISION, defer to the user).

When `Project Requirement Consistency` is `NEEDS_REVISION`: Present the conflicting ADR numbers and conflict details. Use AskUserQuestion to let the user choose:
- "Modify the Issue body to make it consistent" → run requirements review again after modification
- "Review existing ADRs first (using `writing-adr` update flow)" → guide to `/writing-adr` and suspend this step

### Step 3: Return to User

**For Discussion**: Step 2b is skipped, so present the creation completion and next action candidates.

```markdown
Discussion created: #{number}
→ Suggest follow-up discussions or related issues
```

**For Issue**: When Step 2b's `**Review result:**` is PASS, branch in 3 directions based on `**Design assessment:**`.

**When Design assessment is NEEDED (go to design phase):**

```markdown
Item created: #{number}
**Review result:** PASS / **Design assessment:** NEEDED
→ `/design-flow #{issue-number}` to start design (recommended)
→ Or keep in Backlog
```

**When Design assessment is NOT_NEEDED and Size M+ or requirements ambiguous (go to planning phase):**

```markdown
Item created: #{number}
**Review result:** PASS / **Design assessment:** NOT_NEEDED
→ `/prepare-flow #{issue-number}` to start planning (recommended)
→ `/implement-flow #{issue-number}` to implement directly
→ Or keep in Backlog
```

**When Design assessment is NOT_NEEDED and Size XS/S and requirements clear (implement directly):**

```markdown
Item created: #{number}
**Review result:** PASS / **Design assessment:** NOT_NEEDED
→ `/implement-flow #{issue-number}` to implement directly (recommended)
→ Or keep in Backlog
```

Design assessment (NEEDED / NOT_NEEDED) takes priority over Size assessment. If design is NEEDED, guide to `/design-flow` regardless of Size.

See [reference/chain-rules.md](reference/chain-rules.md) for chain decision details.

## Reference Documents

| Document | Content | When to Read |
|----------|---------|--------------|
| [reference/chain-rules.md](reference/chain-rules.md) | Chain decision rules and inference logic | Item creation |
| [reference/purpose-criteria.md](reference/purpose-criteria.md) | Means vs purpose criteria (JTBD-based) | Context analysis (purpose clarity check) |

## Next Steps

Based on Step 2b `review-issue requirements` result, branch in 3 directions: Design NEEDED → `/design-flow`, Design NOT_NEEDED + M+ → `/prepare-flow`, Design NOT_NEEDED + XS/S + clear requirements → `/implement-flow`. See Step 3 for details.

## Evolution Signal Auto-Recording

At the end of the item creation completion report, auto-record Evolution signals following the "Auto-Recording Procedure at Skill Completion" in the `rule-evolution` rule.

**Skip condition:** If the created item's Issue Type is Evolution, skip the entire signal recording (the Evolution Issue itself is an improvement proposal, avoiding duplicate recording).

## GitHub Writing Rules

Issue title and body must comply with the `output-language` rule and `github-writing-style` rule. This rule also applies to the delegated `managing-github-items` skill.

## Notes

- After creation, inform the user and offer the opportunity to request modifications
- Delegate CLI execution to `managing-github-items` (don't call CLI directly)
- Detailed inference tables are available via the `managing-github-items` skill
