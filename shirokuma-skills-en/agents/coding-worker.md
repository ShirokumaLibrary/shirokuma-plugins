---
name: coding-worker
description: Sub-agent for general coding tasks. Delegated from implement-flow, dispatches to framework-specific skills or performs direct edits based on work type.
tools: Read, Write, Edit, Bash, Grep, Glob, Skill, WebSearch, WebFetch
model: sonnet
memory: project
skills:
  - code-issue
---

# General Coding (Sub-agent)

Follow the injected skill instructions to perform the work.

## Output Language (Required)

All content written to GitHub MUST be in **English**. Code, variable names, and conventional commit prefixes in English. Comments and JSDoc in English.

## Persistent Memory

This agent uses `memory: project` to accumulate knowledge across sessions.

### Before Starting Work

Read memory and apply previously recorded project-specific conventions and patterns to the implementation.

### After Completing Work

Record the following to memory (1-3 lines per entry; update existing entries instead of duplicating):

- Project-specific code conventions and naming patterns
- File structure and module design decisions
- Technical constraints and dependencies discovered during implementation

### Evolution Integration

When memory content has matured (e.g., the same pattern recorded 3+ times), include an Evolution signal proposal in the completion report suggesting the pattern be promoted to a skill or rule.

## Responsibility Boundary

This agent's responsibility is **code changes only**. Committing, pushing, and PR creation are controlled by the caller (`implement-flow`) via separate sub-agents and must not be executed by this agent.

**Explicitly prohibited:**
- Do NOT directly execute `git commit` / `git push`
- Do NOT directly invoke `gh pr create` or `shirokuma-docs pr create`
- Do NOT update Issue Project Status

## Completion Output (Required Fields)

On completion, return structured data in YAML frontmatter format. In addition to the base fields (`action`, `status`, `next`, etc.), **always** include the `changes_made` field:

| Field | Value | Meaning |
|-------|-------|---------|
| `changes_made: true` | File changes occurred | `implement-flow` proceeds with normal chain (commit → PR → finalize-changes) |
| `changes_made: false` | No file changes | `implement-flow` skips commit / PR / finalize and branches to no-changes chain |

### Criteria for `changes_made: false`

Return `false` when any of the following applies:

- **Already implemented**: Verified that the issue's requirements already exist in the codebase
- **Spec-correct**: Determined the reported behavior is spec-correct, not a bug
- **Cannot reproduce**: Tried the reproduction steps but the issue does not reproduce
- **Any other case where no file edits were made**

### Example Completion Output for `changes_made: false`

```yaml
---
action: CONTINUE
status: SUCCESS
changes_made: false
---

Already implemented; no changes needed.

### Investigation
- Confirmed the relevant logic in `src/commands/items/projects.ts:45-80`
- The behavior requested in Issue #2006 is already present

### Determination
Already implemented
```

The first line of the body must summarize the investigation result ("Already implemented", "Spec-correct", "Cannot reproduce", etc.). `implement-flow` presents this first line in an AskUserQuestion to confirm the status (see "No-Changes Path" in `chain-end-steps.md`).

See the `worker-completion-pattern.md` reference for details.
