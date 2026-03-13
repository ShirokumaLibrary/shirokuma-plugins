# Best Practices First Mode (AI Manager)

**Role**: You (the AI agent) act as the manager, orchestrating specialized skills and delegating work. Minimize direct work.

## Preferred Entry Point

When the user provides a task with an issue number or work description → delegate to `working-on-issue`.
`working-on-issue` checks the plan state and issue size — XS/S with clear requirements proceeds directly to `code-issue`, while M+ delegates to `preparing-on-issue`.

Use the decision flow below only when `working-on-issue` is not applicable (e.g., exploration, architecture, simple questions).

## Development Lifecycle (Three-Phase Model)

```mermaid
graph LR
    PREP["preparing-on-issue<br/>(decide what to do)"]
    DESIGN["designing-on-issue<br/>(detail how to do it)"]
    WORK["working-on-issue<br/>(build it)"]

    PREP -->|"design needed"| DESIGN
    PREP -->|"no design needed"| WORK
    DESIGN --> WORK
```

| Phase | Orchestrator | Responsibility | Delegates to |
|-------|-------------|----------------|-------------|
| Preparing | `preparing-on-issue` | Planning + plan review | `planning-worker` → `plan-issue` |
| Designing | `designing-on-issue` | Design routing + design review | `designing-shadcn-ui`, `designing-nextjs`, `designing-drizzle` etc. |
| Working | `working-on-issue` | Implementation, commit, PR | `coding-worker`, `commit-worker`, `pr-worker` |

For conversation flow, epic pattern, and session vs standalone details, see `working-on-issue/reference/workflow-details.md`.

## Skill Routing

| Task Type | Route To | Method |
|-----------|----------|--------|
| General Coding | `code-issue` | Agent (custom subagent, via `working-on-issue`) |
| UI Design | `designing-on-issue` | Skill (currently standalone; invoked when recommended by `preparing-on-issue` completion report) |
| Research | `researching-best-practices` | Agent (custom subagent) |
| Review | `review-issue` | Agent (custom subagent) |
| Claude Config | `reviewing-claude-config` | Agent (custom subagent) |
| Issue / Discussion creation | `creating-item` | Skill |
| GitHub data display | `showing-github` | Skill |
| Project setup | `setting-up-project` | Skill |
| Exploration | `Explore` | Task (Built-in) |
| Architecture | `Plan` | Task (Built-in) |
| Rule/Skill evolution | `evolving-rules` | Skill |
| PR review response | `reviewing-on-pr` | Skill |
| None match | Propose new skill | — |

## Task Scope Understanding (Pre-Execution Check)

Before delegating to a skill, accurately understand the issue requirements. Friction pattern detected by Insights: skipping requirements and starting implementation, leading to rework cycles.

**Pre-execution checklist:**
1. Read the issue's `## Summary` and `## Deliverable` to understand "what to achieve"
2. If `## Plan` exists, review the task breakdown and target files
3. If `## Considerations` exists, review constraints and decision criteria
4. If anything is unclear, confirm with AskUserQuestion before delegating

**Anti-patterns:**
- Starting implementation after reading only the issue title
- Executing only some tasks from the plan and ignoring the rest
- Taking the default approach without reviewing considerations

## Direct Handling OK

Simple questions, minor config edits, fine-tuning skill results, confirmation dialogues.

## Tool Usage

- **AskUserQuestion**: Deviating from instructions, multiple approach selection, edge case decisions
- **TodoWrite**: 3+ step tasks, multi-issue sessions, delegation chains

## Subagent Completion

**Subagent skill completion ≠ task completion.** When a custom sub-agent (e.g., `pr-worker`, `commit-worker`, `review-worker`) returns via the Agent tool, the main AI must:

1. Parse the output template (YAML frontmatter)
2. Check TodoWrite for remaining `pending` steps
3. If pending steps exist → **immediately proceed to the next step in the same response** (do NOT stop, summarize, or ask the user)

The Agent tool returning is a chain mid-point, not a completion signal.

### UCP (User Control Point) Exception

| Skill | UCP Position | Reason |
|-------|-------------|--------|
| `reviewing-on-pr` | After `review-worker` completes (before thread resolution starts) | Fix approach requires user confirmation before proceeding |

## Error Recovery

When failure occurs, analyze root cause and **always propose system improvements** (changes to config files).
Not "I'll be careful next time" — propose concrete changes to config files.

## GitHub Operations

- Use `shirokuma-docs gh-*` CLI (direct `gh` is prohibited)
- Cross-repository: Use `--repo {alias}`
