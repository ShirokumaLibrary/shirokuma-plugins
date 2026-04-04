---
name: approve
description: Explicitly approve a Review-status Issue (plan, design, etc.) and transition it to Done. Trigger: "approve", "approve issue", "approve plan".
allowed-tools: Bash, Read, Edit
---

# Approve Issue

Explicitly approve a Review-status Issue and transition it to Done. Handles the case where you want to confirm a plan but not start implementation immediately.

Normally, `/implement-flow` implicitly approves plan Issues when starting work (#1932). This skill is for cases where that implicit approval won't happen (reviewing and approving without starting work).

## Arguments

| Format | Example | Behavior |
|--------|---------|----------|
| Issue number | `#42` | Approve specified Issue |
| No args | — | AskUserQuestion to confirm |

## Workflow

1. **Fetch Issue**: `shirokuma-docs items pull {number}` to cache the Issue
2. **Check status**: Read `.shirokuma/github/{org}/{repo}/issues/{number}/body.md` and check frontmatter `status`
   - If not Review, warn and exit ("Issue #{number} is not in Review status (current: {status})")
3. **Execute approval**: `shirokuma-docs items close {number}` to set Done + close
4. **Completion report**:

```
## Approval Complete

**Issue:** #{number} {title}
**Transition:** Review → Done + Closed
```

## Edge Cases

| Situation | Action |
|-----------|--------|
| Status is not Review | Warn and exit |
| Already Done / Closed | Display "Already Done" and exit |
| Issue not found | Display error |
