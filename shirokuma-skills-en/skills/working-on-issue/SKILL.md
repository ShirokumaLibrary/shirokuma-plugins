---
name: working-on-issue
description: Dispatches work by taking an issue number or task description, selecting the appropriate skill, and orchestrating the full workflow from implementation to PR. Triggers: "work on", "work on #42", "do this", "start working".
allowed-tools: Bash, Read, Grep, Glob, AskUserQuestion, TodoWrite
---

# Working on Issue (Orchestrator)

> **Chain Autonomous Progression**: Subagent skill results are intermediate chain data, not final user-facing output. When TodoWrite has pending steps, immediately parse the YAML frontmatter and proceed to the next step. Stopping after a subagent result forces the user to manually type "continue", breaking the autonomous workflow that makes this orchestrator valuable. Log a one-line summary and invoke the next tool in the same response.

Orchestrate the full workflow from planning to implementation, commit, and PR based on issue type or task description.

**Note**: For session setup, use `starting-session`. This skill works both within a session and standalone (without `starting-session`). It is the primary entry point for working on a specific task in either mode.

## TodoWrite Registration (Required)

Register **all chain steps** in TodoWrite **before starting work**.

**Implementation / Bug Fix / Refactoring / Chore:**

| # | content | activeForm | Skill |
|---|---------|------------|-------|
| 1 | Implement changes | Implementing changes | `coding-on-issue` (subagent) |
| 2 | Commit and push changes | Committing and pushing | `committing-on-issue` (subagent) |
| 3 | Create pull request | Creating pull request | `creating-pr-on-issue` (subagent) |
| 4 | Post work summary | Posting work summary | Manager direct: `issues comment` |
| 5 | Update Status to Review | Updating Status to Review | Manager direct: `issues update` |

**Research:**

| # | content | activeForm | Skill |
|---|---------|------------|-------|
| 1 | Conduct research | Conducting research | `researching-best-practices` (subagent) |
| 2 | Save findings to Discussion | Creating Discussion | `shirokuma-docs discussions create` |

Update each step to `in_progress` when starting and `completed` when done.

## Workflow

### Step 1: Analyze Work

**Issue number provided**: `shirokuma-docs show {number}` to fetch title/body/labels/status/priority/size.

#### Sub-Issue Detection

When `shirokuma-docs show {number}` output contains a `parentIssue` field, the issue is a sub-issue of an epic:

1. Reference the parent issue's `## Plan` section to understand overall context
2. Set base branch to the parent's integration branch instead of `develop` (Step 3)
3. `creating-pr-on-issue` will self-detect the sub-issue via the `parentIssue` field, so explicit context passing is not required (if passed, it is used as supplementary; otherwise, self-detection is the fallback)

```bash
# Check parent issue
shirokuma-docs show {parent-number}
```

#### Plan Check (when issue number provided)

Check if issue body contains `## Plan` section (detected by `^## Plan` line prefix).

| Plan state | Action |
|-----------|--------|
| No plan | → Delegate to `preparing-on-issue` |
| Plan exists | → Pass `## Plan` section as context to implementation skill |

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
| General Coding | Implementation, bug fix, refactoring, config, Markdown editing | `coding-on-issue` (subagent) | Yes (implementation, bug fix, refactoring) |
| Research | Keywords: `research`, `investigate` | `researching-best-practices` (subagent) | No |
| Review | Keywords: `review`, `audit` | `reviewing-on-issue` (subagent) | No |
| Project Setup | Keywords: `setup project`, `initialize` | `setting-up-project` | No |

**Pre-resolution logic**: Subagent workers cannot use `AskUserQuestion`, so the manager (main AI) resolves edge cases before invocation:

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

**Output parse checkpoint** — On receiving subagent output, execute these checks in order:

1. **Extract YAML frontmatter** (block delimited by `---`)
2. **action field**: Read `action` → STOP/FIX/REVISE/CONTINUE determines the next behavior
3. **status field**: Read `status` → log for record
4. **Body first line**: Extract the first line of the body after the frontmatter → use as `log_one_line_summary()`
5. **action = CONTINUE**: Immediately invoke the skill specified in the `next` field

If action = CONTINUE, invoke the next Skill/Bash tool in the **same response**. Do not output anything except a one-line summary before the tool call.

**TodoWrite continuation invariant**: After each subagent skill completes, check TodoWrite. If any step is still `pending`, you MUST invoke the next tool call in the same response — generating a final text-only response while pending steps remain is a chain-breaking error.

**Chain delegation table (MUST follow)** — After receiving a subagent skill result, invoke exactly the skill indicated by the `next` field:

| Completed Skill | `next` field | Next Skill to Invoke | Prohibited Action |
|----------------|-------------|---------------------|------------------|
| `coding-on-issue` | `committing-on-issue` | `committing-on-issue` | Do NOT re-invoke `coding-on-issue` |
| `committing-on-issue` | `creating-pr-on-issue` | `creating-pr-on-issue` | Do NOT delegate to `coding-on-issue` |
| `creating-pr-on-issue` | — | **Start manager-managed steps** (see below) | Do NOT delegate to subagent |

**Manager-managed steps after `creating-pr-on-issue` (required checklist):**

When `creating-pr-on-issue` returns its result, execute the following steps **within the same chain** sequentially. Each step is registered as `pending` in TodoWrite — do NOT stop while pending steps remain:

