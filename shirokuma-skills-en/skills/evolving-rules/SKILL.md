---
name: evolving-rules
description: Analyzes evolution signals for rules and skills, proposing improvements based on accumulated feedback. Triggers: "rule evolution", "rules evolution", "evolve rules", "evolution flow", "signal analysis".
allowed-tools: Bash, Read, Grep, Glob, Skill, AskUserQuestion, TaskCreate, TaskUpdate, TaskGet, TaskList
---

# Rule & Skill Evolution

Analyze feedback signals accumulated in Evolution Issues and propose improvements to project-specific rules and skills.

## Scope

- **Category:** Orchestrator
- **Scope:** Collect and analyze signals from Evolution Issues, record improvement proposals as Issues. Handles user confirmation (AskUserQuestion), delegation to `creating-item` skill, and closing Evolution Issues.
- **Out of scope:** Directly modifying rule/skill files (proposals are recorded as Issues; implementation is delegated to the `implement-flow` workflow)

## Workflow

### Step 1: Collect Signals

Fetch signals from Evolution Issues.

```bash
# Search for Evolution Issues (analysis phase uses --limit 10 for cross-analysis. See evolution-details.md "Standard Search & Creation Flow" for value guidelines)
shirokuma-docs items list --issue-type Evolution --limit 10
```

If an Issue is found, fetch details including comments:

```bash
shirokuma-docs items pull {number}
# → Read .shirokuma/github/{number}.md and comment files in .shirokuma/github/{number}/
```

**If no signals**: Report "No Evolution signals accumulated yet. Record signals during daily work." and exit.

### Step 2: Pattern Analysis

Delegate to Task(Explore) to reduce context consumption. Classify comments into categories:

| Category | Description | Example |
|----------|-------------|---------|
| Rule friction | Rule doesn't match reality, was ignored | "git-commit-style scope is ambiguous" |
| Missing pattern | Uncovered case | "Test naming convention undefined" |
| Skill improvement | Skill behavior issue | "review-issue lint execution order inefficient" |
| Lint trend | Lint violation trends | "Rule A violations increasing" |
| Success rate | Task completion metrics | "First-review pass rate declining" |

**Recurring pattern detection**: 3+ signals targeting the same subject → candidate for improvement proposal.

### Step 3: Impact Assessment

Delegate to Agent(Explore) to avoid main context bloat from reading multiple large files:

```
Agent(Explore): Read the following files and summarize their content and dependencies:
- plugin/shirokuma-skills-en/skills/{skill-name}/SKILL.md
- plugin/shirokuma-skills-ja/skills/{skill-name}/SKILL.md
- Any rules referencing {rule-name} (use Grep glob="**/*.md" path="plugin/")
Return: current content summary, cross-references found, EN/JA diff (if any)
```

Assess change impact based on the Agent(Explore) report:
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

### Step 5: User Decision

Get the user's decision on whether to record the proposal as an Issue via AskUserQuestion:

```
Record this improvement proposal as an Issue?
- Create Issue
- Modify and create Issue (enter feedback)
- Skip
```

### Step 6: Create Proposal Issue

Delegate to the `creating-item` skill to record approved proposals as Issues.

Context to pass to `creating-item`:
- **Title**: `{type}: Improve {target name} (Evolution #{evolution-number})`
- **Type**: chore (rule/skill improvement)
- **Background**: Improvement proposal based on signals accumulated in Evolution Issue #{evolution-number}
- **Proposal content**: before/after and rationale from Step 4

After creating the Issue, record a reference to the created Issue in a comment on the original Evolution Issue:

```bash
shirokuma-docs items add comment {evolution-number} --file /tmp/shirokuma-docs/{evolution-number}-evolution-ref.md
```

### Step 7: Update Records and Close Issue

Post an analysis summary comment, update the Evolution Issue body, and close the Issue.

#### 7a: Post Comment (Primary Record)

Record the analysis thinking process as a comment. The comment must meet these content requirements:

- **Analysis summary**: Number of detected patterns, category distribution
- **Apply/skip rationale**: Reasoning for applying each proposal, or judgment rationale for skipping
- **Impact scope**: Assessment of how changes affect other rules/skills

```bash
shirokuma-docs items add comment {number} --file /tmp/shirokuma-docs/{number}-analysis.md
```

#### 7b: Update Body (Structured Summary)

Structure the comment content and consolidate into the body. The body records results only; for impact scope details, refer to the comment history. Update the body following this template:

```markdown
## Evolution Analysis Summary

### Analysis Results
- **Analysis date:** {date}
- **Signals:** {N}
- **Proposals:** {M}
- **Issues created:** {K}

### Created Proposal Issues
| Target | Category | Issue |
|--------|----------|-------|
| {name} | {category} | #{issue-number} |

### Skip Reasons
| Target | Category | Reason |
|--------|----------|--------|
| {name} | {category} | {reason} |

> For impact scope details, refer to the comment history.
```

```bash
shirokuma-docs items push {number}
```

#### 7c: Close Issue

```bash
# Close the Evolution Issue (1 analysis cycle = 1 Issue)
shirokuma-docs items close {number}
```

New signals after closure are recorded in a new Evolution Issue (see `rule-evolution` rule, Evolution Issue Lifecycle section).

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
- `evolving-rules` does not directly apply changes to rules/skills. Proposals are recorded as Issues; implementation is delegated to the `implement-flow` workflow
- Delegate analysis phase to Task(Explore) to save main context
