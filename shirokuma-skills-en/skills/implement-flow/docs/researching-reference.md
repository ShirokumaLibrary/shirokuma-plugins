# Research Work Type Reference

Guide for delegating from `implement-flow` to `researching-best-practices` skill.

## Delegation Conditions

| Condition | Delegate To |
|-----------|-------------|
| Keywords: `research`, `investigate`, `best practices` | `researching-best-practices` |
| Issue type: Research | `researching-best-practices` |

### Boundary Cases

Use these examples to judge ambiguous situations:

| Situation | Action |
|-----------|--------|
| "I know how to implement it, but best practices are unclear" | Delegate to `researching-best-practices` |
| "Selecting an external library (multiple options, unclear trade-offs)" | Delegate to `researching-best-practices` |
| "Standard CRUD feature with known patterns" | Direct implementation (no research needed) |
| "Existing internal pattern can be reused" | Check codebase, then implement directly |
| "Security-sensitive implementation area" | Research first, then implement |
| "Performance optimization — unclear which approach is better" | Delegate to `researching-best-practices` |

## Execution Context

`researching-best-practices` runs as an Agent tool (subagent). Does not pollute main context.

## TDD Not Applied

Research work type does not use TDD.

## What researching-best-practices Provides

- Technical research prioritizing local documentation (`docs search`)
- Supplemental web search-powered technical research
- Best practice comparison and analysis
- Structured research report

## Local Documentation Priority Order

`researching-best-practices` collects information in this order:
1. Check available local documentation via `shirokuma-docs docs detect`
2. If `status: "ready"` sources exist, search locally with `docs search --section --limit 5`
3. Supplement with WebSearch only when local sources are insufficient

## Review Gate

After `researching-best-practices` completes, optionally pass the output through `analyze-issue` with the `research` role before saving to Discussion.

```
implement-flow → researching-best-practices → analyze-issue (research role) → Discussion creation → Complete
```

Invoke `analyze-issue` via Agent tool (`review-worker`) with the following context:

```
role: research
target: research report from researching-best-practices
focus: accuracy, completeness, missing perspectives
```

The `analyze-issue` skill has a `roles/research.md` role definition that guides the review for research outputs. Use this role to ensure the research report is thorough before saving.

**When to apply the review gate**:

| Condition | Apply Review Gate? |
|-----------|-------------------|
| Research for critical architecture decisions | Yes |
| Quick best-practice lookup | Optional |
| Issue type: Research (explicit) | Yes |

## Chain

Research uses Discussion creation instead of the commit → PR chain.

```
researching-best-practices → [analyze-issue (research role)] → Discussion (Research) creation → Complete
```

## Discussion Storage

Research results are saved to Research category Discussion:

```bash
shirokuma-docs items add discussion --file /tmp/shirokuma-docs/research-result.md
```
