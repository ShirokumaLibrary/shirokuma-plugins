---
name: working-on-issue
description: Dispatches work by taking an issue number or task description, selecting the appropriate skill, and orchestrating the full workflow from implementation to PR. Triggers: "work on", "work on #42", "do this", "start working".
allowed-tools: Bash, Read, Grep, Glob, AskUserQuestion, TodoWrite
---

# Working on Issue (Orchestrator)

> **Chain Autonomous Progression**: Fork skill results are intermediate chain data, not final user-facing output. When TodoWrite has pending steps, immediately parse the `## Fork Result` block and proceed to the next step. Stopping after a fork result forces the user to manually type "continue", breaking the autonomous workflow that makes this orchestrator valuable. Log a one-line summary and invoke the next tool in the same response.

Orchestrate the full workflow from planning to implementation, commit, PR, and self-review based on issue type or task description.

**Note**: For session setup, use `starting-session`. This skill works both within a session and standalone (without `starting-session`). It is the primary entry point for working on a specific task in either mode.

## TodoWrite Registration (Required)

Register **all chain steps** in TodoWrite **before starting work**.

**Implementation / Design / Bug Fix / Refactoring / Chore:**

| # | content | activeForm | Skill |
|---|---------|------------|-------|
| 1 | Implement changes | Implementing changes | `coding-on-issue` (fork) / `designing-ui-on-issue` |
| 2 | Commit and push changes | Committing and pushing | `committing-on-issue` (fork) |
| 3 | Create pull request | Creating pull request | `creating-pr-on-issue` (fork) |
| 4 | Run self-review and apply fixes | Running self-review | Manager (main AI) directly manages (see reference) |
| 5 | Update Status to Review | Updating Status to Review | `shirokuma-docs issues update` |

**Research:**

| # | content | activeForm | Skill |
|---|---------|------------|-------|
| 1 | Conduct research | Conducting research | `researching-best-practices` (fork) |
| 2 | Save findings to Discussion | Creating Discussion | `shirokuma-docs discussions create` |

Update each step to `in_progress` when starting and `completed` when done.

## Workflow

### Step 1: Analyze Work

**Issue number provided**: `shirokuma-docs issues show {number}` to fetch title/body/labels/status/priority/size.

#### Sub-Issue Detection

When `shirokuma-docs issues show {number}` output contains a `parentIssue` field, the issue is a sub-issue of an epic:

1. Reference the parent issue's `## Plan` section to understand overall context
2. Set base branch to the parent's integration branch instead of `develop` (Step 3)
3. `creating-pr-on-issue` will self-detect the sub-issue via the `parentIssue` field, so explicit context passing is not required (if passed, it is used as supplementary; otherwise, self-detection is the fallback)

```bash
# Check parent issue
shirokuma-docs issues show {parent-number}
```

#### Plan Check (when issue number provided)

Check if issue body contains `## Plan` section (detected by `^## Plan` line prefix).

| Plan state | Action |
|-----------|--------|
| No plan | → Delegate to `planning-on-issue` |
| Plan exists | → Pass `## Plan` section as context to implementation skill |

#### Transition from Planning Status

| Plan state | Action |
|-----------|--------|
| Planning + no plan | → Delegate to `planning-on-issue` |
| Planning + plan exists | → Transition to Spec Review, ask user approval |

**Text description only**: Classify using dispatch condition table (Step 4) keywords.

### Step 1a: Issue Resolution (text description only)

When called with text only, delegate to `creating-item` skill to ensure an issue exists.

```text
Text description → creating-item → Issue number → Join Step 1
```

### Step 2: Update Status

If issue is not already In Progress: `shirokuma-docs issues update {number} --field-status "In Progress"`

**Spec Review implicit approval**: Invoking `/working-on-issue` is implicit plan approval. Transition to In Progress without confirmation.

### Step 3: Ensure Feature Branch

If on `develop` (or the integration branch for sub-issues), create branch per `branch-workflow` rule:

```bash
# Normal issue
git checkout develop && git pull origin develop
git checkout -b {type}/{number}-{slug}

# Sub-issue (branch from integration branch)
git checkout epic/{parent-number}-{slug} && git pull origin epic/{parent-number}-{slug}
git checkout -b {type}/{number}-{slug}
```

**Sub-issue integration branch detection** (in order):

1. Extract branch name from parent issue body: look for `### Integration Branch` (EN) / `### Integration ブランチ` (JA) heading, extract branch name from the backtick block immediately following (any prefix accepted: `epic/`, `chore/`, `feat/`, etc.)
2. Fallback: `git branch -r --list "origin/*/{parent-number}-*"` (1 match → auto-select, multiple → AskUserQuestion, 0 → fall back to `develop`)
3. Not found: Use `develop` as base and warn user

### Step 3b: Propose ADR (Feature M+ only)

