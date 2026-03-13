---
name: plan-issue
description: "Sub-agent skill for issue planning. Delegated from preparing-on-issue via planning-worker, performs codebase investigation, plan creation, and issue body updates. Not intended for direct invocation."
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Planning on Issue

Analyze issue requirements, create an implementation plan, and persist it to the issue body. This skill performs the actual planning work as a subagent — orchestration (status management, review delegation, user interaction) is handled by `preparing-on-issue`.

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
shirokuma-docs show {number}
```

Review title, body, type, priority, size, labels, and comments.

### Step 2: Codebase Investigation

Investigate code related to the issue requirements.

1. **Existing implementation**: Use Grep/Glob to identify related files
2. **Dependencies**: Identify modules and tests affected by changes
3. **Patterns**: Check for similar implementations in the codebase

### Step 3: Create Plan

Assess the plan depth level from issue content and investigation results, then create a plan matching that level.

Plan templates for each level (Lightweight/Standard/Detailed/Epic) are in [reference/plan-templates.md](reference/plan-templates.md).

### Step 3.5: Post Thinking Process Comment

Post the decision rationale, alternatives, and constraints derived from the investigation as a **primary record** in a comment. Record "why this approach was chosen" before writing the plan to the body (Step 4).

```bash
shirokuma-docs issues comment {number} --body-file - <<'EOF'
## Plan Decision Rationale

### Selected Approach
{The chosen approach and why it was selected}

### Alternatives Considered
{Approaches considered but rejected, with reasons. If none: 'No alternatives (single clear approach)'}

### Constraints Discovered
{Technical constraints or dependencies found during codebase investigation. If none: 'No constraints discovered'}
EOF
```

**Template intent**: The comment records "why this approach was chosen". The body's plan section documents "what will be done" in a structured format, so comments and body serve distinct roles.

> Comment language and style must comply with the `output-language` rule and `github-writing-style` rule.

### Step 4: Write Plan to Issue Body

Write the plan section to the Issue body. This enables `review-issue` to retrieve the plan content via `shirokuma-docs show {number}`.

Append a `## Plan` section to the existing issue body. Use the template from the depth level determined in Step 3.

```bash
shirokuma-docs issues update {number} --body-file /tmp/shirokuma-docs/{number}-body.md
```

**Important**: Preserve the existing body (overview, tasks, deliverables). **Append** the `## Plan` section. If an existing `## Tasks` section exists, the plan's `### Task Breakdown` coexists as more specific implementation steps. When using `shirokuma-docs show {number}` output as the base for the existing body, always strip the YAML frontmatter block (metadata enclosed in `---`) before writing.

> Plan section headings and content must comply with the `output-language` rule. Follow `github-writing-style` rule bullet-point guidelines.

## Constraints

- As an Agent tool (subagent), `TodoWrite` / `AskUserQuestion` are not available
- Progress management and user interaction are handled by the orchestrator (`preparing-on-issue`)
- Plan review is handled by `preparing-on-issue` — this skill only creates the plan
- **Does not update status** — status transitions (Preparing, Designing, Spec Review) are managed by `preparing-on-issue`

## Output Template

After work completes, return the following structured data to the caller. The plan is written to the issue body as the deliverable.

```yaml
---
action: CONTINUE
status: SUCCESS
---

Plan created ({level} level). {one-line plan summary}

### Plan Details
- **Level:** {Lightweight | Standard | Detailed | Epic}
- **Target files:** {N} files
- **Tasks:** {N} steps
```

On failure:

```yaml
---
action: STOP
status: FAIL
---

{error description}
```

**Note**: `next` field is omitted (orchestrator determines next action). `ref` field is omitted (issue body update is the deliverable, not a separate GitHub write).

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
| Issue number | `#42` | Fetch issue and create plan |

## Edge Cases

| Situation | Action |
|-----------|--------|
| Issue body is empty | Create body with plan section only |
| Epic issue (has sub-issues) | Use epic plan template with integration branch and sub-issue structure |

## Rule References

| Rule | Usage |
|------|-------|
| `project-items` | Spec Review status workflow |
| `branch-workflow` | Branch naming reference (for plan documentation) |
| `output-language` | Output language for issue comments and body |
| `github-writing-style` | Bullet-point vs prose guidelines |

## Notes

- **Does not implement** — planning only. Implementation is `working-on-issue`'s responsibility
- Plans are persisted in the issue body — available across sessions
- This skill runs as a subagent via `planning-worker` — orchestration is handled by `preparing-on-issue`
