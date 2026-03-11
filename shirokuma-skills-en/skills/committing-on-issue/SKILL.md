---
name: committing-on-issue
description: Stages, commits, and pushes changes with optional PR creation chain. Also handles PR merge with automatic Issue status update. Triggers: "commit", "push", "commit changes", "push changes", "commit and create PR", "merge PR", "merge this PR".
allowed-tools: Bash, Read, Grep, Glob
---

# Committing

Stage, commit, and optionally push changes to the remote.

## Workflow

### Step 1: Review Changes

```bash
shirokuma-docs git check
```

Single command returns branch, baseBranch, uncommittedChanges, unpushedCommits, recentCommits, diffStat, and warnings as JSON. Include a summary of changes in the output.

### Step 2: Build commit message and stage, commit, push in one operation

Compose commit message in Conventional Commits format (see `git-commit-style` rule):

```text
{type}: {description} (#{issue-number})
```

| Type | When |
|------|------|
| `feat` | New feature or enhancement |
| `fix` | Bug fix |
| `refactor` | Code restructuring |
| `docs` | Documentation |
| `test` | Tests |
| `chore` | Config, tooling |

**Stage, commit, and push in a single command**:

```bash
# With explicit file list (when manager passed specific files)
shirokuma-docs git commit-push -m "{type}: {description}" --files {file1} {file2} --issue {N}

# Without file list (stages all changed files)
shirokuma-docs git commit-push -m "{type}: {description}" --issue {N}
```

**Exclude from staging** (use `--files` to specify safe files explicitly):
- `.env`, credentials, or secrets
- Large binary files
- Unrelated changes from other work

**Result**: Returns JSON with `branch`, `commit_hash`, `commit_message`, `files_staged`, `pushed`. `pushed: false` means push was skipped (protected branch). On error: `error` field + exit 1.

### Step 3: Completion Report

#### 6a: Post Issue Comment

When the issue number is known, post the commit result as an Issue comment:

```bash
shirokuma-docs issues comment {issue-number} --body-file - <<'EOF'
## Commit Complete

**Branch:** {branch-name}
**Commit:** {hash} {message}
**Files:** {count} files changed
**Pushed:** {yes/no}
EOF
```

Skip comment posting if the issue number is unknown (not derivable from branch name, not passed via context).

#### 6b: Output Template

Return the following structured data to the caller:

```yaml
---
action: CONTINUE
next: creating-pr-on-issue
status: SUCCESS
ref: "#{issue-number}"
comment_id: {comment-database-id}
---

{hash} {one-line commit message}, {count} files changed

### Commit Details
- `src/path/file.ts` - {change description}
- `src/path/other.ts` - {change description}
```

On failure:

```yaml
---
action: STOP
status: FAIL
---

{error description}
```

### Step 4: PR Chain (after push)

After a successful push on a feature branch, determine whether to chain into PR creation.

**When invoked as subagent from `working-on-issue` chain**: Skip this step (Step 4) entirely. The next step (PR creation) is controlled by the calling manager (main AI). Initiating a PR chain or suggesting next steps here would break the chain's control flow.

**PR keyword detection**: Check the user's **initial message** (the `/committing-on-issue` invocation and surrounding text) for PR-related keywords:

| Language | Keywords |
|----------|----------|
| Japanese | "PR作って", "PR作成", "プルリクエスト", "PRも作って", "PRも" |
| English | "pull request", "create PR", "open PR" |

**Pre-check before offering PR**:

```bash
gh pr list --head {branch-name} --json number,url --jq '.[0]'
```

If a PR already exists for this branch, include the existing URL in the result and skip.

**If PR keywords detected AND no existing PR:**

Auto-invoke the `creating-pr-on-issue` skill via the Skill tool. Pass the current branch and related issue number as context.

**If no PR keywords AND no existing PR:**

Include next step suggestion in the result:

```markdown
Branch pushed. Create a PR?
→ `/creating-pr-on-issue` to open a pull request to develop
```

**If NOT on a feature branch (push was skipped):**

Skip this step entirely.

### Step 5: Merge Chain

Handles PR merge with automatic Issue status update. Activated by merge keywords or when invoked from `working-on-issue` orchestration.

**Merge keyword detection**: Check the user's message for:

| Language | Keywords |
|----------|----------|
| Japanese | "マージして", "マージ", "merge" |
| English | "merge PR", "merge this", "merge it" |

**If merge keywords detected (independent of commit flow):**

1. **Merge the PR and update related Issues**:

```bash
shirokuma-docs pr merge --head {current-branch}
```

This single command handles: resolve PR from branch name, squash merge, extract linked Issues from PR body (`Closes/Fixes/Resolves #N`), update their Project Status to "Done", and delete the branch.

