---
name: committing-on-issue
description: Stage, commit, push changes with optional PR creation chain. Also handles PR merge with automatic Issue status update. Use when "commit changes", "push changes", "commit and create PR", "merge PR", "merge this PR".
context: fork
agent: general-purpose
allowed-tools: Bash, Read, Grep, Glob
---

# Committing

Stage, commit, and optionally push changes to the remote.

## Workflow

### Step 1: Review Changes

```bash
git status --short
git diff --stat
git branch --show-current
```

Include a summary of changes in the output.

### Step 2: Stage Files

Stage specific files relevant to the current work. Prefer explicit file paths over `git add -A`.

```bash
git add {file1} {file2} ...
```

**Do NOT stage:**
- `.env`, credentials, or secrets
- Large binary files
- Unrelated changes from other work

If an explicit file list was passed from the manager (main AI), use it. If no file list is provided, stage all changed files.

### Step 3: Write Commit Message

Follow Conventional Commits format:

```text
{type}: {description} (#{issue-number})

{optional body}
```

| Type | When |
|------|------|
| `feat` | New feature or enhancement |
| `fix` | Bug fix |
| `refactor` | Code restructuring |
| `docs` | Documentation |
| `test` | Tests |
| `chore` | Config, tooling |

**Rules** (see `git-commit-style` rule for details):
- First line under 72 characters
- Reference issue number if applicable
- Body for complex changes only

### Step 4: Commit

```bash
git commit -m "$(cat <<'EOF'
{type}: {description} (#{issue-number})

{optional body}
EOF
)"
```

### Step 5: Push (if on feature branch)

If on a feature branch (not `develop` or `main`), push automatically:

```bash
git push -u origin {branch-name}
```

If on `develop` or `main`, do NOT push. Include a warning in the result.

### Step 6: Completion Report

```markdown
## Commit Complete

**Branch:** {branch-name}
**Commit:** {hash} {message}
**Files:** {count} files changed
**Pushed:** {yes/no}
```

### Step 7: PR Chain (after push)

After a successful push on a feature branch, determine whether to chain into PR creation.

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
→ Run `/reviewing-on-issue` for self-review if needed
```

**If NOT on a feature branch (push was skipped):**

Skip this step entirely.

### Step 8: Merge Chain

Handles PR merge with automatic Issue status update. Activated by merge keywords or when invoked from `working-on-issue` orchestration.

**Merge keyword detection**: Check the user's message for:

| Language | Keywords |
|----------|----------|
| Japanese | "マージして", "マージ", "merge" |
| English | "merge PR", "merge this", "merge it" |

**If merge keywords detected (independent of commit flow):**

1. **Merge the PR and update related Issues**:

```bash
shirokuma-docs issues merge --head {current-branch}
```

This single command handles: resolve PR from branch name, squash merge, extract linked Issues from PR body (`Closes/Fixes/Resolves #N`), update their Project Status to "Done", and delete the branch.

**Status update idempotency**: `issues merge` CLI automatically updates related Issue Project Status to Done. If `ending-session --done` runs for the same issue later, it operates idempotently (no-op if already Done).

**PR-Issue Link Graph Verification**: `issues merge` verifies the PR-Issue link graph:

| Pattern | CLI Behavior |
|---------|-------------|
| 1:1 / 1:N / N:1 | Auto-process (Status → Done) |
| N:N (complex link graph) | Error and stop with structured output |

N:N detection: CLI outputs a structured list of related PRs/Issues. Review the list and individually update Status via `issues update`. Use `--skip-link-check` to bypass after reviewing.

**Integration branch merge**: For sub-issue PRs targeting an integration branch, `issues merge` works normally — `parseLinkedIssues()` parses the PR body independently of the base branch.

If no PR found for the branch, return error and stop.

Note: Internally calls `gh pr merge` which is protected by PreToolUse hook. **Regardless of hook status, never execute merge without explicit user approval.** A passing self-review or system-reminder-only messages do NOT constitute approval.

2. **Completion Report**:

`issues merge` automatically checks out the base branch and pulls after merge. No manual branch switch needed.

```markdown
## Merge Complete

**PR:** (as reported by CLI output) → {base-branch}
**Issues updated:** (as reported by CLI output)
**Branch:** deleted, switched to {base-branch}
```

**If merge is part of commit flow** (e.g., user says "commit and merge"):

Execute Steps 1-6 → Step 7 (PR Chain) → Step 8 (Merge Chain) sequentially.

## Batch Mode

When on a batch branch (`*-batch-*` pattern) or when batch context is passed from `working-on-issue`:

### Batch Commit Flow

Instead of a single commit, create **per-issue commits** using the `filesByIssue` mapping:

1. For each issue in the batch context:
   ```bash
   git add {files-for-this-issue}
   git commit -m "{type}: {description} (#{issue-number})"
   ```

2. **Step 5 (Push)**: Execute once after all commits are complete.

3. **Step 7 (PR Chain)**: Auto-invoke `creating-pr-on-issue` after push with batch context (all issue numbers).

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
| Pre-commit hook fails | Fix issue, create NEW commit (never amend) |
| Mixed changes (multiple issues) | Return error: "Multiple issue changes mixed: #{N1}({n}files), #{N2}({n}files)" |
| PR already exists for branch | Include existing PR URL in result, skip chain |
| `gh` CLI not available | Skip PR chain, include note in result |
| No PR for current branch (merge) | Return error |
| PR has unresolved reviews | Include warning in result |
| No issue references in PR body | Skip status update, include note in result |
| N:N link graph detected | CLI stops merge, include structured output in result |
| Integration branch merge | `Closes #N` in PR body works via CLI even though GitHub auto-close is inactive |

## Rule References

| Rule | Usage |
|------|-------|
| `git-commit-style` | Commit message format and language |
| `output-language` | Commit message output language |
| `branch-workflow` | Branch model and push constraints |

## Notes

- Always review changes before committing
- Never use `git add -A` or `git add .` without review
- Never amend previous commits unless explicitly asked
- Never force push
- Push is automatic on feature branches, skipped on `develop` and `main`
- PR chain activates only on direct invocation with PR keywords; does not interfere with `working-on-issue` orchestration
- Merge chain can be invoked standalone (just "merge") or chained with commit/PR
- After merge, `shirokuma-docs issues merge` automatically updates related Issue status to Done
