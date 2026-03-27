---
name: prepare-flow
description: "Orchestrates the planning phase for an issue: status management, plan delegation to plan-issue, plan review, and user approval gate. Triggers: \"plan\", \"plan #42\", \"design approach\", \"create plan\"."
allowed-tools: Skill, Agent, Bash, AskUserQuestion, TaskCreate, TaskUpdate, TaskGet, TaskList
---

!`shirokuma-docs rules inject --scope orchestrator`

# Preparing on Issue (Orchestrator)

> **Chain Autonomous Progression**: After the plan review skill (review step) completes, immediately proceed to status update and user return. Stopping after the review skill forces the user to manually prompt continuation, breaking the planning workflow. Use the `**Review result:**` string to determine the review outcome and act without waiting for user input.

Orchestrate the planning phase for an issue: fetch the issue, manage status transitions, delegate plan creation to `plan-issue` (via Agent tool / `plan-worker`), conduct plan review, and return control to the user with a Spec Review approval gate. **Does not proceed to implementation.**

## Task Registration (Required)

Register all chain steps via TaskCreate **before starting work**.

| # | content | activeForm | Skill |
|---|---------|------------|-------|
| 1 | Fetch issue and update status | Fetching issue and updating status | Manager direct: `shirokuma-docs show/update` |
| 2 | [Conditional] Conduct research | Conducting research | `researching-best-practices` (subagent: `research-worker`) |
| 3 | Create the plan | Creating the plan | `plan-issue` (subagent: `plan-worker`) |
| 4 | Review the plan | Reviewing the plan | `review-issue` (subagent: `review-worker`) |
| 5 | [Conditional] Fix review issues and re-review | Fixing review issues and re-reviewing | `plan-issue` (subagent: `plan-worker`) + `review-issue` (subagent: `review-worker`) |
| 6 | Assess design phase need and update status | Assessing design phase need and updating status | Manager direct: `shirokuma-docs items push` |
| 7 | Return plan summary to user | Returning plan summary to user | Manager direct |

Dependencies: step 2 blockedBy 1 (conditional: only when research trigger applies), step 3 blockedBy 1 or 2, step 4 blockedBy 3, step 5 blockedBy 4 (conditional: only on NEEDS_REVISION), step 6 blockedBy 4 or 5, step 7 blockedBy 6.

Update each step to `in_progress` at start and `completed` on finish via TaskUpdate. Step 2 is skipped when no trigger applies. Step 5 is skipped on PASS (may be omitted from the task list).

## Workflow

### Step 1: Fetch Issue

```bash
shirokuma-docs show {number}
```

Review title, body, type, priority, size, labels, and comments.

### Step 1b: Set Status to Preparing + Assign

If the issue status is Backlog, transition to Preparing to record the planning start. Also auto-assign the user.

```bash
shirokuma-docs items pull {number}
# Edit cache frontmatter: status: "Preparing"
shirokuma-docs items push {number}
```

Skip status update if already Preparing or Spec Review. Assignee is idempotent, so always execute.

### Step 2: Research Trigger Assessment (Conditional)

Assess the need for research from the issue title, body, labels, and type using the following heuristics.

#### Research Trigger Conditions (research runs if any one condition is met)

| Condition Category | Assessment Criteria |
|-------------------|---------------------|
| New / unknown library | Issue mentions an external library or technology with no existing usage in the codebase |
| Architecture change | Keywords: `architecture`, `redesign`, `rearchitecture`, `architectural change` |
| Security-related | Keywords: `auth`, `authorization`, `security`, `vulnerability`, `authentication` |
| Performance optimization | Keywords: `performance`, `optimization`, `bottleneck` |
| External API integration | Keywords: `API integration`, `webhook`, `external service`, `external API` |
| Explicit best-practice request | Issue body contains requests like "research best practices", "how should I implement" |

#### Post-Assessment Action

| Result | Action |
|--------|--------|
| No trigger | Proceed to Step 2b (pre-delegation check, research skipped) |
| Trigger applies | Proceed to Step 2a (conduct research) |

> **Reducing false positives**: The keyword list is intentionally conservative. Simple feature additions, bug fixes, and documentation edits normally do not trigger research. When in doubt, default to skipping.

### Step 2a: Conduct Research (Conditional)

When a research trigger applies, delegate to `researching-best-practices` via `research-worker`.

```text
Agent(
  description: "research-worker #{number}",
  subagent_type: "research-worker",
  prompt: "Conduct research needed to plan #{number}. Issue: {title}. Topics to investigate: {specific topics matching the trigger}."
)
```

After research completes, include the findings (recommended patterns, constraints, alternatives) in the `plan-issue` delegation prompt in Step 3.

Pass research results to the `plan-issue` prompt using this format:

