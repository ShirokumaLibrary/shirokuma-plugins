---
scope: default
category: general
priority: required
---

# Git Commit Style

## Commit Message Format

```
{type}: {description} (#{issue-number})

{optional body}
```

## Conventional Commit Types

| Type | When |
|------|------|
| `feat` | New feature or enhancement |
| `fix` | Bug fix |
| `refactor` | Code restructuring (no behavior change) |
| `docs` | Documentation only |
| `test` | Adding or updating tests |
| `chore` | Config, tooling, dependencies |

## Rules

1. **First line under 72 characters**
2. **Reference issue number** when applicable: `(#39)`
3. **Imperative mood** in description: "add feature" not "added feature"
4. **Body is optional** - Use for complex changes that need explanation
5. **Blank line** between subject and body

## Examples

```
feat: add branch workflow rules (#39)

fix: pass repo name to getProjectId for cross-repo support (#34)

refactor: separate marketplace and plugin directory structure (#27)

chore: update dependencies
```

## Code Language

| Element | Language |
|---------|----------|
| Code / Variable names | English |
| Comments / JSDoc / TSDoc | English |
| Commit messages | English (conventional commits format) |
| CLI output messages | Per i18n dictionary (`i18n/cli/`) |

## What NOT to Do

- Do not include `Signed-off-by` lines unless required by project
- Do not use `--no-verify` to skip hooks
- Do not amend commits unless explicitly asked
- Do not force push to the base branch
