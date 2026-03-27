# /create-item Workflow

Create a GitHub Project item (Issue or DraftIssue). When called without arguments, auto-infers from conversation context.

```
/create-item                    # Context auto-inference mode
/create-item "Title"            # With title
```

## Contents

- Step 1: Gather Details + Type Classification
- Step 2: Generate Body
- Step 3: Set Fields
- Step 4: Create
- Step 5: Display Result and Post-Creation Review

## Step 1: Gather Details + Type Classification

With arguments: Use the provided title.
Without arguments: Infer from conversation context:

| Target | Source | Method |
|--------|--------|--------|
| Title | Recent user message | Summarize the problem/feature mentioned before "make this an issue" |
| **Type classification** | Conversation context | See "Type Classification" below |
| Type (Issue Types) | Derived from classification | feature → Feature, bug → Bug, chore → Chore, docs → Docs, research → Research, evolution → Evolution (specify via `--issue-type` option) |
| Label (area) | Conversation context | Infer from impact scope: CLI-related → `area:cli`, plugin-related → `area:plugin`, etc. |
| Priority | Conversation context | Urgency expressions ("urgent" → High, normal → Medium) |
| Body | Type template | Structure using the type-specific template from Step 2 |
| Size | Task estimate | Estimate from task count and impact scope (default S) |

### Type Classification

| Keywords | Type |
|----------|------|
| new feature, add, implement, create | feature |
| bug, fix, error, broken | bug |
| refactor, improve, config, chore, internal | chore |
| documentation, docs, document, readme | docs |
| research, evaluate, compare, investigate | research |
| evolution, signal, evolve, rule improvement | evolution |

### Purpose Clarity Check

When creating an issue, detect cases where the user's message only describes a "means" (what to do) without including a "purpose" (who / what / why). See the `creating-item` skill for detailed criteria.

#### Detecting Means Patterns

If the user's message is structured as "verb + implementation target" only (e.g., "fix the bug", "add an option", "consolidate the commands", "implement the feature"), classify it as a means pattern.

| State | Action |
|-------|--------|
| Purpose (beneficiary, outcome, motivation) is clear | Fill in inferred purpose and create |
| Means pattern detected or purpose unclear | Propose 2-3 purpose candidates and confirm via AskUserQuestion (block creation without purpose) |
| XS size / purpose already stated in conversation | Skip confirmation and create (prevent over-detection) |

#### Example Purpose Proposals

```
Example: User says "add --format option to deps command"

→ Means pattern detected (add = means)

Proposals:
A) "Enable CLI users to choose output format based on use case.
    Currently SVG-only, which is inconvenient for CI or document embedding."
B) "Enable CLI users to get dependency info in JSON format.
    For pipeline integration with other tools."
C) Other (please specify)
```

#### The 3 Elements of a Purpose

A well-formed purpose contains **beneficiary + expected outcome + motivation**:

```
"{Beneficiary} can {expected outcome}. Because {motivation}."
```

Label options (for impact scope classification — area labels):

| Label | Purpose |
|-------|---------|
| `area:cli` | CLI commands |
| `area:plugin` | Plugin-related |
| `area:portal` | Portal site |
| `area:docs` | Documentation |

## Step 2: Generate Body

Use the type-specific template. All types require a `## Purpose` section.

> Template headings and placeholder content must be written in the language specified by the `output-language` rule. Follow `github-writing-style` rule bullet-point guidelines.

### feature (New Feature)

```markdown
## Purpose
{role} can {capability}. {user value}.

## Summary
{technical description}

## Background
{current problems, relevant constraints and dependencies}

## Considerations
- {Perspectives, constraints, and technical considerations for the planning phase}

## Deliverable
{definition of done — include user-verifiable outcomes}
```

**Purpose example**: "CLI users can export dependency graphs in SVG format. To visually understand project structure and streamline onboarding for new members."

### bug (Bug Fix)

```markdown
## Purpose
{role} can {expected behavior}. {current problem}.

## Summary
{technical description of the bug}

## Steps to Reproduce
1. Step 1
2. Step 2

## Expected Behavior
{correct behavior}

## Considerations
- {Root cause investigation angles, impact scope, regression test perspectives}

## Deliverable
{how to verify the fix}
```

