# Rule & Skill Evolution

## Overview

Apply the closed-loop concept from RLAnything to systematically evolve project-specific rules and skills.

```
Policy execution (daily work) → Reward observation (signal collection) → Policy update (improvement proposals) → Environment adaptation (plugin promotion)
```

## Feedback Signals

| Signal Type | Collection Timing | Example |
|------------|-------------------|---------|
| Rule friction | Anytime | Ignored rule X and manually corrected |
| Redo instruction | Anytime | Had to correct skill Z output |
| Review pattern | PR review | Same feedback pattern 3+ times |
| Lint trend | Lint execution | Rule A violations increasing |
| Task success rate | Session end | Issue completion rate |
| PR merge rate | PR merge | First-review pass rate |

## Signal Persistence

Accumulate signals as comments in Evolution Issues.

| Item | Value |
|------|-------|
| Issue Type | Evolution |
| Emoji | 🧬 |
| Title format | `[Evolution] {topic}` |

**Comment format:**

```markdown
**Type:** {Rule friction | Missing pattern | Skill improvement | Lint trend | Success rate}
**Target:** {rule name or skill name or general}
**Context:** {situation description}
**Proposal:** {improvement suggestion}
```

## Evolution Triggers

| Trigger | Condition | Action |
|---------|-----------|--------|
| Reactive | Same signal accumulated 3+ times | Analyze and propose via `evolving-rules` skill |
| Preventive | Pattern recognized during signal recording | Include proposal in comment |
| Periodic | User explicitly invokes `evolving-rules` | Analyze all accumulated signals |
| Session start | `starting-session` detects accumulated signals | Recommend `evolving-rules` invocation (no auto-execution) |
| Skill completion | `working-on-issue`, `preparing-on-issue`, `creating-item`, `designing-on-issue`, `reviewing-on-pr` complete | Auto-record via detection checklist. Display reminder as fallback when no signals detected |
| Eval failure | `skill eval` or `skill optimize` shows failures | Record eval result pattern as evolution signal. Propose description improvement via `evolving-rules` |

## Responsibility Boundaries

| Skill | Responsibility | Input |
|-------|---------------|-------|
| `discovering-codebase-rules` | Code patterns → new rule proposals | Codebase analysis |
| `evolving-rules` | Existing rule/skill improvement proposals | Evolution signals |
| `managing-rules` | Rule file creation/update (executor) | Proposal content |

**Ambiguous area:** When `discovering-codebase-rules` detects existing rule deficiencies, record as a comment in an Evolution Issue. `discovering-codebase-rules` itself does not modify rules (new proposals only).

## Rules

1. **Record signals in Issues** — Accumulate in Evolution Issues, not memory
2. **Respect thresholds** — Trigger analysis at 3+ accumulated signals, no auto-proposals below
3. **Propose cautiously** — Excessive proposals become noise. Reflect DemyAgent's "fewer tool calls are more effective"
4. **No overlap with existing skills** — `discovering-codebase-rules` discovers new patterns, `evolving-rules` improves existing
5. **User approval required** — Apply rule/skill changes only after user confirmation

For eval data reference, Evolution Issue lifecycle, auto-recording procedure at skill completion, and standalone signal recording, see `evolving-rules/reference/evolution-details.md`.
