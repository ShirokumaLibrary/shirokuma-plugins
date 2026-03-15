---
name: working-on-issue
description: Dispatches work by taking an issue number or task description, selecting the appropriate skill, and orchestrating the full workflow from implementation to PR. Triggers: "work on", "work on #42", "do this", "start working".
allowed-tools: Bash, Read, Grep, Glob, Skill, AskUserQuestion, TaskCreate, TaskUpdate, TaskGet, TaskList
---

# Working on Issue (Orchestrator)

> **Chain Autonomous Progression (MOST IMPORTANT RULE)**: When a subagent (Agent tool) returns a result, you **MUST invoke the next tool in the same response**. This is the single most important rule of this orchestrator. Generating a text-only response while TaskList has pending steps is a chain-breaking error that forces the user to manually type "continue". `action: CONTINUE` → immediately invoke the next Agent/Bash tool. `action: STOP` → stop chain and report to user.

Orchestrate the full workflow from planning to implementation, commit, and PR based on issue type or task description.

**Note**: For session setup, use `starting-session`. This skill works both within a session and standalone (without `starting-session`). It is the primary entry point for working on a specific task in either mode.

## Task Registration (Required)

Register **all chain steps** via TaskCreate **before starting work**.

**Implementation / Bug Fix / Refactoring / Chore:**

| # | content | activeForm | Skill |
|---|---------|------------|-------|
| 1 | Implement changes | Implementing changes | `code-issue` (Skill) |
| 2 | Commit and push changes | Committing and pushing | `commit-issue` (subagent) |
| 3 | Create pull request | Creating pull request | `open-pr-issue` (subagent) |
| 4 | Post work summary | Posting work summary | Manager direct: `issues comment` |
| 5 | Update Status to Review | Updating Status to Review | Manager direct: `issues update` |

Dependencies: step 2 blockedBy 1, step 3 blockedBy 2, step 4 blockedBy 3, step 5 blockedBy 4.

**Research:**

| # | content | activeForm | Skill |
|---|---------|------------|-------|
| 1 | Conduct research | Conducting research | `researching-best-practices` (subagent) |
| 2 | Save findings to Discussion | Creating Discussion | `shirokuma-docs discussions create` |

Dependencies: step 2 blockedBy 1.

Use TaskUpdate to set each step to `in_progress` when starting and `completed` when done.

## Workflow

### Step 1: Analyze Work

**Issue number provided**: `shirokuma-docs show {number}` to fetch title/body/labels/status/priority/size.

#### Sub-Issue Detection

When `shirokuma-docs show {number}` output contains a `parentIssue` field, the issue is a sub-issue of an epic:

1. Reference the parent issue's `## Plan` section to understand overall context
2. Set base branch to the parent's integration branch instead of `develop` (Step 3)
3. `open-pr-issue` will self-detect the sub-issue via the `parentIssue` field, so explicit context passing is not required (if passed, it is used as supplementary; otherwise, self-detection is the fallback)

```bash
# Check parent issue
shirokuma-docs show {parent-number}
```

#### Plan Check (when issue number provided)

Check if issue body contains `## Plan` section (detected by `^## Plan` line prefix).

| Plan State | Condition | Action |
|-----------|-----------|--------|
| No plan | Size XS/S (clear requirements) | → Skip planning, proceed directly to `code-issue` |
| No plan | Size M+ or ambiguous requirements | → Delegate to `preparing-on-issue` |
| Plan exists | — | → Pass `## Plan` section as context to implementation skill |

**XS/S direct implementation path criteria:** Apply when the Issue Size field is XS or S, and the title and body clearly indicate what needs to be changed (mechanical transformation such as pattern replacement, type fix, rename). If Size is unset, requirements are ambiguous, or the judgment is uncertain, delegate to `preparing-on-issue`. See `creating-item/reference/chain-rules.md` "Requirements Clarity Criteria" for the canonical definition.

#### Transition from Preparing Status

| Plan state | Action |
|-----------|--------|
| Preparing + no plan | → Delegate to `preparing-on-issue` |
| Preparing + plan exists | → Transition to Spec Review, ask user approval |

**Text description only**: Classify using dispatch condition table (Step 4) keywords.

### Step 1a: Issue Resolution (text description only)

When called with text only, delegate to `creating-item` skill to ensure an issue exists.

```text
Text description → creating-item → Issue number → Join Step 1
```

### Step 2: Update Status

If issue is not already In Progress: `shirokuma-docs issues update {number} --field-status "In Progress"`

