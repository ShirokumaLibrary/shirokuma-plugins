---
name: write-adr
description: Creates, updates, and supersedes Architecture Decision Records (ADRs) as GitHub Discussions following Michael Nygard's format and MADR best practices. Supports three modes (create / update / supersede). Triggers: "ADR", "architecture decision", "create ADR", "write ADR", "record decision", "update ADR", "mark ADR as Deprecated", "change ADR status", "supersede ADR", "replace with new ADR".
allowed-tools: Bash, Read, AskUserQuestion
---

# Writing ADR

Create and update Architecture Decision Records (ADRs) as GitHub Discussions (ADR category) with consistent structure and quality.

## When to Use

| Trigger | Example |
|---------|---------|
| Architecture decision confirmed | "We chose PostgreSQL over MongoDB" |
| Technology selection | "Use Drizzle ORM for database access" |
| Pattern or convention established | "All API routes use middleware auth" |
| Trade-off evaluation completed | "Chose SSR over SSG for dashboard" |
| User explicitly requests creation | "Create ADR for X", "Record this decision" |
| Editing or re-statusing an existing ADR | "Update ADR", "Mark as Deprecated", "Change ADR status" |
| Replacing an old ADR with a new one | "Supersede ADR-001", "Replace with a new ADR" |
| Proposing requirement changes | When an existing Accepted ADR needs to be overturned |

## Mode Detection (Required: Check First)

Determine the operating mode from the call context. Mode boundaries are defined by the **number of target ADRs**:

| Mode | Target ADR Count | Trigger Keywords | Action |
|------|------------------|-----------------|--------|
| **create** (new) | 1 (new) | Recording a new decision (default) | Create a new ADR Discussion in Proposed status |
| **update** (edit existing) | 1 (existing) | "update ADR", "change ADR status", "deprecate ADR", "mark as Deprecated" | Edit an existing ADR body (including status transitions such as Proposed → Accepted, Accepted → Deprecated) |
| **supersede** (replace) | 2 (new + existing) | "supersede ADR", "replace with a new ADR", "mark as Superseded" | Create a new ADR in create mode, then update the old ADR to Superseded status |

Transitioning to Deprecated is an update operation where `new status = Deprecated`, not a separate mode.