For Feature type, Size M+, suggest ADR creation (AskUserQuestion).

### Step 4: Select and Execute Skill

#### Dispatch Condition Table

| Work Type | Condition | Delegate To | TDD |
|-----------|-----------|-------------|-----|
| General Coding | Implementation, bug fix, refactoring, config, Markdown editing | `coding-on-issue` (fork) | Yes (implementation, bug fix, refactoring) |
| UI Design | Keywords: `design`, `UI`, `memorable`, `impressive` | `designing-ui-on-issue` | No |
| Research | Keywords: `research`, `investigate` | `researching-best-practices` (fork) | No |
| Review | Keywords: `review`, `audit` | `reviewing-on-issue` (fork) | No |
| Project Setup | Keywords: `setup project`, `initialize` | `setting-up-project` | No |

**Pre-resolution logic**: Fork workers cannot use `AskUserQuestion`, so the manager (main AI) resolves edge cases before invocation:

| Edge Case | Manager's (Main AI) Pre-action |
|-----------|---------------------|
| Staging target files unclear | Check `git status` and pass file list as argument |
| Multiple branch matches | Check branch list and pass correct branch as argument |
| Uncommitted changes present | Invoke `committing-on-issue` first |

#### TDD Workflow (when TDD applies)

For TDD-applicable work types, wrap the `coding-on-issue` invocation with TDD:

```text
Test Design → Test Creation → Test Gate → [coding-on-issue] → Test Run → Verification
```

See [docs/tdd-workflow.md](docs/tdd-workflow.md) for details.

#### Work Type References

| Work Type | Reference |
|-----------|-----------|
| Implementation | [docs/coding-reference.md](docs/coding-reference.md) |
| Design | [docs/designing-reference.md](docs/designing-reference.md) |
| Review | [docs/reviewing-reference.md](docs/reviewing-reference.md) |
| Research | [docs/researching-reference.md](docs/researching-reference.md) |

### Step 5: Sequential Workflow Execution

After work completes, execute the chain **automatically**. No user confirmation between steps.

| Work Type | Chain |
|-----------|-------|
| General Coding / Design | Work → Commit → PR → Simplify → Self-Review → Status Update |
| Research | Research → Discussion |

- **Merge is NOT part of the chain**
- No confirmation between steps, one-line progress reports
- On failure: stop chain, report status, return control to user

**Chain completion guarantee**: After each fork skill returns its Fork Result, the manager (main AI) parses the `## Fork Result` block and **immediately proceeds to the next step**. Fork Result summaries are limited to one line and do not wait for user input. The Status Update at the end of the chain is executed directly by the manager (main AI) (not via fork), eliminating the risk of chain interruption.

**Post-fork-result behavior (pseudocode):**

```text
for each step in [commit, pr, simplify, self_review, status_update]:
  fork_output = invoke_fork_skill(step)
  fork_result = parse_fork_result(fork_output)  // Extract ## Fork Result block
  if fork_result.status == "FAIL":
    handle_failure(fork_result)
    break
  log_one_line_summary(fork_result.summary)
  update_todo(step, "completed")
  immediately_invoke_next_step()  // ← Do NOT wait for user input
```

**Fork Result Status values:**

| Status | Used By | Meaning |
|--------|---------|---------|
| SUCCESS | committing-on-issue, creating-pr-on-issue, coding-on-issue | Completed successfully |
| PASS | reviewing-on-issue (self-review) | No issues detected |
| FAIL | All fork skills | Error or issues requiring action |
| NEEDS_REVISION | reviewing-on-issue (plan review) | Plan needs revision |

Fork Results are internal processing data, not user-facing output. Presenting raw fork output exposes technical intermediates that disrupt the user's workflow experience. Output only a one-line summary and immediately proceed to the next tool call.

#### Self-Review Loop (Manager = Main AI Directly Manages)

After PR creation, the manager (main AI) directly manages self-review. See [reference/self-review-workflow.md](reference/self-review-workflow.md) for details.

Self-review should be launched via Skill tool (`reviewing-on-issue` / `reviewing-claude-config`), not Agent (general-purpose). Review skills post PR comments as part of their workflow — launching via other means causes review findings to not be recorded on the PR, losing the audit trail.

**State transition overview:**

```text
[SIMPLIFY] /simplify initial pass → commit & push (if changes)
    ↓
[REVIEW] Launch review → [PARSE] Parse result → [PRESENT] Present result → Decision
  ├── PASS → [COMPLETE]
  ├── FAIL + Auto-fixable → [FIX] Task fix → [CONVERGE] Convergence check → [REVIEW]
  └── FAIL + Not auto-fixable → [REPORT]
```

