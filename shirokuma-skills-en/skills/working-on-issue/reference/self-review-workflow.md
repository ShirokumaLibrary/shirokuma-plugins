# Self-Review Workflow Reference

Detailed specification of the self-review loop executed within the `working-on-issue` Step 5 chain.

## Contents

- State Transitions
- File Category Detection
- /simplify Initial Pass
- PASS/FAIL Criteria
- Convergence Check Logic
- Fix Agent (Task)
- Out-of-Scope Follow-up Issue Creation
- Review Findings Comment Verification
- Expected PR Comment Pattern
- Fix Summary Comment
- Issue Body Update
- Self-Review Completion Report
- Progress Reporting Template

## State Transitions

```text
[Chain] committing → creating-pr → Self-review start
    ↓
[SIMPLIFY] /simplify initial pass (only when code-category files exist)
    ↓  Changes found → commit & push / No changes or failure → skip
[REVIEW] Launch review (Subagent: reviewing-on-issue / reviewing-claude-config)
    ↓  Note: subagent posts PR comment (Step 6) before returning structured output
[PARSE] Parse YAML frontmatter + PASS/FAIL determination
    ↓
[PRESENT] Present self-review result summary to user (using completion report template)
    ↓
  ├── PASS → [COMPLETE]
  ├── NEEDS_FIX (Auto-fixable: yes) → [FIX]
  └── FAIL (Auto-fixable: no) → chain stop, [REPORT]

[FIX] Delegate fix (Task: general-purpose) → Receive fix summary
    ↓
[CONVERGE] Convergence check
    ↓
  ├── Progress → [REVIEW] (re-review)
  ├── Not converging → [REPORT]
  └── Safety limit (5) → [REPORT]

[REPORT] Report to user
    ↓
[COMPLETE] Create out-of-scope Issues → Verify review findings comment → Post response complete comment (required)
    ↓
[POST-REVIEW] Post Work Summary → Status → Review update → Evolution signal recording
```

> **POST-REVIEW steps**: Even after reaching COMPLETE, TodoWrite still has pending steps (Work Summary, Status Update). The manager MUST immediately proceed to the next step as long as pending steps remain.

## File Category Detection

Get changed files via `git diff --name-only develop..HEAD` and classify:

| Category | Condition |
|----------|-----------|
| config | Files under `.claude/skills/`, `.claude/rules/`, `.claude/agents/`, `.claude/output-styles/`, `.claude/commands/`, `plugin/` |
| code | `.ts`, `.tsx`, `.js`, `.jsx` files |
| docs | `.md` files (excluding config paths above) |

### Review Routing

| File Composition | Review Method |
|-----------------|---------------|
| config only | Invoke `reviewing-claude-config` only |
| code/docs only (no config) | Invoke `reviewing-on-issue` only |
| mixed (config + code/docs) | Invoke `reviewing-on-issue` → `reviewing-claude-config` sequentially → merge results |

#### Fallback When `reviewing-claude-config` Is Unavailable

When `reviewing-claude-config` is not in the skill list, apply these fallbacks:

| File Composition | Fallback |
|-----------------|----------|
| config only | Use `reviewing-on-issue` docs role as substitute. If docs role is also unavailable, fall back to a self-check checklist (manually verify config file structure, consistency, and best-practice compliance) |
| mixed (config + code/docs) | Continue with `reviewing-on-issue` only (config portion review is omitted) |

### Result Merging Rules (Mixed Case)

- Status: either FAIL → FAIL; either NEEDS_FIX (and no FAIL) → NEEDS_FIX; both PASS → PASS
- Critical: sum of both
- Fixable-warning: sum of both
- Out-of-scope: sum of both
- Files with issues: merge
- Auto-fixable: either no → no
- Out-of-scope items: merge

## /simplify Initial Pass

Run `/simplify` once as a pre-pass before the self-review loop. It performs 3-parallel review (reuse, quality, efficiency) with auto-fixes on changed code, raising the quality baseline.

### Execution Condition

Only run when `code` category files are present in the file category detection results. Skip if only `config` or `docs` files.

### Invocation

