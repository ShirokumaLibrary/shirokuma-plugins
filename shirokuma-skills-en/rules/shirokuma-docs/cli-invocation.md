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
shirokuma-docs dashboard
shirokuma-docs issue list
shirokuma-docs lint tests -p .

# Wrong - unnecessary overhead
npx shirokuma-docs dashboard
```

## Prohibited Commands (Covered by CLI)

The following commands are handled internally by the `shirokuma-docs` CLI. Direct use is prohibited.

| Prohibited Command | CLI Alternative |
|-------------------|----------------|
| `gh issue list`, `gh issue view`, `gh issue create` | `shirokuma-docs issue list`, `issue context {number}`, `issue add` |
| `gh issue comment` | `shirokuma-docs issue comment {number} --file {file}` |
| `gh issue edit` | `shirokuma-docs issue update {number}` / `status transition {number} --to <status>` |
| `gh issue close` | `shirokuma-docs issue close {number}` |
| `gh pr create`, `gh pr view`, `gh pr list` | `shirokuma-docs pr create`, `pr show`, `pr list` |
| `gh pr review`, `gh api .../pulls/.../comments` | `shirokuma-docs pr comments`, `pr reply`, `pr resolve` |
| `gh project item-list`, `gh project field-list` | `shirokuma-docs issue list`, `issue fields` (`project list/fields` deprecated) |
| `gh api .../discussions` | `shirokuma-docs discussion list`, `discussion search` |
| `gh search issues` | `shirokuma-docs issue search` |
| `gh search issues --include-prs` | `shirokuma-docs issue search --type issues` |
| Discussions cross-search | `shirokuma-docs issue search --type discussions` |
| Issues + Discussions cross-search | `shirokuma-docs issue search --type issues,discussions` |

### Common Mistake Patterns

```bash
# NG: raw gh commands
gh issue view 42
gh pr create --base develop --title "..."

# OK: shirokuma-docs CLI
shirokuma-docs issue context 42
shirokuma-docs pr create --from-file /tmp/shirokuma-docs/pr.md
```

**Exception**: Operations not covered by the `shirokuma-docs` CLI (e.g., `gh repo view` for repository metadata) may use `gh` directly.

## Verbose Option

Default output is minimal (errors, warnings, success messages only). Progress logs and detailed info are suppressed.

- **Do not** use `--verbose` in AI workflows — it increases context window consumption
- `--verbose` is for human debugging only