Only execute the "Workflow (create mode)" section below for create mode. For update mode, see [Existing ADR Update Sub-flow](#existing-adr-update-sub-flow). For supersede mode, see [ADR Supersede Sub-flow](#adr-supersede-sub-flow).

## ADR Numbering

ADR numbers are assigned sequentially. Before creating a new ADR:

```bash
shirokuma-docs discussion adr list
```

Extract the highest existing ADR number and increment by 1.

## Workflow (create mode)

### Step 1: Gather Context

Collect decision context from the conversation or ask the user:

| Required | Information |
|----------|-------------|
| Yes | What decision was made? |
| Yes | What problem or need triggered this decision? |
| Yes | What alternatives were considered? |
| Recommended | What are the consequences (positive and negative)? |
| Optional | Who was involved in the decision? |
| Optional | Related ADRs (supersedes, relates to) |

If key information is missing, use `AskUserQuestion` to gather it.

### Step 2: Search Existing ADRs

Check for related or conflicting ADRs:

```bash
shirokuma-docs discussion adr list
shirokuma-docs discussion search "relevant keywords"
```

If a related ADR exists, note it in the "Related Decisions" section.

### Step 3: Determine ADR Depth

| Depth | When | Template |
|-------|------|----------|
| Standard | Most decisions | [Standard ADR](reference/adr-templates.md#standard-adr) |
| Lightweight | Small, low-risk decisions | [Lightweight ADR](reference/adr-templates.md#lightweight-adr) |

**Lightweight criteria**: Single-option decision with obvious rationale, low blast radius, easily reversible.

### Step 4: Generate ADR Content

Write the ADR to a temporary file using the appropriate template from [reference/adr-templates.md](reference/adr-templates.md).

```bash
cat > /tmp/shirokuma-docs/adr-{number}.md << 'ADREOF'
{ADR content from template}
ADREOF
```

### Step 5: Create Discussion

```bash
shirokuma-docs discussion adr create "ADR-{NNN}: {title}"
```

Then update the body with the generated content:

```bash
# Write updated content to temp file, then update
shirokuma-docs issue update {discussion-number} --body /tmp/shirokuma-docs/{discussion-number}-body.md
```

### Step 6: Link Related ADRs

If this ADR supersedes another:

1. Comment on the superseded ADR noting the new one
2. Include `Superseded by ADR-{NNN}` in the old ADR

## ADR Status Management

| Status | Meaning | When to Set |
|--------|---------|-------------|
| Proposed | Decision under discussion | Initial creation |
| Accepted | Decision confirmed | After team agreement |
| Deprecated | No longer relevant | When context changes |
| Superseded | Replaced by newer ADR | When new ADR replaces this |

Status is tracked in the ADR body header. Update with:

```bash
# Write updated body to temp file, then update
shirokuma-docs issue update {number} --body /tmp/shirokuma-docs/{number}-body.md
```

## Existing ADR Update Sub-flow

**Applicable mode:** update

Edit the body of a single ADR. Status transitions (e.g., Proposed → Accepted, Accepted → Deprecated) are also handled in this sub-flow. Transitioning to Superseded spans two ADRs and is handled in the [ADR Supersede Sub-flow](#adr-supersede-sub-flow) instead.

### Step 1: Get Target ADR Number

```bash
shirokuma-docs discussion adr list
```

Display the list and confirm the target ADR number via AskUserQuestion.

### Step 2: Confirm Change Type

Use AskUserQuestion to confirm:

> How do you want to update this ADR?
> - **Body only**: Keep the status unchanged and edit Context/Decision/Consequences sections
> - **Status change (Proposed → Accepted, etc.)**: Move to an approved status
> - **Status change (→ Deprecated)**: No longer relevant, deprecated without replacement (if there is a replacement, use supersede mode instead)

> **Note:** If the user requests "mark as Superseded", this sub-flow does not apply. Redirect to the [ADR Supersede Sub-flow](#adr-supersede-sub-flow).

### Step 3: Retrieve and Update ADR Body

```bash
# Retrieve ADR body
shirokuma-docs discussion adr get {number}
```

Edit the retrieved body and write to a temp file:
- **Body-only update**: Edit the target sections
- **Status change**: Update the header `**Status:** {old value}` → `**Status:** {new value}`
- Append change record and rationale to the "Change History" section at the end of the body (add section if missing)

```bash
# Apply updated body
shirokuma-docs issue update {discussion-number} --body /tmp/shirokuma-docs/{number}-body.md
```

### Step 4: Completion Report

```markdown
## ADR Updated

**Number:** ADR-{NNN}
**Change type:** {body update|status change}
**Previous Status:** {Proposed|Accepted}
**New Status:** {Accepted|Deprecated}
**Discussion:** #{discussion-number}
```

> **Field classification:** `**Previous Status:**` and `**New Status:**` are Conditional fields output only on status changes. For body-only updates, include only `**Change type:** body update` and omit the status fields.

## ADR Supersede Sub-flow

**Applicable mode:** supersede

A two-ADR operation that creates a new ADR and transitions the old ADR to Superseded status. This is an integrated flow that runs create and update in sequence.

### Step 1: Get Old ADR Number

```bash
shirokuma-docs discussion adr list
```

Display the list and confirm the old ADR number to be replaced via AskUserQuestion.

### Step 2: Collect Supersede Rationale and New ADR Context

Use AskUserQuestion to collect:

- Why the old ADR is being replaced (technology evolution, requirement change, decision re-evaluation, etc.)
- Content of the new decision
- Alternatives considered
- Expected consequences

### Step 3: Create the New ADR (internally execute create mode)

Execute Steps 2-5 of [Workflow (create mode)](#workflow-create-mode) to create the new ADR Discussion. In the new ADR body's "Related Decisions" section, record `**Supersedes:** ADR-{old-number}`.

### Step 4: Update the Old ADR's Status (internally execute update mode)

Use Step 3 of the [Existing ADR Update Sub-flow](#existing-adr-update-sub-flow) to update the old ADR body:

- `**Status:** Accepted` → `**Status:** Superseded by ADR-{new-number}`
- Append `Superseded by ADR-{new-number}: {reason}` to the Change History section

### Step 5: Add Reference Comment on the Old ADR

```bash
# Add comment to old ADR
cat > /tmp/shirokuma-docs/{old-number}-comment.md << 'EOF'
This ADR has been replaced by ADR-{new-number}. See #{new-discussion-number} for details.
EOF
shirokuma-docs issue comment {old-discussion-number} --file /tmp/shirokuma-docs/{old-number}-comment.md
```

### Step 6: Completion Report

```markdown
## ADR Superseded

**New ADR:** ADR-{new-number} (Discussion #{new-discussion-number})
**Old ADR:** ADR-{old-number} (Discussion #{old-discussion-number})
**Previous Status:** Accepted
**New Status:** Superseded by ADR-{new-number}
**Supersede reason:** {summary}
```

## Requirement Change Proposal and Approval Flow

**Target scenario:** When an existing Accepted ADR or confirmed requirement needs to be overturned.

### Flow Overview

1. **Propose**: Collect the change reason, impact scope, and alternatives via AskUserQuestion
2. **Approve**: Select via AskUserQuestion: "Create a new ADR and mark the old one as Superseded" or "Change the existing ADR status to Deprecated"
3. **Update old ADR**: Execute the sub-flow for the selected mode
4. **Notify**: After the status change, post a comment with change details to affected related Issues (optional: confirm with user)

### Approval Branch

| Selection | Mode Used | Action |
|-----------|-----------|--------|
| Create new ADR and mark as Superseded | supersede | Execute the [ADR Supersede Sub-flow](#adr-supersede-sub-flow) (create new ADR + update old ADR) |
| Only change to Deprecated | update | Execute the [Existing ADR Update Sub-flow](#existing-adr-update-sub-flow) with new status set to Deprecated |

## Completion Report (create mode)

```markdown
## ADR Created

**Number:** ADR-{NNN}
**Title:** {title}
**Status:** {Proposed|Accepted}
**Discussion:** #{discussion-number}
[**Supersedes:** ADR-{old-number}]
```

## Edge Cases

| Situation | Action |
|-----------|--------|
| ADR number conflict | Re-check `discussion adr list` and use next available |
| Related ADR found during search | Reference it in "Related Decisions" |
| User unsure about alternatives | Help brainstorm with `AskUserQuestion` |
| Decision is trivial | Suggest lightweight template or skip ADR |
| Superseding an existing ADR | Update both old and new ADR bodies |

## Scope

**Category:** Mutation worker — creates and updates Discussions.

This skill handles:
- Creating new ADR Discussions (create mode)
- Editing an existing ADR body and transitioning its status (update mode, including Proposed → Accepted and Accepted → Deprecated)
- Creating a new ADR and marking the old one as Superseded (supersede mode, two-ADR replacement operation)
- Guiding the requirement change proposal and approval flow

Out of scope:
- Modifying code or configuration files
- Discussion operations unrelated to ADR lifecycle management

## Rules

1. **Always search first** — avoid duplicate or conflicting ADRs
2. **Context over conclusion** — the reasoning matters more than the decision itself
3. **Record trade-offs honestly** — include both positive and negative consequences
4. **One decision per ADR** — keep ADRs focused and atomic
5. **Immutable history** — deprecate or supersede, never delete ADRs

## Anti-patterns

- Do not create ADRs for trivial decisions (library minor version bumps, formatting choices)
- Do not combine multiple unrelated decisions into one ADR
- Do not skip the search step — duplicate ADRs cause confusion
- Do not write ADR content in a language other than the project's `output-language` rule

## Tools

| Tool | When |
|------|------|
| Bash | `shirokuma-docs discussion adr` commands, temp file creation |
| Read | Reading existing ADR content for superseding links |
| AskUserQuestion | Gathering missing decision context from user |

TaskCreate / TaskUpdate not needed (6-step linear workflow with no branching).
