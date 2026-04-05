---
name: implement-flow
description: Dispatches work by taking an issue number or task description, selecting the appropriate skill, and orchestrating the full workflow from implementation to PR. Triggers: "work on", "work on #42", "do this", "start working".
allowed-tools: Bash, Read, Grep, Glob, Skill, AskUserQuestion, TaskCreate, TaskUpdate, TaskGet, TaskList
---

!`shirokuma-docs rules inject --scope orchestrator`

# Working on Issue (Orchestrator)

> **Chain Autonomous Progression (MOST IMPORTANT RULE)**: When a Skill tool or Agent tool completes, you **MUST invoke the next tool in the same response**. This is the single most important rule of this orchestrator. Generating a text-only response while TaskList has pending steps is a chain-breaking error that forces the user to manually type "continue".

Orchestrate the full workflow from planning to implementation, commit, and PR based on issue type or task description.

**Note**: For session setup, use `starting-session`. This skill works both within a session and standalone (without `starting-session`). It is the primary entry point for working on a specific task in either mode.

## Task Registration (Required)

Register **all chain steps** via TaskCreate **before starting work**.

**Implementation / Bug Fix / Refactoring / Chore:**

| # | content | activeForm | Skill |
|---|---------|------------|-------|
| 1 | Implement changes | Implementing changes | `code-issue` (subagent: `coding-worker`) |
| 2 | Commit and push changes | Committing and pushing | `commit-issue` (subagent) |
| 3 | Create pull request | Creating pull request | `open-pr-issue` (subagent) |
| 4 | Simplify and improve code | Improving code | `/simplify` (Skill tool) |
| 5 | Run security review | Running security review | `reviewing-security` (Skill tool) |
| 6 | Post work summary | Posting work summary | Manager direct: `items add comment` |
| 7 | Update Status to Review | Updating Status to Review | Manager direct: `items push` |

Dependencies: step 2 blockedBy 1, step 3 blockedBy 2, step 4 blockedBy 3, step 5 blockedBy 4, step 6 blockedBy 5, step 7 blockedBy 6.

**Research:**

| # | content | activeForm | Skill |
|---|---------|------------|-------|
| 1 | Conduct research | Conducting research | `researching-best-practices` (subagent) |
| 2 | Save findings to Discussion | Creating Discussion | `shirokuma-docs items add discussion` |

Dependencies: step 2 blockedBy 1.

Use TaskUpdate to set each step to `in_progress` when starting and `completed` when done.

## Workflow

### Step 1: Analyze Work

#### Plan Issue Auto-Resolution (Step 1 Pre-processing)

When the received issue title starts with "Plan: " or "計画: ", treat it as a plan issue and auto-redirect to the parent issue:

1. Check the `parent` field from the cache frontmatter
2. If `parent` is set → run `items pull` with the parent issue number, and continue the flow using the parent issue number (the plan issue number is only used for plan context reference)
3. If `parent` is not set → re-fetch via `items pull {number}` to check for `parent`
4. If `parent` is still unknown → display error message and stop:
   "Cannot determine parent issue for plan issue #{number}. Please specify the parent issue number directly."

**Issue number provided**: `shirokuma-docs items pull {number}` to fetch and cache, then read `.shirokuma/github/{org}/{repo}/issues/{number}/body.md` to extract title/body/labels/status/priority/size.

#### Sub-Issue Detection

When `.shirokuma/github/{org}/{repo}/issues/{number}/body.md` frontmatter contains a `parentIssue` field, the issue is a sub-issue of an epic:

1. Identify the plan issue (child issue with a title starting with "Plan:" or "計画:") from the parent's `subIssuesSummary`, fetch it via `items pull {plan-issue-number}`, and use its body as overall context
2. Set base branch to the parent's integration branch instead of `develop` (Step 3)
3. `open-pr-issue` will self-detect the sub-issue via the `parentIssue` field, so explicit context passing is not required (if passed, it is used as supplementary; otherwise, self-detection is the fallback)

```bash
# Check parent issue
shirokuma-docs items pull {parent-number}
# → Read .shirokuma/github/{org}/{repo}/issues/{parent-number}/body.md
# Identify child issue with title starting with "Plan:" from subIssuesSummary
shirokuma-docs items pull {plan-issue-number}
# → Fetch plan body and use as context
```

