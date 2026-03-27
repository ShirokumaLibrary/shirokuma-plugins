---
scope: default
category: shirokuma-docs
priority: required
---

# shirokuma-docs CLI Invocation

## Direct Call (No npx)

`shirokuma-docs` is installed globally. Always call it directly:

```bash
# Correct
shirokuma-docs session start
shirokuma-docs issues list
shirokuma-docs lint tests -p .

# Wrong - unnecessary overhead
npx shirokuma-docs session start
```

## Prohibited Commands (Covered by CLI)

The following commands are handled internally by the `shirokuma-docs` CLI. Direct use is prohibited.

| Prohibited Command | CLI Alternative |
|-------------------|----------------|
| `gh issue list`, `gh issue view`, `gh issue create` | `shirokuma-docs issues list`, `show`, `issues create` |
| `gh issue comment` | `shirokuma-docs issues comment` / `comment` |
| `gh issue edit` | `shirokuma-docs issues update` |
| `gh issue close` | `shirokuma-docs issues close` |
| `gh pr create`, `gh pr view`, `gh pr list` | `shirokuma-docs pr create`, `pr show`, `pr list` |
| `gh pr review`, `gh api .../pulls/.../comments` | `shirokuma-docs pr comments`, `pr reply`, `pr resolve` |
| `gh project item-list`, `gh project field-list` | `shirokuma-docs projects list`, `projects fields` |
| `gh api .../discussions` | `shirokuma-docs discussions list`, `discussions search` |
| `gh search issues` | `shirokuma-docs search` |

### Common Mistake Patterns

```bash
# NG: raw gh commands
gh issue view 42
gh pr create --base develop --title "..."

# OK: shirokuma-docs CLI
shirokuma-docs show 42
shirokuma-docs pr create --from-file /tmp/shirokuma-docs/pr.md
```

**Exception**: Operations not covered by the `shirokuma-docs` CLI (e.g., `gh repo view` for repository metadata) may use `gh` directly.

## Verbose Option

Default output is minimal (errors, warnings, success messages only). Progress logs and detailed info are suppressed.

- **Do not** use `--verbose` in AI workflows — it increases context window consumption
- `--verbose` is for human debugging only