```
Create a plan for #{number}.

## Research Findings (Reference)
{research-worker output: official recommendations, project patterns, recommendations summary}
```

If research-worker errors, log a warning, skip research, and proceed to Step 3 (plan creation without research).

### Step 2b: Pre-delegation Checks

#### Existing Plan Check

Check if issue body contains `## Plan` section (detected by `^## Plan` line prefix).

| Plan state | Action |
|-----------|--------|
| No plan | Proceed to Step 3 (delegate to plan-issue) |
| Plan exists | Ask whether to overwrite (AskUserQuestion) before proceeding |

### Step 3: Delegate to plan-worker

Invoke `plan-worker` via Agent tool to delegate plan creation to the `plan-issue` skill.

```text
Agent(
  description: "plan-worker plan #{number}",
  subagent_type: "plan-worker",
  prompt: "Create a plan for #{number}."
)
```

The plan-issue skill performs codebase investigation, creates the plan, posts a thinking process comment, and writes the plan to the issue body.

#### Post-Completion Handling

If plan-worker completes successfully, proceed to Step 5 (plan review). If an error occurs, stop and report to the user.

### Step 3 delegation prompt note

When research was conducted (Step 2a), include the `## Research Findings (Reference)` section in the delegation prompt. When research was skipped, use the standard prompt (`Create a plan for #{number}.`).

### Step 5: Plan Review (Skill Delegation)

Reviewing in the same context that wrote the plan cannot catch blind spots. Delegate review to `review-issue` plan role via Agent tool (`review-worker`). Since the plan-issue skill writes a summary link to the Issue body and posts plan details as a comment, the reviewer can access the detailed plan from the link in the body.

#### Skill Availability Check (Fallback)

Before launching the review, verify that `review-issue` is available in the skill list.

| State | Action |
|-------|--------|
| Skill available | Proceed to "Invoke the Reviewer" below |
| Skill unavailable | Use "Fallback (self-check)" instead |

**Fallback (self-check)**: When `review-issue` is unavailable, verify plan quality using this checklist:
- [ ] Does the plan address all requirements in the Issue?
- [ ] Are there any missing tasks?
- [ ] Is the deliverable (definition of done) clearly defined?
- [ ] Are risks/concerns identified (for complex Issues)?

If all checks pass, proceed to Step 6.

#### Invoke the Reviewer

Invoke `review-worker` with plan role via the Agent tool. `review-issue` will fetch the Issue body itself via `shirokuma-docs show {number}`.

```text
Agent(
  description: "review-worker plan #{number}",
  subagent_type: "review-worker",
  prompt: "plan #{number}"
)
```

The review result is posted as an Issue comment by `review-issue`, and structured output is returned.

#### Processing Review Output

| Output Status | Action |
|--------|--------|
| PASS | Follow "On PASS" below |
| NEEDS_REVISION | Follow "On Failure" below to fix and re-review |

#### Review Result Determination

Determine the result from the `**Review result:**` string in review-worker's output. Scan the Agent tool output body for `**Review result:** PASS` or `**Review result:** NEEDS_REVISION`.

| Result String | Action |
|--------------|--------|
| `**Review result:** PASS` | Follow "On PASS" below |
| `**Review result:** NEEDS_REVISION` | Follow "On Failure" below |

> **Immediate Progression (Required)**: On PASS, **do NOT stop here** — proceed immediately to "On PASS" below → Step 6 → Step 7. Update the TodoList "plan review" task to `completed` before moving on. Ending with text-only output is a chain break error.

#### On PASS

> **Chain Autonomous Progression**: Once you reach this section, execute all actions (post comment → Step 6 → Step 7) **within the same response** without stopping. Do not pause for user input.

1. Post a **plan review response comment** (evidence that the review passed):

```bash
shirokuma-docs items add comment {number} --file /tmp/shirokuma-docs/{number}-review-pass.md
```

Where `/tmp/shirokuma-docs/{number}-review-pass.md` contains the plan review response (PASS result, fixes summary if any).

If PASS was reached after NEEDS_REVISION cycles, include revision details in the file:

```bash
shirokuma-docs items add comment {number} --file /tmp/shirokuma-docs/{number}-review-pass.md
```

#### On Failure

When NEEDS_REVISION is returned:

1. Classify issues from subagent output `### Detail` into **[Plan]** and **[Issue description]**
2. **[Issue description]** issues → Fix the relevant sections in the issue body (overview, background, tasks, etc.)
3. **[Plan]** issues → Re-delegate to `plan-issue` with revision instructions, or fix the plan section directly and update the `## Plan` section in the Issue body
4. After fixes, re-run the review via Agent tool (same `review-worker` plan role)
5. **Max retries: 2** (initial review + up to 2 fix-and-review cycles)
6. On 3rd NEEDS_REVISION → Stop the loop, report to user for their judgment