#### Plan Check (when issue number provided)

Check `subIssuesSummary` for a child issue with a title starting with "Plan:" or "計画:".

| Plan State | Condition | Action |
|-----------|-----------|--------|
| — | Review / Ready status | → Status priority path (follow flow below) |
| No plan issue | Size XS/S (clear requirements) and not a sub-issue, and not Review / Ready | → Skip planning, proceed directly to `code-issue` |
| No plan issue | Size M+ or ambiguous requirements | → Delegate to `prepare-flow` |
| No plan issue | Sub-issue (`parentIssue` present) | → Delegate to `prepare-flow` regardless of size |
| Plan issue exists | — | → Fetch plan issue body via `items pull {plan-issue-number}` and pass as context to implementation skill |

#### Review / Ready Status Priority Path

Review / Ready status is an explicit signal that planning is complete. It takes priority over Size-based determination regardless of issue size. Decision flow:

```
Review / Ready status
  → Check for plan issue (child issue with title starting "Plan:" in subIssuesSummary)
    exists → Fetch plan issue body and use as context (same as normal path)
    none → Anomaly: status is Review/Ready but no plan found
           → Display warning message, fall back to Size-based determination
```

Warning message example for anomaly fallback: "⚠️ Status is Review but no plan issue was found. Falling back to Size-based determination."

#### Fetching Plan Details

When a plan issue exists (new approach):

```bash
shirokuma-docs items pull {plan-issue-number}
# → Read .shirokuma/github/{org}/{repo}/issues/{plan-issue-number}/body.md to get plan content
```

**XS/S direct implementation path criteria:** Apply when the Issue Size field is XS or S, and the title and body clearly indicate what needs to be changed (mechanical transformation such as pattern replacement, type fix, rename). Sub-issues (`parentIssue` field present) always require a plan regardless of size. Additionally, issues with Review or Ready status are excluded from this path (the status priority path is evaluated first). If Size is unset, requirements are ambiguous, the issue is a sub-issue, or judgment is uncertain, delegate to `prepare-flow`. See the `creating-item` skill "Requirements Clarity Criteria" for the canonical definition.

#### Transition from Preparing Status

| Plan state | Action |
|-----------|--------|
| Preparing + no plan | → Delegate to `prepare-flow` |
| Preparing + plan exists | → Transition to Review, ask user approval |

**Text description only**: Classify using dispatch condition table (Step 4) keywords.

### Step 1a: Issue Resolution (text description only)

When called with text only, delegate to `creating-item` skill to ensure an issue exists.

```text
Text description → creating-item → Issue number → Join Step 1
```

### Step 2: Update Status

If issue is not already In Progress: edit cache frontmatter `status: "In Progress"` then `shirokuma-docs items push {number}`

**Review / Ready implicit approval**: Invoking `/implement-flow` from Review or Ready is implicit plan approval. Transition to In Progress without confirmation.

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

### Step 3c: Detect Local Documentation (coding tasks only)

For coding-type tasks (implementation, bug fix, refactoring), detect available local documentation before invoking `code-issue`:

```bash
shirokuma-docs docs detect --format json
```

Collect sources with `status: "ready"` from the output and include them in the Agent tool prompt:

```text
Documentation sources (status: ready):
- nextjs16: packages=[next]
- tailwindcss: packages=[tailwindcss]

Use `shirokuma-docs docs search "<keyword>" --source <name> --section --limit 5` to search during implementation.
```

Omit this section if no sources have `status: "ready"`. Skip this step for non-coding tasks (research, review, setup).

### Step 4: Select and Execute Skill

#### Dispatch Condition Table

| Work Type | Condition | Delegate To | TDD |
|-----------|-----------|-------------|-----|
| General Coding | Implementation, bug fix, refactoring, config, Markdown editing | `code-issue` (subagent: `coding-worker`) | Yes (implementation, bug fix, refactoring) |
| Research | Keywords: `research`, `investigate` | `researching-best-practices` (subagent) | No |
| Review | Keywords: `review`, `audit` | `review-issue` (subagent: `review-worker`) | No |
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
| General Coding | Work → Commit → PR → /simplify → reviewing-security → Work Summary → Status Update |
| Research | Research → Discussion |
| Review | Review → Report posted → Complete (no commit/PR chain) |

