# Implementation Work Type Reference

Guide for delegating from `working-on-issue` to `code-issue` (subagent).

## Delegation Structure

```text
working-on-issue (manager = main AI)
  → code-issue (subagent worker)
      → framework-specific skill (Skill delegation, dynamically discovered via `skills routing coding`)
      → direct edit (Markdown, skills, config, etc.)
```

## Delegation Conditions

| Condition | Route |
|-----------|-------|
| Labels: `area:frontend`, `area:cli` + framework related | `code-issue` → discovered `coding-*` skill |
| Keywords: `implement`, `create`, `add`, `build` | `code-issue` → discovered `coding-*` skill |
| Keywords: `fix`, `bug` | `code-issue` → discovered `coding-*` skill or direct edit |
| Markdown / documentation | `code-issue` → direct edit |
| Skill / rule / agent editing | `code-issue` → direct edit |
| Refactoring | `code-issue` → direct edit |
| Config / Chore | `code-issue` → direct edit |

## TDD Integration

TDD common workflow is **required** for implementation work:

```text
[TDD: Test Design → Creation → Gate] → code-issue → [TDD: Test Run → Verification]
```

`working-on-issue` orchestrates TDD steps, `code-issue` focuses on implementation only.

## What Framework-Specific Skills Provide

Framework-specific coding skills (e.g., `coding-nextjs` from `shirokuma-nextjs` plugin) provide:

- Framework-specific templates (Server Actions, components, pages, etc.)
- Framework-specific patterns (auth, ORM, styling, security, etc.)
- Large-scale feature implementation guidelines

## Standalone Invocation

Users can invoke framework-specific skills directly (non-subagent, with Tasks API/AskUserQuestion access). `code-issue` is the standard route from `working-on-issue`, but standalone invocation paths are maintained.