**Spec Review / Ready implicit approval**: Invoking `/working-on-issue` from Spec Review or Ready is implicit plan approval. Transition to In Progress without confirmation.

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
| General Coding | Implementation, bug fix, refactoring, config, Markdown editing | `code-issue` (Skill) | Yes (implementation, bug fix, refactoring) |
| Research | Keywords: `research`, `investigate` | `researching-best-practices` (subagent) | No |
| Review | Keywords: `review`, `audit` | `review-issue` (Skill) | No |
| Project Setup | Keywords: `setup project`, `initialize` | `setting-up-project` | No |

**Pre-resolution logic**: Subagent workers cannot use `AskUserQuestion`, so the manager (main AI) resolves edge cases before invocation:

| Edge Case | Manager's (Main AI) Pre-action |
|-----------|---------------------|
| Staging target files unclear | Check `git status` and pass file list as argument |
| Multiple branch matches | Check branch list and pass correct branch as argument |
| Uncommitted changes present | Invoke `commit-issue` first |

#### TDD Workflow (when TDD applies)

For TDD-applicable work types, wrap the `code-issue` invocation with TDD:

```text
Test Design → Test Creation → Test Gate → [code-issue] → Test Run → Verification
```

See [docs/tdd-workflow.md](docs/tdd-workflow.md) for details.

#### Work Type References

| Work Type | Reference |
|-----------|-----------|
| Implementation | [docs/coding-reference.md](docs/coding-reference.md) |
| Review | [docs/reviewing-reference.md](docs/reviewing-reference.md) |
| Research | [docs/researching-reference.md](docs/researching-reference.md) |

### Step 5: Sequential Workflow Execution

After work completes, execute the chain **automatically**. No user confirmation between steps.

| Work Type | Chain |
|-----------|-------|
| General Coding | Work → Commit → PR → Work Summary → Status Update |
| Research | Research → Discussion |

- **Merge is NOT part of the chain**
- No confirmation between steps, one-line progress reports
- On failure: stop chain, report status, return control to user

**Chain completion guarantee**: After each subagent skill returns its structured output, the manager (main AI) parses the YAML frontmatter and **immediately proceeds to the next step**. The body's first line is used as a one-line summary and does not wait for user input. The Status Update at the end of the chain is executed directly by the manager (main AI) (not via subagent), eliminating the risk of chain interruption.

**Output parse checkpoint** — On receiving subagent output:

