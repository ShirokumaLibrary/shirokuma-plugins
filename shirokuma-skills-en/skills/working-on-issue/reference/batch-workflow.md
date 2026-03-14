# Batch Mode Reference

When multiple issue numbers are provided (e.g., `#101 #102 #103`), activate batch mode.

## Batch Detection

Detect multiple `#N` patterns in the arguments. If 2+ issues detected → batch mode.

## Batch Eligibility Check

Before starting, verify all issues meet `batch-workflow` rule criteria:
- All issues are Size XS or S
- Issues share a common `area:*` label or affect related files
- Total issues ≤ 5

If any issue fails eligibility, inform user and suggest individual processing.

## Batch Task Registration Template

Register all chain steps via TaskCreate:

```text
[1] Implement #N1 / Implementing #N1
[2] Implement #N2 / Implementing #N2
...
[K] Commit and push all changes / Committing and pushing (addBlockedBy: K-1)
[K+1] Create pull request / Creating pull request (addBlockedBy: K)
[K+2] Update Status to Review for all Issues / Updating Status (addBlockedBy: K+1)
```

## Batch Workflow

1. **Bulk status update**: All issues → In Progress simultaneously
   ```bash
   shirokuma-docs issues update {n} --field-status "In Progress"
   # (repeat for each issue)
   ```

2. **Branch creation** (first time only):
   ```bash
   git checkout develop && git pull origin develop
   git checkout -b {type}/{issue-numbers}-batch-{slug}
   ```
   Type determination: single type → use it; mixed → `chore`.

3. **Issue loop**: For each issue:
   - Fetch issue details: `shirokuma-docs show {number}`
   - Execute implementation (delegate to `code-issue` subagent)
   - Quality checkpoint: verify changed files + run related tests
   - Track `filesByIssue` mapping for scoped commits
   - **Do NOT chain** Commit → PR during the loop

4. **Post-loop chain**: After all issues are implemented:
   - Chain to `commit-issue` (subagent) with batch context
   - `commit-issue` handles per-issue scoped commits
   - Then chain to `open-pr-issue` (subagent) for a single batch PR
   - Update all Issue statuses to Review

## Batch Context

Maintain across the issue loop:

```typescript
{
  currentIssue: number,
  remainingIssues: number[],
  completedIssues: number[],
  filesByIssue: Map<number, string[]>
}
```

Track files changed per issue using `git diff --name-only` before/after each implementation.

## Parallel Batch Mode (Experimental)

> Activated with the `--parallel` flag. Uses `isolation: worktree` for worktree-isolated parallel processing.

### Prerequisites

- All issues are Size XS or S
- No overlapping changed files between issues (completely independent file sets)
- Concurrency: default 3, max 5

### Parallel Batch Task Registration Template

```text
[1] Update all Issue statuses to In Progress / Updating statuses
[2] Implement #N1, #N2, #N3 in parallel / Implementing in parallel
[3] Update Status to Review for all Issues / Updating Status
```

### Parallel Batch Workflow

1. **Token cost warning**: Display estimated cost (agent count × cost) before launch, confirm via AskUserQuestion

   ```
   Launching parallel batch mode (experimental).
   - Target issues: #N1, #N2, #N3
   - Agent count: 3
   - Each agent executes implement→commit→PR on an isolated worktree
   - Token consumption scales linearly with agent count

   Proceed?
   ```

2. **Bulk status update**: All issues → In Progress

3. **Parallel agent launch**: Launch `parallel-coding-worker` simultaneously for each issue

   ```text
   Agent(
     description: "parallel-coding-worker #{n}",
     subagent_type: "parallel-coding-worker",
     isolation: "worktree",
     prompt: "Implement, commit, and create PR for #{issue-number}.",
     run_in_background: true
   )
   ```

   - Launch all agents **in a single response** (`run_in_background: true`)
   - Each agent operates in its own worktree, creating a `{type}/{number}-{slug}` branch
   - Each agent self-sufficiently creates a PR (PR-based aggregation)

4. **Wait and aggregate results**: After all agents complete, parse each result's YAML frontmatter

5. **Bulk status update**:
   - Successful issues → update to `Review`
   - Failed issues → revert to `Pending` and report errors to user

6. **Completion report**:

   ```
   ## Parallel Batch Complete

   | Issue | Status | PR |
   |-------|--------|-----|
   | #N1 | SUCCESS | PR #X1 |
   | #N2 | SUCCESS | PR #X2 |
   | #N3 | FAIL | — |

   **Failed issues:**
   - #N3: {error details}
   ```

### Error Handling

| Situation | Action |
|-----------|--------|
| Some agents fail | Update successful issues to `Review`, revert failed issues to `Pending` |
| All agents fail | Keep all issues at `In Progress`, report errors |
| Worktree creation failure | Skip the affected issue, continue with the rest |
| Dependency setup failure | Report as FAIL within the agent |

### Sequential vs Parallel Comparison

| Aspect | Sequential Batch | Parallel Batch |
|--------|-----------------|----------------|
| Branch | 1 branch (batch branch) | Independent branch per issue |
| PR | 1 PR | Independent PR per issue |
| File conflicts | Tolerated (sequential) | Not allowed (worktree isolation) |
| Processing speed | Sequential | Parallel (up to 5 concurrent) |
| Token cost | 1 agent | Proportional to agent count |
| Stability | Stable | Experimental |
