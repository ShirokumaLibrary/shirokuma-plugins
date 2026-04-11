---
scope: default
category: general
priority: required
---

# Completion Report Style Guide

Ensure "same system" consistency across skill completion reports. Consistency, not uniformity.

## Heading

Use `## {Action Noun} Complete` as the standard heading.

| Good | Bad |
|------|-----|
| `## Commit Complete` | `## Results` |
| `## Plan Complete: #42 Title` | `## Summary Display` |
| `## Rule Created` | `## Output` |

Append `: #{number} {title}` when contextual identification is useful.

## Summary Paragraph (Recommended)

Before the KV pairs, add a **1–2 sentence summary paragraph stating what was done**.

```
## Commit Complete

Updated 2 rules (`github-writing-style` and `completion-report-style`) and 5 skill writing templates.

**Branch:** feat/2090-writing-style
**Commit:** abc1234 refactor: update writing rules
**Files:** 7 files changed
**Pushed:** yes
```

A summary paragraph conveys the **intent and scope** of the change, providing more context than KV pairs alone. It may be omitted when the intent is self-evident from the KV pairs alone (e.g., a single minor file change).

## Key-Value Display

Use `**{Label}:** {value}` format.

```
**Branch:** feat/42-xxx
**Status:** Review
**Location:** .claude/rules/my-rule.md
```

## Structure Selection

| Data Shape | Structure |
|-----------|-----------|
| 2 or fewer key-value pairs | `**Key:** value` bullet list |
| 3+ column tabular data | Table |
| Ordered list | Numbered list |

For detailed bullets vs prose guidelines in GitHub content (Issues, PRs, Discussions), see the `github-writing-style` rule.

## GitHub References

| Target | Format |
|--------|--------|
| Issue / PR / Discussion | `#123` |
| External links | Full URL |
| File paths | Backtick `path/to/file` |

## Next Steps

| Invocation | Next Steps |
|-----------|------------|
| Chain (via implement-flow) | Omit (chain auto-executes) |
| Standalone | Always suggest |

## Skill Category Guide

| Category | Template Required | Examples |
|----------|------------------|---------|
| Workflow | Required (strict) | commit-issue, open-pr-issue |
| Config Management | Required (strict) | coding-claude-config |
| Analysis | Required (with tables) | evolving-rules, prepare-flow |
| Display / Orchestrator | Not required | showing-github, implement-flow |
| Delegator | Deferred to caller | review-issue, create-item-flow |

Skills that do not require templates may omit the completion report section entirely.

## Information Hierarchy

Arrange completion report information in this priority order:

```
Level 1: Heading (outcome + context ID)        -- 1 second scan
Level 2: Summary paragraph (intent + scope)    -- 3 second scan
Level 3: KV pairs (critical facts)             -- 5 second scan
Level 4: Table or list (details)               -- 15 second scan
Level 5: Prose explanation (rationale)          -- 30+ second read
```

**1-second test**: The heading + the first sentence of the summary paragraph must convey the outcome and where to find the artifact.

## Field Classification

Classify each field in a template:

| Classification | Meaning | Template Notation |
|---------------|---------|-------------------|
| Fixed | Always present, same format | `**Label:** {value}` |
| Conditional | Present only when applicable | `[**Label:** {value}]` |
| Freeform | Variable-length content | `{description}` |

Avoid omitting Fixed fields or always showing Conditional fields.

## Prohibited Patterns

- Raw URLs for GitHub references (`https://github.com/.../issues/42` → `#42`)
- Markdown links for GitHub references (`[#123](URL)` → `#123`)
- Verb forms in headings (`## Generate Report` → `## Report Generated`)
- Inconsistent section names (do not mix "confirmation", "summary display", "report generation")
- Process narration ("First I read the file..." → state results only)
- Self-referential verbosity ("Successfully completed!" → state facts only)