| State | Action |
|-------|--------|
| SIMPLIFY | Invoke `/simplify` via Skill tool (only when code-category files exist; run once, skip on failure) |
| REVIEW | Launch `reviewing-on-issue` / `reviewing-claude-config` as fork |
| PARSE | Parse Fork Result, PASS/FAIL determination |
| PRESENT | Present self-review result summary to user |
| FIX | Delegate fix to `Task(general-purpose)` |
| CONVERGE | Convergence check (numeric-based, stop after 2 consecutive non-decreases) |
| REPORT | Report remaining issues to user |
| COMPLETE | Create out-of-scope Issues → Post fix comment |

**Safety limit**: 5 iterations (2 critical + 2 warning + 1 buffer). On reaching limit, convert remaining fixable-warnings to follow-up Issues.

**Batch mode self-review**: Run once for the entire batch PR. After completion, update all batch Issue statuses to Review.

#### Status Update (End of Chain)

After self-review completion, update Status to Review for issues with a number:

```bash
shirokuma-docs issues update {number} --field-status "Review"
```

**Status fallback verification**: After chain completion, check Status via `shirokuma-docs issues show {number}`. If still In Progress → directly update with `shirokuma-docs issues update {number} --field-status "Review"` (idempotent: re-updating to Review when already Review is harmless).

### Step 6: Evolution Signal Auto-Recording

After successful chain completion (skip on chain failure), auto-record Evolution signals detected during the session following the "Auto-Recording Procedure at Skill Completion" in the `rule-evolution` rule.

#### 6a: Introspection Checks

Self-review the session using the detection checklist (see `rule-evolution` rule).

#### 6b: Environment Checks (Lint Metrics)

Regardless of introspection check results, fetch lint metrics once:

```bash
shirokuma-docs lint-tests -p . --format json 2>/dev/null
```

| Condition | Action |
|-----------|--------|
| `summary.errorCount > 0` | Record as Evolution signal + propose follow-up Issue creation |
| `summary.warningCount > 0` | Report count (signal type: lint trend) |
| Command failure | Skip (environment checks are best-effort) |

#### 6c: Signal Recording

- Introspection or environment checks detected signals → Post comment to Evolution Issue → Display 1-line recording confirmation
- No signals → Check for accumulated signals → Display reminder (fallback)

Do not register in TodoWrite (non-blocking processing, not a work step).

## Batch Mode

When multiple issue numbers are provided (e.g., `#101 #102 #103`), activate batch mode. See [reference/batch-workflow.md](reference/batch-workflow.md) for detection, eligibility, TodoWrite template, workflow, and context details.

## Arguments

| Format | Example | Behavior |
|--------|---------|----------|
| Issue number | `#42` | Fetch issue, analyze type |
| Multiple issues | `#101 #102 #103` | Batch mode |
| Description | `implement dashboard` | Text classification → `creating-item` |
| No argument | — | AskUserQuestion |

## Edge Cases

| Situation | Action |
|-----------|--------|
| Issue not found | AskUserQuestion for number |
| Issue Done/Released | Warn, confirm reopen |
| Already In Progress | Continue without status change |
| Wrong branch | AskUserQuestion: switch or continue |
| Chain failure | Report completed/remaining steps, return control |
| Sub-issue with no integration branch | Use `develop` as base, warn user |
| Epic issue selected directly | Propose working on a sub-issue instead |

## Rule References

| Rule | Usage |
|------|-------|
| `branch-workflow` | Branch naming, creation from `develop`, integration branch |
| `batch-workflow` | Batch eligibility, quality standards, branch naming |
| `epic-workflow` reference | Epic/sub-issue workflow overview |
| `project-items` | Status workflow, field requirements |
| `git-commit-style` | Commit message format |
| `output-language` | GitHub output language convention |
| `github-writing-style` | Bullet-point vs prose guidelines |

## Tool Usage

| Tool | When |
|------|------|
| AskUserQuestion | Requirement clarification, approach selection, edge cases (manager (main AI) pre-resolves) |
| TodoWrite | Chain step registration (required for all work) |
| Bash | Git operations, `shirokuma-docs issues` commands |

## Notes

- This skill is the **manager (the main-process AI agent)** — actual work is delegated to fork workers
- Update issue status before starting
- Ensure correct feature branch
- TDD-applicable work types wrap `coding-on-issue` invocation with TDD ([docs/tdd-workflow.md](docs/tdd-workflow.md))
- Workflow executes sequentially (Commit → PR → Simplify → Self-Review → Status Update). **Merge is NOT included**
- Self-review is directly managed by the manager (main AI) ([reference/self-review-workflow.md](reference/self-review-workflow.md))
- Chain execution stops on error and returns control to user
- **Chain autonomous progression**: Fork Results are intermediate chain data. Stopping after receiving one forces the user to manually prompt "continue", which defeats the purpose of an automated workflow chain. As long as TodoWrite has pending steps, immediately parse the `## Fork Result` block and execute the next step's Skill/Bash tool call. Log a one-line summary and invoke the next tool in the same response
