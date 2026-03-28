---
name: plan-issue
description: "Skill for issue planning. Delegated from prepare-flow via Skill tool, performs codebase investigation, plan creation, and issue body updates. Not intended for direct invocation."
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

!`shirokuma-docs rules inject --scope plan-worker`

# Planning on Issue

Analyze issue requirements, create an implementation plan, and persist it to the issue body. This skill performs the actual planning work — orchestration (status management, review delegation, user interaction) is handled by `prepare-flow`.

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
4. **Skill behavior change ripple check**: When the issue involves skill behavior changes (deprecation, responsibility change, behavioral modification), grep for the skill name across the following file categories and verify no descriptions based on the old behavior remain:
   - `i18n/cli/{ja,en}.json` skill descriptions
   - `plugin/*/rules/` skill responsibility descriptions
   - `plugin/*/skills/*/reference/` descriptions referencing other skill behavior
   - `plugin/specs/skills/*/evals/` evaluation scenarios

### Step 3: Create Plan

Assess the plan depth level from issue content and investigation results, then create a plan matching that level.

Plan templates for each level (Lightweight/Standard/Detailed/Epic) are in [reference/plan-templates.md](reference/plan-templates.md).

### Step 3.5: Post Thinking Process Comment

Post the decision rationale, alternatives, and constraints derived from the investigation as a **primary record** in a comment. Record "why this approach was chosen" before writing the plan to the body (Step 4).

```bash
shirokuma-docs items add comment {number} --file /tmp/shirokuma-docs/{number}-reasoning.md
```

**Template intent**: The comment records "why this approach was chosen". The body's plan section documents "what will be done" in a structured format, so comments and body serve distinct roles.

> Comment language and style must comply with the `output-language` rule and `github-writing-style` rule.

### Step 4: Post Plan as Comment

Post the full plan content as a comment (comment-link pattern). Use the template matching the depth level determined in Step 3.

```bash
PLAN_RESULT=$(shirokuma-docs items add comment {number} --file /tmp/shirokuma-docs/{number}-plan-comment.md)
PLAN_COMMENT_URL=$(echo "$PLAN_RESULT" | jq -r '.comment_url')
```

After posting, use the returned `comment_url` in the next step.

> Comment language and style must comply with the `output-language` rule and `github-writing-style` rule.

### Step 4.5: Write Summary Link to Issue Body

Write the plan summary link section to the Issue body. This enables `review-issue` to retrieve the plan link via `shirokuma-docs show {number}` and access the detailed comment.

Append a `## Plan` section to the existing issue body. Format:

```markdown
## Plan

> Details: {PLAN_COMMENT_URL}

### Approach
{1-2 line summary of the approach determined in Step 3}
```

```bash
shirokuma-docs items push {number}
```

**Important**: Preserve the existing body (overview, tasks, deliverables). **Append** the `## Plan` section. When using `shirokuma-docs show {number}` output as the base for the existing body, always strip the YAML frontmatter block (metadata enclosed in `---`) before writing.

> Plan section headings and content must comply with the `output-language` rule.

## Constraints

- Runs via Skill tool (main context), but progress management and user interaction are handled by the orchestrator (`prepare-flow`)
- Plan review is handled by `prepare-flow` — this skill only creates the plan
- **Does not update status** — status transitions (Preparing, Designing, Spec Review) are managed by `prepare-flow`

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
| `project-items` | Spec Review status workflow, comment-link body structure |
| `branch-workflow` | Branch naming reference (for plan documentation) |
| `output-language` | Output language for issue comments and body |
| `github-writing-style` | Bullet-point vs prose guidelines |

## Notes

- **Does not implement** — planning only. Implementation is `implement-flow`'s responsibility
- Plans are persisted in the issue body — available across sessions
- This skill is invoked via Skill tool from `prepare-flow` — orchestration is handled by `prepare-flow`