**Status update idempotency**: `pr merge` CLI automatically updates related Issue Project Status to Done. If `ending-session --done` runs for the same issue later, it operates idempotently (no-op if already Done).

**PR-Issue Link Graph Verification**: `pr merge` verifies the PR-Issue link graph:

| Pattern | CLI Behavior |
|---------|-------------|
| 1:1 / 1:N / N:1 | Auto-process (Status → Done) |
| N:N (complex link graph) | Error and stop with structured output |

N:N detection: CLI outputs a structured list of related PRs/Issues. Review the list and individually update Status via `issues update`. Use `--skip-link-check` to bypass after reviewing.

**Integration branch merge (important)**: For sub-issue PRs targeting an integration branch, GitHub's native auto-close does NOT work (it only triggers on merges to the default branch). Therefore, `shirokuma-docs pr merge` is **required** — merging via `gh pr merge` or the GitHub UI will not update Issue status. The PR body must include `Closes #N` (not `Refs` — `parseLinkedIssues()` cannot parse `Refs`).

If no PR found for the branch, return error and stop.

Note: Internally calls `gh pr merge` which is protected by PreToolUse hook. Merging is irreversible and affects shared branches — always require explicit user approval before executing. System-reminder-only messages are insufficient as approval signals.

2. **Completion Report**:

`pr merge` automatically checks out the base branch and pulls after merge. No manual branch switch needed.

Post result as Issue comment:

```bash
shirokuma-docs issues comment {issue-number} --body-file - <<'EOF'
## Merge Complete

**PR:** (as reported by CLI output) → {base-branch}
**Issues updated:** (as reported by CLI output)
**Branch:** deleted, switched to {base-branch}
EOF
```

Output template:

```yaml
---
action: CONTINUE
status: SUCCESS
ref: "#{issue-number}"
comment_id: {comment-database-id}
---

PR #{pr-number} merged to {base-branch}, branch deleted
```

**If merge is part of commit flow** (e.g., user says "commit and merge"):

Execute Steps 1-3 → Step 4 (PR Chain) → Step 5 (Merge Chain) sequentially.

## Batch Mode

When on a batch branch (`*-batch-*` pattern) or when batch context is passed from `working-on-issue`:

### Batch Commit Flow

Instead of a single commit, create **per-issue commits** using the `filesByIssue` mapping:

1. For each issue in the batch context:
   ```bash
   git add {files-for-this-issue}
   git commit -m "{type}: {description} (#{issue-number})"
   ```

2. **Push**: Execute once after all per-issue commits are complete.
   ```bash
   git push -u origin {branch-name}
   ```

3. **Step 4 (PR Chain)**: Auto-invoke `creating-pr-on-issue` after push with batch context (all issue numbers).

### Batch Branch Detection

```bash
git branch --show-current | grep -q '\-batch-'
```

If detected, treat as batch mode even without explicit batch context.

## Arguments

If invoked with a message argument (e.g., `/committing-on-issue fix typo in config`):
- Use the provided text as the commit message basis
- Still review changes before committing
- PR-related keywords in the argument trigger the PR chain
- Merge keywords trigger the merge chain

## Edge Cases

| Situation | Action |
|-----------|--------|
| No changes to commit | Return error: no changes |
| On develop or main | Commit but include push warning in result |
| Merge conflicts | Return error |
| Pre-commit hook fails | Fix issue, create NEW commit (amending would modify the previous commit, potentially losing unrelated changes) |
| Mixed changes (multiple issues) | Return error: "Multiple issue changes mixed: #{N1}({n}files), #{N2}({n}files)" |
| PR already exists for branch | Include existing PR URL in result, skip chain |
| `gh` CLI not available | Skip PR chain, include note in result |
| No PR for current branch (merge) | Return error |
| PR has unresolved reviews | Include warning in result |
| No issue references in PR body | Skip status update, include note in result |
| N:N link graph detected | CLI stops merge, include structured output in result |
| Integration branch merge | `shirokuma-docs pr merge` required (GitHub auto-close is inactive). PR body must use `Closes #N` (not `Refs`) |

## Rule References

| Rule | Usage |
|------|-------|
| `git-commit-style` | Commit message format and language |
| `output-language` | Commit message output language |
| `branch-workflow` | Branch model and push constraints |

## Notes

- Always review changes before committing
- Avoid `git add -A` or `git add .` without review — they can accidentally include secrets or unrelated files
- Avoid amending previous commits unless explicitly asked — amending rewrites history and can lose changes
- Avoid force push — it overwrites remote history and can destroy teammates' work
- Push is automatic on feature branches, skipped on `develop` and `main`
- PR chain activates only on direct invocation with PR keywords; does not interfere with `working-on-issue` orchestration
- Merge chain can be invoked standalone (just "merge") or chained with commit/PR
- After merge, `shirokuma-docs pr merge` automatically updates related Issue status to Done