```
plan-issue → Plan written to body
  → Agent(review-worker plan)
    → NEEDS_REVISION → Fix + Update body → Re-review
                         ↓ (failed twice)
                    Report to user
    → PASS → Response comment
```

### Step 6: Design Phase Assessment (Before Status Transition)

Analyze the plan content to determine whether a design phase is needed. The assessment result determines the target status.

| Condition | Decision |
|-----------|----------|
| Plan contains UI/frontend design section | Design phase needed |
| Issue has `area:frontend` label | Design phase needed |
| Plan contains keywords: `UI design`, `screen design`, `schema design`, `data model design` | Design phase needed |
| None of the above | No design phase needed |

### Step 6a: Update Status (Based on Assessment)

| Assessment Result | Status Transition | Rationale |
|-------------------|------------------|-----------|
| No design phase needed | → Spec Review | Ready for direct implementation |
| Design phase needed | → Designing | Guide user to run `design-flow` |

```bash
# When no design phase needed: edit cache frontmatter status: "Spec Review"
shirokuma-docs items push {number}

# When design phase needed: edit cache frontmatter status: "Designing"
shirokuma-docs items push {number}
```

### Step 7: Return to User

Display a plan summary and request approval. The plan is a contract with the user — proceeding without approval risks wasted work on a misaligned approach.

Show a summary matching the plan depth level and design phase assessment. Follow the `completion-report-style` rule for formatting.

**Required fields** (all levels):
- **Status:** current status (Spec Review or Designing)
- **Level:** plan depth (Lightweight / Standard / Detailed / Epic)
- **Approach:** one-line summary

**Additional fields** (Standard/Detailed/Epic):
- **Target files** and **Tasks** count (Standard/Detailed)
- **Design phase** indicator when design is needed
- **Sub-issues** count and **Integration branch** (Epic)

**Next steps guidance** (vary by condition):

| Condition | Next steps |
|-----------|-----------|
| Lightweight / Standard without design | `/implement-flow #{number}` |
| Standard/Detailed with design needed | `/design-flow #{number}` (recommended) or `/implement-flow #{number}` (skip design) |
| Epic | `/implement-flow #{number}` (creates sub-issues, integration branch, proposes order) |

Always ask the user to review the plan and provide feedback if changes are needed.

#### Evolution Signal Auto-Recording

At the end of the plan completion report, auto-record Evolution signals following the "Auto-Recording Procedure at Skill Completion" in the `rule-evolution` rule.

## Arguments

| Format | Example | Behavior |
|--------|---------|----------|
| Issue number | `#42` | Fetch issue and start planning orchestration |
| No argument | — | Ask for issue number via AskUserQuestion |

## Edge Cases

| Situation | Action |
|-----------|--------|
| `## Plan` section already exists | Ask whether to overwrite (AskUserQuestion) before delegating |
| Issue is Done/Released | Show warning |
| Issue body is empty | Proceed (planning worker will create body with plan) |
| Status is already Preparing | Continue, skip status update |
| Status is already Spec Review | Update plan, keep status |
| Epic issue (has sub-issues) | Planning worker uses epic plan template |

## Rule References

| Reference | Usage |
|-----------|-------|
| `project-items` rule | Preparing/Designing/Spec Review status workflow |
| `output-language` rule | Output language for issue comments and body |
| `github-writing-style` rule | Bullet-point vs prose guidelines |
| `implement-flow` skill | Worker completion unified pattern, UCP check |

## Tool Usage

| Tool | When |
|------|------|
| Bash | `shirokuma-docs show/update/issues comment` |
| Agent (research-worker) | Step 2a: Conduct research (conditional, subagent, context isolation) |
| Agent (plan-worker) | Step 3: Delegate plan creation (sub-agent, context isolation) |
| Agent (review-worker) | Step 5: Plan review (subagent, context isolation) |
| AskUserQuestion | Overwrite confirmation, issue number prompt |
| TaskCreate, TaskUpdate | Planning orchestration step progress tracking |

## Notes

- This skill is the **orchestrator** — actual plan creation is delegated to `plan-worker` (`plan-issue` skill) via Agent tool
- **Does not implement** — planning only. Implementation is `implement-flow`'s responsibility
- Plans are persisted in the issue body — available across sessions
- `Spec Review` is the user approval gate — self-approving would bypass the human quality check that catches misaligned assumptions early
- **Chain autonomous progression**: After the review skill (Step 5) completes, stopping forces the user to manually prompt continuation. Immediately proceed to Steps 6-7 based on the `**Review result:**` string. Check TaskList for remaining pending steps after each skill result