The manager (main AI) invokes via the `Skill` tool:

```text
skill: "simplify"
```

### Output Handling

Fire-and-forget (no PASS/FAIL determination). The quality gate is handled by the subsequent `[REVIEW]` state.

### Commit Processing

After `/simplify` completes, the manager (main AI) performs:

1. Check for changes via `git diff`
2. Changes found → `git add -A` + commit + push
   - Commit message: `refactor: apply /simplify quality improvements (#{issue-number})`
3. No changes → skip

### On Failure

Optional step — on error or timeout, skip and proceed to `[REVIEW]`.

### Batch Mode

Run once for the entire batch PR (same as the review loop).

> **⚠ Required**: SIMPLIFY is a quality-baseline **pre-pass**, not a substitute for self-review. After SIMPLIFY completes (changes, no changes, or failure), always proceed to the `[REVIEW]` state and invoke `reviewing-on-issue` / `reviewing-claude-config` via the Skill tool. Skipping `[REVIEW]` after SIMPLIFY is prohibited.

## PASS/NEEDS_FIX/FAIL Criteria

- **PASS**: critical = 0 and fixable-warning = 0 (out-of-scope only is still PASS)
- **NEEDS_FIX**: (critical > 0 or fixable-warning > 0) and Auto-fixable = yes
- **FAIL**: (critical > 0 or fixable-warning > 0) and Auto-fixable = no (chain stop)

## Convergence Check Logic

Compare the total count of `critical + fixable-warning` against the previous iteration.

| State | Logic | Action |
|-------|-------|--------|
| Total decreased from previous | Progress | Continue |
| Total same as previous | Grace period | Continue once (fix may have introduced different issues) |
| Total not decreased for 2 consecutive iterations | Not converging | Report to user |
| Total increased from previous | Worsening | Report to user immediately |
| Total = 0 | Complete | PASS |
| Safety limit (5) reached | Failsafe | Report to user |

**Safety limit rationale (5 iterations)**: Up to 2 for critical fixes + up to 2 for fixable-warning fixes + 1 buffer.

**Safety limit fallback**: Convert remaining fixable-warnings to follow-up Issues and treat as PASS after user confirmation.

## Fix Agent (Task)

When fixes are needed, delegate to `Task(general-purpose)`.

### Prompt Template

