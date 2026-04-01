---
scope:
  - coding-worker
  - design-worker
  - plan-worker
  - review-worker
category: general
priority: preferred
---

# Local Documentation Priority Lookup

Check local documentation before WebSearch when looking up external library APIs or patterns.

## Activation Condition

Applies when you need to reference external library APIs, configuration, or patterns. Skip when working only with project-internal code.

## Procedure

### 1. Detect Documentation Sources

```bash
shirokuma-docs docs detect --format json
```

Check if any sources have `status: "ready"`. If no sources are available, end this rule's processing and use WebSearch as needed.

### 2. Local Search

Search against `status: "ready"` sources:

```bash
shirokuma-docs docs search "<technology> <feature>" --source <source-name> --section --limit 5
```

### 3. Fallback

Use WebSearch only when local documentation lacks the needed information or is insufficient.

## Priority Order

1. Local documentation (`shirokuma-docs docs search`)
2. WebSearch / WebFetch (official documentation)

## Skill-Specific Override

When a skill's SKILL.md includes its own local documentation search step (e.g., `review-issue` with `--limit 3`), the skill-specific `--limit` value takes precedence over this rule's default (`--limit 5`).
