---
name: planning-on-issue
description: Creates an implementation plan for an issue and persists it to the issue body for user approval. Triggers: "plan", "plan #42", "design approach", "create plan".
allowed-tools: Bash, Read, Grep, Glob, Task, AskUserQuestion, TodoWrite
---

# Planning on Issue

> **Chain Autonomous Progression**: After the plan review fork (Step 4) returns its result, immediately proceed to Steps 5-7 (post comment, update body, set Spec Review). Stopping after the review fork forces the user to manually prompt continuation, breaking the planning workflow. Parse the YAML frontmatter `action` field and act without waiting for user input.

Analyze issue requirements, create an implementation plan, and persist it to the issue body. After planning, set status to Spec Review and return control to the user. **Does not proceed to implementation.**

## Plan Depth Levels

Plan depth is determined by **issue content complexity**, not by Size.

| Level | Content | Examples |
|-------|---------|----------|
| Lightweight | 1-2 line approach + confirmation | Typo fix, config change, simple bug fix |
| Standard | Approach + target files + task breakdown | New feature, refactoring, moderate fix |
| Detailed | Multi-option comparison + risk analysis + test strategy | Architecture change, breaking change, multi-system integration |

### Depth Assessment Criteria

AI assesses from issue title/body/type/comments:

| Criteria | Lightweight | Standard | Detailed |
|----------|-------------|----------|----------|
| Estimated files changed | 1-2 | 3-5 | 6+ |
| Design decisions | None | Present | Multiple options |
| Impact on existing behavior | None | Limited | Widespread |
| Test impact | Existing sufficient | Additions needed | Strategy review needed |

If any criterion matches a higher level, use that level.

## Workflow

### Step 1: Fetch Issue

```bash
shirokuma-docs issues show {number}
```

Review title, body, type, priority, size, labels, and comments.

### Step 1b: Set Status to Planning + Assign

If the issue status is Backlog, transition to Planning to record the planning start. Also auto-assign the user.

```bash
shirokuma-docs issues update {number} --field-status "Planning"
shirokuma-docs issues update {number} --add-assignee @me
```

Skip status update if already Planning or Spec Review. Assignee is idempotent, so always execute.

### Step 2: Codebase Investigation

Investigate code related to the issue requirements.

1. **Existing implementation**: Use Grep/Glob to identify related files
2. **Dependencies**: Identify modules and tests affected by changes
3. **Patterns**: Check for similar implementations in the codebase

Use Task (Explore agent) for broad investigation to minimize context consumption.

### Step 3: Create Plan

Assess the plan depth level from issue content and investigation results, then create a plan matching that level.

#### Lightweight Plan

```markdown
## Plan

### Approach
{1-2 line description of the approach}
```

#### Standard Plan

> When tasks have dependencies, include a diagram following the Mermaid guidelines in the `github-writing-style` rule.

```markdown
## Plan

### Approach
{Selected approach and rationale}

### Target Files
- `path/to/file.ts` - {Summary of changes}

### Task Breakdown
- [ ] Task 1
- [ ] Task 2
```

#### Detailed Plan

> Follow the Mermaid guidelines in the `github-writing-style` rule to include diagrams for task dependencies, state transitions, or component interactions.

```markdown
## Plan

### Approach
{Multi-option comparison and selection rationale}

### Target Files
- `path/to/file.ts` - {Summary of changes}

### Task Breakdown
- [ ] Task 1
- [ ] Task 2

### Risks / Concerns
- {Breaking changes, performance, security, etc.}
```

#### Epic Plan (Issues with Sub-Issues)

For issues where `subIssuesSummary.total > 0`, use the extended template that includes sub-issue structure and integration branch.

> Follow the Mermaid guidelines in the `github-writing-style` rule to visualize sub-issue dependencies and execution order.