**Purpose example**: "CLI users can run the `deps` command successfully. Currently, projects with circular dependencies cause an infinite loop."

### chore (Internal Improvement / Refactoring)

```markdown
## Purpose
Developers can {what}. {current problem}.

## Summary
{technical description}

## Background
{motivation, current issues, quantitative evidence if available}

## Considerations
- {Impact scope, compatibility with existing code, performance implications}

## Deliverable
{how to verify improvement — quantitative metrics if possible}
```

**Purpose example**: "Developers can run tests faster. Currently CI takes 8 minutes, slowing the feedback loop."

### research (Investigation)

```markdown
## Purpose
Team can make a decision on {subject}. {what is uncertain}.

## Summary
{scope of investigation}

## Investigation Items
- [ ] Item 1

## Decision Criteria
{what needs to be learned for completion}

## Deliverable
{output format — Discussion / ADR / comparison table}
```

**Purpose example**: "Team can select a full-text search implementation approach. Currently using JSON index, but scalability is unverified."

### Lightweight Issues

For typo fixes, single-line changes, and other XS-sized issues:
- Purpose section can be a single sentence (e.g., "Users can read documentation correctly. There is a typo.")
- Background section is optional

> **Background section**: Plan review (`plan-issue` Step 4) evaluates plans from the issue body alone. Missing background, constraints, or dependencies will cause the reviewer to return NEEDS_REVISION. For lightweight issues (typo fixes, etc.), a single line suffices.

## Step 3: Set Fields

| Field | Options | Default |
|-------|---------|---------|
| Issue Type (**required**) | Feature / Bug / Task / Chore / Docs / Research / Evolution | (from type inference) |
| Priority | Critical / High / Medium / Low | Medium |
| Size | XS / S / M / L / XL | S |
| Status | Backlog / Ready | Backlog |

## Step 4: Create

### Temp File Naming Convention

Issue numbers are assigned by GitHub at creation time — they are unknown beforehand. Do NOT use predicted issue numbers in temp file names.

| Timing | Pattern | Example |
|--------|---------|---------|
| Before creation | `/tmp/shirokuma-docs/{slug}-body.md` | `/tmp/shirokuma-docs/add-format-option-body.md` |
| After creation | `/tmp/shirokuma-docs/{number}-body.md` allowed | `/tmp/shirokuma-docs/42-body.md` |

```bash
# Issue (recommended — frontmatter includes metadata)
shirokuma-docs items add issue --file /tmp/shirokuma-docs/{slug}.md

# Sub-Issue (frontmatter includes parent field)
shirokuma-docs items add issue --file /tmp/shirokuma-docs/{slug}.md

# DraftIssue (lightweight)
shirokuma-docs projects create \
  --title "Title" --body-file /tmp/shirokuma-docs/add-format-option-body.md \
  --field-status "Backlog" --priority "Medium"
```

### Sub-Issue Creation Guidance

When creating sub-issues of an epic (parent issue):

- Use `--parent {parent-issue-number}` to set the parent-child relationship
- Include a reference to the parent issue (`Refs #{parent-number}`) in the sub-issue body
- Set Issue Type appropriate to the individual task, not inherited from the parent
- Size should reflect the individual task's effort (sub-issues are typically S/M even if parent is L/XL)

**Recommended body sections:**

```markdown
## Purpose
{Sub-task purpose}

## Summary
{Technical description}

## Parent Issue
Refs #{parent-number} — {parent issue title}

## Considerations
- {Alignment with parent issue plan, dependencies}

## Deliverable
{Definition of done}
```

See `epic-workflow` reference for the full epic workflow.

## Step 5: Display Result and Post-Creation Review

```markdown
## Item Created
**Issue:** #123 | **Label:** area:cli | **Priority:** Medium | **Status:** Backlog

Review the issue body content on GitHub. If the title, body, or fields need changes, provide instructions.
```

After displaying the result, pause and give the user the opportunity to review and request modifications before proceeding to chain decision.
