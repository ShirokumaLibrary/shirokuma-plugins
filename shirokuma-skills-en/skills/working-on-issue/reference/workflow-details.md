# Workflow Details

Supplementary details for the `best-practices-first` rule. Covers conversation flow, epic pattern, and session vs standalone details.

## Conversation Flow

Each phase typically runs in a separate Claude Code conversation. Context flows between conversations via Issue body (plan) and Issue comments (work summaries).

```mermaid
graph TD
    C1["Conversation 1: Issue creation<br/>/creating-item (standalone)"]
    C2["Conversation 2: Planning<br/>/preparing-on-issue #N (standalone)"]
    C2D["Conversation 2.5: Design (optional)<br/>/designing-on-issue #N (standalone)"]
    C3["Conversation 3: Implementation<br/>Small: /working-on-issue #N (standalone)<br/>Large: /starting-session #N"]
    C4["Conversation 4: Continuation (large only)<br/>/starting-session #N → context restore"]

    C1 -->|"Backlog → user decision"| C2
    C2 -->|"design needed"| C2D
    C2 -->|"no design needed (Spec Review → user approval)"| C3
    C2D -->|"Spec Review → user approval"| C3
    C3 -->|"context overflow"| C4
    C3 -->|"completed"| Done["PR → Review → Done"]
    C4 --> Done
    Done -->|"review feedback"| C5["Conversation 5: Review response<br/>/reviewing-on-pr #PR (standalone)"]
    C5 --> Done
```

Small tasks may complete planning + implementation in a single conversation.

## Epic Pattern (XL Issues with Sub-Issues)

```mermaid
graph TD
    E1["Conversation 1: Epic planning<br/>/preparing-on-issue #N"]
    E2["Conversation 2: Epic kickoff<br/>/working-on-issue #N<br/>(auto-creates sub-issues + integration branch)"]
    E3["Conversation 3+: Sub-issue work<br/>/working-on-issue #sub (standalone)<br/>or /starting-session #sub"]

    E1 -->|"Spec Review → user approval"| E2
    E2 -->|"sub-issues created"| E3
    E3 -->|"all sub-issues done"| Final["Final PR: integration → develop"]
```

Key points:
- `/working-on-issue #{epic}` auto-creates sub-issues from the plan and creates the integration branch
- Each sub-issue is worked on independently (standalone or session)
- Parent issue session recommended for managing cross-cutting context across sub-issues

## Session vs Standalone

### Session Usage Criteria

Use sessions when **context overflow risk** is high — i.e., the work is likely to span multiple conversations and context continuity provides significant value.

| Use Session | Use Standalone |
|-------------|---------------|
| Many files modified (10+) | Completes in one conversation |
| Epic (parent issue bound session + sub-issue standalone) | Localized changes (1-3 files) |
| Multi-day work (M/L size) | Independent single task |
| Two-phase work (research → implement) | Documentation, config changes |

### Skill Session Support

| Skill | Session | Standalone | Notes |
|-------|---------|------------|-------|
| working-on-issue | Yes | Yes | Entry point for both modes |
| preparing-on-issue | Yes | Yes | Via working-on-issue or standalone |
| plan-issue | Yes | — | Subagent via planning-worker (from preparing-on-issue) |
| code-issue | Yes | — | Subagent delegation from working-on-issue only |
| coding-nextjs | Yes | Yes | Via code-issue or standalone |
| designing-on-issue | — | Yes | Currently standalone (invoked from preparing-on-issue completion report) |
| designing-shadcn-ui | Yes | Yes | Via designing-on-issue or standalone |
| designing-nextjs | Yes | Yes | Via designing-on-issue or standalone |
| creating-item | — | Yes | Always standalone-capable |
| commit-issue | Yes | Yes | Subagent (standalone also runs as subagent) |
| open-pr-issue | Yes | Yes | Subagent (via chain or standalone) |
| reviewing-on-pr | — | Yes | PR review response (new conversation entry point) |
| starting-session | Yes | — | Session start only (`#N` for issue-bound, no arg for unbound) |
| ending-session | Yes | — | Session end only |

### Standalone Handover Guideline

Standalone `working-on-issue` automatically posts a work summary to the Issue comment on chain completion. No `ending-session` needed.

For substantial standalone work without `working-on-issue`:

| Standalone Scope | Action |
|-----------------|--------|
| Quick single-skill invocation (typo fix, item creation) | Not needed |
| Multiple commits or significant code changes | Recommend `ending-session` |
| Research findings or architecture investigation | Recommend creating a Discussion |
