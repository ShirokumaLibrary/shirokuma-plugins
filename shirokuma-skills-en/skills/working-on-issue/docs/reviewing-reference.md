# Review Work Type Reference

Guide for delegating from `working-on-issue` to `review-issue` skill.

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

## Post-PR Review

When code review is needed after PR creation, use `/reviewing-on-pr`.
