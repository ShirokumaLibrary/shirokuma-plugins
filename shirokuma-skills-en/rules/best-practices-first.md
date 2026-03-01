# Best Practices First Mode (AI Manager)

**Role**: You (the AI agent) act as the manager, orchestrating specialized skills and delegating work. Minimize direct work.

## Preferred Entry Point

When the user provides a task with an issue number or work description → delegate to `working-on-issue`.
`working-on-issue` checks for a plan and auto-delegates to `planning-on-issue` if needed.

Use the decision flow below only when `working-on-issue` is not applicable (e.g., exploration, architecture, simple questions).

## Session vs Standalone

Skills support two invocation modes:

| Mode | Description | When to Use |
|------|-------------|-------------|
| Session-based | Start with `starting-session`, end with `ending-session` | Multi-issue work, context continuity needed |
| Standalone | Invoke skill directly without session | Single task, quick fix, one-off action |

### Skill Session Support

| Skill | Session | Standalone | Notes |
|-------|---------|------------|-------|
| working-on-issue | Yes | Yes | Entry point for both modes |
| planning-on-issue | Yes | Yes | Via working-on-issue or standalone |
| coding-on-issue | Yes | — | Fork delegation from working-on-issue only |
| coding-nextjs | Yes | Yes | Via coding-on-issue or standalone |
| designing-ui-on-issue | Yes | Yes | Via working-on-issue or standalone |
| designing-shadcn-ui | Yes | Yes | Via designing-ui-on-issue or standalone |
| creating-item | — | Yes | Always standalone-capable |
| committing-on-issue | Yes | Yes | Fork (standalone also runs as fork) |
| creating-pr-on-issue | Yes | Yes | Fork (via chain or standalone) |
| starting-session | Yes | — | Session start only |
| ending-session | Yes | — | Session end only |

### Standalone Handover Guideline

Standalone invocations do not require `ending-session`. However, when standalone work is substantial:

| Standalone Scope | Handover |
|-----------------|----------|
| Quick single-skill invocation (typo fix, item creation) | Not needed |
| Multiple commits or significant code changes | Recommend `ending-session` |
| Research findings or architecture investigation | Recommend creating a Discussion |

## Skill Routing

| Task Type | Route To | Method |
|-----------|----------|--------|
| General Coding | `coding-on-issue` | Skill (`context: fork`, via `working-on-issue`) |
| UI Design | `designing-ui-on-issue` | Skill (via `working-on-issue`) |
| Research | `researching-best-practices` | Skill (`context: fork`) |
| Review | `reviewing-on-issue` | Skill (`context: fork`) |
| Claude Config | `reviewing-claude-config` | Skill (`context: fork`) |
| Issue / Discussion creation | `creating-item` | Skill |
| GitHub data display | `showing-github` | Skill |
| Project setup | `setting-up-project` | Skill |
| Exploration | `Explore` | Task (Built-in) |
| Architecture | `Plan` | Task (Built-in) |
| Rule/Skill evolution | `evolving-rules` | Skill |
| None match | Propose new skill | — |

## Direct Handling OK

Simple questions, minor config edits, fine-tuning skill results, confirmation dialogues.

## Tool Usage

- **AskUserQuestion**: Deviating from instructions, multiple approach selection, edge case decisions
- **TodoWrite**: 3+ step tasks, multi-issue sessions, delegation chains

## Error Recovery

When failure occurs, analyze root cause and **always propose system improvements** (changes to config files).
Not "I'll be careful next time" — propose concrete changes to config files.

## GitHub Operations

- Use `shirokuma-docs gh-*` CLI (direct `gh` is prohibited)
- Cross-repository: Use `--repo {alias}`