1. Read `action` from YAML frontmatter
2. `action: CONTINUE` → **immediately** invoke the skill in the `next` field **in the same response** (output only a one-line summary from the body's first line)
3. `action: STOP` / `REVISE` → stop chain, report to user

**The core rule: when you receive `action: CONTINUE`, respond with a tool call, not text output.**

Exception: If `ucp_required: true` or `suggestions_count > 0`, present to user via AskUserQuestion before continuing (see [reference/worker-completion-pattern.md](reference/worker-completion-pattern.md)).

**Tasks continuation invariant**: After each subagent skill completes, check TaskList. If any step is still `pending`, you MUST invoke the next tool call in the same response — generating a final text-only response while pending steps remain is a chain-breaking error.

**Chain delegation table (MUST follow)** — After receiving a subagent skill result, invoke exactly the skill indicated by the `next` field:

| Completed Skill | `next` field | Next Skill to Invoke | Prohibited Action |
|----------------|-------------|---------------------|------------------|
| `code-issue` | `commit-issue` | `commit-issue` | Do NOT re-invoke `code-issue` |
| `commit-issue` | `open-pr-issue` | `open-pr-issue` | Do NOT delegate to `code-issue` |
| `open-pr-issue` | — | **Start manager-managed steps** (see below) | Do NOT delegate to subagent |

**Manager-managed steps after `open-pr-issue` (most common break point):**

`open-pr-issue` has no `next` field (the next steps are manager-direct, not subagent). PR creation gives a visual "done" feeling, but **TaskList still has pending steps**. When `open-pr-issue` returns, do NOT stop — execute the following via Bash tools **in the same response**:

1. **Work Summary**: Post work summary as Issue comment (Bash: `shirokuma-docs issues comment`)
2. **Status Update**: `shirokuma-docs issues update {number} --field-status "Review"` (Bash)
3. **Evolution**: Auto-record signals (Step 6)

> **Why breaks happen here**: PR creation has strong visual "completion" cues that cause the LLM to output a summary and stop. But the chain is not done until TaskList pending count reaches 0.

**Post-subagent-result behavior (pseudocode):**

```text
for each step in [commit, pr, work_summary, status_update]:
  // GUARD: TaskList has pending steps → this iteration MUST execute (do NOT stop)
  subagent_output = invoke_subagent_skill(step)
  frontmatter, body = parse_yaml_frontmatter(subagent_output)
  action = frontmatter.action                    // CONTINUE | STOP | REVISE
  if action == "STOP":
    handle_failure(frontmatter, body)             // Chain stop, report to user
    break
  // action == "CONTINUE" → proceed immediately
  summary = body.split("\n")[0]                    // Body first line as summary
  log_one_line_summary(summary)
  TaskUpdate(step, "completed")
  if TaskList.any(status == "pending"):           // Pending tasks remain → MUST continue
    invoke_skill(frontmatter.next)                // Invoke next skill in SAME response
  // End of chain only when all tasks are completed
```

**Output template field definitions:**

| Field | Required | Values | Description |
|-------|----------|--------|-------------|
| `action` | Yes | `CONTINUE` / `STOP` / `REVISE` | Behavioral directive for orchestrator (first field) |
| `next` | Conditional | skill name | Skill to invoke when `action: CONTINUE` |
| `status` | Yes | `SUCCESS` / `PASS` / `NEEDS_FIX` / `FAIL` / `NEEDS_REVISION` | Result state |
| `ref` | Conditional | GitHub reference | Human-readable reference when GitHub write occurred |
| `comment_id` | Conditional | numeric (database_id) | Only when a comment was posted. For reply-to / edit |
| `ucp_required` | No | boolean | Set to `true` when the worker requires user judgment |
| `suggestions_count` | No | number | Number of improvement suggestions |
| `followup_candidates` | No | string[] | Follow-up Issue candidates |

The `Summary` field is abolished. Instead, the **body's first line** is treated as the summary.

**Status → Action mapping:**

| Status | Action | Used By | Chain Behavior |
|--------|--------|---------|----------------|
| SUCCESS | CONTINUE | commit-issue, open-pr-issue, code-issue | Proceed to next step |
| FAIL | STOP | All subagent skills | Chain stop, report to user |
| NEEDS_REVISION | REVISE | review-issue (plan review) | Enter revision loop |

Subagent outputs are internal processing data, not user-facing output. Presenting raw subagent output exposes technical intermediates that disrupt the user's workflow experience. Output only a one-line summary and immediately proceed to the next tool call.

#### Skill and Subagent Invocation Pattern

Skills are invoked via Skill tool (main context) or Agent tool (subagent). Skills that need project-specific rules (paths-based) run in the main context via Skill tool. Simple operations (git, gh) run as subagents.

| Skill | Invocation | Reason |
|-------|-----------|--------|
| `code-issue` | Skill tool | Needs project rules (development-patterns, security-boundary, etc.) |
| `review-issue` | Skill tool | Needs project rules for rule-compliant review |
| `reviewing-claude-config` | Skill tool | Needs project rules for quality standards |
| `commit-issue` | Agent (`commit-worker`) | Git operations only, no project rules needed |
| `open-pr-issue` | Agent (`pr-worker`) | GitHub operations only, no project rules needed |
| `researching-best-practices` | Agent (`research-worker`) | External research, no project rules needed |

**Skill tool invocation:**

```text
Skill(
  skill: "{skill-name}",
  args: "#{issue-number}"
)
```

**Agent tool invocation (for kept subagents only):**

```text
Agent(
  description: "{worker-name} #{number}",
  subagent_type: "{worker-name}",
  prompt: "#{issue-number}"
)
```

**The `pr-worker` prompt MUST include the issue number.** `open-pr-issue` includes `Closes #{issue-number}` in the PR body when launched with an issue number, linking the PR to the issue. If the issue number is omitted, `Closes` is skipped and the PR will not be linked to the issue.

> **CRITICAL — Chain continuation after Agent tool returns**: When a sub-agent (e.g., `pr-worker`, `commit-worker`) completes and the Agent tool returns, **check TaskList for remaining `pending` steps**. If pending steps remain (work summary, status update, evolution), **immediately proceed to the next pending step in the same response**. Do NOT stop, summarize, or ask the user. The Agent tool returning is a chain mid-point, not a completion signal.

#### Work Summary (Issue Comment)

After PR creation, post a technical work summary to the Issue as a comment. This is the primary context record that `starting-session #N` will restore in future sessions.

The work summary focuses on **technical work details** — what was changed, which files were modified, and technical decisions made. Session-level context (cross-cutting decisions, blockers, next steps) is handled separately by `ending-session`.

```bash
shirokuma-docs issues comment {number} --body-file /tmp/shirokuma-docs/{number}-work-summary.md
```

Where `/tmp/shirokuma-docs/{number}-work-summary.md` contains:

```markdown
## Work Summary

### Changes
{What was implemented or fixed — technical details}

### Modified Files
- `path/file.ts` - {Change description}

### Pull Request
PR #{pr-number}

### Technical Decisions
- {Decision and rationale}
```

Skip this step if no issue number is associated with the work.

**Standalone completion**: When `working-on-issue` completes its chain (standalone or within a session), the Work Summary is automatically posted. This eliminates the need for `ending-session` to repeat technical details — `ending-session` only adds session-level context (cross-cutting decisions, blockers, next steps).

#### Status Update (End of Chain)

After work summary is posted, update Status to Review for issues with a number:

```bash
shirokuma-docs issues update {number} --field-status "Review"
```

**Status fallback verification**: After chain completion, check Status via `shirokuma-docs show {number}`. If still In Progress → directly update with `shirokuma-docs issues update {number} --field-status "Review"` (idempotent: re-updating to Review when already Review is harmless).

#### Next Steps Suggestion (End of Chain)

After Status update, present next action candidates to the user. Extract the PR number from `open-pr-issue`'s `ref` field to provide specific guidance. If `ref` is unavailable (e.g., PR not created), omit the `/reviewing-on-pr` line.

```
## Next Steps

- `/reviewing-on-pr #{pr-number}` — Run self-review on the PR
```

### Step 6: Evolution Signal Auto-Recording

After successful chain completion (skip on chain failure), auto-record Evolution signals following the "Auto-Recording Procedure at Skill Completion" in the `rule-evolution` rule. Do not register as a task (non-blocking processing).

## Batch Mode

When multiple issue numbers are provided (e.g., `#101 #102 #103`), activate batch mode.

### Sequential Batch (Default)

Process issues that share common files sequentially in a single branch and PR. See [reference/batch-workflow.md](reference/batch-workflow.md) for detection, eligibility, task registration template, workflow, and context details.

### Parallel Batch (Deprecated)

> **Deprecated**: Parallel batch mode (`--parallel` flag) has been removed. The `parallel-coding-worker` agent has been deprecated as part of the subagent architecture simplification. Use sequential batch mode instead.

## Arguments

| Format | Example | Behavior |
|--------|---------|----------|
| Issue number | `#42` | Fetch issue, analyze type |
| Multiple issues | `#101 #102 #103` | Sequential batch mode |
| Description | `implement dashboard` | Text classification → `creating-item` |
| No argument | — | AskUserQuestion |

### Flags

| Flag | Description |
|------|-------------|
| `--headless` | Headless mode. Applies default behaviors to UCPs and skips interactive confirmations |

### Flag Combinations

| Combination | Behavior |
|-------------|----------|
| `--headless` (single issue) | Headless mode for single issue (see Headless Mode section) |

## Headless Mode

When `--headless` is specified, default behaviors are applied to implementation-phase UCPs (User Control Points), completing the chain without interactive confirmations. Use for batch execution via `claude -p` or to skip confirmations within an interactive session.

### Preconditions

All of the following must be met to run in headless mode:

1. An **explicit issue number** is provided as an argument
2. The issue status is **Spec Review** or **Ready**
3. The issue body contains a `## Plan` (EN) or `## 計画` (JA) section

If any precondition is not met, display an error message and stop (no fallback to normal mode).

> **Note:** Issues with statuses other than Spec Review / Ready (e.g., In Progress, Preparing, Backlog) will also stop with a precondition error when `--headless` is specified. Issues in Preparing status require interactive planning via `preparing-on-issue` and are therefore excluded from headless mode.

### UCP Default Behaviors

| UCP ID | Location | Normal Mode | Headless Mode Default |
|--------|----------|-------------|----------------------|
| W1 | No-argument invocation | AskUserQuestion for number | Stop with precondition error |
| W2 | Issue is Done/Released | Confirm reopen | Warn and stop (prevent accidental execution) |
| W3 | ADR proposal (Feature M+) | AskUserQuestion for confirmation | Skip (continue without ADR) |
| W4 | Wrong branch detected | AskUserQuestion for switch | Warn and stop (highest risk) |
| W5 | Worker's ucp_required flag | AskUserQuestion with suggestions | Skip and record in Issue comment |

#### W5 Skip Recording in Issue Comment

When W5 (worker UCP) is skipped in headless mode, record it as an Issue comment in the following format:

```
**[Headless] UCP Skipped:** {worker name}
**Suggestion:** {summary of skipped suggestion}
**Default action:** Skipped and continued
```

### Usage Examples

```bash
# Batch execution via claude -p
claude -p "/working-on-issue --headless #42"

# Skip confirmations within interactive session
/working-on-issue #42 --headless
```

## Edge Cases

| Situation | Action |
|-----------|--------|
| Issue not found | AskUserQuestion for number |
| Issue Done/Released | Warn, confirm reopen |
| Already In Progress | Continue without status change |
| Wrong branch | AskUserQuestion: switch or continue |
| Chain failure | Report completed/remaining steps, return control |
| Sub-issue with no integration branch | Use `develop` as base, warn user |
| Epic issue selected directly | See "Epic Issue Entry Point" below |
| `--headless` + precondition not met | Display error message and stop |
| `--headless` + wrong branch (W4) | Warn and stop (no auto-switch) |
| `--headless` + worker UCP (W5) | Skip and record in Issue comment |

## Epic Issue Entry Point

When an epic issue is directly specified (detected by `subIssuesSummary.total > 0` or a `### Sub-Issue Structure` section in the plan), execute the following flow instead of standard implementation dispatch.

### Pre-condition: Plan with Sub-Issue Structure

The epic must have a `## Plan` with a `### Sub-Issue Structure` section. If no plan exists, delegate to `preparing-on-issue` first (standard flow).

### Epic Workflow

1. **Create integration branch**: Extract branch name from `### Integration Branch` in the plan, create from `develop`:
   ```bash
   git checkout develop && git pull origin develop
   git checkout -b epic/{number}-{slug}
   git push -u origin epic/{number}-{slug}
   ```

2. **Create sub-issues in batch**: Parse the `### Sub-Issue Structure` table from the plan. For each row, create a sub-issue via CLI:
   ```bash
   shirokuma-docs issues create --from-file /tmp/shirokuma-docs/{slug}.md \
     --parent {epic-number} --field-status "Backlog"
   ```
   Body: Minimal stub referencing the parent plan (`See #{epic-number} for full plan`).
   After creation, update the epic's `### Sub-Issue Structure` table with actual issue numbers.

3. **Present execution order**: Based on the `### Execution Order` section or dependency column, display the recommended order and end. Do NOT propose immediate work start — each sub-issue should be worked on in a separate conversation per the epic pattern in `best-practices-first`:
   ```
   Epic setup complete.

   **Integration branch:** `epic/{number}-{slug}`
   **Sub-issues created:** #{sub1}, #{sub2}, #{sub3}

   Recommended execution order:
   1. #{sub1} - {title} (no dependencies)
   2. #{sub2} - {title} (depends on #{sub1})
   3. #{sub3} - {title} (depends on #{sub2})

   Start each sub-issue in a new conversation with `/working-on-issue #{sub}`.
   ```

### Responsibility Note

Sub-issue creation in this flow uses `shirokuma-docs issues create` directly (not `creating-item`). The plan already specifies sub-issue details, so `creating-item`'s inference logic is unnecessary.

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
| `worker-completion-pattern` reference | Worker completion unified pattern, extended schema |

## Tool Usage

| Tool | When |
|------|------|
| AskUserQuestion | Requirement clarification, approach selection, edge cases (manager (main AI) pre-resolves) |
| TaskCreate, TaskUpdate | Chain step registration and status updates (required for all work) |
| TaskList, TaskGet | Check pending steps and task state |
| Bash | Git operations, `shirokuma-docs issues` commands |

## Notes

- This skill is the **manager (the main-process AI agent)** — work is delegated via Skill tool (code-issue, review-issue, reviewing-claude-config) or Agent tool (commit-worker, pr-worker, research-worker)
- Update issue status before starting
- Ensure correct feature branch
- TDD-applicable work types wrap `code-issue` invocation with TDD ([docs/tdd-workflow.md](docs/tdd-workflow.md))
- Workflow executes sequentially (Commit → PR → Work Summary → Status Update). **Merge is NOT included**
- Chain execution stops on error and returns control to user
- **Chain autonomous progression (MOST IMPORTANT)**: When you receive `action: CONTINUE`, respond with a tool call, not text output. As long as TaskList has pending steps, invoke the next Skill/Agent/Bash tool in the same response. The `open-pr-issue` → manager steps transition is the most common break point — immediately execute Work Summary → Status Update via Bash
