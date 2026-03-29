---
name: writing-adr
description: Creates Architecture Decision Records (ADRs) as GitHub Discussions following Michael Nygard's format and MADR best practices. Triggers: "ADR", "architecture decision", "create ADR", "write ADR", "record decision".
allowed-tools: Bash, Read, AskUserQuestion
---

# Writing ADR

Create Architecture Decision Records (ADRs) as GitHub Discussions (ADR category) with consistent structure and quality.

## When to Use

| Trigger | Example |
|---------|---------|
| Architecture decision confirmed | "We chose PostgreSQL over MongoDB" |
| Technology selection | "Use Drizzle ORM for database access" |
| Pattern or convention established | "All API routes use middleware auth" |
| Trade-off evaluation completed | "Chose SSR over SSG for dashboard" |
| User explicitly requests | "Create ADR for X", "Record this decision" |

## ADR Numbering

ADR numbers are assigned sequentially. Before creating a new ADR:

```bash
shirokuma-docs items adr list
```

Extract the highest existing ADR number and increment by 1.

## Workflow

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
shirokuma-docs items adr list
shirokuma-docs items discussions search "relevant keywords"
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
shirokuma-docs items adr create "ADR-{NNN}: {title}"
```

Then update the body with the generated content:

```bash
shirokuma-docs items pull {discussion-number}
# Edit the body in .shirokuma/github/{discussion-number}.md then push
shirokuma-docs items push {discussion-number}
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
shirokuma-docs items pull {number}
# Edit the body in .shirokuma/github/{number}.md then push
shirokuma-docs items push {number}
```

## Completion Report

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
| ADR number conflict | Re-check `items adr list` and use next available |
| Related ADR found during search | Reference it in "Related Decisions" |
| User unsure about alternatives | Help brainstorm with `AskUserQuestion` |
| Decision is trivial | Suggest lightweight template or skip ADR |
| Superseding an existing ADR | Update both old and new ADR bodies |

## Scope

**Category:** Mutation worker — creates Discussions.

This skill creates ADR Discussions only. It does not:
- Modify code or configuration files
- Update existing ADR content (use `items pull` → edit cache body → `items push`)
- Manage ADR lifecycle beyond initial creation and superseding links

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
| Bash | `shirokuma-docs items adr` commands, temp file creation |
| Read | Reading existing ADR content for superseding links |
| AskUserQuestion | Gathering missing decision context from user |

TaskCreate / TaskUpdate not needed (6-step linear workflow with no branching).
