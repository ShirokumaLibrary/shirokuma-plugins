# Implementation Work Type Reference

Guide for delegating from `working-on-issue` to `code-issue` (subagent).

## Delegation Structure

```text
working-on-issue (manager = main AI)
  → code-issue (subagent worker)
      → coding-nextjs (Skill delegation, Next.js specific)
      → direct edit (Markdown, skills, config, etc.)
```

## Delegation Conditions

| Condition | Route |
|-----------|-------|
| Labels: `area:frontend`, `area:cli` + Next.js related | `code-issue` → `coding-nextjs` |
| Keywords: `implement`, `create`, `add`, `build` | `code-issue` → `coding-nextjs` |
| Keywords: `fix`, `bug` | `code-issue` → `coding-nextjs` or direct edit |
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

## What coding-nextjs Provides

- Next.js-specific templates (Server Actions, components, pages)
- Framework-specific patterns (Better Auth, Drizzle ORM, CSP, CSRF, etc.)
- Large-scale feature implementation guidelines

## Standalone Invocation

Users can also invoke `/coding-nextjs` directly (non-subagent, with Tasks API/AskUserQuestion access). `code-issue` is the standard route from `working-on-issue`, but the existing standalone invocation path is maintained.
