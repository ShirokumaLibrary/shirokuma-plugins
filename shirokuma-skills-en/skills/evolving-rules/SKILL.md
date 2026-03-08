---
name: evolving-rules
description: Analyzes evolution signals for rules and skills, proposing improvements based on accumulated feedback. Triggers: "rule evolution", "rules evolution", "evolve rules", "evolution flow", "signal analysis".
allowed-tools: Bash, Read, Grep, Glob, AskUserQuestion, TodoWrite, Skill
---

# Rule & Skill Evolution

Analyze feedback signals accumulated in Evolution Issues and propose improvements to project-specific rules and skills.

## Workflow

### Step 1: Collect Signals

Fetch signals from Evolution Issues.

```bash
# Search for Evolution Issues
shirokuma-docs issues list --issue-type Evolution --limit 10
```

If an Issue is found, fetch details including comments:

```bash
shirokuma-docs show {number}
shirokuma-docs issues comments {number}
```

**If no signals**: Report "No Evolution signals accumulated yet. Record signals during daily work." and exit.

### Step 2: Pattern Analysis

Delegate to Task(Explore) to reduce context consumption. Classify comments into categories:

| Category | Description | Example |
|----------|-------------|---------|
| Rule friction | Rule doesn't match reality, was ignored | "git-commit-style scope is ambiguous" |
| Missing pattern | Uncovered case | "Test naming convention undefined" |
| Skill improvement | Skill behavior issue | "reviewing-on-issue lint execution order inefficient" |
| Lint trend | Lint violation trends | "Rule A violations increasing" |
| Success rate | Task completion metrics | "First-review pass rate declining" |

**Recurring pattern detection**: 3+ signals targeting the same subject → candidate for improvement proposal.

### Step 3: Impact Assessment

Read the current content of target rules/skills:

```bash
# For rules
Grep pattern="{rule-name}" glob="**/*.md" path="plugin/"

# For skills
Read plugin/shirokuma-skills-en/skills/{skill-name}/SKILL.md
```

Assess change impact:
- Dependencies with other rules/skills
- Impact on existing behavior
- Need for both EN/JA changes

### Step 4: Propose Updates

Present concrete changes in before/after format:

```markdown
## Proposal: Improve {target name}

**Signal count:** {N}
**Category:** {Rule friction | Missing pattern | Skill improvement}

### Before
{Current content (relevant section)}

### After
{Proposed content}

### Rationale
{Evidence from signals}
```

### Step 5: User Approval

Get approval via AskUserQuestion:

```
Apply this improvement proposal?
- Apply
- Modify and apply (enter feedback)
- Skip
```

### Step 6: Apply

Delegate approved proposals to `managing-rules` or `managing-skills` skill via the Skill tool. The delegated skill handles EN/JA updates and quality checks per `config-authoring-flow` rule.

```
Skill: managing-rules (or managing-skills)
Args: Update {target file}
```

**Implementation approach:**
- Delegate to `managing-rules` or `managing-skills` for file changes — direct editing of `plugin/` files bypasses the EN/JA sync and quality review that these skills provide
- The delegated skill is responsible for updating both EN/JA files and running `reviewing-claude-config` per `config-authoring-flow` rule
- If the Skill tool call fails, report the error to the user instead of falling back to direct editing (direct editing would skip the sync/review safeguards)

### Step 7: Update Records and Close Issue

Post an analysis summary comment, update the Evolution Issue body, and close the Issue.

#### 7a: Post Comment (Primary Record)

Record the analysis thinking process as a comment. The comment must meet these content requirements:

- **Analysis summary**: Number of detected patterns, category distribution
- **Apply/skip rationale**: Reasoning for applying each proposal, or judgment rationale for skipping
- **Impact scope**: Assessment of how changes affect other rules/skills

```bash
shirokuma-docs issues comment {number} --body-file - <<'EOF'
## Analysis Complete: {date}

### Analysis Summary
Analyzed {N} signals. {Category distribution summary}.

### Applied
- {target}: {change summary}. {rationale for applying}

### Skipped
- {target}: {rationale for skipping}

### Impact Scope
{Impact on other rules/skills. If none: "No impact"}
EOF
```

#### 7b: Update Body (Structured Summary)

Structure the comment content and consolidate into the body. The body records results only; for impact scope details, refer to the comment history. Update the body following this template:

```markdown
## Evolution Analysis Summary

### Analysis Results
- **Analysis date:** {date}
- **Signals:** {N}
- **Proposals:** {M}
- **Applied:** {K}

### Applied Improvements
| Target | Category | Change Summary |
|--------|----------|---------------|
| {name} | {category} | {summary} |

### Skip Reasons
| Target | Category | Reason |
|--------|----------|--------|
| {name} | {category} | {reason} |

> For impact scope details, refer to the comment history.
```

```bash
shirokuma-docs issues update {number} --body-file /tmp/shirokuma-docs/{number}-body.md
```

#### 7c: Close Issue

```bash
# Close the Evolution Issue (1 analysis cycle = 1 Issue)
gh issue close {number}
```

New signals after closure are recorded in a new Evolution Issue (see `rule-evolution` rule, Evolution Issue Lifecycle section).

## Completion Report

```markdown
## Evolution Analysis Complete

**Signals analyzed:** {N}
**Proposals:** {M}
**Applied:** {K}

| Target | Category | Action |
|--------|----------|--------|
| {name} | {category} | {Applied / Skipped} |
```

## Edge Cases

| Situation | Action |
|-----------|--------|
| No Evolution Issue exists | Propose creating an Evolution Issue for the project |
| Fewer than 3 signals | Report "Too few signals for analysis" |
| Target rule/skill doesn't exist | Propose creation (delegate to `managing-rules`) |
| Only EN or JA version exists | Propose creating/updating both |

## Notes

- Responsibility separation from `discovering-codebase-rules`: `evolving-rules` improves **existing** rules/skills, `discovering-codebase-rules` discovers **new** patterns
- Avoid excessive proposals — respect the threshold (3+ signals), propose cautiously
- Never modify rules/skills without user approval
- Delegate analysis phase to Task(Explore) to save main context