```text
Fix the issues identified in the following self-review results.

## Review Results
{Full subagent output from reviewing-on-issue / reviewing-claude-config}

## Fix Targets
- Critical: {count}
- Fixable-warning: {count}

## Fix Procedure
1. Identify and fix the file for each finding
2. Stage fixed files with `git add`
3. Commit message: `fix: address self-review findings [iter {n}] (#{issue-number})`
4. Report unfixable findings as "cannot fix"

## Output Format
Report fix summary in this format:
- Files fixed: {n}
- Commit hash: {hash}
- Fix list:
  - `{file}`: {fix description} ({critical/warning})
- Cannot fix list (if any):
  - `{file}`: {reason}
```

### Fix Task Specification

| Item | Details |
|------|---------|
| Input | Full subagent output (output template with `### Detail`) from reviewing-on-issue / reviewing-claude-config |
| Output | Fix summary (file count, commit hash, fix list) |
| Tools | Read, Edit, Bash — Task(general-purpose) has access to all tools |
| Commit message | `fix: address self-review findings [iter {n}] (#{issue-number})` |
| On error | Report unfixable findings as "cannot fix" in summary |

## Out-of-Scope Follow-up Issue Creation

After the self-review loop completes (PASS, loop stopped, or safety limit reached), if the final iteration's subagent output contains `Out-of-scope items`, create follow-up Issues.

**Deduplication**: Only use the out-of-scope list from the final iteration. Results from each iteration are preserved in PR comments so no information is lost.

```bash
shirokuma-docs issues create --from-file /tmp/shirokuma-docs/{number}-out-of-scope.md \
  --field-status "Backlog"
```

**Conditional execution**: Skip if out-of-scope count is 0.

## Review Findings Comment Verification

In the `[COMPLETE]` state processing, verify that the subagent completed Step 6 PR comment posting.

### Verification Procedure

```bash
shirokuma-docs issues comments {PR#}
```

Check the comment list for review findings comments (the review summary posted by `reviewing-on-issue` / `reviewing-claude-config` in Step 6).

### Fallback

If review findings comments are missing:

1. Display warning: `⚠ Review findings comment was not posted. Posting fallback summary comment.`
2. Post a simplified comment from the subagent output summary:

```bash
shirokuma-docs issues comment {PR#} --body-file /tmp/shirokuma-docs/{number}-review-fallback.md
```

**Fallback comment template:**

```markdown
## Self-Review Findings (Fallback)

**Status:** {PASS | FAIL}
**Critical:** {n} / **Fixable-warning:** {n} / **Out-of-scope:** {n}

> This comment was auto-generated from the subagent output summary because the review skill's Step 6 was not executed.
```

## Expected PR Comment Pattern

| Case | Review Findings Comment | Response Complete Comment | Total |
|------|------------------------|--------------------------|-------|
| PASS (no issues) | 1 | 1 (required) | 2 |
| PASS + out-of-scope | 1 | 1 (required) | 2 |
| NEEDS_FIX → auto-fix → PASS | 1 per iter | 1 (required) | iter count + 1 |
| NEEDS_FIX → cannot converge | 1 per iter | 1 (required) | iter count + 1 |

Review findings comments are posted by the `reviewing-on-issue` / `reviewing-claude-config` subagent in Step 6. The response complete comment is posted by the manager (main AI, `working-on-issue`) in the `[COMPLETE]` state — always required.

## Response Complete Comment (Required)

After self-review finishes (PASS or cannot converge), **always** post a response complete comment to the PR. Recording both the review result and the corresponding response as a pair makes review handling traceable.

```bash
shirokuma-docs issues comment {PR#} --body-file /tmp/shirokuma-docs/{number}-review-response.md
```

**Template (no fixes — PASS):**

```markdown
## Self-Review Response Complete

**Fixed:** None (no issues detected)
```

**Template (fixes applied — PASS):**

```markdown
## Self-Review Response Complete

**Iterations:** {n}
**Fixed:** {critical} critical, {fixable-warning} warning

### Fix List
| File | Fix Description | Classification | Commit |
|------|----------------|----------------|--------|
| `path/to/file.ts` | {fix description} | critical | {short-hash} |

[If follow-up Issues exist:]
### Follow-up Issues
- #{follow-up-number}: {title} (out-of-scope)
```

**Template (cannot converge):**

```markdown
## Self-Review Response Complete (Not Converged)

**Iterations:** {n}
**Unresolved:** {critical} critical, {fixable-warning} warning

### Remaining Issues
- {issue description}

Manual review and fixes required.
```

## Issue Body Update

If review findings require Issue body updates (e.g., task list additions, security fix notes):

- **Consolidate into body**: Integrate review findings into the relevant section of the Issue body (task list, deliverables, etc.). Follow patterns in `item-maintenance.md`.

**Conditional execution**: If review is PASS with no findings, skip.

## Self-Review Completion Report

```markdown
## Self-Review Complete

| Item | Count |
|------|-------|
| Issues detected | {total} |
| Auto-fixed | {fixed} |
| Remaining issues | {remaining} |
| Follow-up Issues | {follow-up} |

[No issues: "No issues were detected"]
[PASS + out-of-scope: "No issues were detected ({n} follow-up Issues)"]
[Remaining: "The following issues remain unresolved: {list}"]
```

## Progress Reporting Template

```text
Self-review [1/5]: Category detection → config + code (mixed)
  Running reviewing-on-issue...
  Running reviewing-claude-config...
  → Merged result: 1 critical, 2 fixable-warning detected, launching fix Task...
  → Fix complete, commit & push

Self-review [2/5]: Re-reviewing...
  → 0 critical, 1 fixable-warning detected (decreased), launching fix Task...

Self-review [3/5]: Re-reviewing...
  → PASS (0 critical, 0 fixable-warning, 1 out-of-scope)
  → Creating follow-up Issues...
```
