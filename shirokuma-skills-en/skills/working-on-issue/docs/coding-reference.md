# Implementation Work Type Reference

Guide for delegating from `working-on-issue` to `coding-on-issue` (fork).

## Delegation Structure

```text
working-on-issue (manager)
  → coding-on-issue (fork worker)
      → coding-nextjs (Skill delegation, Next.js specific)
      → direct edit (Markdown, skills, config, etc.)
```

## Delegation Conditions

| Condition | Route |
|-----------|-------|
| Labels: `area:frontend`, `area:cli` + Next.js related | `coding-on-issue` → `coding-nextjs` |
| Keywords: `implement`, `create`, `add`, `build` | `coding-on-issue` → `coding-nextjs` |
| Keywords: `fix`, `bug` | `coding-on-issue` → `coding-nextjs` or direct edit |
| Markdown / documentation | `coding-on-issue` → direct edit |
| Skill / rule / agent editing | `coding-on-issue` → direct edit |
| Refactoring | `coding-on-issue` → direct edit |
| Config / Chore | `coding-on-issue` → direct edit |

## TDD Integration

TDD common workflow is **required** for implementation work:

```text
[TDD: Test Design → Creation → Gate] → coding-on-issue → [TDD: Test Run → Verification]
```

`working-on-issue` orchestrates TDD steps, `coding-on-issue` focuses on implementation only.

## What coding-nextjs Provides

- Next.js-specific templates (Server Actions, components, pages)
- Framework-specific patterns (Better Auth, Drizzle ORM, CSP, CSRF, etc.)
- Large-scale feature implementation guidelines

## Standalone Invocation

Users can also invoke `/coding-nextjs` directly (non-fork, with TodoWrite/AskUserQuestion access). `coding-on-issue` is the standard route from `working-on-issue`, but the existing standalone invocation path is maintained.
