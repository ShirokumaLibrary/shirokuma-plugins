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
| Was a PR already created? | `gh pr list --head {branch}` (direct `gh` — `shirokuma-docs pr list` does not support branch filter) |
| Are commits pushed to remote? | `git log --oneline origin/{branch}..HEAD` |

**Idempotent**: Conditional — if the PR already exists, `open-pr-issue` will detect and skip creation. If not, it will create one.

**Recovery action**: Re-invoke `open-pr-issue` via Agent tool (`pr-worker`).

### review-worker Failed

| Check | Command |
|-------|---------|
| Was a review report posted? | Check Issue comments via `shirokuma-docs issue comments {number}` |

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

When a revert is required after a PR has been merged (issue is Done), the canonical path is the CLI-integrated `issue rollback` command (#2024 Phase 1-D):

```bash
shirokuma-docs issue rollback {plan-issue#} --action revert
```

This command batch-executes:

1. Create a revert branch (`revert/pr-{N}` branched from develop / parent base)
2. Run `git revert -m 1 --no-commit` to undo the merge commit
3. Create a revert PR (title: `Revert: PR #N`, body with `Closes #{plan-issue#}`)
4. Reset the plan Issue status back to `Backlog` (slated for re-implementation)

After the revert PR is merged, run `/implement-flow #{plan-issue#}` in a new conversation to re-implement (a new feature branch will be created).

For "cancelled" decisions, after merging the revert PR, run `shirokuma-docs issue cancel {plan-issue#}` to mark it as Done(NOT_PLANNED).

> The legacy procedure (manual revert + manual status change) was unified into `issue rollback --action revert` in #2024 Phase 1-D. Manual operation is still possible, but the CLI command is the canonical path.

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
