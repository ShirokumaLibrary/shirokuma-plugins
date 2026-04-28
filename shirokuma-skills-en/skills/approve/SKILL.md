---
name: approve
description: Explicitly approve a Review-status Issue (plan, design, etc.) and transition it to Done. The Issue remains Open (closed when the parent closes). Trigger: "approve", "approve issue", "approve plan".
allowed-tools: Bash, Read, Edit
---

# Approve Issue

Explicitly approve a Review-status Issue and transition it to Done (Issue remains Open). Handles the case where you want to confirm a plan but not start implementation immediately.

Normally, `/implement-flow` implicitly approves plan Issues when starting work (#1932). This skill is for cases where that implicit approval won't happen (reviewing and approving without starting work).

## Arguments

| Format | Example | Behavior |
|--------|---------|----------|
| Issue number | `#42` | Approve specified Issue |
| No args | — | AskUserQuestion to confirm |

## Workflow

1. **Execute approval**: Run `shirokuma-docs status approve {number}`. The CLI validates status internally and exits with `result: "error"` if the Issue is not in Review.
2. **Branch on result**: Inspect `result` in the JSON output
   - `"ok"` → Show completion report and present `next_suggestions` to the user
   - `"error"` → Display the `message` field as-is and exit
3. **Completion report** (when `result: "ok"`):

```
## Approval Complete

**Issue:** #{number} {title}
**Transition:** Review → Done (remains Open)

### Next Actions
{next_suggestions content}
```

## Edge Cases

| Situation | Action |
|-----------|--------|
| Not Review / Already Done / Issue not found | Surface the CLI `result: "error"` `message` and exit |
