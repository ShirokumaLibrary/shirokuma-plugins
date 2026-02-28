---
name: creating-pr-on-issue
description: Create a GitHub pull request for the current branch to develop (or integration branch for sub-issues). Use when "create pull request", "create PR", "open PR".
context: fork
agent: general-purpose
allowed-tools: Bash, Read, Grep, Glob
---

# Creating Pull Request

Create a GitHub pull request from the current feature branch.

## Workflow

### Step 1: Verify Branch State

PRs target `develop` for daily work (see `branch-workflow` rule):

```bash
git branch --show-current
git status --short
git log --oneline develop..HEAD
```

**Pre-checks:**
- Must be on a feature branch (not `develop` or `main`)
- All changes should be committed
- Branch should have commits ahead of `develop`

If on `develop` or `main`, return an error.

### Step 2: Push Branch

Ensure the branch is pushed and up to date:

```bash
git push -u origin {branch-name}
```

### Step 2b: Base Branch Detection

Default is `develop`. When invoked with an issue number, automatically detect sub-issues and use the integration branch as base.

#### Sub-Issue Auto-Detection

If the `shirokuma-docs issues show {number}` output contains a `parentIssue` field, the issue is a sub-issue:

```yaml
parentIssue:
  number: 958
  title: "Migrate to Octokit"
```

If context was passed from `working-on-issue`, use it; otherwise, self-detect using the above (fallback structure).

#### Integration Branch Extraction

When a sub-issue is detected, determine the integration branch in this order:

1. **Extract from parent issue body**: Fetch the parent issue with `shirokuma-docs issues show {parent-number}` and look for a `### Integration Branch` (EN) / `### Integration ブランチ` (JA) heading. Extract the branch name from the backtick block immediately following the heading (any prefix accepted: `epic/`, `chore/`, `feat/`, etc.)
2. **Fallback (remote branch search)**: `git branch -r --list "origin/*/{parent-number}-*"`
   - 1 match → auto-select
   - Multiple matches → select first match, include alternatives in result
   - 0 matches → fall back to `develop`, include warning in result
3. **Final fallback**: `develop`

```bash
# Sub-issue
base_branch="{type}/{parent-number}-{slug}"

# Normal
base_branch="develop"
```

**Note**: For PRs targeting the integration branch, the GitHub sidebar will not display the issue link. `Closes #N` should still be included in the PR body (the CLI's `issues merge` parses it independently and works correctly).

### Step 3: Analyze Changes

Review all commits on the branch to draft PR content:

```bash
git log --oneline {base_branch}..HEAD
git diff --stat {base_branch}..HEAD
```

Understand the full scope of changes, not just the latest commit.

### Step 4: Create PR

Write the PR body to a file, then create the PR. When changes meet the Mermaid conditions in the `github-writing-style` rule, include diagrams in the PR body.

```markdown
<!-- /tmp/shirokuma-docs/{number}-pr-body.md -->
## Summary
- {bullet point 1}
- {bullet point 2}

## Related Issues
{Closes #N or Refs #N}

## Test plan
- [ ] {test item 1}
- [ ] {test item 2}
```

```bash
shirokuma-docs issues pr-create --base {base_branch} --title "{title}" --body-file /tmp/shirokuma-docs/{number}-pr-body.md
```

**Title rules:**
- Under 70 characters
- Conventional commit prefixes (`feat:`, `fix:`, `chore:`, `docs:`, etc.) are always in English
- **Text after the prefix must be in English**
- No issue number in title (goes in body)

**Title examples:**

```text
feat: add branch workflow rules
fix: resolve cross-repo Projects lookup
docs: update CLAUDE.md command table
chore: update dependencies
```

**Bad examples (non-English text in EN plugin):**

```text
feat: ブランチワークフロールールを追加    ← Wrong: not English
docs: CLAUDE.md のコマンド一覧を更新      ← Wrong: not English
```

**Body rules:**
- Summary: 1-3 bullet points of what changed
- Related Issues: `Closes #N` for completed items, `Refs #N` for related
- Test plan: checklist of verification steps

### Step 5: Completion Report

```markdown
## Pull Request Created

**PR:** {url}
**Branch:** {branch} → {base-branch}
**Commits:** {count}

### Summary
{brief description}

### Linked Issues
- Closes #{number}
- Refs #{number}
```

## Batch Mode

When on a batch branch or when batch context (multiple issue numbers) is provided:

### Batch PR Body

Extract issue numbers from the batch branch commit log and generate an issue-by-issue change summary:

```bash
git log --oneline develop..HEAD
```

**PR body format:**

```markdown
## Summary
{Overall batch description}

## Changes by Issue

### #{N1}: {title}
- {change summary from commits}

### #{N2}: {title}
- {change summary from commits}

## Related Issues
Closes #{N1}
Closes #{N2}
Closes #{N3}

## Test Plan
- [ ] {verification steps}
```

## Arguments

If invoked with an issue number (e.g., `/creating-pr-on-issue 39`):
- Include `Closes #39` in the PR body
- Derive PR title from the issue context

## Language

PR titles and bodies must be in English. Conventional commit prefixes (`feat:`, `fix:`, etc.) are always in English.

Review reports output by `reviewing-on-issue` during self-review must also follow the `output-language` rule.

## Edge Cases

| Situation | Action |
|-----------|--------|
| On develop or main | Return error: must be on a feature branch |
| Uncommitted changes | Return error: commit first |
| No commits ahead of base | Return error: nothing to create PR for |
| PR already exists for branch | Include existing PR URL in result |
| Push fails | Return error, suggest `git pull --rebase` |
| Sub-issue with no integration branch found | Use `develop` as base, include warning in result |
| Integration branch PR | Include `Closes #N` in body (GitHub sidebar won't show link, but CLI handles it) |
| Multiple branches match fallback search | Select first match, include alternatives in result |
| Base branch was wrong after PR creation | Fix via REST API: `gh api repos/{owner}/{repo}/pulls/{pr-number} --method PATCH -f base="correct-branch"` |

## Next Steps (Standalone Invocation Only)

When invoked from the `working-on-issue` chain, the chain continues automatically; this section does not apply. Only when invoked standalone:

```text
PR created. Next steps:
→ Run `/reviewing-on-issue` for self-review if needed
→ `/ending-session` to save handover and update issue statuses
```

## Notes

- Always push before creating PR
- Never create PRs from `develop` or `main`
- Daily work PRs target `develop`; only hotfixes target `main`
- Direct PRs to `main` are prohibited (exception: hotfixes only)
- Include issue references for automatic linking
- PR body should be informative but concise
