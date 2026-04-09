---
name: prepare-flow
description: "Orchestrates the planning phase for an issue: status management, plan delegation to plan-issue, plan review, and user approval gate. Triggers: \"plan\", \"plan #42\", \"design approach\", \"create plan\"."
allowed-tools: Skill, Agent, Bash, AskUserQuestion, TaskCreate, TaskUpdate, TaskGet, TaskList
---

!`shirokuma-docs rules inject --scope orchestrator`

# Preparing on Issue (Orchestrator)

> **Chain Autonomous Progression**: After the plan review skill (review step) completes, immediately proceed to status update and user return. Stopping after the review skill forces the user to manually prompt continuation, breaking the planning workflow. Use the `**Review result:**` string to determine the review outcome and act without waiting for user input.

Orchestrate the planning phase for an issue: fetch the issue, manage status transitions, delegate plan creation to `plan-issue` (via Agent tool / `plan-worker`), conduct plan review, and return control to the user with a Review approval gate. **Does not proceed to implementation.**

## Task Registration (Required)

Register all chain steps via TaskCreate **before starting work**.

| # | content | activeForm | Skill |
|---|---------|------------|-------|
| 1 | Fetch issue and update status | Fetching issue and updating status | Manager direct: `shirokuma-docs items context/transition` |
| 2 | [Conditional] Conduct research | Conducting research | `researching-best-practices` (subagent: `research-worker`) |
| 3 | Create the plan | Creating the plan | `plan-issue` (subagent: `plan-worker`) |
| 4 | Review the plan | Reviewing the plan | `review-issue` (subagent: `review-worker`) |
| 5 | [Conditional] Fix review issues and re-review | Fixing review issues and re-reviewing | `plan-issue` (subagent: `plan-worker`) + `review-issue` (subagent: `review-worker`) |
| 4a | [Conditional] Create sub-issues for epic plan | Creating sub-issues | Manager direct: `shirokuma-docs items add issue/parent/update` |
| 6 | Update status and return plan summary to user | Updating status and returning plan summary to user | Manager direct: `shirokuma-docs items transition` |

Dependencies: step 2 blockedBy 1 (conditional: only when research trigger applies), step 3 blockedBy 1 or 2, step 4 blockedBy 3, step 5 blockedBy 4 (conditional: only on NEEDS_REVISION), step 4a blockedBy 4 or 5 (conditional: only for epic plans), step 6 blockedBy 4 or 5 or 4a.

Update each step to `in_progress` at start and `completed` on finish via TaskUpdate. Step 2 is skipped when no trigger applies. Task 5 (revision loop) is skipped on PASS (may be omitted from the task list).

## Workflow

### Step 1: Fetch Issue

```bash
shirokuma-docs items context {number}
# → Read .shirokuma/github/{org}/{repo}/issues/{number}/body.md
```

Review title, body, type, priority, size, labels, and comments.

### Step 1b: Set Status to In Progress + Assign

If the issue status is Backlog, transition to In Progress to record the planning start. Also auto-assign the user.

```bash
shirokuma-docs items transition {number} --to "In Progress"
# Assign the user
shirokuma-docs items update {number} --assign "@me"
```

Skip status update if already In Progress or Review. Assignee is idempotent, so always execute.

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

Check `subIssuesSummary` to see whether a child issue with a title starting with "Plan:" exists.

| Plan state | Action |
|-----------|--------|
| No plan issue | Proceed to Step 3 (delegate to plan-issue) |
| Plan issue exists | Ask whether to overwrite (AskUserQuestion) before proceeding |

#### Sub-issue reset path when non-plan sub-issues exist

When child issues with titles that do NOT start with "Plan:" exist (count > 0), ask the user before re-planning (AskUserQuestion):

- **Continue (re-plan keeping existing sub-issues)**: Update the plan document only; keep existing sub-issues.
- **Reset (cancel all sub-issues and re-plan)**: Execute the following:
  1. Cancel all non-plan sub-issues via `shirokuma-docs items transition {sub-number} --to Cancelled` for each
  2. Run `shirokuma-docs items integrity --fix` → parent transitions to Backlog automatically when all sub-issues are Cancelled
  3. Return to Step 1b to re-transition to In Progress, then proceed to Step 3 (plan-issue delegation)

### Step 3: Delegate to plan-worker

Invoke `plan-worker` via Agent tool to delegate plan creation to the `plan-issue` skill.

```text
Agent(
  description: "plan-worker plan #{number}",
  subagent_type: "plan-worker",
  prompt: "Create a plan for #{number}."
)
```

The plan-issue skill performs codebase investigation, creates the plan, creates a plan issue, posts a thinking process comment, and sets up the parent-child relationship.

#### Post-Completion Handling

If plan-worker completes successfully, proceed to Step 4 (plan review). If an error occurs, stop and report to the user.

### Step 3 delegation prompt note

When research was conducted (Step 2a), include the `## Research Findings (Reference)` section in the delegation prompt. When research was skipped, use the standard prompt (`Create a plan for #{number}.`).

### Step 4: Plan Review (Skill Delegation)

Reviewing in the same context that wrote the plan cannot catch blind spots. Delegate review to `review-issue` plan role via Agent tool (`review-worker`). Since the plan-issue skill creates a plan issue (child issue), the reviewer can identify the child issue with a title starting with "Plan:" from `subIssuesSummary` and fetch its body directly via `items context {plan-issue-number}`.

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

If all checks pass, proceed to Step 5.

#### Invoke the Reviewer

Invoke `review-worker` with plan role via the Agent tool. `review-issue` will fetch the Issue body itself via `shirokuma-docs items context {number}`.

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