```markdown
## Plan

### Approach
{Overall strategy}

### Integration Branch
`epic/{number}-{slug}`

### Sub-Issue Structure

| # | Issue | Description | Dependencies | Size |
|---|-------|-------------|--------------|------|
| 1 | #{sub1} | {summary} | — | S |
| 2 | #{sub2} | {summary} | #{sub1} | M |

### Execution Order
{Recommended order based on dependencies}

### Task Breakdown
- [ ] Create integration branch
- [ ] #{sub1}: {task summary}
- [ ] #{sub2}: {task summary}
- [ ] Final PR: integration → develop

### Risks / Concerns
- {Dependency risks between sub-issues}
```

See `epic-workflow` reference for details.

### Step 4: Plan Review (Fork Delegation)

Reviewing in the same context that wrote the plan cannot catch blind spots. Delegate review to `reviewing-on-issue` plan role as fork for a fresh-context review.

#### Launching the Reviewer

Invoke `reviewing-on-issue` with plan role via the Skill tool. `reviewing-on-issue` will fetch the Issue body itself via `shirokuma-docs issues show {number}`, so embedding the Issue body in the prompt is not needed.

```text
Skill(reviewing-on-issue, args: "plan #{number}")
```

The review result is posted as an Issue comment by `reviewing-on-issue`, and a Fork Signal is returned.

#### Processing Fork Signal

| Fork Signal Status | Action |
|--------|--------|
| PASS | Proceed to Step 5 |
| NEEDS_REVISION | Follow "On Failure" below to fix and re-review |

#### Fork Signal Parse Checkpoint

On receiving fork output, execute these checks in order:

1. **Extract YAML frontmatter** (block delimited by `---`)
2. **action field**: Read `action` → CONTINUE (PASS) or REVISE (NEEDS_REVISION)
3. **status field**: Read `status` → log for record
4. **Body first line**: Extract the first line after frontmatter → one-line summary
5. **action = CONTINUE**: Proceed to Step 5
6. **action = REVISE**: Follow "On Failure" below

Fork Signal is internal processing data — output only a one-line summary before proceeding.

#### On Failure

When NEEDS_REVISION is returned:

1. Classify issues from Fork Signal `### Detail` into **[Plan]** and **[Issue description]**
2. **[Issue description]** issues → Fix the relevant sections in the issue body (overview, background, tasks, etc.)
3. **[Plan]** issues → Fix the plan section
4. After fixes, re-run the review via Skill (same `reviewing-on-issue` plan role)
5. **Max retries: 2** (initial review + up to 2 fix-and-review cycles)
6. On 3rd NEEDS_REVISION → Stop the loop, report to user for their judgment

```
Plan → Skill(reviewing-on-issue plan) → NEEDS_REVISION → Fix → Re-review → PASS → Step 5
                                                                       ↓ (failed twice)
                                                                 Report to user
```

### Step 5: Update Issue Body with Plan

Follow the comment-first workflow (see `project-items` rule, "Workflow Order" section) in this order:

#### 5a: Post Decision Rationale as Comment (PASS only)

Post the planning decision rationale as a **primary record** in a comment. Record the decision process that would only exist in comments, not a summary of the body.

```bash
shirokuma-docs issues comment {number} --body-file - <<'EOF'
## Plan Decision Rationale

### Selected Approach
{The chosen approach and why it was selected}

### Alternatives Considered
{Approaches considered but rejected, with reasons. If none: 'No alternatives (single clear approach)'}

### Constraints Discovered
{Technical constraints or dependencies found during codebase investigation. Omit if none}
EOF
```

**Template intent**: The comment records "why this approach was chosen". The body's plan section documents "what will be done" in a structured format, so comments and body serve distinct roles.

> Comment language and style must comply with the `output-language` rule and `github-writing-style` rule.

#### 5b: Append Plan Section to Issue Body

Append a `## Plan` section to the existing issue body. Use the template from the depth level determined in Step 3.

```bash
shirokuma-docs issues update {number} --body-file /tmp/shirokuma-docs/{number}-body.md
```

