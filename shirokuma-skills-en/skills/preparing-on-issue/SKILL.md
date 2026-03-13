---
name: preparing-on-issue
description: "Orchestrates the planning phase for an issue: status management, plan delegation to planning-worker, plan review, and user approval gate. Triggers: \"plan\", \"plan #42\", \"design approach\", \"create plan\"."
allowed-tools: Agent, Bash, AskUserQuestion, TodoWrite
---

# Preparing on Issue (Orchestrator)

> **Chain Autonomous Progression**: After the plan review subagent (review step) returns its result, immediately proceed to status update and user return. Stopping after the review subagent forces the user to manually prompt continuation, breaking the planning workflow. Parse the YAML frontmatter `action` field and act without waiting for user input.

Orchestrate the planning phase for an issue: fetch the issue, manage status transitions, delegate plan creation to `planning-worker`, conduct plan review, and return control to the user with a Spec Review approval gate. **Does not proceed to implementation.**

## Workflow

### Step 1: Fetch Issue

```bash
shirokuma-docs show {number}
```

Review title, body, type, priority, size, labels, and comments.

### Step 1b: Set Status to Preparing + Assign

If the issue status is Backlog, transition to Preparing to record the planning start. Also auto-assign the user.

```bash
shirokuma-docs issues update {number} --field-status "Preparing"
shirokuma-docs issues update {number} --add-assignee @me
```

Skip status update if already Preparing or Spec Review. Assignee is idempotent, so always execute.

### Step 2: Pre-delegation Checks

#### Existing Plan Check

Check if issue body contains `## Plan` section (detected by `^## Plan` line prefix).

| Plan state | Action |
|-----------|--------|
| No plan | Proceed to Step 3 (delegate to planning-worker) |
| Plan exists | Ask whether to overwrite (AskUserQuestion) before proceeding |

### Step 3: Delegate to Planning Worker

Invoke `plan-issue` via the Agent tool (custom subagent `planning-worker`).

```text
Agent(planning-worker, args: "#{number}")
```

The planning worker performs codebase investigation, creates the plan, posts a thinking process comment, and writes the plan to the issue body. It returns structured output on completion.

#### Processing Subagent Output

Parse the YAML frontmatter from the planning worker's output:

1. **Extract YAML frontmatter** (block delimited by `---`)
2. **action field**: Read `action` → CONTINUE (SUCCESS) or STOP (FAIL)
3. **status field**: Read `status` → log for record
4. **Body first line**: Extract the first line after frontmatter → one-line summary

| Output Status | Action |
|--------|--------|
| SUCCESS | Proceed to Step 4 (plan review) |
| FAIL | Stop, report to user |

### Step 4: Plan Review (Subagent Delegation)

Reviewing in the same context that wrote the plan cannot catch blind spots. Delegate review to `reviewing-on-issue` plan role via subagent for a fresh-context review. Since the plan was written to the Issue body by the planning worker, the reviewer can retrieve it via `shirokuma-docs show {number}`.

#### Skill Availability Check (Fallback)

Before launching the subagent, verify that `reviewing-on-issue` is available in the skill list.

| State | Action |
|-------|--------|
| Skill available | Proceed to "Launching the Reviewer" below |
| Skill unavailable | Use "Fallback (self-check)" instead |

**Fallback (self-check)**: When `reviewing-on-issue` is unavailable, verify plan quality using this checklist:
- [ ] Does the plan address all requirements in the Issue?
- [ ] Are there any missing tasks?
- [ ] Is the deliverable (definition of done) clearly defined?
- [ ] Are risks/concerns identified (for complex Issues)?

If all checks pass, proceed to Step 5.

#### Launching the Reviewer

Invoke `reviewing-on-issue` with plan role via the Agent tool (custom subagent `review-worker`). `reviewing-on-issue` will fetch the Issue body itself via `shirokuma-docs show {number}`.

```text
Agent(review-worker, args: "plan #{number}")
```

The review result is posted as an Issue comment by `reviewing-on-issue`, and structured output is returned.

#### Processing Review Output

| Output Status | Action |
|--------|--------|
| PASS | Follow "On PASS" below |
| NEEDS_REVISION | Follow "On Failure" below to fix and re-review |

#### Output Parse Checkpoint

On receiving subagent output, execute these checks in order:

1. **Extract YAML frontmatter** (block delimited by `---`)
2. **action field**: Read `action` → CONTINUE (PASS) or REVISE (NEEDS_REVISION)
3. **status field**: Read `status` → log for record
4. **UCP check**: If `ucp_required` or `suggestions_count > 0` → present to user via AskUserQuestion (see `working-on-issue/reference/worker-completion-pattern.md` for details)
5. **Body first line**: Extract the first line after frontmatter → one-line summary
6. **action = CONTINUE with no UCP**: Follow "On PASS" below
7. **action = REVISE**: Follow "On Failure" below

Subagent output is internal processing data — output only a one-line summary before proceeding.

#### On PASS

1. Post a **plan review response comment** (evidence that the review passed):

```bash
shirokuma-docs issues comment {number} --body-file - <<'EOF'
## Plan Review Response Complete

**Review result:** PASS
**Fixes:** None (plan approved as-is)
EOF
```

If PASS was reached after NEEDS_REVISION cycles:

```bash
shirokuma-docs issues comment {number} --body-file - <<'EOF'
## Plan Review Response Complete

**Review result:** PASS (after {n} revision(s))
**Fixes:** {summary of changes made}
EOF
```

