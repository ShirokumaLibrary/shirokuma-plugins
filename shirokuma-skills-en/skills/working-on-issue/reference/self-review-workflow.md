# Self-Review Workflow Reference

Specification of self-review executed within the `working-on-issue` Step 5 chain.

The self-review state machine (REVIEW → FIX → CONVERGE loop) has been migrated to review-worker's self-review mode. See `agents/review-worker/reference/self-review-mode.md` for details.

## Contents

- working-on-issue Responsibilities
- /simplify Initial Pass
- review-worker Invocation
- Result Parsing and Post-Processing
- Expected PR Comment Pattern
- Self-Review Completion Report

## working-on-issue Responsibilities

| Responsibility | Owner |
|---------------|-------|
| `/simplify` pre-pass execution | working-on-issue (manager) |
| Commit & push after SIMPLIFY | working-on-issue (manager) |
| Agent invocation of review-worker | working-on-issue (manager) |
| Result parsing (action/status) | working-on-issue (manager) |
| Recommendations post-processing | working-on-issue (manager) |
| Plan-gap Evolution signal recording | working-on-issue (manager) |
| REVIEW → FIX → CONVERGE loop | review-worker (internal to sub-agent) |
| Review result PR comment posting | review-worker (internal to sub-agent) |
| Response complete comment posting | review-worker (internal to sub-agent) |
| Out-of-scope follow-up Issue creation | review-worker (internal to sub-agent) |

## /simplify Initial Pass

Run `/simplify` once as a pre-pass before self-review.

### Execution Condition

Only run when `code` category files (`.ts/.tsx/.js/.jsx`) are present in the file category detection results (`git diff --name-only develop..HEAD`). Skip if only `config` or `docs` files.

### Invocation

The manager (main AI) invokes via the `Skill` tool:

```text
skill: "simplify"
```

### Output Handling

Fire-and-forget (no PASS/FAIL determination). The quality gate is handled by the subsequent review-worker.

### Commit Processing

After `/simplify` completes, the manager (main AI) performs:

1. Check for changes via `git diff`
2. Changes found → `git add -A` + commit + push
   - Commit message: `refactor: apply /simplify quality improvements (#{issue-number})`
3. No changes → skip

### On Failure

Optional step — on error or timeout, skip and proceed to review-worker invocation.

### Batch Mode

Run once for the entire batch PR.

> **⚠ Required**: SIMPLIFY is a quality-baseline **pre-pass**, not a substitute for self-review. After SIMPLIFY completes, always invoke review-worker's self-review mode.

## review-worker Invocation

```text
Agent(
  description: "review-worker self-review #{number}",
  subagent_type: "review-worker",
  prompt: "self-review #{number}"
)
```

review-worker completes the REVIEW → FIX → CONVERGE loop internally and returns only the final result.

## Result Parsing and Post-Processing

### YAML Frontmatter Parsing

```yaml
---
action: {CONTINUE | STOP}
status: {PASS | NEEDS_FIX_RESOLVED | FAIL}
ref: "PR #{pr-number}"
---
```

### Action-Based Behavior

| action | Behavior |
|--------|----------|
| CONTINUE | Proceed to post-processing → Work Summary → Status Update → Evolution |
| STOP | Chain stop, report to user |

### Recommendations Post-Processing

| Classification | Action |
|---------------|--------|
| `[trivial]` | Propose immediate fix (AskUserQuestion) |
| `[rule]` | Record as Evolution signal |
| `[trigger:*]` / `[one-off]` | Propose follow-up Issue creation |

### Plan-Gap Processing

When plan-gap count > 0, record as Evolution signal for `planning-on-issue` improvement.

## Expected PR Comment Pattern

Pattern of comments posted by review-worker. Used by working-on-issue to verify the existence of review findings.

| Case | Review Findings Comment | Response Complete Comment | Total |
|------|------------------------|--------------------------|-------|
| PASS (no issues) | 1 | 1 (required) | 2 |
| PASS + out-of-scope | 1 | 1 (required) | 2 |
| NEEDS_FIX → auto-fix → PASS | 1 per iter | 1 (required) | iter count + 1 |
| NEEDS_FIX → cannot converge | 1 per iter | 1 (required) | iter count + 1 |

Both review findings comments and response complete comments are posted internally by review-worker.

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
