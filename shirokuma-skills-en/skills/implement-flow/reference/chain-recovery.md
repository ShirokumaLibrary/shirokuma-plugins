# Chain Recovery Reference

Guide for recovering from interrupted chains in `implement-flow`.

See also: [chain-execution.md](chain-execution.md)

## State Detection Checklist by Interruption Point

Before recovery, identify where the chain stopped. Check the following in order:

### coding-worker Failed

| Check | Command |
|-------|---------|
| Are there uncommitted changes? | `git status` |
| Is there any partial implementation? | Check modified files with `git diff` |
| Are there test failures? | `pnpm test` or relevant test command |

**Idempotent**: Yes — re-invoking `code-issue` (Agent: `coding-worker`) is safe. Existing changes will be overwritten or continued as needed.

**Recovery action**: Re-invoke `code-issue` via Agent tool (`coding-worker`). Pass the same plan context.

### commit-worker Failed

| Check | Command |
|-------|---------|
| Are there staged but uncommitted changes? | `git status` |
| Was a partial commit created? | `git log --oneline -3` |
| Is the branch pushed? | `git log --oneline origin/{branch}..HEAD` |

**Idempotent**: Yes — re-invoking `commit-issue` (Agent: `commit-worker`) is safe. Duplicate commits are prevented by checking git status.

**Recovery action**: Re-invoke `commit-issue` via Agent tool (`commit-worker`).

### pr-worker Failed

| Check | Command |
|-------|---------|
| Was a PR already created? | `gh pr list --head {branch}` (direct `gh` — `shirokuma-docs items pr list` does not support branch filter) |
| Are commits pushed to remote? | `git log --oneline origin/{branch}..HEAD` |

**Idempotent**: Conditional — if the PR already exists, `open-pr-issue` will detect and skip creation. If not, it will create one.

**Recovery action**: Re-invoke `open-pr-issue` via Agent tool (`pr-worker`).

### review-worker Failed

| Check | Command |
|-------|---------|
| Was a review report posted? | Check Issue comments via `shirokuma-docs items comments {number}` |

**Idempotent**: Yes — re-invoking `review-issue` (Agent: `review-worker`) is safe. A new report will be generated.

**Recovery action**: Re-invoke `review-issue` via Agent tool (`review-worker`).

## Resumable State: `pending` Steps in TaskList

TaskList `pending` steps define the resumable state. When the chain is interrupted:

1. Run `TaskList` to see which steps are `pending`
2. The first `pending` step is the recovery entry point
3. Re-invoke the corresponding worker from that step

```text
Example: If "commit" is pending and "implement" is completed
→ Re-invoke commit-issue (Agent: commit-worker)
→ Do NOT re-run code-issue
```

## General Recovery Flow

```
1. Run TaskList → identify pending steps
2. Verify current state (git status, gh pr list, etc.)
3. Re-invoke the failed worker
4. Continue chain from that point
```

## Notes

- Never skip steps — each worker produces output consumed by the next
- If recovery fails repeatedly, stop and report to user with current state
- For `/simplify` failures, re-invoke via Skill tool (not Agent)
- For `reviewing-security` failures, re-invoke via Skill tool (not Agent)

## Recovery after PR Revert

When a revert is required after a PR has been merged (issue is Done):

1. Create and merge a revert PR (via GitHub UI or `git revert`)
2. Manually update the original issue status to `Backlog` (re-implement) or `Cancelled` (cancelled)
3. If re-implementing, run `/implement-flow #{number}` in a new conversation (a new branch will be created)

> Revert is a manual operation and is not part of the `implement-flow` chain.

## Idempotency Guarantees

If the `implement-flow` chain stops mid-way (network error, session disconnect, etc.), run the same `/implement-flow #{number}` again in a new conversation. The following idempotency guarantees allow safe resumption (supplement to "General Recovery Flow" above):

| State | Behavior |
|-------|----------|
| Branch already exists | Switch to existing branch via `git checkout {branch}` (no re-creation) |
| Status already In Progress | Skip status change |
| Already committed and pushed | `commit-worker` detects no diff and skips |
| PR already exists | `pr-worker` detects existing PR and skips |
| `/simplify` already done | Safe to re-run (idempotent) |
| Security review already done | Safe to re-run (idempotent) |
| Work summary already posted | Duplicate comment is posted (manually delete) |

> Only the work summary lacks idempotency. If duplicated, delete the extra manually.
