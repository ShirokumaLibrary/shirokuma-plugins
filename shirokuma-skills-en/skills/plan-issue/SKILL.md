---
name: plan-issue
description: "Skill for issue planning. Delegated from prepare-flow via Skill tool, performs codebase investigation, plan creation, and plan issue creation. Not intended for direct invocation."
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

!`shirokuma-docs rules inject --scope plan-worker`

# Planning on Issue

Analyze issue requirements, create an implementation plan, and persist it as a plan issue (child issue). This skill performs the actual planning work — orchestration (status management, review delegation, user interaction) is handled by `prepare-flow`.

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
shirokuma-docs items context {number}
# → Read .shirokuma/github/{org}/{repo}/issues/{number}/body.md
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

### Step 4: Create Plan Issue

Create a plan issue using `items add issue` with the plan content from Step 3 as the body.

Create the plan issue body file:

```bash
cat > /tmp/shirokuma-docs/{number}-plan-issue.md <<'EOF'
---
title: "Plan: {parent issue title}"
status: "Review"
labels: ["area:plan"]
---

## Plan

{Full plan content based on the level-specific template from Step 3}

## Parent Issue

See #{parent-number} for the task context.
EOF
shirokuma-docs items add issue --file /tmp/shirokuma-docs/{number}-plan-issue.md
```

After the plan issue is created, record the returned issue number as `PLAN_ISSUE_NUMBER`.

> The plan issue body language and style must comply with the `output-language` rule and `github-writing-style` rule.

### Step 4a: Post Thinking Process Comment to Plan Issue

Post the decision rationale, alternatives, and constraints as a **comment on the plan issue** (not the parent issue).

```bash
cat > /tmp/shirokuma-docs/{number}-reasoning.md <<'EOF'
## Plan Decision Rationale

### Selected Approach
{The chosen approach and the reason for selecting it}

### Alternatives Considered
{Alternatives evaluated and why they were rejected. If none: "No alternatives (single clear approach)"}

### Constraints Discovered
{Technical constraints and dependencies found during codebase investigation. If none: "No constraints"}
EOF
shirokuma-docs items add comment {PLAN_ISSUE_NUMBER} --file /tmp/shirokuma-docs/{number}-reasoning.md
```

> Comment language and style must comply with the `output-language` rule and `github-writing-style` rule.

### Step 4b: Set Parent-Child Relationship

Register the plan issue as a child of the parent issue using the `items parent` command.

```bash
shirokuma-docs items parent {PLAN_ISSUE_NUMBER} {parent-number}
```

## Constraints

- Runs via Skill tool (main context), but progress management and user interaction are handled by the orchestrator (`prepare-flow`)
- Plan review is handled by `prepare-flow` — this skill only creates the plan
- **Does not update status** — status transitions (In Progress, Review) are managed by `prepare-flow`
- Plan issues are created with status `Review` and label `area:plan`

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
| Issue body is empty | Create plan issue with plan content only |
| Epic issue (has sub-issues) | Use epic plan template with integration branch and sub-issue structure (exclude the plan issue itself from sub-issue counts) |

## Rule References

| Rule | Usage |
|------|-------|
| `project-items` | Review status workflow |
| `branch-workflow` | Branch naming reference (for plan documentation) |
| `output-language` | Output language for issue comments and body |
| `github-writing-style` | Bullet-point vs prose guidelines |

## Notes

- **Does not implement** — planning only. Implementation is `implement-flow`'s responsibility
- Plans are persisted as plan issues (child issues) — available across sessions
- This skill is invoked via Skill tool from `prepare-flow` — orchestration is handled by `prepare-flow`
