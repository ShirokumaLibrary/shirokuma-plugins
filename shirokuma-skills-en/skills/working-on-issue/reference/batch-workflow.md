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

## Batch TodoWrite Template

```text
[1] Implement #N1 / Implementing #N1
[2] Implement #N2 / Implementing #N2
...
[K] Commit and push all changes / Committing and pushing
[K+1] Create pull request / Creating pull request
[K+2] Run self-review / Running self-review
[K+3] Update Status to Review for all Issues / Updating Status
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
   - Execute implementation (delegate to `coding-on-issue` fork)
   - Quality checkpoint: verify changed files + run related tests
   - Track `filesByIssue` mapping for scoped commits
   - **Do NOT chain** Commit → PR during the loop

4. **Post-loop chain**: After all issues are implemented:
   - Chain to `committing-on-issue` (fork) with batch context
   - `committing-on-issue` handles per-issue scoped commits
   - Then chain to `creating-pr-on-issue` (fork) for a single batch PR
   - Self-review loop (once for entire batch PR)
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