- **Merge is NOT part of the chain**
- No confirmation between steps, one-line progress reports
- On failure: stop chain, report status, return control to user

**Chain completion guarantee**: After each skill/subagent completes, the manager (main AI) **immediately proceeds to the next step**. The Status Update at the end of the chain is executed directly by the manager (not via subagent), eliminating the risk of chain interruption.

**Skill tool vs Agent tool completion patterns:**

| Invocation Method | Completion Handling |
|-------------------|-------------------|
| Skill tool (`reviewing-claude-config`, etc.) | Completes in main context. Proceed to next step if no errors. No YAML parsing needed |
| Agent tool (`commit-worker`, `pr-worker`) | Parse YAML frontmatter for `action` field: `CONTINUE` → next step, `STOP` → halt (see [reference/worker-completion-pattern.md](reference/worker-completion-pattern.md)) |

**Agent tool output parse checkpoint** — On receiving Agent tool (subagent) output:

1. Read `action` from YAML frontmatter
2. `action: CONTINUE` → **immediately** invoke the skill in the `next` field **in the same response** (output only a one-line summary from the body's first line)
3. `action: STOP` / `REVISE` → stop chain, report to user

Exception: If `ucp_required: true` or `suggestions_count > 0`, present to user via AskUserQuestion before continuing.

**The core rule: when a skill or subagent completes, respond with a tool call, not text output.**

**Tasks continuation invariant**: After each skill/subagent completes, check TaskList. If any step is still `pending`, you MUST invoke the next tool call in the same response — generating a final text-only response while pending steps remain is a chain-breaking error.

See [reference/chain-execution.md](reference/chain-execution.md) for the full chain delegation table, pseudocode, and Agent tool structured data field definitions.

#### Skill and Subagent Invocation Pattern

Skills are invoked via Skill tool (main context) or Agent tool (subagent). Skills benefiting from context isolation run as subagents to prevent main context bloat. Rules are injected into sub-agents via `` `shirokuma-docs rules inject --scope {worker}` `` in each worker skill.

| Skill | Invocation | Reason |
|-------|-----------|--------|
| `code-issue` | Agent (`coding-worker`) | Context isolation (implementation work bloats main context) |
| `/simplify` | Skill tool | Claude Code built-in skill, runs in main context |
| `reviewing-security` | Skill tool | Wraps `!claude -p '/security-review'`. **Do NOT substitute with `review-issue`. Do NOT invoke via Agent tool** |
| `review-issue` | Agent (`review-worker`) | Context isolation + opus model selection |
| `reviewing-claude-config` | Skill tool | Needs project rules for quality standards, relatively lightweight |
| `commit-issue` | Agent (`commit-worker`) | Git operations only |
| `open-pr-issue` | Agent (`pr-worker`) | GitHub operations only |
| `researching-best-practices` | Agent (`research-worker`) | External research |

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

**⚠️ The `pr-worker` prompt MUST include the issue number:**

```text
Agent(
  description: "pr-worker #{issue-number}",
  subagent_type: "pr-worker",
  prompt: "#{issue-number}"
)
```

`open-pr-issue` includes `Closes #{issue-number}` in the PR body when launched with an issue number, linking the PR to the issue. **If the issue number is omitted, `Closes` is skipped and the PR will not be linked to the issue.**

> **CRITICAL — Chain continuation after Skill tool / Agent tool returns**: When a Skill tool (`/simplify`, `reviewing-security`, etc.) or sub-agent (`pr-worker`, `commit-worker`, etc.) completes, **check TaskList for remaining `pending` steps**. If pending steps remain (commit, PR creation, work summary, status update), **immediately proceed to the next pending step in the same response**. Do NOT stop, summarize, or ask the user. A Skill tool or Agent tool returning is a chain mid-point, not a completion signal. The PR → `/simplify` → `reviewing-security` transition is particularly prone to chain breaks — pay extra attention.

#### Work Summary (Issue Comment)

After PR creation, post a technical work summary to the Issue as a comment. This is the primary context record referenced in future conversations for Issue context.

The work summary focuses on **technical work details** — what was changed, which files were modified, and technical decisions made.

```bash
shirokuma-docs items add comment {number} --file /tmp/shirokuma-docs/{number}-work-summary.md
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

**Standalone completion**: When `implement-flow` completes its chain (standalone or within a session), the Work Summary is automatically posted.

#### Status Update (End of Chain)

**IMPORTANT**: Do NOT update Status to Review at PR creation time. The `/simplify` and `/security-review` review steps must complete first. Update Status only after work summary is posted.

Update Status to Review for issues with a number:

```bash
shirokuma-docs items push {number}
```

(Cache frontmatter `status` should be set to `"Review"` before push.)

**Status fallback verification**: After chain completion, read `.shirokuma/github/{org}/{repo}/issues/{number}/body.md` frontmatter to check status. If still In Progress → edit cache frontmatter `status: "Review"` and `shirokuma-docs items push {number}` (idempotent: re-updating to Review when already Review is harmless).

#### Plan Issue Done Update (End of Chain)

After the Status update, update the plan issue to Done if one exists.

**Top-level issue case** (no parent issue):
Identify the plan issue from the `subIssuesSummary` of the issue fetched in Step 1 — look for a child issue whose title starts with "Plan:" or "計画:".

**Sub-issue case** (has a parent issue):
Re-run `shirokuma-docs items pull {parent-number}` at the end of the chain to get the latest `subIssuesSummary` (other sub-issue statuses may have changed during chain execution). Look for a sibling issue whose title starts with "Plan:" or "計画:".

**Epic case** (parent issue has multiple work sub-issues):
Similarly, re-fetch the parent issue at the end of the chain to use the latest `subIssuesSummary`. Only update the plan issue to Done if all work sub-issues (excluding the plan issue itself) have a status of Done or Not Planned. If any work sub-issue remains in another status, skip the update.

**Plan issue update procedure**:

```bash
# 1. Pull plan issue cache (skip if already cached from Step 1)
shirokuma-docs items pull {plan-number}

# 2. Edit frontmatter status to "Done" in the cache file
# .shirokuma/github/{org}/{repo}/issues/{plan-number}/body.md — use Edit tool

# 3. Push to reflect on GitHub
shirokuma-docs items push {plan-number}
```

- **Skip pull when already cached**: In the top-level case, the plan issue was already fetched in Step 1 — go directly to step 2 (edit frontmatter) and step 3 (push). The sub-issue/epic cases require the pull since the plan issue was not fetched earlier.
- **Plan issue not found**: Silent skip (no warning). Covers cases like XS/S direct implementation path where no plan issue exists.
- **Idempotent**: Re-updating to Done when already Done is harmless.

#### Next Steps Suggestion (End of Chain)

After Status update, present next action candidates to the user. Extract the PR number from `open-pr-issue`'s output to provide specific guidance. If the PR number is unavailable (e.g., PR not created), omit the `/review-flow` line.

```
## Next Steps

- `/review-flow #{pr-number}` — Run self-review on the PR
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
2. The issue status is **Review** or **Ready**
3. A plan issue (child issue with title starting with "Plan:" or "計画:") exists

If any precondition is not met, display an error message and stop (no fallback to normal mode).

> **Note:** Issues with statuses other than Review / Ready (e.g., In Progress, Preparing, Backlog) will also stop with a precondition error when `--headless` is specified. Issues in Preparing status require interactive planning via `prepare-flow` and are therefore excluded from headless mode.

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
claude -p "/implement-flow --headless #42"

# Skip confirmations within interactive session
/implement-flow #42 --headless
```

## Edge Cases

| Situation | Action |
|-----------|--------|
| Issue not found | AskUserQuestion for number |
| Issue Done/Released | Warn, confirm reopen |
| Already In Progress | Continue without status change |
| Wrong branch | AskUserQuestion: switch or continue |
| Chain failure | Report completed/remaining steps, return control. See "Chain Recovery Procedure" below |
| Issue was reverted (after PR revert) | After merging revert PR, move original issue back to Backlog and re-implement on a new branch. See "Recovery after PR Revert" below |
| Sub-issue with no integration branch | Use `develop` as base, warn user |
| Epic issue selected directly | Check for non-plan child issues; see "Epic Issue Entry Point" below |
| `--headless` + precondition not met | Display error message and stop |
| `--headless` + wrong branch (W4) | Warn and stop (no auto-switch) |
| `--headless` + worker UCP (W5) | Skip and record in Issue comment |

### Recovery after PR Revert

When a revert is required after a PR has been merged (issue is Done):

1. Create and merge a revert PR (via GitHub UI or `git revert`)
2. Manually update the original issue status to `Backlog` (re-implement) or `Not Planned` (cancelled)
3. If re-implementing, run `/implement-flow #{number}` in a new conversation (a new branch will be created)

> Revert is a manual operation and is not part of the `implement-flow` chain.

### Chain Recovery Procedure

If the `implement-flow` chain stops mid-way (network error, session disconnect, etc.), run the same `/implement-flow #{number}` again in a new conversation. The following idempotency guarantees allow safe resumption:

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

## Epic Issue Entry Point

When an epic issue is directly specified (detected by non-plan child issues existing, or a plan issue whose body contains a `### Sub-Issue Structure` section), execute the following flow instead of standard implementation dispatch.

### Pre-condition: Plan Issue with Sub-Issue Structure

The epic must have a plan issue (child issue with title starting with "Plan:" or "計画:") whose body contains a `### Sub-Issue Structure` section. If no plan issue exists, delegate to `prepare-flow` first (standard flow).

### Epic Workflow

1. **Create integration branch**: Extract branch name from `### Integration Branch` in the plan, create from `develop`:
   ```bash
   git checkout develop && git pull origin develop
   git checkout -b epic/{number}-{slug}
   git push -u origin epic/{number}-{slug}
   ```

   | Condition | Step 2 |
   |-----------|--------|
   | No non-plan child issues exist | Create sub-issues |
   | Non-plan child issues already exist | Skip (already created by `prepare-flow`) |

2. **Create sub-issues in batch** (only when no non-plan child issues exist): Skip this step if sub-issues were already created by `prepare-flow`. Parse the `### Sub-Issue Structure` table from the plan issue body. For each row, create a sub-issue via CLI:
   ```bash
   shirokuma-docs items add issue --file /tmp/shirokuma-docs/{slug}.md
   ```
   Body: Minimal stub referencing the parent plan (`See #{epic-number} for full plan`).
   After creation, update the plan issue's `### Sub-Issue Structure` table placeholders (`#{sub1}`, etc.) with actual issue numbers and sync via `items push {plan-issue-number}`.

3. **Present execution order**: Based on the `### Execution Order` section or dependency column, display the recommended order and end. Do NOT propose immediate work start — each sub-issue should be worked on in a separate conversation per the epic pattern in `best-practices-first`:
   ```
   Epic setup complete.

   **Integration branch:** `epic/{number}-{slug}`
   **Sub-issues created:** #{sub1}, #{sub2}, #{sub3}

   Recommended execution order:
   1. #{sub1} - {title} (no dependencies)
   2. #{sub2} - {title} (depends on #{sub1})
   3. #{sub3} - {title} (depends on #{sub2})

   Start each sub-issue in a new conversation with `/implement-flow #{sub}`.
   ```

### Responsibility Note

Sub-issue creation in this flow uses `shirokuma-docs items add issue` directly (not `creating-item`). The plan already specifies sub-issue details, so `creating-item`'s inference logic is unnecessary.

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
| Bash | Git operations, `shirokuma-docs items` commands |

## Notes

- This skill is the **manager (the main-process AI agent)** — work is delegated via Agent tool (coding-worker, review-worker, commit-worker, pr-worker, research-worker) or Skill tool (reviewing-claude-config)
- Update issue status before starting
- Ensure correct feature branch
- TDD-applicable work types wrap `code-issue` invocation with TDD ([docs/tdd-workflow.md](docs/tdd-workflow.md))
- Workflow executes sequentially (Commit → PR → Work Summary → Status Update). **Merge is NOT included**
- Chain execution stops on error and returns control to user
- **Chain autonomous progression (MOST IMPORTANT)**: When a Skill tool or Agent tool completes, respond with a tool call, not text output. As long as TaskList has pending steps, invoke the next Skill/Agent tool in the same response. The `open-pr-issue` → manager steps transition is the most common break point — immediately execute Work Summary → Status Update via Bash
