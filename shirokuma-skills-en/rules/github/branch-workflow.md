---
scope: default
category: github
priority: required
---

<!-- managed-by: shirokuma-docs@0.1.0 -->

# Branch Workflow

## Branch Model

| Branch | Role | Branches from | Merges to | Persistent | Protected |
|--------|------|---------------|-----------|-----------|-----------|
| `main` | Production releases. Tagged for each version | - | - | Yes | Yes |
| `develop` | Integration. Default branch for PRs | `main` (initial) | `main` (release PR) | Yes | Yes |
| `feat/*`, `fix/*`, `chore/*`, `docs/*` | Daily work | `develop` | `develop` (PR) | No | No |
| `hotfix/*` | Urgent production fix | `main` | `main` (PR), then cherry-pick to `develop` | No | No |
| `epic/*` | Epic integration | `develop` | `develop` (final PR) | No | No |
| `release/X.x` | Old major maintenance (only when needed) | tag | stays on branch (tag) | Conditional | Yes |

**Key principles:**
- `develop` is the **default branch** on GitHub (PR target)
- `main` reflects **production state** only
- Feature branches always branch from `develop`
- Direct commits to `develop` or `main` are not allowed

## Base Branch Detection

For daily work, the base branch is `develop`. Detect dynamically:

```bash
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'
```

If the above fails (e.g., shallow clone), fall back to:

```bash
gh repo view --json defaultBranchRef -q .defaultBranchRef.name
```

## Branch Naming

### Feature Branches

```
{type}/{issue-number}-{slug}
```

| Type | When |
|------|------|
| `feat` | Feature, Enhancement |
| `fix` | Bug fix |
| `chore` | Chore, Refactor, Config, Research |
| `docs` | Documentation |

**Slug rules:** Derive from issue title, lowercase kebab-case, max 40 characters, English only.

**Examples:**
```
feat/39-branch-workflow-rules
fix/34-cross-repo-project-resolution
chore/27-plugin-directory-structure
docs/32-session-naming-convention
```

### Batch Branches

```
{type}/{issue-numbers}-batch-{slug}
```

Used when processing multiple XS/S issues together. See `batch-workflow` rule for details.

**Type determination:** Single type → use it. Mixed types → `chore`.

### Integration Branches (Epic)

```
epic/{parent-issue-number}-{slug}
```

- Branch from `develop`; sub-issue branches branch from the integration branch
- Sub-issue PRs target the integration branch
- After all sub-issues complete, create a final PR from integration branch to `develop`

See `epic-workflow` reference for details.

### Hotfix Branches

```
hotfix/{issue-number}-{slug}
```

Branch from `main`, not `develop`. Used for urgent production fixes only.

### Release Maintenance Branches

```
release/{major}.x
```

Created from a tag when old major version needs a patch. Not used for regular releases.

## Daily Workflow

1. Branch from `develop`
2. Commit changes during session
3. Push branch and create PR to `develop`
4. User reviews and merges PR

### 1. Branch Creation (Session Start)

```bash
git checkout develop
git pull origin develop
git checkout -b {type}/{issue-number}-{slug}
```

### 2. Development (During Session)

- Commit frequently with descriptive messages
- Reference issue number in commits: `feat: add branch workflow rules (#39)`
- Follow existing commit message conventions

### 3. PR Creation (Session End)

```bash
git push -u origin {branch-name}
shirokuma-docs items pr create --from-file /tmp/shirokuma-docs/pr.md
```

- PR title: concise summary (under 70 characters)
- Link issue: include `Closes #{number}` or `Refs #{number}` in body
- Status moves to **Review**

### 4. Review and Merge

- User reviews the PR on GitHub
- **AI MUST NOT merge PRs without explicit user instruction** — Enforced by PreToolUse hook
- Merge via squash merge (recommended) only after user approval
- Branch is deleted after merge, status moves to **Done**

## Rules

1. **Always branch from develop** - Ensure `develop` is up to date before branching (exception: sub-issues branch from the integration branch)
2. **One branch per issue** - Do not mix unrelated changes (exception: batch mode per `batch-workflow` rule, epics per `epic-workflow` reference)
3. **Push before session end** - Unpushed work risks being lost
4. **PR required for merge** - No direct pushes to `develop` or `main`
5. **Never merge without user approval** - Enforced by PreToolUse hook
6. **Delete branch after merge** - Keep repository clean
7. **PR to develop for daily work** - Only hotfixes target `main` directly
8. **Tag every release** - All versions recorded as tags on `main`

## Destructive Command Protection

The shirokuma-skills-en plugin includes a PreToolUse hook that **blocks** destructive commands before execution. This is not advisory — the commands are denied at the tool level.

### Default Blocked Commands

| Rule ID | Blocked Command | Reason |
|---------|-----------------|--------|
| `pr-merge` | `gh pr merge` / `pr merge` | PR merge requires explicit user approval |
| `force-push` | `git push --force` / `git push -f` | Force push overwrites remote history |
| `hard-reset` | `git reset --hard` | Discards all uncommitted changes |
| `discard-worktree` | `git checkout .` / `git restore .` | Discards working tree changes |
| `clean-untracked` | `git clean -f` | Deletes untracked files |
| `force-delete-branch` | `git branch -D` | Force deletes a branch |

### Project Override

Projects can allow specific commands via `shirokuma-docs.config.yaml`:

```yaml
hooks:
  allow:
    - pr-merge
    # - force-push
    # - hard-reset
```

### False-Positive Prevention

The hook strips quoted strings from commands before pattern matching. Text inside `--body "..."` or similar arguments does not trigger blocks.

## Abandonment Workflow

When work on an issue is stopped without completing it (context switch, blocked, deprioritized):

### Steps

```bash
# 1. Close the PR without merging (add reason as a comment)
shirokuma-docs items pr close <pr-number> --body-file - <<'EOF'
Closing due to: <reason>
Work in progress. Can be resumed from branch feat/N-slug.
EOF

# 2. Cancel the issue (set status to Not Planned)
shirokuma-docs items cancel <issue-number> --body-file - <<'EOF'
<cancellation reason>
EOF

# 3. Switch to base branch locally
git checkout develop
```

`--delete-branch` can be added to `pr close` if the branch is no longer needed.

## Edge Cases

| Situation | Action |
|-----------|--------|
| Already on a feature branch | Continue working, skip branch creation |
| Multiple issues in one session | Create separate branches, or group related items |
| Uncommitted changes on develop | Stash or commit before branching |
| Branch already exists for issue | Switch to existing branch |
| Conflict with develop | Rebase before PR: `git rebase develop` |
| Default branch is still `main` | See default branch setup procedure |
| Need to fix production urgently | Use Hotfix Workflow |
| Sub-issue with no integration branch found | Use `develop` as base and warn user |
| Need to abandon work mid-session | Use Abandonment Workflow above |

Default branch setup, hotfix workflow, release workflow, and maintenance branch details are auto-loaded when the `managing-github-items` skill is executed.
