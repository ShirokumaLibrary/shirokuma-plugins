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
shirokuma-docs items dashboard
shirokuma-docs items list
shirokuma-docs lint tests -p .

# Wrong - unnecessary overhead
npx shirokuma-docs items dashboard
```

## Prohibited Commands (Covered by CLI)

The following commands are handled internally by the `shirokuma-docs` CLI. Direct use is prohibited.

| Prohibited Command | CLI Alternative |
|-------------------|----------------|
| `gh issue list`, `gh issue view`, `gh issue create` | `shirokuma-docs items list`, `items context {number}`, `items add issue` |
| `gh issue comment` | `shirokuma-docs items add comment {number} --file {file}` |
| `gh issue edit` | `shirokuma-docs items update {number}` / `items transition {number} --to <status>` |
| `gh issue close` | `shirokuma-docs items close {number}` |
| `gh pr create`, `gh pr view`, `gh pr list` | `shirokuma-docs items pr create`, `items pr show`, `items pr list` |
| `gh pr review`, `gh api .../pulls/.../comments` | `shirokuma-docs items pr comments`, `items pr reply`, `items pr resolve` |
| `gh project item-list`, `gh project field-list` | `shirokuma-docs items list`, `items fields` (`items projects list/fields` deprecated) |
| `gh api .../discussions` | `shirokuma-docs items discussions list`, `items discussions search` |
| `gh search issues` | `shirokuma-docs items search` |
| `gh search issues --include-prs` | `shirokuma-docs items search --type issues` |
| Discussions cross-search | `shirokuma-docs items search --type discussions` |
| Issues + Discussions cross-search | `shirokuma-docs items search --type issues,discussions` |

### Common Mistake Patterns

```bash
# NG: raw gh commands
gh issue view 42
gh pr create --base develop --title "..."

# OK: shirokuma-docs CLI
shirokuma-docs items context 42
shirokuma-docs items pr create --from-file /tmp/shirokuma-docs/pr.md
```

**Exception**: Operations not covered by the `shirokuma-docs` CLI (e.g., `gh repo view` for repository metadata) may use `gh` directly.

## Verbose Option

Default output is minimal (errors, warnings, success messages only). Progress logs and detailed info are suppressed.

- **Do not** use `--verbose` in AI workflows — it increases context window consumption
- `--verbose` is for human debugging only
