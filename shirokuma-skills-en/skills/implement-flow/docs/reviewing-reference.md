# Review Work Type Reference

Guide for delegating from `implement-flow` to `review-issue` skill.

## Delegation Conditions

| Condition | Delegate To |
|-----------|-------------|
| Keywords: `review`, `audit`, `security check` | `review-issue` |
| PR review request | `review-issue` |

## Execution Context

`review-issue` runs as an Agent tool (subagent). Does not pollute main context.

## TDD Not Applied

Review work type does not use TDD.

## What review-issue Provides

- Role-specific reviews (code, security, test, docs, plan)
- Issue / PR context-based review
- Review results posted as PR comments

## Chain

Review work type does NOT execute the commit → PR chain (completes with report).

```
review-issue → Report posted → Complete
```

## Post-Review Follow-up

After `review-issue` completes, the manager evaluates the output and determines the next action:

| Condition | Action |
|-----------|--------|
| `ucp_required: true` in worker output | Present review findings to user via AskUserQuestion before proceeding |
| `followup_candidates` present | Propose follow-up Issues to user |
| No issues found | Report completion to user |
| Issues found (code changes needed) | AskUserQuestion: proceed with fixes or create follow-up Issues |

Do NOT automatically start `code-issue` based on review findings — always present results to user first.

## Post-PR Review

When code review is needed after PR creation, use `/review-flow`.
