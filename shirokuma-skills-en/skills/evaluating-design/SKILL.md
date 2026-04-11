---
name: evaluating-design
description: Conducts visual evaluation with the user after implementation completes. Checks the dev server, presents a review checklist, and collects feedback, returning APPROVED / NEEDS_REVISION / DIRECTION_CHANGE. Called as Phase 4 of design-flow via Skill tool.
allowed-tools: Bash, AskUserQuestion
---

# Design Evaluation

Conducts visual evaluation with the user after implementation completes. Called as Phase 4 of `design-flow`.

## Context

The following context is passed from the calling `design-flow`:

- List of changed file paths
- Design type (whether it is a UI design)

## Skip Condition

For design types without visual elements (e.g., data model design), the caller skips this skill and proceeds directly to Phase 5.

## Workflow

### Step 1: Dev Server Check

```bash
# Check if dev server is running
lsof -i :3000 2>/dev/null || echo "dev server not running"
```

Suggest starting the dev server if it is not running.

### Step 2: User Review

Present the following via `AskUserQuestion`:

- List of changed file paths
- Review URL (if dev server is running: `http://localhost:3000`)
- Review checklist:
  - [ ] Typography is distinctive
  - [ ] Color palette is cohesive
  - [ ] Motion/animation impression
  - [ ] Layout visual interest
  - [ ] Overall impression

Present choices:
1. **Approve** → Visual evaluation complete, return to caller
2. **Request changes** → Receive feedback and return to caller (re-delegate to design skill in Phase 3)
3. **Change direction** → Notify caller of direction change (return to Phase 2)

### Reference: Safety Limit

The visual evaluation loop is limited to **3 iterations maximum**.

The calling `design-flow` manages the iteration count and proceeds directly to Phase 5 without calling this skill when the limit is reached. On reaching the limit, proceed with the current state and suggest a follow-up Issue for further improvements.

## Output

Return the following to the caller (`design-flow`) based on the user's choice:

| Choice | Return Value |
|--------|-------------|
| Approve | `APPROVED` |
| Request changes | `NEEDS_REVISION: {feedback}` |
| Change direction | `DIRECTION_CHANGE` |

## Tool Usage

| Tool | When |
|------|------|
| Bash | Dev server check (Step 1) |
| AskUserQuestion | Visual evaluation (Step 2) |

## Notes

- This skill uses `AskUserQuestion` and must be called via Skill tool (main context); Agent delegation is not allowed
- Iteration count management is the responsibility of the calling `design-flow`
