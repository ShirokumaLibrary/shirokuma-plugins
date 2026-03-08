---
name: creating-pr-on-issue
description: Creates a GitHub pull request from the current branch targeting develop (or integration branch for sub-issues). Triggers: "create pull request", "create PR", "open PR", "submit PR".
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
shirokuma-docs git check
```

Single command returns branch, baseBranch, isFeatureBranch, uncommittedChanges, unpushedCommits, recentCommits, diffStat, and warnings as JSON.

**Pre-checks (use JSON values):**
- `isFeatureBranch` is `true` (not `develop` or `main`)
- `hasUncommittedChanges` is `false` (all changes committed)
- `recentCommits` has commits ahead of `baseBranch`

If `isFeatureBranch` is `false`, return an error.

### Step 2: Push Branch

Ensure the branch is pushed and up to date:

```bash
git push -u origin {branch-name}
```

### Step 2b: Base Branch Detection

Default is `develop`. When invoked with an issue number, automatically detect sub-issues and use the integration branch as base.

#### Sub-Issue Auto-Detection

If the `shirokuma-docs show {number}` output contains a `parentIssue` field, the issue is a sub-issue:

```yaml
parentIssue:
  number: 958
  title: "Migrate to Octokit"
```

If context was passed from `working-on-issue`, use it; otherwise, self-detect using the above (fallback structure).

#### Integration Branch Extraction

When a sub-issue is detected, determine the integration branch in this order:

1. **Extract from parent issue body**: Fetch the parent issue with `shirokuma-docs show {parent-number}` and look for a `### Integration Branch` (EN) / `### Integration ブランチ` (JA) heading. Extract the branch name from the backtick block immediately following the heading (any prefix accepted: `epic/`, `chore/`, `feat/`, etc.)
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

**Note**: For PRs targeting the integration branch, the GitHub sidebar will not display the issue link. `Closes #N` should still be included in the PR body (the CLI's `pr merge` parses it independently and works correctly).

### Step 3: Analyze Changes

Use `recentCommits` and `diffStat` from the Step 1 `shirokuma-docs git check` JSON output. Understand the full scope of changes, not just the latest commit.

### Step 4: Create PR

Write the PR body to a file, then create the PR. When changes meet the Mermaid conditions in the `github-writing-style` rule, include diagrams in the PR body.

```markdown
<!-- /tmp/shirokuma-docs/{number}-pr.md -->
## Summary
- {bullet point 1}
- {bullet point 2}

## Related Issues
Closes #{issue-number}

## Test plan
- [ ] {test item 1}
- [ ] {test item 2}
```

```bash
shirokuma-docs pr create --from-file /tmp/shirokuma-docs/{number}-pr.md
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
- Related Issues: Always use `Closes #N` (not `Refs #N` — the CLI's `parseLinkedIssues()` only matches `Closes/Fixes/Resolves` patterns)
- Test plan: checklist of verification steps

### Step 4b: PR Link Comment (non-default base branch only)

When the base branch is not the repository's default branch (e.g., integration branch-based PR), GitHub's sidebar PR link is not displayed. Automatically post a PR link comment to the related issues.

**Condition**: `base_branch !== default_branch`

```bash
shirokuma-docs issues comment {issue-number} --body-file - <<'EOF'
🔗 PR #{pr-number} is linked to this issue.
EOF
```

In batch mode, post to each issue referenced by `Closes`.

Skip this step for default branch-based PRs (GitHub's native PR link works correctly).

### Step 5: Fork Signal

PR creation itself is a GitHub write (the deliverable), so no additional GitHub write is needed. Return the following structured data to the caller:

```yaml
---
action: CONTINUE
next: reviewing-on-issue
status: SUCCESS
ref: "PR #{pr-number}"
---

{branch} → {base-branch}, {count} commits, Closes #{issue-number}

### PR Body
## Summary
- {bullet point 1}
...
```

On failure:

```yaml
---
action: STOP
status: FAIL
---

{error description}
```

When existing PR detected:

```yaml
---
action: CONTINUE
next: reviewing-on-issue
status: SUCCESS
ref: "PR #{existing-pr-number}"
---

Existing PR detected, creation skipped
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
| Integration branch PR | Always include `Closes #N` in body (not `Refs` — CLI's `parseLinkedIssues()` only matches `Closes/Fixes/Resolves`. GitHub sidebar won't show link, but CLI handles it) |
| Multiple branches match fallback search | Select first match, include alternatives in result |
| Base branch was wrong after PR creation | Fix via REST API: `gh api repos/{owner}/{repo}/pulls/{pr-number} --method PATCH -f base="correct-branch"` |

## Next Steps (Standalone Invocation Only)

**When invoked as fork from `working-on-issue` chain**: Omit this section — next step suggestions disrupt the chain's autonomous progression by introducing unnecessary pauses. Return only the completion report (Step 5).

Only when invoked standalone:

```text
PR created. Next steps:
→ Run `/reviewing-on-issue` for self-review if needed
→ `/ending-session` to save handover and update issue statuses
```

## Notes

- Always push before creating PR
- Create PRs from feature branches, not `develop` or `main` — PRs from protected branches have no meaningful diff
- Daily work PRs target `develop`; only hotfixes target `main`
- Reserve `main` as PR target for hotfixes only — routing daily work to `main` bypasses the integration branch
- Always use `Closes #N` for issue references (not `Refs #N` — the CLI's `parseLinkedIssues()` cannot parse `Refs`, so Issues won't close on merge)
- PR body should be informative but concise
