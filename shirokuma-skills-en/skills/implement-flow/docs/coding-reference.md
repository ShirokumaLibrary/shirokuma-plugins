# Implementation Work Type Reference

Guide for delegating from `implement-flow` to `code-issue` (subagent).

## Delegation Structure

```text
implement-flow (manager = main AI)
  ↓ Step 3c: detect local documentation via docs detect
  → code-issue (subagent worker)
      → framework-specific skill (Skill delegation, dynamically discovered via `skills routing coding`)
      → direct edit (Markdown, skills, config, etc.)
```

## Local Documentation Integration

Before delegating coding tasks, check for local documentation availability and include `status: "ready"` sources in the `code-issue` prompt (see Step 3c). `code-issue` runs `docs search --section --limit 5` against the provided sources to aid implementation.

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

`implement-flow` orchestrates TDD steps, `code-issue` focuses on implementation only.

## What Framework-Specific Skills Provide

Framework-specific coding skills (e.g., `coding-nextjs` from `shirokuma-nextjs` plugin) provide:

- Framework-specific templates (Server Actions, components, pages, etc.)
- Framework-specific patterns (auth, ORM, styling, security, etc.)
- Large-scale feature implementation guidelines

## Standalone Invocation

Users can invoke framework-specific skills directly (non-subagent, with Tasks API/AskUserQuestion access). `code-issue` is the standard route from `implement-flow`, but standalone invocation paths are maintained.
