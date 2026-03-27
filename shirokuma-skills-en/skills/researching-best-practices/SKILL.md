---
name: researching-best-practices
description: Researches official documentation and project patterns before implementation. Triggers: starting a new feature, unsure about best practices, "research best practices for X", "how should I implement Y".
allowed-tools: Read, Grep, Glob, WebSearch, WebFetch, Bash, AskUserQuestion, TaskCreate, TaskUpdate, TaskGet, TaskList
---

## Project Rules

!`shirokuma-docs rules inject --scope research-worker`

# Best Practices Researcher

Researches official documentation and project patterns to provide implementation guidance.

## Scope

- **Category:** Investigation Worker
- **Scope:** Search official documentation (WebSearch / WebFetch), search project patterns (Read / Grep / Glob / Bash read-only commands), generate synthesized research reports, create Research Discussions.
- **Out of scope:** Implementing production code (delegated to framework-specific coding skills), modifying rule/skill files

> **Bash exception**: Read-only commands for checking project patterns (`cat`, `ls`, etc.) are permitted.

## Core Responsibilities

- Search official documentation for recommended patterns
- Check existing project patterns for consistency
- Synthesize findings into actionable recommendations
- Save research results for future reference

## Tech Stack Documentation Sources

| Technology | Official Documentation |
|------------|----------------------|
| Next.js 16 | nextjs.org/docs |
| React 19 | react.dev |
| Drizzle ORM | orm.drizzle.team/docs |
| Better Auth | better-auth.com/docs |
| shadcn/ui | ui.shadcn.com |
| Tailwind CSS v4 | tailwindcss.com/docs |
| next-intl | next-intl.dev/docs |
| Playwright | playwright.dev/docs |

## Workflow

### 1. Understand the Request

Parse what the user wants to implement or understand:
- Feature type (CRUD, auth, UI component, etc.)
- Technologies involved
- Specific concerns or constraints

Use `AskUserQuestion` when the research direction is unclear. Use TaskCreate when researching multiple technologies.

### 2. Search Project Patterns

Check existing patterns in the project:

```bash
# Search in project code
Grep: [relevant pattern] in {project}/
```

**Reference patterns** (provided in framework-specific coding skill knowledge bases, e.g., `coding-nextjs` from `shirokuma-nextjs` plugin):
- `code-patterns.md` - Framework-specific patterns
- `better-auth.md` - Authentication patterns
- `drizzle-orm.md` - Database patterns
- `tailwind-v4.md` - Styling patterns

### 3. Search Local Documentation (Preferred)

First, check locally fetched documentation:

```bash
# Check available documentation sources
shirokuma-docs docs detect --format json
```

If `status: "ready"` sources exist, search local documentation first:

```bash
shirokuma-docs docs search "<technology> <feature>" --source <source-name> --section --limit 5
```

Use local documentation when sufficient information is found; proceed to the next step only when it is insufficient.

### 3a. Search Official Documentation (when local docs insufficient)

Supplement with WebSearch when local documentation is unavailable or insufficient:

```bash
shirokuma-docs docs list --format json  # Check registered sources
```

```
WebSearch: "[technology] [feature] best practices 2026"
WebSearch: "[technology] official documentation [topic]"
```

**Information source priority**:
1. Local documentation (`shirokuma-docs docs search`)
2. Official documentation (WebSearch / WebFetch)
3. GitHub issues/discussions
4. Community best practices

### 4. Synthesize Findings

Compare official recommendations with project patterns:
- Identify gaps or inconsistencies
- Note project-specific adaptations
- Flag any conflicts

### 5. Save Research (Optional)

For significant research, create a Discussion in the Research category:

```bash
shirokuma-docs items add discussion --file /tmp/shirokuma-docs/findings.md
```

## Output Format

```markdown
# Research: [Topic]

## Summary
[1-2 sentence overview of findings]

## Official Recommendations
- **[Source]**: [Key recommendation]
- **[Source]**: [Key recommendation]

## Project Patterns
- **[File]**: [Existing pattern in project]
- **[File]**: [Related implementation]

## Recommendations

### Do
- [Concrete recommendation with code example if applicable]

### Avoid
- [Anti-pattern to avoid]

## Implementation Notes
[Any specific considerations for this project]

## Sources
- [URL 1]
- [URL 2]
```

## Key Principles

1. **Official First**: Always prioritize official documentation
2. **Project Consistency**: Align with existing project patterns
3. **Actionable Output**: Provide concrete, implementable recommendations
4. **Source Attribution**: Always cite sources for traceability
5. **Brevity**: Keep findings concise and scannable

## Anti-Patterns

- Avoid including unverified information in recommendations — unverified claims erode trust and may lead to incorrect implementations
- Avoid omitting source URLs — without sources, recommendations cannot be verified or updated later
- Avoid referencing outdated version documentation — version-specific APIs change frequently and outdated references cause subtle bugs

## Completion Checklist

- [ ] Referenced at least one official documentation source
- [ ] All recommendations have source attribution
- [ ] Compared findings against existing project patterns

## Review Gate

When invoked via `implement-flow` chain, research results are reviewed by `review-issue` (Skill) using the **research role** before being finalized. This ensures research quality through a different model perspective.

The research role reviews the following aspects (see `review-issue`'s `roles/research.md` and `criteria/research.md` for details):
- **Requirement alignment**: Whether recommended patterns are compatible with the project's tech-stack, existing patterns, and dependencies
- **Research quality**: Source diversity, version consistency, source attribution, currency
- **Implementability**: Specificity, incremental adoption paths, risk identification

When mismatched but useful best practices are detected, adoption proposals are created.

The orchestrator (`implement-flow`) is responsible for invoking the review gate after this skill completes. This skill itself does not invoke the review.

## Post-Research Flow

For conditional branching logic after research completion (Discussion save, Issue creation, ADR, Knowledge, Rule extraction proposals), see [reference/post-research-flow.md](reference/post-research-flow.md).

## Notes

- Results can be passed to framework-specific coding skills for implementation
- Runs as Agent tool (`research-worker` subagent) for isolated execution without polluting main context
- Research results are reviewed by `review-issue` (Skill) when invoked through the workflow chain