> **Immediate Progression (Required)**: On PASS, **do NOT stop here** — proceed immediately to "On PASS" below → Step 5 → Step 6. Update the TodoList "plan review" task to `completed` before moving on. Ending with text-only output is a chain break error.

#### On PASS

> **Chain Autonomous Progression**: Once you reach this section, execute all actions (post comment → Step 5 → Step 6) **within the same response** without stopping. Do not pause for user input.

1. Post a **plan review response comment** (evidence that the review passed):

```bash
shirokuma-docs items add comment {number} --file /tmp/shirokuma-docs/{number}-review-pass.md
```

Where `/tmp/shirokuma-docs/{number}-review-pass.md` contains the plan review response (PASS result, fixes summary if any).

If PASS was reached after NEEDS_REVISION cycles, include revision details in the file:

```bash
shirokuma-docs items add comment {number} --file /tmp/shirokuma-docs/{number}-review-pass.md
```

→ Proceed to Step 4a (if epic plan) or Step 5.

### Step 4a: Auto-create Sub-issues (Epic Plans Only)

After review PASS, execute this step if the plan issue body contains a `### Sub-Issue Structure` section **and** no non-plan child issues exist (count of child issues with titles NOT starting with "Plan:" === 0). Skip and proceed to Step 5 if the condition is not met.

The plan issue number is found by scanning `subIssuesSummary` for a child issue with a title starting with "Plan:". Fetch its body via `items context {plan-issue-number}` to check for the `### Sub-Issue Structure` section.

#### Sub-issue Creation Procedure

1. Parse the `### Sub-Issue Structure` table and create each sub-issue:
   ```bash
   # Create the body file for each sub-issue
   cat > /tmp/shirokuma-docs/{parent-number}-sub-{n}.md <<'EOF'
   ---
   title: "{sub-issue title}"
   status: "Backlog"
   ---

   See #{parent-number} for full plan.
   EOF

   # Create the sub-issue
   shirokuma-docs items add issue --file /tmp/shirokuma-docs/{parent-number}-sub-{n}.md

   # Set parent-child relationship
   shirokuma-docs items parent {sub-number} {parent-number}
   ```

2. After all sub-issues are created, update the placeholders (`#{sub1}`, etc.) in the epic's `### Sub-Issue Structure` table with actual issue numbers and sync via `items update {parent-number} --body /tmp/shirokuma-docs/{parent-number}-body.md`.

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

### Step 5: Update Status (Issue → Review)

```bash
shirokuma-docs items transition {number} --to Review
```

### Step 6: Return to User

Display a plan summary and request approval. The plan is a contract with the user — proceeding without approval risks wasted work on a misaligned approach.

Show a summary matching the plan depth level. Follow the `completion-report-style` rule for formatting.

**Required fields** (all levels):
- **Status:** Review
- **Level:** plan depth (Lightweight / Standard / Detailed / Epic)
- **Approach:** one-line summary

**Additional fields** (Standard/Detailed/Epic):
- **Target files** and **Tasks** count (Standard/Detailed)
- **Sub-issues** count and **Integration branch** (Epic)
- **Plan issue:** Number of the created plan issue (all levels)
- **Created sub-issues:** List of created sub-issue numbers (Epic, when Step 4a executed)

**Next steps guidance** (vary by condition):

| Condition | Next steps |
|-----------|-----------|
| Normal (Lightweight / Standard / Detailed) | `/implement-flow #{plan number}` |
| Epic (non-plan sub-issues already created) | Guide each sub-issue number with `/implement-flow #{sub-number}` (creates integration branch, proposes order) |
| Epic (no non-plan sub-issues yet) | Guide each sub-issue number with `/implement-flow #{sub-number}` (creates sub-issues, integration branch, proposes order) |

> **Unified rule**: Always create a plan Issue regardless of plan level, and present `#{plan number}`. The Lightweight-without-plan-issue path is removed. Design guidance (`/design-flow`) is `create-item-flow`'s responsibility and must not appear in `prepare-flow` next steps.

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
| Child issue with title starting with "Plan:" already exists | Ask whether to overwrite (AskUserQuestion) before delegating |
| Issue is Done | Show warning |
| Issue body is empty | Proceed (planning worker will create the plan issue) |
| Status is already In Progress | Continue, skip status update |
| Status is already Review | Update plan issue, keep status |
| Epic issue (has non-plan sub-issues) | Planning worker uses epic plan template |

## Rule References

| Reference | Usage |
|-----------|-------|
| `project-items` rule | In Progress/Review status workflow |
| `output-language` rule | Output language for issue comments and body |
| `github-writing-style` rule | Bullet-point vs prose guidelines |
| `implement-flow` skill | Worker completion unified pattern, UCP check |

## Tool Usage

| Tool | When |
|------|------|
| Bash | `shirokuma-docs items context/transition/update/add comment` |
| Agent (research-worker) | Step 2a: Conduct research (conditional, subagent, context isolation) |
| Agent (plan-worker) | Step 3: Delegate plan creation (sub-agent, context isolation) |
| Agent (review-worker) | Step 4: Plan review (subagent, context isolation) |
| AskUserQuestion | Overwrite confirmation, issue number prompt |
| TaskCreate, TaskUpdate | Planning orchestration step progress tracking |

## Notes

- This skill is the **orchestrator** — actual plan creation is delegated to `plan-worker` (`plan-issue` skill) via Agent tool
- **Does not implement** — planning only. Implementation is `implement-flow`'s responsibility
- Plans are persisted as plan issues (child issues) — available across sessions
- `Review` is the user approval gate — self-approving would bypass the human quality check that catches misaligned assumptions early
- **Chain autonomous progression**: After the review skill (Step 4) completes, stopping forces the user to manually prompt continuation. Immediately proceed to Steps 5-6 based on the `**Review result:**` string. Check TaskList for remaining pending steps after each skill result
