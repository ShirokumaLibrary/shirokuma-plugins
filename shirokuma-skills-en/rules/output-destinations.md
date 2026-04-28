---
paths:
  - ".claude/skills/**/*.md"
# Scope note: This rule uses 'paths' (skill-file-scoped) rather than 'scope: default' intentionally.
# Rationale: output destination decisions are relevant only during skill authoring and editing.
# Loading this rule globally (scope: default) would add noise to non-skill contexts.
# The skill context (when reading/writing .claude/skills/**/*.md) is the correct load point.
---

# Output Destinations Rule

## Overview

Claude Code skills produce two types of output. Route each to the appropriate destination.

## Output Types

| Type | Purpose | Destination | Lifetime |
|------|---------|-------------|----------|
| **Working reports** | Human review during work | GitHub Discussions (Reports) | Temporary |
| **Final documentation** | Project-wide records | shirokuma-docs generate portal | Permanent |

## Working Reports

**Use for**: Review reports, implementation progress, lint results

**Destination**: GitHub Discussions → Reports category

```bash
# Create via shirokuma-docs CLI (frontmatter includes metadata)
shirokuma-docs discussion add --file /tmp/shirokuma-docs/report.md
```

**Characteristics**:
- Created during active work sessions
- For human confirmation and feedback
- Can be periodically cleaned up
- Viewable in GitHub browser UI

## Final Documentation

**Use for**: Complete feature docs, API references, architecture diagrams

**Destination**: shirokuma-docs generate portal

```bash
# Build portal
shirokuma-docs generate portal -p . -o docs/portal

# Or via skill
/shirokuma-md build
```

**Characteristics**:
- Created after work completion
- Permanent project documentation
- Auto-generated from code annotations
- Viewable at docs portal URL

## Migration from Local Logs

**Old pattern** (deprecated):
```
logs/reports/YYYY-MM-DD-*.md
logs/reviews/YYYY-MM-DD-*.md
```

**New pattern**:
```
Working → GitHub Discussions (Reports)
Final   → shirokuma-docs generate portal
```

## Skill Updates

When updating skills, replace local log references:

| Old | New |
|-----|-----|
| `Save to logs/reports/` | `Create Discussion in Reports category` |
| `Save to logs/reviews/` | `Create Discussion in Reports category` |
| Report file path output | Discussion URL output |

## PR Reviews → PR Comments

Review results targeting a PR should be posted directly as PR comments.

```bash
shirokuma-docs issue comment {PR#} --file /tmp/shirokuma-docs/{PR#}-review-summary.md
```

| Condition | Destination |
|-----------|-------------|
| PR review (normal) | PR comment (summary) |
| PR review (5+ errors) | PR comment + Discussion (detailed) |
| File/directory review | Discussion (Reports) |

## Reports Category Usage

| Purpose | Example |
|---------|---------|
| Comprehensive review reports | Project-wide security audit |
| Research results | Best practice research, technology comparisons |
| Self-review feedback | Pattern accumulation from automated review loops |

**Do NOT save to Reports**: PR-specific review results (→ post as PR comment instead)

## Notes

- **No local files**: Avoid storing reports in repository
- **Browser-friendly**: GitHub Discussions for easy human review
- **Clean separation**: Temporary (Discussions) vs Permanent (Portal)
- **PR reviews → PR comments**: Post PR-targeted reviews directly on the PR
