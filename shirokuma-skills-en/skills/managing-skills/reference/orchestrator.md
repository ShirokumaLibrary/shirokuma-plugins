# Orchestrator Skill Templates

Templates for creating project-specific orchestrator skills (`designing-*` / `coding-*`) and the specialist skills they discover and delegate to.

## Overview

The shirokuma-skills plugin includes two extensible orchestrators:

| Orchestrator | Discovers | Naming Convention |
|-------------|-----------|-------------------|
| `designing-on-issue` | `designing-*` skills | `designing-{domain}` |
| `code-issue` | `coding-*` skills | `coding-{domain}` |

These orchestrators use a hybrid discovery mechanism (`shirokuma-docs skills routing {prefix}`) to find both built-in and project-specific skills at runtime. Creating a skill that follows the naming convention automatically makes it discoverable.

## Template: Orchestrator Skill

For creating a new orchestrator that routes to specialist skills (rare — most projects extend existing orchestrators instead).

```yaml
---
name: {orchestrating-domain}
description: Routes to appropriate {domain} skills based on requirements. Delegates to {specialist-a}, {specialist-b}. Triggers: "{keyword1}", "{keyword2}".
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch, AskUserQuestion, TodoWrite, Skill
---
```

**Key requirements:**
- `allowed-tools` MUST include `Skill` (for delegation) and `AskUserQuestion` (for user decisions)
- Description must list the specialist skills it delegates to
- Include a dispatch table mapping conditions to specialist skills

### Orchestrator Structure

```markdown
# {Domain} Workflow (Orchestrator)

## Workflow

### Phase 1: Context Reception
{Gather requirements from Issue or arguments}

### Phase 2: Discovery / Analysis
{Analyze requirements to determine which specialist to invoke}

#### Skill Discovery (Run Before Dispatch)

\`\`\`bash
shirokuma-docs skills routing {prefix}
\`\`\`

#### Dispatch Table

| Type | Condition | Route |
|------|-----------|-------|
| {type-a} | {condition} | `{specialist-a}` via Skill |
| {type-b} | {condition} | `{specialist-b}` via Skill |

### Phase 3: Delegate to Specialist
{Invoke the selected specialist via Skill tool}

### Phase 4: Evaluation / Review
{Post-implementation quality check}

### Phase 5: Completion
{Return control or chain to next step}

## Notes
- This skill is an orchestrator — actual work is delegated to specialist skills
- Include AskUserQuestion for ambiguous routing decisions
```

## Template: Project-Specific Specialist Skill

For creating a specialist skill that is discovered and delegated to by an orchestrator.

### Frontmatter (Critical)

```yaml
---
name: {prefix}-{domain}
description: {What this skill does for the specific domain}. Triggers: "{keyword1}", "{keyword2}".
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
---
```

**Naming rules:**
- MUST start with `designing-` or `coding-` prefix to be discoverable
- Use kebab-case: `designing-graphql`, `coding-fastify`
- The `name` field in frontmatter MUST match the directory name
- `description` field is required — the CLI reads it for routing decisions

**allowed-tools rules:**
- Do NOT include `AskUserQuestion` — specialist skills run inside worker subagents that cannot use interactive tools
- Do NOT include `TodoWrite` — progress tracking is managed by the parent orchestrator
- Include `Skill` only if the specialist further delegates to other skills

### Specialist Structure

```markdown
# {Domain} {Design|Implementation}

{One-line purpose statement.}

> **{Design|Implementation} is this skill's responsibility.** {Other skill} handles {other concern}.

## Workflow

### 0. Tech Stack Verification
{Read CLAUDE.md and project config to confirm relevant tech stack}

### 1. Context Reception
{When delegated from orchestrator, use provided context. When standalone, gather from Issue.}

### 2. Analysis / Design
{Core domain-specific logic}

### 3. Output
{Structured output document or code changes}

### 4. Review Checklist
{Domain-specific quality checks}

## Reference Documents

| Document | Content | When to Read |
|----------|---------|--------------|
| [patterns/{file}](patterns/{file}) | {description} | {condition} |

## Anti-Patterns
{Domain-specific anti-patterns to avoid}

## Next Steps

When delegated from orchestrator, control returns automatically.

When standalone:
\`\`\`
{Domain} complete. Next steps:
-> /commit-issue to commit changes
-> /working-on-issue for the full workflow
\`\`\`

## Notes
- Build verification is NOT needed for design-only skills
- When delegated, use the provided Design Brief / context as-is
```

## Discovery Mechanism

### How It Works

1. The orchestrator calls `shirokuma-docs skills routing {prefix}` before dispatch
2. The CLI scans available skills matching the `{prefix}-*` naming pattern
3. Each discovered skill's `description` is returned for routing decisions
4. The orchestrator routes to the best-matching skill based on Issue requirements

### Sources

| Source | Priority | Example |
|--------|----------|---------|
| Built-in (plugin) | Higher | `designing-shadcn-ui`, `coding-nextjs` |
| Project `.claude/skills/` | Standard | `.claude/skills/designing-graphql/SKILL.md` |
| Config `shirokuma-docs.config.yaml` | Standard | `skills.routing.designing` entries |

### Making a Skill Discoverable

1. Name it `{prefix}-{domain}` (e.g., `designing-graphql`)
2. Include `name` and `description` in YAML frontmatter
3. Place in `.claude/skills/` or plugin `skills/` directory
4. The skill appears in `shirokuma-docs skills routing {prefix}` output

## Dispatch Compatibility Checklist

Before creating an orchestrator-compatible specialist skill, verify:

- [ ] **Name**: Starts with `designing-` or `coding-` prefix
- [ ] **Frontmatter**: Has `name` and `description` fields
- [ ] **allowed-tools**: Does NOT include `AskUserQuestion` or `TodoWrite`
- [ ] **Context reception**: Handles both delegated (with context) and standalone modes
- [ ] **No build verification**: Design skills skip build steps (orchestrator handles this)
- [ ] **Next steps**: Includes both delegated and standalone next steps sections