**Important**: Preserve the existing body (overview, tasks, deliverables). **Append** the `## Plan` section. If an existing `## Tasks` section exists, the plan's `### Task Breakdown` coexists as more specific implementation steps.

> Plan section headings and content must comply with the `output-language` rule. Follow `github-writing-style` rule bullet-point guidelines.

### Step 6: Update Status

```bash
shirokuma-docs issues update {number} --field-status "Spec Review"
```

### Step 7: Return to User

Display a plan summary and request approval. The plan is a contract with the user — proceeding without approval risks wasted work on a misaligned approach.

Show a summary matching the plan depth level:

#### For Lightweight Plans

```markdown
## Plan Complete: #{number} {title}

**Status:** Spec Review (awaiting approval)
**Level:** Lightweight

### Plan Summary
- **Approach:** {one-line summary}

If approved, run `/working-on-issue #{number}` to start implementation.
```

#### For Standard/Detailed Plans

```markdown
## Plan Complete: #{number} {title}

**Status:** Spec Review (awaiting approval)
**Level:** {Standard | Detailed}

### Plan Summary
- **Approach:** {one-line summary}
- **Target files:** {N} files
- **Tasks:** {N} steps

Review the plan. If approved, run `/working-on-issue #{number}` to start implementation.
If changes are needed, provide feedback.
```

#### Evolution Signal Auto-Recording

At the end of the plan completion report, auto-record Evolution signals detected during the session following the "Auto-Recording Procedure at Skill Completion" in the `rule-evolution` rule.

1. Self-review the session using the detection checklist (see `rule-evolution` rule)
2. Signals detected → Post comment to Evolution Issue → Display 1-line recording confirmation
3. No signals → Check for accumulated signals → Display reminder (fallback)

## GitHub Writing Rules

Issue comments and body content must comply with the `output-language` rule and `github-writing-style` rule.

**NG example (English setting but wrong language):**

```
### アプローチ
各スキルに GitHub 書き込みルールの参照を追加し...  ← Wrong language for English setting
```

**OK example:**

```
### Approach
Add GitHub writing rule references to each skill...
```

## Arguments

| Format | Example | Behavior |
|--------|---------|----------|
| Issue number | `#42` | Fetch issue and start planning |
| No argument | — | Ask for issue number via AskUserQuestion |

## Edge Cases

| Situation | Action |
|-----------|--------|
| `## Plan` section already exists | Ask whether to overwrite (AskUserQuestion) |
| Issue is Done/Released | Show warning |
| Issue body is empty | Create body with plan section only |
| Status is already Planning | Continue planning, skip status update |
| Status is already Spec Review | Update plan, keep status |
| Epic issue (has sub-issues) | Use epic plan template with integration branch and sub-issue structure |

## Rule References

| Rule | Usage |
|------|-------|
| `project-items` | Spec Review status workflow |
| `branch-workflow` | Branch naming reference (for plan documentation) |
| `output-language` | Output language for issue comments and body |
| `github-writing-style` | Bullet-point vs prose guidelines |

## Tool Usage

| Tool | When |
|------|------|
| Bash | `shirokuma-docs issues show/update` |
| Read/Grep/Glob | Codebase investigation |
| Task (Explore) | Broad code investigation |
| Skill (reviewing-on-issue) | Step 4: Fresh-context plan review (fork delegation) |
| AskUserQuestion | Overwrite confirmation, issue number prompt |
| TodoWrite | Planning step progress tracking |

## Notes

- **Does not implement** — planning only. Implementation is `working-on-issue`'s responsibility
- Plans are persisted in the issue body — available across sessions
- `Spec Review` is the user approval gate — self-approving would bypass the human quality check that catches misaligned assumptions early
- Use Explore agent during investigation to minimize context consumption
- **Chain autonomous progression**: After the review fork (Step 4) returns, stopping forces the user to manually prompt continuation. Immediately proceed to Steps 5-7 based on the YAML frontmatter `action` field