1. **Work Summary**: Post work summary as Issue comment
2. **Status Update**: `shirokuma-docs issues update {number} --field-status "Review"`
3. **Evolution**: Auto-record signals (Step 6)

**Post-subagent-result behavior (pseudocode):**

```text
for each step in [commit, pr, work_summary, status_update]:
  // GUARD: TodoWrite has pending steps → this iteration MUST execute (do NOT stop)
  subagent_output = invoke_subagent_skill(step)
  frontmatter, body = parse_yaml_frontmatter(subagent_output)
  action = frontmatter.action                    // CONTINUE | STOP | REVISE
  if action == "STOP":
    handle_failure(frontmatter, body)             // Chain stop, report to user
    break
  // action == "CONTINUE" → proceed immediately
  summary = body.split("\n")[0]                    // Body first line as summary
  log_one_line_summary(summary)
  update_todo(step, "completed")
  if todos.any(status == "pending"):              // Pending todos remain → MUST continue
    invoke_skill(frontmatter.next)                // Invoke next skill in SAME response
  // End of chain only when all todos are completed
```

**Output template field definitions:**

| Field | Required | Values | Description |
|-------|----------|--------|-------------|
| `action` | Yes | `CONTINUE` / `STOP` / `REVISE` | Behavioral directive for orchestrator (first field) |
| `next` | Conditional | skill name | Skill to invoke when `action: CONTINUE` |
| `status` | Yes | `SUCCESS` / `PASS` / `NEEDS_FIX` / `FAIL` / `NEEDS_REVISION` | Result state |
| `ref` | Conditional | GitHub reference | Human-readable reference when GitHub write occurred |
| `comment_id` | Conditional | numeric (database_id) | Only when a comment was posted. For reply-to / edit |

The `Summary` field is abolished. Instead, the **body's first line** is treated as the summary.

**Status → Action mapping:**

| Status | Action | Used By | Chain Behavior |
|--------|--------|---------|----------------|
| SUCCESS | CONTINUE | committing-on-issue, creating-pr-on-issue, coding-on-issue | Proceed to next step |
| FAIL | STOP | All subagent skills | Chain stop, report to user |
| NEEDS_REVISION | REVISE | reviewing-on-issue (plan review) | Enter revision loop |

Subagent outputs are internal processing data, not user-facing output. Presenting raw subagent output exposes technical intermediates that disrupt the user's workflow experience. Output only a one-line summary and immediately proceed to the next tool call.

#### Subagent Invocation Pattern

The following skills are launched via custom sub-agents (AGENT.md). `/simplify` continues to be launched via Skill tool.

| Skill | Sub-agent name |
|-------|---------------|
| `planning-on-issue` | `planning-worker` |
| `coding-on-issue` | `coding-worker` |
| `committing-on-issue` | `commit-worker` |
| `creating-pr-on-issue` | `pr-worker` |
| `reviewing-on-issue` | `review-worker` |
| `reviewing-claude-config` | `config-review-worker` |
| `researching-best-practices` | `research-worker` |

```text
Agent(
  description: "{worker-name} #{number}",
  subagent_type: "{worker-name}",
  prompt: "{args}"
)
```

Each sub-agent has the corresponding skill's full content auto-injected via the `skills` frontmatter field.

> **CRITICAL — Chain continuation after Agent tool returns**: When a custom sub-agent (e.g., `pr-worker`, `commit-worker`) completes and the Agent tool returns, **check TodoWrite for remaining `pending` steps**. If pending steps remain (work summary, status update, evolution), **immediately proceed to the next pending step in the same response**. Do NOT stop, summarize, or ask the user. The Agent tool returning is a chain mid-point, not a completion signal.

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

### Step 6: Evolution Signal Auto-Recording

After successful chain completion (skip on chain failure), auto-record Evolution signals detected during the session following the "Auto-Recording Procedure at Skill Completion" in the `rule-evolution` rule. This includes environment checks (lint metrics), as `working-on-issue` is a target skill for environment checks per the `rule-evolution` rule.

1. Self-review the session using the detection checklist (see `rule-evolution` rule)
2. Signals detected → Post comment to Evolution Issue → Display 1-line recording confirmation
3. No signals → Check for accumulated signals → Display reminder (fallback)

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
| Epic issue selected directly | See "Epic Issue Entry Point" below |

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

## Tool Usage

| Tool | When |
|------|------|
| AskUserQuestion | Requirement clarification, approach selection, edge cases (manager (main AI) pre-resolves) |
| TodoWrite | Chain step registration (required for all work) |
| Bash | Git operations, `shirokuma-docs issues` commands |

## Notes

- This skill is the **manager (the main-process AI agent)** — actual work is delegated to subagent workers
- Update issue status before starting
- Ensure correct feature branch
- TDD-applicable work types wrap `coding-on-issue` invocation with TDD ([docs/tdd-workflow.md](docs/tdd-workflow.md))
- Workflow executes sequentially (Commit → PR → Work Summary → Status Update). **Merge is NOT included**
- Chain execution stops on error and returns control to user
- **Chain autonomous progression**: Subagent outputs are intermediate chain data. Stopping after receiving one forces the user to manually prompt "continue", which defeats the purpose of an automated workflow chain. As long as TodoWrite has pending steps, immediately parse the YAML frontmatter and execute the next step's Agent/Bash tool call. Log a one-line summary and invoke the next tool in the same response
