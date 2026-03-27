---
paths:
  - ".claude/skills/**/*.md"
  - ".claude/agents/**/*.md"
  - ".claude/output-styles/**/*.md"
  - ".claude/commands/**/*.md"
---

# Claude Config Authoring Rules

## Naming Convention

**Format**: `gerund-form` (verb + -ing), lowercase, hyphens, max 64 chars

```yaml
# Good
name: processing-pdfs
name: managing-agents

# Bad
name: PDF-Processor    # Not gerund, uppercase
name: helper           # Too vague
```

### Orchestrator Skill Naming Pattern

Orchestrator skills (skills that coordinate multiple workers) use the `{verb}-flow` pattern.

```yaml
# Orchestrators (good)
name: prepare-flow     # Planning phase orchestrator
name: design-flow      # Design phase orchestrator
name: implement-flow   # Implementation phase orchestrator
name: review-flow      # Review response orchestrator

# Worker skills (standard gerund form)
name: plan-issue       # Planning worker
name: code-issue       # Implementation worker
name: commit-issue     # Commit worker
```

The `-flow` suffix is reserved for orchestrators only. Do not use on worker skills.

## Description (CRITICAL)

**Template**: `[What it does]. Use when [triggers].`

**Requirements**:
- Max 1024 characters
- Third person voice
- Include WHAT (capability) and WHEN (triggers)
- NO angle brackets (`<example>` forbidden)

```yaml
# Good
description: Extract text from PDF files. Use when working with PDFs or user mentions "PDF", "PDF処理".

# Bad
description: Helps with documents  # Too vague, no triggers
```

## File Size Limits

- `SKILL.md` / `AGENT.md`: Under 500 lines
- Challenge every sentence for necessity
- Move detailed content to reference files

## Language Guidelines

| File Type | Language |
|-----------|----------|
| SKILL.md / AGENT.md | English |
| rules/*.md | English |
| output-styles/*.md | English |
| CLAUDE.md | English |
| description (SKILL.md frontmatter) | English keywords only (see below) |

- **Avoid**: Heavy table formatting (token-inefficient)
- **EN plugin description**: English keywords only (no Japanese triggers)
- **JA plugin description**: Japanese + English technical terms that Japanese users actually type (e.g., "コミット" + "commit")
- **No fake slash commands**: Only reference `/skill-name` if the command actually exists. Use plain quoted keywords instead (e.g., "commit" not "/commit")

## File Structure

```
skill-name/
├── SKILL.md        # Required, <500 lines
├── reference.md    # Optional, detailed specs
├── examples.md     # Optional, I/O examples
└── scripts/        # Optional, automation
```

## Template Definition Conventions

### Placeholder Notation

Standard notation is `{placeholder}` (curly braces, lowercase, snake_case or kebab-case).

```markdown
**Branch:** {branch-name}
**Status:** {status}
**Issue:** #{number} {title}
```

| Notation | Allowed | Use Case |
|----------|---------|----------|
| `{placeholder}` | Standard | All templates |
| `{{PLACEHOLDER}}` | Template engine files only | Handlebars `.template` files |
| `<placeholder>` | CLI command examples only | Bash argument notation |

Always use `{placeholder}` in SKILL.md explanatory text.

### Completion Report Templates

Completion report templates are only needed for **subagent skills** (invoked via Agent tool) that return structured data to the orchestrator. Skill-tool invoked skills (running in main context) follow the `completion-report-style` rule instead — no per-skill template needed.

| Skill type | Template needed | Examples |
|------------|----------------|---------|
| Subagent (Agent tool) | Yes — YAML frontmatter + markdown | commit-issue, open-pr-issue |
| Main context (Skill tool) | No — use `completion-report-style` rule | managing-rules, code-issue |

### Code Block Language Tags

| Content | Language Tag |
|---------|-------------|
| CLI command examples | `bash` |
| Config file examples | `yaml` / `json` |
| GitHub body templates | `markdown` |

## Anti-Patterns

- Deep reference chains (keep ONE level from SKILL.md)
- Windows backslashes (use forward slashes only)
- Too many options without defaults
- Vague naming without specific triggers
- Long explanations of LLM-known concepts
- Motivational/philosophy sections ("why" over "what")
- **Omitting workflows** (flows must not be left to LLM inference)
- **Omitting tool usage instructions** (TaskCreate, TaskUpdate, AskUserQuestion, etc.)
- **Omitting NG cases** (without prohibitions, LLM defaults to its own behavior)

## Validation Checklist

Before committing:
- [ ] Name: gerund form, lowercase
- [ ] Description: triggers, third person, no `<>`
- [ ] SKILL.md: under 500 lines
- [ ] Frontmatter: valid YAML (spaces, not tabs)
- [ ] Paths: forward slashes only
- [ ] **Workflow**: Step-by-step flow documented
- [ ] **Tool usage**: TaskCreate / TaskUpdate / AskUserQuestion usage points specified
- [ ] **NG cases**: Skill-specific prohibitions and checklists present
- [ ] Coder skills: Known concept explanations removed, reference only
- [ ] Reviewer skills: Checklist coverage is sufficient
- [ ] **Write quality**: GitHub write templates contain no implicit references (see "No Implicit References" section in `best-practices-writing.md`)