#### On Failure

When NEEDS_REVISION is returned:

1. Classify issues from subagent output `### Detail` into **[Plan]** and **[Issue description]**
2. **[Issue description]** issues → Fix the relevant sections in the issue body (overview, background, tasks, etc.)
3. **[Plan]** issues → Re-delegate to `planning-worker` with revision instructions, or fix the plan section directly and update the `## Plan` section in the Issue body
4. After fixes, re-run the review via Agent tool (same custom subagent `review-worker` plan role)
5. **Max retries: 2** (initial review + up to 2 fix-and-review cycles)
6. On 3rd NEEDS_REVISION → Stop the loop, report to user for their judgment

```
Planning worker → Plan written to body
  → Agent(review-worker plan)
    → NEEDS_REVISION → Fix + Update body → Re-review
                         ↓ (failed twice)
                    Report to user
    → PASS → Response comment
```

### Step 5: Design Phase Assessment (Before Status Transition)

Analyze the plan content to determine whether a design phase is needed. The assessment result determines the target status.

| Condition | Decision |
|-----------|----------|
| Plan contains UI/frontend design section | Design phase needed |
| Issue has `area:frontend` label | Design phase needed |
| Plan contains keywords: `UI design`, `screen design`, `schema design`, `data model design` | Design phase needed |
| None of the above | No design phase needed |

### Step 5a: Update Status (Based on Assessment)

| Assessment Result | Status Transition | Rationale |
|-------------------|------------------|-----------|
| No design phase needed | → Spec Review | Ready for direct implementation |
| Design phase needed | → Designing | Guide user to run `designing-on-issue` |

```bash
# When no design phase needed
shirokuma-docs issues update {number} --field-status "Spec Review"

# When design phase needed
shirokuma-docs issues update {number} --field-status "Designing"
```

### Step 6: Return to User

Display a plan summary and request approval. The plan is a contract with the user — proceeding without approval risks wasted work on a misaligned approach.

Show a summary matching the plan depth level and design phase assessment:

#### For Lightweight Plans

```markdown
## Plan Complete: #{number} {title}

**Status:** Spec Review (awaiting approval)
**Level:** Lightweight

### Plan Summary
- **Approach:** {one-line summary}

If approved, run `/working-on-issue #{number}` to start implementation.
```

#### For Standard/Detailed Plans (No Design Phase)

```markdown
## Plan Complete: #{number} {title}

**Status:** Spec Review (awaiting approval)
**Level:** {Standard | Detailed}

### Plan Summary
- **Approach:** {one-line summary}
- **Target files:** {N} files
- **Tasks:** {N} steps

### Next Steps
→ `/working-on-issue #{number}` to start implementation

Review the plan. If approved, start with the above.
If changes are needed, provide feedback.
```

#### For Standard/Detailed Plans (Design Phase Needed)

```markdown
## Plan Complete: #{number} {title}

**Status:** Designing (awaiting design phase)
**Level:** {Standard | Detailed}

### Plan Summary
- **Approach:** {one-line summary}
- **Target files:** {N} files
- **Tasks:** {N} steps
- **Design phase:** Required

### Next Steps
→ `/designing-on-issue #{number}` to run design first (recommended)
→ To skip design, run `/working-on-issue #{number}` for direct implementation

Review the plan. If approved, start with one of the above.
If changes are needed, provide feedback.
```

#### For Epic Plans (Sub-Issue Structure)

When the plan includes a sub-issue structure (`### Sub-Issue Structure` section), display an epic-specific completion report with next steps guidance:

```markdown
## Plan Complete: #{number} {title}

**Status:** Spec Review (awaiting approval)
**Level:** Detailed (Epic)

### Plan Summary
- **Approach:** {one-line summary}
- **Sub-issues:** {N} issues
- **Integration branch:** `epic/{number}-{slug}`

### Next Steps
1. Run `/working-on-issue #{number}` — this will automatically:
   - Create all sub-issues from the plan
   - Create the integration branch
   - Propose execution order based on dependencies
   - Start work on the first sub-issue

Review the plan. If approved, run `/working-on-issue #{number}` to begin.
If changes are needed, provide feedback.
```

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

| Rule | Usage |
|------|-------|
| `project-items` | Preparing/Designing/Spec Review status workflow |
| `output-language` | Output language for issue comments and body |
| `github-writing-style` | Bullet-point vs prose guidelines |
| `working-on-issue/reference/worker-completion-pattern.md` | Worker completion unified pattern, UCP check |

## Tool Usage

| Tool | When |
|------|------|
| Bash | `shirokuma-docs show/update/issues comment` |
| Agent (planning-worker) | Step 3: Delegate plan creation |
| Agent (review-worker) | Step 4: Fresh-context plan review (custom subagent delegation) |
| AskUserQuestion | Overwrite confirmation, issue number prompt |
| TodoWrite | Planning orchestration step progress tracking |

## Notes

- This skill is the **orchestrator** — actual plan creation is delegated to `planning-worker` subagent
- **Does not implement** — planning only. Implementation is `working-on-issue`'s responsibility
- Plans are persisted in the issue body — available across sessions
- `Spec Review` is the user approval gate — self-approving would bypass the human quality check that catches misaligned assumptions early
- **Chain autonomous progression**: After the review subagent (Step 4) returns, stopping forces the user to manually prompt continuation. Immediately proceed to Steps 5-6 based on the YAML frontmatter `action` field
